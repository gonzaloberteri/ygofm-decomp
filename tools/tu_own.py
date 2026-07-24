"""Propose translation-unit boundaries from *exclusively owned* data.

`tools/tu_detect.py` tracked the band of data each function references, and was
too noisy to be useful: 111 candidate boundaries with a median implied unit of
4 functions, because functions freely reference other units' globals and that
swamps the signal.

This takes a stricter line.  A data symbol referenced by exactly **one**
function is almost certainly a static belonging to that function's translation
unit -- nothing else can see it.  Shared symbols are discarded entirely rather
than averaged in.  Since the linker emits each object's data in the same order
as its code, the owned addresses should climb monotonically as you walk forward
through the code, and a retreat marks an object boundary.

    py -3 tools/tu_own.py
    py -3 tools/tu_own.py --write
"""
import argparse
import json
import os
import re
import statistics
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import funcs as funcs_mod                                        # noqa: E402

ASM = os.path.join(REPO, "asm", "code_002800.s")
LABEL = re.compile(r"^(?:glabel|dlabel)\s+(\S+)")
ADDR = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8})[^*]*\*/")
DREF = re.compile(r"\bD_(8[0-9A-F]{7})\b")


def collect():
    out, cur = [], None
    for line in open(ASM):
        m = LABEL.match(line)
        if m:
            cur = {"name": m.group(1), "addr": None, "refs": set()}
            out.append(cur)
            continue
        if cur is None:
            continue
        m = ADDR.match(line)
        if m and cur["addr"] is None:
            cur["addr"] = int(m.group(1), 16)
        for d in DREF.findall(line):
            cur["refs"].add(int(d, 16))
    fns = [f for f in out if f["addr"] is not None]
    fns.sort(key=lambda f: f["addr"])
    return fns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()

    fns = collect()
    game = [f for f in fns if f["addr"] < funcs_mod.GAME_END]

    # how many functions reference each data symbol (across the whole binary,
    # so SDK references also count against exclusivity)
    refcount = defaultdict(int)
    for f in fns:
        for a in f["refs"]:
            refcount[a] += 1

    for f in game:
        owned = sorted(a for a in f["refs"] if refcount[a] == 1)
        f["owned"] = owned

    with_owned = [f for f in game if f["owned"]]
    total_refs = sum(len(f["refs"]) for f in game)
    total_owned = sum(len(f["owned"]) for f in game)
    print("game functions: %d" % len(game))
    print("data references: %d total, %d exclusively owned (%.1f%%)"
          % (total_refs, total_owned,
             100.0 * total_owned / total_refs if total_refs else 0))
    print("functions with at least one owned symbol: %d" % len(with_owned))

    # Walk only the functions that carry the signal; a function with no owned
    # data tells us nothing and must not reset the running position.
    boundaries = []
    last = None
    for f in with_owned:
        lo = f["owned"][0]
        if last is not None and lo < last:
            boundaries.append({"addr": f["addr"], "name": f["name"],
                               "owned_lo": lo, "retreat": last - lo})
        last = max(last, f["owned"][-1]) if last is not None else f["owned"][-1]

    print("candidate boundaries: %d" % len(boundaries))

    idx = {f["name"]: i for i, f in enumerate(game)}
    cuts = sorted(idx[b["name"]] for b in boundaries)
    sizes, prev = [], 0
    for c in cuts:
        if c > prev:
            sizes.append(c - prev)
            prev = c
    sizes.append(len(game) - prev)
    sizes = [s for s in sizes if s]
    if sizes:
        print("implied unit sizes: median %.0f functions, mean %.1f, max %d"
              % (statistics.median(sizes), statistics.mean(sizes), max(sizes)))

    print("\n  %-10s %-22s %-12s %s" % ("addr", "function", "owned_lo", "retreat"))
    for b in boundaries[:args.show]:
        print("  0x%08X %-22s 0x%08X   -0x%X"
              % (b["addr"], b["name"], b["owned_lo"], b["retreat"]))
    if len(boundaries) > args.show:
        print("  ... and %d more" % (len(boundaries) - args.show))

    if args.write:
        path = os.path.join(REPO, "config", "tu_owned.json")
        json.dump(boundaries, open(path, "w"), indent=2)
        print("\nwrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
