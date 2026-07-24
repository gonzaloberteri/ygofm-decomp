"""Carve the monolithic disassembly around functions that now exist in C.

splat emits one .s per code region.  Once a function is decompiled, its bytes
must come from the compiled C instead, so the surrounding assembly has to be
split into the runs that are still assembly, with holes where C takes over.

Splitting on function boundaries is safe: MIPS branches and `.L` labels stay
inside a function, so no local reference crosses a new file boundary.  Anything
that does cross shows up as an undefined symbol at link time rather than as a
silent byte difference.

Returns, and writes to build/asm_parts/, a list of (vram, path) fragments.
"""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM_DIR = os.path.join(REPO, "asm")
PARTS = os.path.join(REPO, "build", "asm_parts")

LABEL = re.compile(r"^(?:glabel|dlabel)\s+(\S+)")
# Instruction lines carry the raw word, data lines may not:
#     /* 82B74 80092B74 00000000 */ .word 0x00000000
#     /* 82B72 80092B72 */          .short 0xC000
# Both forms have to yield an address, otherwise trailing data at the end of a
# code region gets dropped from the fragments and silently zero-filled.
ADDR = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8})[^*]*\*/")
PROLOGUE = ('.include "macro.inc"\n\n.set noat\n.set noreorder\n\n'
            '.section .text, "ax"\n\n')


def parse_functions(path):
    """[(name, first_vram, [lines])] in file order."""
    out, cur = [], None
    for line in open(path):
        m = LABEL.match(line)
        if m:
            cur = {"name": m.group(1), "vram": None, "lines": [line]}
            out.append(cur)
            continue
        if cur is None:
            continue
        cur["lines"].append(line)
        m = ADDR.match(line)
        if m and cur["vram"] is None:
            cur["vram"] = int(m.group(1), 16)
    return [f for f in out if f["vram"] is not None]


def write_fragment_macros():
    """Emit a macro.inc for fragments with the `.size` directives removed.

    `endlabel`/`enddlabel` expand to `.size sym, . - sym`.  Once the assembly is
    split, a symbol's start and the `.` that closes it can land in different
    files, and the expression stops being a constant.  `.size` is metadata that
    never reaches the output bytes, so dropping it costs nothing.  Generated
    from the real macro.inc so the two cannot drift apart.
    """
    src = os.path.join(REPO, "include", "macro.inc")
    out = os.path.join(PARTS, "macro.inc")
    with open(src) as fp, open(out, "w") as dst:
        for line in fp:
            if line.strip().startswith(".size"):
                dst.write("    # .size dropped: see tools/split_asm.py\n")
            else:
                dst.write(line)


def split(decompiled):
    """decompiled: set of function names now built from C."""
    os.makedirs(PARTS, exist_ok=True)
    for stale in os.listdir(PARTS):
        os.remove(os.path.join(PARTS, stale))
    write_fragment_macros()

    fragments = []
    for fn in sorted(os.listdir(ASM_DIR)):
        if not fn.endswith(".s"):
            continue
        funcs = parse_functions(os.path.join(ASM_DIR, fn))

        run = []
        for f in funcs + [None]:
            if f is not None and f["name"] not in decompiled:
                run.append(f)
                continue
            if run:
                vram = run[0]["vram"]
                path = os.path.join(PARTS, "part_%08X.s" % vram)
                with open(path, "w") as fp:
                    fp.write(PROLOGUE)
                    for g in run:
                        fp.writelines(g["lines"])
                fragments.append((vram, path))
                run = []
    return fragments


if __name__ == "__main__":
    frags = split(set())
    print("%d fragment(s)" % len(frags))
    for vram, path in frags[:5]:
        print("  %08X  %s" % (vram, os.path.basename(path)))
