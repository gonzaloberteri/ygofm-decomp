"""Attempt every candidate function automatically: m2c -> compile -> compare.

m2c's `--valid-syntax` mode emits C that compiles without human intervention,
so a large share of small functions can be matched with no hand-editing at all.
Whatever matches is kept; whatever does not is left for manual work, with the
mismatch recorded so the hard cases can be triaged by shape rather than one at
a time.

    py -3 tools/autodecomp.py --limit 50
    py -3 tools/autodecomp.py --all
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import threading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import funcs as funcs_mod                                        # noqa: E402
from match import asm_inventory, object_functions, original_words  # noqa: E402

M2C = os.path.join(REPO, "tools", "m2c", "m2c.py")
CC = os.path.join(REPO, "tools", "cc.py")
ASM = os.path.join(REPO, "asm", "code_002800.s")
CONTEXT = os.path.join(REPO, "build", "context.c")
OUTDIR = os.path.join(REPO, "src", "auto")
GAME_END = funcs_mod.GAME_END

HEADER = '#include "types.h"\n#include "m2c_macros.h"\n\n'

GP_BASE = 0x8009AF08
# m2c does not know what $gp points at, so a small-data access comes out as
# M2C_FIELD(saved_reg_gp, s8 *, 0x239) with saved_reg_gp left undeclared.  $gp is
# a known constant, so each of those names a specific global: rewriting it into a
# real extern at gp+offset both compiles and lets the assembler emit the GPREL16
# relocation that reproduces the original offset.
#
# Two syntactic families occur, and both have to be recognised or the whole
# function is thrown away:
#
#   M2C_FIELD(saved_reg_gp, T *, off)   the object at gp+off, read as T
#   saved_reg_gp + off                  the *address* gp+off (addiu $r, $gp, off)
#
# The offset itself is never checked by tools/match.py -- R_MIPS_GPREL16 masks
# the low 16 bits away, since the linker owns them -- so it has to be right by
# construction rather than by observation.  It is: the offset is what picks the
# extern's name, and the name is what the link resolves back to gp+off.  The
# load/store opcode and base register are *not* masked, so a wrong type does
# show up as a mismatch rather than as a false match.
GP_FIELD_HEAD = re.compile(r"\bM2C_FIELD\(\s*saved_reg_gp\s*,")
GP_ADDR = re.compile(r"\bsaved_reg_gp\s*([-+])\s*"
                     r"(0[xX][0-9A-Fa-f]+|\d+)\b")
# "T *", "T **", ... -- a plain object or pointer type
GP_PLAIN_TYPE = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*(?:\s+[A-Za-z_][A-Za-z0-9_]*)*)\s*(\*+)$")
# "M2C_UNK (**)(void *, s32)" -- pointer to a function pointer.  The name has to
# go inside the parentheses, which is why this cannot share the plain path.
GP_FUNC_TYPE = re.compile(r"^(.*?)\(\s*\*\s*\*\s*\)\s*(\(.*\))$", re.S)
INT_LITERAL = re.compile(r"^[-+]?(?:0[xX][0-9A-Fa-f]+|[0-9]+)$")


def _const(text):
    """Integer value of a C integer literal, or None if it is not one."""
    text = text.strip()
    if not INT_LITERAL.match(text):
        return None
    return int(text, 16) if "x" in text.lower() else int(text, 10)


def _gp_decl(ctype, name):
    """`extern` declaration of the object that `*(ctype)(gp + off)` reads.

    m2c's second M2C_FIELD argument is a *pointer* to the accessed object, so
    the object's own type is that with one indirection removed -- and the name
    belongs wherever C's declarator syntax puts it, which for a function
    pointer is inside the parentheses.  Returns None for any type this cannot
    reproduce exactly; guessing would cost more downstream than skipping does.
    """
    ctype = " ".join(ctype.split())
    m = GP_FUNC_TYPE.match(ctype)
    if m:
        # "M2C_UNK (**)(void *)" -> "M2C_UNK (*D_800E9DB0)(void *)"
        return "%s (*%s)%s" % (m.group(1).strip(), name, m.group(2))
    m = GP_PLAIN_TYPE.match(ctype)
    if m:
        base, stars = m.group(1), m.group(2)[:-1]
        if not stars and base == "void":
            return None            # `extern void x;` is not a declaration
        return "%s %s%s" % (base, stars, name)
    return None


def _split_args(text):
    """Split a macro argument list on its top-level commas."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def _close_paren(text, i):
    """Index just past the ')' matching the '(' at text[i], or -1."""
    depth = 0
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def rewrite_gp(body):
    """Replace saved_reg_gp accesses with declared externs at gp+offset."""
    decls = {}

    def declare(name, decl):
        # One address cannot be two different types at once.  m2c does not
        # currently produce that, but silently keeping one of the two would
        # change what the other access reads, so refuse instead.
        return decls.setdefault(name, decl) == decl

    # Field accesses.  Innermost first, because M2C_FIELD nests -- the outer
    # one's base is the inner one's result and must not be touched here.
    while True:
        m = GP_FIELD_HEAD.search(body)
        if m is None:
            break
        open_at = body.index("(", m.start())
        end = _close_paren(body, open_at)
        if end < 0:
            return None, None
        args = _split_args(body[open_at + 1:end - 1])
        if len(args) != 3:
            return None, None
        off = _const(args[2])
        if off is None:
            return None, None      # computed offset: not one fixed global
        name = "D_%08X" % (GP_BASE + off)
        decl = _gp_decl(args[1].strip(), name)
        if decl is None or not declare(name, decl):
            return None, None
        body = body[:m.start()] + name + body[end:]

    # Address-of forms.  `void *` rather than a made-up object type: nothing in
    # the instruction says what lives there, and a wrong guess would silently
    # compile.  A dereference of the result -- which happens when m2c has lost
    # the load width -- then fails to compile instead of reading a wrong width.
    failed = []

    def addr(m):
        off = _const(m.group(2))
        if off is None:
            failed.append(True)
            return m.group(0)
        name = "D_%08X" % (GP_BASE + (off if m.group(1) == "+" else -off))
        # An address-of and a field access can name the same object; the field
        # access knows the real type, so it wins.
        decls.setdefault(name, "u8 " + name)
        return "((void *) &%s)" % name

    body = GP_ADDR.sub(addr, body)
    if failed or "saved_reg_gp" in body:
        return None, None          # a form we do not handle; skip this function
    prologue = "".join("extern %s;\n" % decls[n] for n in sorted(decls))
    return body, prologue + ("\n" if prologue else "")


