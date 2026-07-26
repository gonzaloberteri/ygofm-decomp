"""Compile one C file the way the original build did.

    cpp -> CC1PSX (GCC 2.95.2, from Psy-Q 4.6) -> maspsx -> mipsel-none-elf-as

CC1PSX and ASPSX are 32-bit PE binaries, so they run natively under WOW64 --
no emulation layer needed on Windows.  maspsx stands in for ASPSX 2.86: the
Psy-Q assembler expands certain macros (div-by-zero checks, `la`, `li`, load
delay slots) differently from GNU as, and those differences are visible in the
final bytes, so they have to be reproduced rather than approximated.

    py -3 tools/cc.py src/foo.c build/src/foo.o
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toolchain

REPO = toolchain.REPO
PSYQ = toolchain.PSYQ
MASPSX = os.path.join(REPO, "tools", "maspsx", "maspsx.py")

ASPSX_VERSION = "2.86"
CFLAGS_CONFIG = os.path.join(REPO, "config", "cflags.json")


FLAG_COMMENT = re.compile(r"decomp-flags:\s*([^*/\n]+)")


def flags_for(src):
    """Per-file compiler/assembler flags.

    Three sources, later winning: the defaults, `config/cflags.json`, and a
    `decomp-flags:` comment in the file itself, e.g.

        /* decomp-flags: opt=-O2 as_G=8 */

    The in-file form exists so that work can be parallelised: several people or
    processes decompiling different functions at once would otherwise all have
    to edit one shared JSON file, and whoever wrote last would win.  A file that
    carries its own flags is also self-explanatory to read.
    """
    import json
    cfg = {"default": {"opt": "-O3", "cc1_G": 8, "as_G": 0}, "files": {}}
    if os.path.exists(CFLAGS_CONFIG):
        cfg.update(json.load(open(CFLAGS_CONFIG)))
    out = dict(cfg.get("default", {}))
    rel = os.path.relpath(os.path.abspath(src), REPO).replace("\\", "/")
    out.update(cfg.get("files", {}).get(rel, {}))

    try:
        head = open(src, encoding="utf-8", errors="replace").read(2048)
    except OSError:
        return out
    m = FLAG_COMMENT.search(head)
    if m:
        for token in m.group(1).split():
            if "=" not in token:
                continue
            key, _, value = token.partition("=")
            key = key.strip()
            if key in ("as_G", "cc1_G", "expand_div"):
                out[key] = int(value)
            elif key == "opt":
                # comma separated too: part of the binary was built with no -O
                # at all, so `opt=-O0,-fomit-frame-pointer` has to be sayable.
                out[key] = value
            elif key == "cc1_extra":
                # comma separated, because the comment is split on whitespace:
                #   cc1_extra=-fno-schedule-insns2,-fno-peephole
                out[key] = [t for t in value.split(",") if t]
    return out

# Recovered by tools/flagsweep.py, not guessed.  -O2 gets simple leaf functions
# right but picks a different register for globals accessed via %hi/%lo; -O3 is
# what the original build used.  -G8 puts small objects in the small-data area,
# which is why so much of the game addresses through $gp.
CC1_BASE = ["-quiet", "-fgnu-linker", "-mgas"]
INCLUDES = [toolchain.PSYQ_INCLUDE, os.path.join(REPO, "include"),
            os.path.join(REPO, "src")]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write("FAILED: %s\n%s\n%s\n"
                         % (" ".join(cmd), r.stdout, r.stderr))
        sys.exit(1)
    return r


def compile_c(src, obj, extra_flags=(), as_g=None, expand_div=None, cc1_g=None):
    tmp = obj + ".i"
    asm = obj + ".s"
    os.makedirs(os.path.dirname(obj) or ".", exist_ok=True)

    cpp_cmd = [toolchain.binutil("cpp"),
               "-undef", "-nostdinc", "-D__GNUC__=2", "-D__OPTIMIZE__",
               "-Dmips", "-D__mips__", "-D__PSX__", "-DPSX"]
    for inc in INCLUDES:
        cpp_cmd += ["-I", inc]
    cpp_cmd += [src, tmp]
    run(cpp_cmd)

    fl = flags_for(src)
    if as_g is not None:
        fl["as_G"] = as_g
    if expand_div is not None:
        fl["expand_div"] = expand_div
    if cc1_g is not None:
        fl["cc1_G"] = cc1_g
    # `opt` may carry several tokens, comma separated: part of the binary was
    # built with no -O at all, so `opt=-O0,-fomit-frame-pointer` must be sayable.
    opt_flags = [t for t in str(fl["opt"]).split(",") if t]
    cc1_flags = CC1_BASE + opt_flags + ["-G%d" % fl["cc1_G"]]
    # Per-file cc1 flags beyond -O/-G.  Needed because no single -O level
    # reproduces some functions: -O1 gives the original's epilogue order but the
    # wrong prologue, -O2 the reverse, and the difference is the post-reload
    # scheduler hoisting `lw $ra` above trailing stores.  That is reachable only
    # by naming the pass, e.g. cc1_extra=-fno-schedule-insns2.
    cc1_flags += list(fl.get("cc1_extra", []))
    # cc1's own /0 guard is deliberately left ON under expand_div.  maspsx
    # consumes it and re-emits ASPSX's two-guard macro in its place, so the two
    # cannot stack -- and suppressing it is actively harmful, because without
    # the guard block sitting between them the scheduler hoists the epilogue
    # loads into the gap between `div` and `mfhi`, which the original does not.
    # psyq_cc1() is an argv *prefix*, not a path: off Windows CC1PSX.EXE is a
    # 32-bit PE and the prefix carries a loader (wibo) in front of it.  The
    # absolute POSIX paths in `tmp`/`asm` need no translation -- the loader maps
    # the host filesystem at Z:\ and the current drive is always Z: here.
    run(toolchain.psyq_cc1() + cc1_flags + list(extra_flags) + [tmp, "-o", asm])

    maspsx_flags = ["--aspsx-version", ASPSX_VERSION, "--run-assembler",
                    "--gnu-as-path", toolchain.binutil("as"),
                    "--dont-force-G0"]
    # ASPSX guards division with checks for /0 *and* INT_MIN/-1, and puts mfhi
    # after both.  GNU as emits only the /0 check, so any function containing a
    # `%` or `/` is a few instructions short unless maspsx expands it itself.
    if fl.get("expand_div"):
        maspsx_flags.append("--expand-div")

    with open(asm) as fp:
        stage = subprocess.run(
            # --dont-force-G0 matters: maspsx injects -G0 by default, which
            # cancels the small-data area and turns every gp-relative access
            # back into a %hi/%lo pair.
            [sys.executable, MASPSX] + maspsx_flags +
            ["-march=r3000", "-mabi=32", "-EL", "-G%d" % fl["as_G"],
             "-O0", "-o", obj],
            stdin=fp, capture_output=True, text=True)
    if stage.returncode != 0:
        sys.stderr.write("maspsx/as failed:\n%s\n%s\n" % (stage.stdout, stage.stderr))
        sys.exit(1)
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("obj")
    ap.add_argument("--flags", default="",
                    help="extra CC1PSX flags, space separated")
    ap.add_argument("--as-g", type=int, default=None,
                    help="override the assembler's -G for this file")
    ap.add_argument("--expand-div", type=int, default=None,
                    help="override ASPSX division macro expansion for this file")
    ap.add_argument("--cc1-g", type=int, default=None,
                    help="override the compiler's -G for this file")
    args = ap.parse_args()
    out = compile_c(args.src, args.obj,
                    args.flags.split() if args.flags else (), args.as_g,
                    args.expand_div, args.cc1_g)
    print("built %s" % out)


if __name__ == "__main__":
    main()
