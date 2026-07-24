"""Build a type/signature context file for m2c.

Without context m2c guesses every callee's signature, which is a large part of
why its output compiles to the wrong instruction count.  Feeding it the real
Psy-Q headers fixes the signatures of every SDK function -- and 401 of those are
already located in the binary by tools/psyq_sigs.py, so the names line up.

The output must be preprocessed C, which is what m2c's --context expects.

    py -3 tools/gen_context.py   ->  build/context.c
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSYQ_INC = os.path.join(REPO, "tools", "bin", "psyq", "p46", "Psy-Q - 46",
                        "INCLUDE")
CPP = os.path.join(REPO, "tools", "bin", "bin", "mipsel-none-elf-cpp.exe")
OUT = os.path.join(REPO, "build", "context.c")

# Order matters: LIBGTE.H typedefs SVECTOR/VECTOR/MATRIX, which LIBGPU.H,
# LIBGS.H and LIBHMD.H all use in struct fields.  The inline-assembly GTE
# headers are deliberately excluded -- they are full of asm statements that the
# preprocessor passes straight through and pycparser then rejects.
HEADERS = [
    "SYS/TYPES.H", "LIBGTE.H", "LIBAPI.H", "LIBETC.H", "LIBGPU.H",
    "LIBCD.H", "LIBSPU.H", "LIBSND.H", "LIBPAD.H", "LIBMCRD.H",
    "LIBCARD.H", "LIBMATH.H", "LIBDS.H", "LIBPRESS.H", "LIBGS.H",
]

# KERNEL.H pulls in ASM.H, which does `#define v0 $2` and friends.  Those
# aliases rewrite ordinary struct fields -- `u_char u0, v0, u1, v1;` came out as
# `u_char u0, $2, u1, $3;`.  Pre-defining the include guard skips the header.
CPP_DEFINES = ["-D_ASM_H"]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    stub = os.path.join(REPO, "build", "context_stub.c")
    with open(stub, "w") as fp:
        fp.write('#include "%s"\n' % os.path.join(REPO, "include", "types.h")
                 .replace("\\", "/"))
        for h in HEADERS:
            path = os.path.join(PSYQ_INC, h.replace("/", os.sep))
            if os.path.exists(path):
                fp.write('#include "%s"\n' % path.replace("\\", "/"))
            else:
                print("  missing (skipped): %s" % h)

    cmd = ([CPP, "-undef", "-nostdinc", "-D__GNUC__=2", "-Dmips", "-D__mips__"]
           + CPP_DEFINES
           + ["-I", PSYQ_INC, "-I", os.path.join(REPO, "include"), stub, OUT])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return 1

    # m2c parses this with pycparser, which rejects GNU extensions that survive
    # preprocessing.  Drop the lines that carry them.
    keep = []
    for line in open(OUT, errors="replace"):
        s = line.strip()
        if s.startswith("#"):
            continue
        if "__asm__" in s or "__attribute__" in s or "__inline" in s:
            continue
        keep.append(line)
    open(OUT, "w").write("".join(keep))

    decls = sum(1 for line in open(OUT) if line.strip().endswith(";"))
    print("wrote %s (%d declarations)" % (OUT, decls))
    return 0


if __name__ == "__main__":
    sys.exit(main())