def run_m2c(name):
    cmd = [sys.executable, M2C, "--target", "mipsel-gcc-c", "--valid-syntax",
           "--function", name]
    # Real Psy-Q signatures for every callee; without them m2c guesses, which
    # is a large part of why its output compiles to the wrong size.
    if os.path.exists(CONTEXT):
        cmd += ["--context", CONTEXT]
    r = subprocess.run(cmd + [ASM], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    body = r.stdout
    if "M2C_ERROR" in body or "GLOBAL_ASM" in body:
        return None
    return body


def attempt(name, inv, tmpdir):
    src = os.path.join(tmpdir, name + ".c")
    obj = os.path.join(tmpdir, name + ".o")

    body = run_m2c(name)
    if body is None:
        return "m2c-failed", None

    body, gp_decls = rewrite_gp(body)
    if body is None:
        return "gp-unhandled", None

    open(src, "w").write(HEADER + gp_decls + body)

    vram, size = inv[name]
    orig = original_words(vram, size)
    # ASPSX expands division into a two-guard macro that GCC never emits, so a
    # function containing one cannot match without --expand-div.  Decide from the
    # original words rather than from the C: opcode 0 with funct 0x1A/0x1B is
    # `div`/`divu`, which is exact, where scanning the source for `/` and `%`
    # would also hit comments and format strings.
    has_div = any((w >> 26) == 0 and (w & 0x3F) in (0x1A, 0x1B) for w in orig)

    # Both knobs varied per translation unit in the original build: the
    # assembler's -G (proven -- enabling it globally broke %hi/%lo functions) and
    # almost certainly the optimisation level too.  Search rather than guess;
    # whichever combination reproduces the bytes is the right one.
    # cc1_G and -fno-strength-reduce are here because both were found to change
    # the instruction *count*, not just register choice, which is the half of
    # the search this pass used to skip:
    #   cc1_G=0 makes cc1 emit its own %hi/%lo, so two uses of one symbol's
    #     address share a `lui`; with cc1_G=8 gas expands each macro separately
    #     and the function comes out one instruction long per extra `lui`.
    #   -fno-strength-reduce stops check_dbra_loop reversing a counted loop into
    #     a countdown, and changes whether a giv is created at all.
    # Both land failures in the `size-differs` bucket, which is ~49% of them, so
    # skipping these knobs made that bucket look like a types problem.
    best = "compile-failed"
    for opt, as_g, exp_div, cc1_g, extra in [
            (o, g, d, cg, x)
            for o in ("-O2", "-O3", "-O1", "-Os")
            for g in (0, 8)
            for d in ((0, 1) if has_div else (0,))
            for cg in (8, 0)
            for x in ("", ",-fno-strength-reduce")]:
        # "--flags=-O2" as one argv entry, not two: argparse treats a separate
        # "-O2" as an option token and refuses it as a value.  A multi-word
        # value happens to slip through, which is why this only broke here.
        r = subprocess.run([sys.executable, CC, src, obj, "--as-g", str(as_g),
                            "--expand-div", str(exp_div),
                            "--cc1-g", str(cc1_g),
                            "--flags=" + opt + extra],
                           capture_output=True, text=True)
        if r.returncode != 0:
            continue
        try:
            built = object_functions(obj)
        except Exception:
            best = "objread-failed"
            continue
        if name not in built:
            best = "not-emitted"
            continue

        words, masks = built[name]
        if size != len(words) * 4:
            best = "size-differs"
            continue

        mism = sum(1 for i in range(len(words))
                   if (words[i] & masks[i]) != (orig[i] & masks[i]))
        if mism == 0:
            return "match", (open(src).read(), as_g, opt, exp_div, cc1_g, extra)
        best = "differs:%d/%d" % (mism, len(words))
    return best, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max-insns", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4,
                    help="parallel workers; the work is subprocess-bound")
    args = ap.parse_args()

    all_funcs = funcs_mod.parse()
    inv = asm_inventory()

    # A function already written by hand is not a candidate.  Two files covering
    # the same span is the collision that broke the tree once before: the
    # hand-written one is the better source -- it carries the reasoning, and its
    # types were chosen rather than inferred -- so it wins, and regenerating a
    # duplicate beside it is pure risk.
    by_hand = {os.path.splitext(f)[0]
               for f in os.listdir(os.path.join(REPO, "src", "manual"))
               if f.endswith(".c")}

    cands = [f for f in all_funcs
             if f["addr"] < GAME_END
             and f["name"] in inv
             and f["insns"] <= args.max_insns
             and f["name"].startswith("func_")
             and f["name"] not in by_hand]
    cands.sort(key=lambda f: f["insns"])
    if not args.all:
        cands = cands[:args.limit]

    # Results accumulate in build/ and replace src/auto in one move at the end.
    # src/auto is read by tools/build.py and tools/progress_map.py, and a
    # half-populated directory makes the progress map show a collapse that never
    # happened -- so it must never be observable in a torn state.
    staging = os.path.join(REPO, "build", "auto_out")
    if os.path.isdir(staging):
        shutil.rmtree(staging)
    os.makedirs(staging)
    tmpdir = os.path.join(REPO, "build", "auto")
    os.makedirs(tmpdir, exist_ok=True)

    # Each function is independent -- one m2c run and up to six compile attempts,
    # all of it subprocess-bound -- so a thread pool scales nearly linearly and
    # the GIL is irrelevant.  Results are keyed by name and consumed in candidate
    # order afterwards, so output stays deterministic regardless of finish order.
    results = {}
    done = [0]
    lock = threading.Lock()

    def work(f):
        out = attempt(f["name"], inv, tmpdir)
        with lock:
            results[f["name"]] = out
            done[0] += 1
            if done[0] % 50 == 0 or done[0] == len(cands):
                hits = sum(1 for v in results.values() if v[0] == "match")
                print("  %d/%d attempted, %d matched"
                      % (done[0], len(cands), hits), flush=True)

    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(work, cands))

    stats = {}
    matched = []
    as_overrides = {}
    for f in cands:
        name = f["name"]
        status, text = results[name]
        stats[status.split(":")[0]] = stats.get(status.split(":")[0], 0) + 1
        if status != "match":
            continue
        body, as_g, opt, exp_div, cc1_g, extra = text
        open(os.path.join(staging, name + ".c"), "w").write(body)
        matched.append((name, f["insns"]))
        over = {}
        if as_g != 0:
            over["as_G"] = as_g
        if opt != "-O3":
            over["opt"] = opt
        if exp_div:
            over["expand_div"] = exp_div
        if cc1_g != 8:
            over["cc1_G"] = cc1_g
        if extra:
            over["cc1_extra"] = extra.lstrip(",")
        if over:
            as_overrides["src/auto/%s.c" % name] = over

    print("\n=== results over %d candidates ===" % len(cands))
    for k in sorted(stats, key=lambda k: -stats[k]):
        print("  %-16s %d" % (k, stats[k]))

    insns = sum(n for _, n in matched)
    print("\nmatched %d functions, %d instructions (%d bytes)"
          % (len(matched), insns, insns * 4))
    # record the per-file assembler -G that the build needs
    path = os.path.join(REPO, "config", "cflags.json")
    cfg = json.load(open(path))
    cfg.setdefault("files", {})
    # Only a full run is the authority on what src/auto contains, so only a
    # full run may drop the src/auto overrides it did not reproduce.  A partial
    # run that purged them left every other generated file on the *default*
    # flags -- the .c file still there, still listed, and no longer matching.
    # That is how `--limit 6` turned 340 ok into 256 ok, 84 failing.
    if args.all:
        cfg["files"] = {k: v for k, v in cfg["files"].items()
                        if not k.startswith("src/auto/")}
    cfg["files"].update(as_overrides)
    cfg["files"] = {k: cfg["files"][k] for k in sorted(cfg["files"])}
    json.dump(cfg, open(path, "w"), indent=2)
    print("recorded flag overrides for %d of %d matched file(s)"
          % (len(as_overrides), len(matched)))

    # How the staged output reaches src/auto depends on whether this run
    # actually considered every candidate.
    #
    # It used to be an unconditional `rmtree(src/auto); rename(staging)`, which
    # is right for a full run and silently destructive for any other: a
    # `--limit 6` run replaced 340 files with 6 and deleted 175 matched
    # functions.  Nothing caught it, because the deleted functions simply fall
    # back to their assembly and the build stays byte-identical -- the only
    # symptom is the progress number dropping, which is not a gate.
    #
    # So: a full run still swaps, because that is the only way a function that
    # has *stopped* matching gets removed.  A partial run merges.
    os.makedirs(OUTDIR, exist_ok=True)
    if args.all:
        for stale in os.listdir(OUTDIR):
            if stale.endswith(".c") and not os.path.exists(
                    os.path.join(staging, stale)):
                os.remove(os.path.join(OUTDIR, stale))
    for f in os.listdir(staging):
        shutil.copyfile(os.path.join(staging, f), os.path.join(OUTDIR, f))
    shutil.rmtree(staging)
    print("written to src/auto/ (%d file(s), %s)"
          % (len(matched), "full run: stale files removed" if args.all
             else "partial run: merged, nothing removed"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
