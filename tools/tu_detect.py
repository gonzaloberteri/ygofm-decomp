"""Propose translation-unit boundaries in the linked code.

A linker emits each object's `.text` and its `.data`/`.sdata`/`.rodata` in the
same order, so within one translation unit the data a function touches tends to
sit in one band, and the band advances as you walk forward through the code.
Where that band jumps, an object boundary is likely.

Two independent signals are combined:

  * absolute data references, from `%hi`/`%lo` pairs naming `D_8xxxxxxx`
  * small-data offsets, from `n($gp)` and `addiu rX, $gp, n`

Neither is conclusive alone -- a function may reference another unit's globals,
and `extern` small variables still get `%hi/%lo` -- so this reports candidate
boundaries with a confidence, rather than pretending to be authoritative.

    py -3 tools/tu_detect.py
    py -3 tools/tu_detect.py --write   # write config/tu_boundaries.json
"""
import argparse
import json
import os
import re
import statistics
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import funcs as funcs_mod                                        # noqa: E402

ASM = os.path.join(REPO, "asm", "code_002800.s")
LABEL = re.compile(r"^(?:glabel|dlabel)\s+(\S+)")
ADDR = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8})[^*]*\*/")
DREF = re.compile(r"\bD_(8[0-9A-F]{7})\b")
GPREF = re.compile(r"(-?0x[0-9A-Fa-f]+)\(\$gp\)")
GPADD = re.compile(r"addiu\s+\$\w+,\s*\$gp,\s*(-?0x[0-9A-Fa-f]+)")


def collect():
    out, cur = [], None
    for line in open(ASM):
        m = LABEL.match(line)
        if m:
            cur = {"name": m.group(1), "addr": None, "data": set(), "gp": set()}
            out.append(cur)
            continue
        if cur is None:
            continue
        m = ADDR.match(line)
        if m and cur["addr"] is None:
            cur["addr"] = int(m.group(1), 16)
        for d in DREF.findall(line):
            cur["data"].add(int(d, 16))
        for g in GPREF.findall(line) + GPADD.findall(line):
            cur["gp"].add(int(g, 16))
    return [f for f in out if f["addr"] is not None
            and f["addr"] < funcs_mod.GAME_END]


def median_or_none(values):
    # median of an even-length list is a float; addresses must stay integral
    return int(statistics.median(values)) if values else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=25)
    args = ap.parse_args()

    fns = collect()
    fns.sort(key=lambda f: f["addr"])
    print("game functions: %d" % len(fns))

    for f in fns:
        f["dmed"] = median_or_none(sorted(f["data"]))
        f["gmed"] = median_or_none(sorted(f["gp"]))

    # Track each output section separately.  Mixing them was hopeless: a single
    # function may touch a static at 0x8009xxxx and a const table at 0x801Bxxxx,
    # and a median over both moves by hundreds of KB for reasons that have
    # nothing to do with unit boundaries.
    BANDS = [("data/bss", 0x80092C00, 0x8013A000),
             ("rodata",   0x801AC000, 0x801D9400)]

    for f in fns:
        for label, lo, hi in BANDS:
            vals = sorted(a for a in f["data"] if lo <= a < hi)
            f[label] = median_or_none(vals)

    # Inside one unit the band drifts forward; a retreat means we left it.
    boundaries = []
    last = {label: None for label, _, _ in BANDS}
    last["gp"] = None
    for i, f in enumerate(fns):
        score, why = 0, []
        for label, _, _ in BANDS:
            v = f[label]
            if v is None:
                continue
            if last[label] is not None and v < last[label] - 0x200:
                score += 1
                why.append("%s -0x%X" % (label, last[label] - v))
            last[label] = v
        if f["gmed"] is not None:
            if last["gp"] is not None and f["gmed"] < last["gp"] - 0x20:
                score += 1
                why.append("gp -0x%X" % (last["gp"] - f["gmed"]))
            last["gp"] = f["gmed"]
        if score:
            boundaries.append({"index": i, "addr": f["addr"],
                               "name": f["name"], "score": score,
                               "why": ", ".join(why)})

    strong = [b for b in boundaries if b["score"] >= 2]
    print("candidate boundaries: %d (%d supported by both signals)"
          % (len(boundaries), len(strong)))

    sizes = []
    prev = 0
    for b in boundaries:
        sizes.append(b["index"] - prev)
        prev = b["index"]
    sizes.append(len(fns) - prev)
    sizes = [s for s in sizes if s]
    if sizes:
        print("implied unit sizes: median %d functions, max %d, min %d"
              % (statistics.median(sizes), max(sizes), min(sizes)))

    print("\n  %-10s %-22s %-6s %s" % ("addr", "function", "score", "evidence"))
    for b in boundaries[:args.show]:
        print("  0x%08X %-22s %-6d %s"
              % (b["addr"], b["name"], b["score"], b["why"]))
    if len(boundaries) > args.show:
        print("  ... and %d more" % (len(boundaries) - args.show))

    if args.write:
        path = os.path.join(REPO, "config", "tu_boundaries.json")
        json.dump(boundaries, open(path, "w"), indent=2)
        print("\nwrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
