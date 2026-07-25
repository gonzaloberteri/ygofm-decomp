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
GP_FIELD = re.compile(
    r"M2C_FIELD\(\s*saved_reg_gp\s*,\s*([A-Za-z_][A-Za-z0-9_ ]*?)\s*\*\s*,"
    r"\s*(0x[0-9A-Fa-f]+|-?\d+)\s*\)")


def rewrite_gp(body):
    """Replace saved_reg_gp field accesses with declared externs."""
    decls = {}

    def sub(m):
        ctype, off = m.group(1).strip(), int(m.group(2), 0)
        name = "D_%08X" % (GP_BASE + off)
        decls[name] = ctype
        return name

    new = GP_FIELD.sub(sub, body)
    if "saved_reg_gp" in new:
        return None, None          # a form we do not handle; skip this function
    prologue = "".join("extern %s %s;\n" % (t, n)
                       for n, t in sorted(decls.items()))
    return new, prologue + ("\n" if prologue else "")


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

    # Both knobs varied per translation unit in the original build: the
    # assembler's -G (proven -- enabling it globally broke %hi/%lo functions) and
    # almost certainly the optimisation level too.  Search rather than guess;
    # whichever combination reproduces the bytes is the right one.
    best = "compile-failed"
    for opt, as_g in [(o, g) for o in ("-O2", "-O3", "-O1") for g in (0, 8)]:
        # "--flags=-O2" as one argv entry, not two: argparse treats a separate
        # "-O2" as an option token and refuses it as a value.  A multi-word
        # value happens to slip through, which is why this only broke here.
        r = subprocess.run([sys.executable, CC, src, obj, "--as-g", str(as_g),
                            "--flags=" + opt],
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
        vram, size = inv[name]
        if size != len(words) * 4:
            best = "size-differs"
            continue

        orig = original_words(vram, size)
        mism = sum(1 for i in range(len(words))
                   if (words[i] & masks[i]) != (orig[i] & masks[i]))
        if mism == 0:
            return "match", (open(src).read(), as_g, opt)
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

    cands = [f for f in all_funcs
             if f["addr"] < GAME_END
             and f["name"] in inv
             and f["insns"] <= args.max_insns
             and f["name"].startswith("func_")]
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
        body, as_g, opt = text
        open(os.path.join(staging, name + ".c"), "w").write(body)
        matched.append((name, f["insns"]))
        over = {}
        if as_g != 0:
            over["as_G"] = as_g
        if opt != "-O3":
            over["opt"] = opt
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
    # Replace the src/auto entries rather than merging into them.  This run is
    # the authority on what src/auto contains, so merging would leave overrides
    # behind for files it no longer produces, and those stale entries would
    # silently apply to a future file of the same name.
    cfg["files"] = {k: v for k, v in cfg["files"].items()
                    if not k.startswith("src/auto/")}
    cfg["files"].update(as_overrides)
    cfg["files"] = {k: cfg["files"][k] for k in sorted(cfg["files"])}
    json.dump(cfg, open(path, "w"), indent=2)
    print("recorded flag overrides for %d of %d matched file(s)"
          % (len(as_overrides), len(matched)))

    # single atomic-ish swap: src/auto is never seen partially written
    if os.path.isdir(OUTDIR):
        shutil.rmtree(OUTDIR)
    os.makedirs(os.path.dirname(OUTDIR), exist_ok=True)
    os.rename(staging, OUTDIR)
    print("written to src/auto/ (%d file(s))" % len(matched))
    return 0


if __name__ == "__main__":
    sys.exit(main())
