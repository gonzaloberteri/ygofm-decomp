"""Print our compiled output next to the original, instruction by instruction.

tools/match.py says *how many* instructions differ and, when the count matches,
which words.  When the count does *not* match it can only say "size 280,
original 288", and the useful question -- which instruction went missing -- needs
the two streams side by side.

    py -3 tools/sidebyside.py src/manual/func_8004B734.c

Note `objdump -d` elides runs of all-zero words unless given `-z`, and `nop` is
0x00000000.  Comparing by eye without it silently loses every nop, which is
exactly the class of difference this tool exists to show.
"""
import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import cc                                                          # noqa: E402

ASM = os.path.join(REPO, "asm", "code_002800.s")
import toolchain                                                   # noqa: E402
OBJDUMP = toolchain.binutil("objdump")

INSN = re.compile(r"^\s*/\*\s*\w+\s+(\w{8})\s+(\w{8})\s+\*/\s+(.*)")
OURS = re.compile(r"^\s+([0-9a-f]+):\s+([0-9a-f]{8})\s+(.*)")


def original(name):
    out, cur = [], None
    for line in open(ASM, encoding="utf-8", errors="replace"):
        m = re.match(r"^glabel\s+(\S+)", line)
        if m:
            cur = m.group(1)
            continue
        if cur != name:
            continue
        m = INSN.match(line)
        if m:
            out.append((m.group(2), m.group(3).strip()))
    return out


def compiled(src, name):
    obj = os.path.join(REPO, "build", "sidebyside.o")
    cc.compile_c(src, obj)
    r = subprocess.run([OBJDUMP, "-d", "-z", obj], capture_output=True, text=True)
    out, seen = [], False
    for line in r.stdout.splitlines():
        if re.match(r"^[0-9a-f]+ <%s>:" % re.escape(name), line):
            seen = True
            continue
        if not seen:
            continue
        m = OURS.match(line)
        if m:
            out.append((m.group(2), m.group(3).strip()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--func", default=None,
                    help="defaults to the file's basename")
    args = ap.parse_args()
    name = args.func or os.path.splitext(os.path.basename(args.src))[0]

    orig = original(name)
    ours = compiled(args.src, name)
    if not orig:
        sys.exit("%s not found in %s" % (name, os.path.basename(ASM)))

    print("original %d insns, ours %d\n" % (len(orig), len(ours)))
    print("      %-38s %s" % ("original", "ours"))
    for i in range(max(len(orig), len(ours))):
        o = orig[i] if i < len(orig) else ("", "---")
        u = ours[i] if i < len(ours) else ("", "---")
        # Compare the mnemonic only.  Register names and branch targets are
        # rendered differently by the two disassemblers, so a full text compare
        # would flag every line and hide the signal.
        same = o[1].split()[:1] == u[1].split()[:1]
        print("%s%-3d %-38s %s" % ("   " if same else ">> ", i, o[1], u[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
