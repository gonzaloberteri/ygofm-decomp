"""Find functions the disassembly merged, and emit labels to split them.

spimdisasm only starts a new function where it has a reason to, so several
`glabel ... endlabel` spans actually contain two or more functions: after the
first `jr $ra` and its delay slot, unlabelled code continues with a fresh
prologue.  `func_8004293C`'s span covers four functions.

This matters twice over:

  * `tools/match.py` measures a function as its whole span, so correct C for the
    first function is reported as the wrong size and can never match.  Three
    hand-decompilation batches each hit this independently.
  * the function inventory therefore **overstates sizes and understates the
    function count**, which skews the progress figures.

Detection is conservative.  A split is proposed only where `jr $ra` plus its
delay slot is followed by an instruction that plausibly begins a function --
a stack adjustment, or a jump/branch target already referenced elsewhere -- and
never inside a region the disassembler marked as data.

    py -3 tools/split_funcs.py            report
    py -3 tools/split_funcs.py --write     append to config/symbol_addrs.txt
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

ASM_DIR = os.path.join(REPO, "asm")
SYMBOLS = os.path.join(REPO, "config", "symbol_addrs.txt")

LABEL = re.compile(r"^(?:glabel|dlabel|alabel|jlabel)\s+(\S+)")
END = re.compile(r"^endlabel\s+(\S+)")
INSN = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8}) ([0-9A-F]{8}) \*/\s+(\S+)(.*)$")


def spans():
    """[(name, [(vram, word, mnemonic, rest), ...])] for each labelled span."""
    out = []
    for fn in sorted(os.listdir(ASM_DIR)):
        if not fn.endswith(".s"):
            continue
        cur = None
        for line in open(os.path.join(ASM_DIR, fn)):
            m = LABEL.match(line)
            if m:
                cur = (m.group(1), [])
                out.append(cur)
                continue
            if END.match(line):
                cur = None
                continue
            m = INSN.match(line)
            if m and cur is not None:
                cur[1].append((int(m.group(1), 16), int(m.group(2), 16),
                               m.group(3), m.group(4)))
    return out


def find_splits():
    """Addresses that look like the start of a merged-in second function."""
    proposals = []
    for name, insns in spans():
        if len(insns) < 4:
            continue
        for i, (vram, word, mnem, rest) in enumerate(insns):
            if mnem != "jr" or "$ra" not in rest:
                continue
            nxt = i + 2                     # skip the delay slot
            if nxt >= len(insns):
                continue                    # jr $ra ended the span: normal
            start_vram, _, start_mnem, start_rest = insns[nxt]

            # A function almost always opens by making stack room, or (for a
            # leaf) by immediately doing work with no prologue.  Requiring the
            # stack adjustment keeps this conservative -- a leaf tail merged
            # into a previous function is left alone rather than guessed at.
            is_prologue = (start_mnem == "addiu" and "$sp, $sp, -" in start_rest)
            if not is_prologue:
                continue
            proposals.append({"container": name, "addr": start_vram,
                              "after": vram,
                              "insns_before": nxt,
                              "insns_after": len(insns) - nxt})
    return proposals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    props = find_splits()
    print("spans containing a merged second function: %d" % len(props))
    if props:
        print("\n  %-22s %-12s %-12s %s"
              % ("container", "split at", "before/after", "note"))
        for p in props:
            print("  %-22s 0x%08X   %3d / %-6d %s"
                  % (p["container"], p["addr"], p["insns_before"],
                     p["insns_after"], "jr $ra at 0x%08X" % p["after"]))

    total_hidden = len(props)
    print("\n%d function(s) are currently invisible to the inventory" % total_hidden)

    if args.write and props:
        existing = open(SYMBOLS).read() if os.path.exists(SYMBOLS) else ""
        added = 0
        with open(SYMBOLS, "a") as fp:
            fp.write("\n// Split points found by tools/split_funcs.py: code that\n"
                     "// continues past a jr $ra with no label of its own.\n")
            for p in props:
                name = "func_%08X" % p["addr"]
                if name in existing:
                    continue
                fp.write("%s = 0x%08X; // type:func\n" % (name, p["addr"]))
                added += 1
        print("appended %d symbol(s) to %s" % (added, SYMBOLS))
        print("re-run splat and tools/build.py to pick them up")
    return 0


if __name__ == "__main__":
    sys.exit(main())
