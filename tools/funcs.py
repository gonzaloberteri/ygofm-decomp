"""Inventory the functions in the disassembly.

Everything below GAME_END is code Konami wrote and has to be decompiled;
everything above it is Psy-Q and only needs naming (see tools/psyq_sigs.py).

    py -3 tools/funcs.py                 summary
    py -3 tools/funcs.py --candidates    small leaf functions, easiest first
"""
import argparse
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(REPO, "asm")
GAME_END = 0x80073704          # first Psy-Q symbol; game code lies below
GP_BASE  = 0x8009AF08          # set at 0x80012A54: lui $gp,0x800A / addiu $gp,$gp,-0x50F8

LABEL = re.compile(r"^(?:glabel|dlabel)\s+(\S+)")
INSN = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8}) [0-9A-F]{8} \*/\s+(\S+)")


def parse():
    funcs = []
    for fn in sorted(os.listdir(ASM)):
        if not fn.endswith(".s"):
            continue
        cur = None
        for line in open(os.path.join(ASM, fn)):
            m = LABEL.match(line)
            if m:
                cur = {"name": m.group(1), "addr": None, "insns": 0,
                       "calls": 0, "file": fn, "ops": set(), "gp": False}
                funcs.append(cur)
                continue
            m = INSN.match(line)
            if m and cur is not None:
                if cur["addr"] is None:
                    cur["addr"] = int(m.group(1), 16)
                cur["insns"] += 1
                if "$gp" in line:
                    cur["gp"] = True
                op = m.group(2)
                cur["ops"].add(op)
                if op in ("jal", "jalr"):
                    cur["calls"] += 1
    return [f for f in funcs if f["addr"] is not None and f["insns"] > 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    funcs = parse()
    game = [f for f in funcs if f["addr"] < GAME_END]
    sdk = [f for f in funcs if f["addr"] >= GAME_END]

    print("functions: %d total, %d game, %d sdk" % (len(funcs), len(game), len(sdk)))
    print("game code instructions: %d (%d bytes)"
          % (sum(f["insns"] for f in game), sum(f["insns"] for f in game) * 4))

    leaves = [f for f in game if f["calls"] == 0]
    print("game leaf functions (no jal/jalr): %d" % len(leaves))

    # $gp-relative access needs the small-data layout reconstructed before it
    # can be matched, so these are blocked until translation units are split.
    gp = [f for f in game if f["gp"]]
    gp_ins = sum(f["insns"] for f in gp)
    all_ins = sum(f["insns"] for f in game)
    print("game functions using $gp: %d (%d insns, %.1f%% of game code)"
          % (len(gp), gp_ins, gp_ins / all_ins * 100))
    print("reachable without $gp:    %d (%d insns, %.1f%%)"
          % (len(game) - len(gp), all_ins - gp_ins,
             (all_ins - gp_ins) / all_ins * 100))

    if args.candidates:
        # small leaves with no multiply/divide and no coprocessor ops are the
        # least likely to need compiler-flag archaeology on the first attempt
        HARD = {"mult", "multu", "div", "divu", "mfhi", "mflo", "mtc2", "mfc2",
                "cop2", "lwc2", "swc2", "ctc2", "cfc2"}
        easy = [f for f in leaves if 4 <= f["insns"] <= 40
                and not (f["ops"] & HARD)]
        easy.sort(key=lambda f: f["insns"])
        print("\neasiest %d candidates:" % min(args.limit, len(easy)))
        print("  %-22s %-10s %6s" % ("name", "addr", "insns"))
        for f in easy[:args.limit]:
            print("  %-22s 0x%08X %6d" % (f["name"], f["addr"], f["insns"]))


if __name__ == "__main__":
    main()
