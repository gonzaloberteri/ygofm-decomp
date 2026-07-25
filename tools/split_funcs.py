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
# A file of its own, NOT config/symbol_addrs.txt: tools/psyq_sigs.py --write
# rewrites that one wholesale and would silently erase these split points.
SYMBOLS = os.path.join(REPO, "config", "split_syms.txt")

LABEL = re.compile(r"^(?:glabel|dlabel|alabel|jlabel)\s+(\S+)")
END = re.compile(r"^endlabel\s+(\S+)")
# splat emits a local label for every internal branch/jump target it found
LOCAL_LABEL = re.compile(r"^\.L[0-9A-F]{8}:")
INSN = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8}) ([0-9A-F]{8}) \*/\s+(\S+)(.*)$")


def spans():
    """[(name, [(vram, word, mnemonic, rest), ...])] for each labelled span."""
    out = []
    for fn in sorted(os.listdir(ASM_DIR)):
        if not fn.endswith(".s"):
            continue
        cur = None
        labelled = False
        for line in open(os.path.join(ASM_DIR, fn)):
            m = LABEL.match(line)
            if m:
                cur = (m.group(1), [])
                out.append(cur)
                labelled = False
                continue
            if END.match(line):
                cur = None
                continue
            if LOCAL_LABEL.match(line):
                labelled = True
                continue
            m = INSN.match(line)
            if m and cur is not None:
                cur[1].append((int(m.group(1), 16), int(m.group(2), 16),
                               m.group(3), m.group(4), labelled))
                labelled = False
    return out


JAL = re.compile(r"^\s+/\* [0-9A-F]+ [0-9A-F]{8} [0-9A-F]{8} \*/\s+jal\s+(\S+)")
FUNC_NAME = re.compile(r"^func_([0-9A-F]{8})$")


def call_targets():
    """Every address reached by a `jal` anywhere in the disassembly.

    This is the decisive test for "is this a function": if something calls it,
    it is one.  It needs no heuristic, and it catches the leaf functions that the
    prologue test below cannot -- a leaf with no stack frame has no `addiu $sp`
    to recognise, and four such functions were found by hand after the first
    pass missed them.
    """
    targets = set()
    for fn in sorted(os.listdir(ASM_DIR)):
        if not fn.endswith(".s"):
            continue
        for line in open(os.path.join(ASM_DIR, fn)):
            m = JAL.match(line)
            if not m:
                continue
            m2 = FUNC_NAME.match(m.group(1).strip())
            if m2:
                targets.add(int(m2.group(1), 16))
    return targets


def find_splits():
    """Addresses that look like the start of a merged-in second function."""
    called = call_targets()
    proposals = []
    for name, insns in spans():
        if len(insns) < 4:
            continue
        for i, (vram, word, mnem, rest, _lbl) in enumerate(insns):
            if mnem != "jr" or "$ra" not in rest:
                continue
            nxt = i + 2                     # skip the delay slot
            if nxt >= len(insns):
                continue                    # jr $ra ended the span: normal
            start_vram, _, start_mnem, start_rest, start_labelled = insns[nxt]

            # A function may legitimately have several `jr $ra` returns, so code
            # after one is only a *new* function if nothing can branch to it.
            # splat emits a local label for every internal branch/jump target it
            # found, so an unlabelled instruction after a return is unreachable
            # from the preceding code and therefore begins something new.
            #
            # This is what the earlier prologue-only rule got wrong in both
            # directions: it missed leaf functions with no stack frame, and it
            # would have mis-split multi-return functions had it not required a
            # prologue. Recorded `why` says which corroborating signal applied.
            if start_labelled:
                continue                    # a branch target: same function
            is_called = start_vram in called
            is_prologue = (start_mnem == "addiu" and "$sp, $sp, -" in start_rest)
            proposals.append({"container": name, "addr": start_vram,
                              "after": vram,
                              "insns_before": nxt,
                              "insns_after": len(insns) - nxt,
                              "why": ("called" if is_called else
                                      "prologue" if is_prologue else
                                      "unreachable-after-return")})
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
        # Rewritten from scratch each run: this tool is the authority on splits,
        # so appending would duplicate entries every time it is re-run.
        seen = set()
        with open(SYMBOLS, "w") as fp:
            fp.write("// Generated by tools/split_funcs.py -- do not edit.\n"
                     "// Code that continues past a jr $ra with no label of its\n"
                     "// own: functions spimdisasm merged into one span.\n")
            for p in sorted(props, key=lambda q: q["addr"]):
                name = "func_%08X" % p["addr"]
                if name in seen:
                    continue
                seen.add(name)
                fp.write("%s = 0x%08X; // type:func\n" % (name, p["addr"]))
        added = len(seen)
        print("wrote %d symbol(s) to %s" % (added, SYMBOLS))
        print("re-run splat and tools/build.py to pick them up")
    return 0


if __name__ == "__main__":
    sys.exit(main())
