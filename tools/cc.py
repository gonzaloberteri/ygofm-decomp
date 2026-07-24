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
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSYQ = os.path.join(REPO, "tools", "bin", "psyq", "p46", "Psy-Q - 46")
CC1 = os.path.join(PSYQ, "BIN", "CC1PSX.EXE")
GNU_AS = os.path.join(REPO, "tools", "bin", "bin", "mipsel-none-elf-as.exe")
CPP = os.path.join(REPO, "tools", "bin", "bin", "mipsel-none-elf-cpp.exe")
MASPSX = os.path.join(REPO, "tools", "maspsx", "maspsx.py")

ASPSX_VERSION = "2.86"

# Recovered by tools/flagsweep.py, not guessed.  -O2 gets simple leaf functions
# right but picks a different register for globals accessed via %hi/%lo; -O3 is
# what the original build used.  -G8 puts small objects in the small-data area,
# which is why so much of the game addresses through $gp.
CC1_FLAGS = ["-quiet", "-O3", "-G8", "-fgnu-linker", "-mgas"]
INCLUDES = [os.path.join(PSYQ, "INCLUDE"), os.path.join(REPO, "include"),
            os.path.join(REPO, "src")]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write("FAILED: %s\n%s\n%s\n"
                         % (" ".join(cmd), r.stdout, r.stderr))
        sys.exit(1)
    return r


def compile_c(src, obj, extra_flags=()):
    tmp = obj + ".i"
    asm = obj + ".s"
    os.makedirs(os.path.dirname(obj) or ".", exist_ok=True)

    cpp_cmd = [CPP, "-undef", "-nostdinc", "-D__GNUC__=2", "-D__OPTIMIZE__",
               "-Dmips", "-D__mips__", "-D__PSX__", "-DPSX"]
    for inc in INCLUDES:
        cpp_cmd += ["-I", inc]
    cpp_cmd += [src, tmp]
    run(cpp_cmd)

    run([CC1] + CC1_FLAGS + list(extra_flags) + [tmp, "-o", asm])

    with open(asm) as fp:
        stage = subprocess.run(
            [sys.executable, MASPSX, "--aspsx-version", ASPSX_VERSION,
             "--run-assembler", "--gnu-as-path", GNU_AS,
             "-march=r3000", "-mabi=32", "-EL", "-O0", "-o", obj],
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
    args = ap.parse_args()
    out = compile_c(args.src, args.obj, args.flags.split() if args.flags else ())
    print("built %s" % out)


if __name__ == "__main__":
    main()
