"""Search CC1PSX flag combinations for the ones that make a file match.

Psy-Q projects routinely used different flags per translation unit, and the
optimisation level is not recoverable from the binary by inspection -- it has
to be found by trying.  This brute-forces the small space of plausible flags
and reports which combinations match the most functions.

    py -3 tools/flagsweep.py src/globals.c
"""
import argparse
import itertools
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

# -Os is not decoration: one function matched only at -Os, and it got two
# others closer than any other level. It was missing from the first sweep.
OPT = ["-O0", "-O1", "-O2", "-O3", "-Os"]
TOGGLES = [
    [],
    ["-fno-builtin"],
    ["-funroll-loops"],
    ["-fpeephole"],
    ["-fno-peephole"],
    ["-fomit-frame-pointer"],
    ["-fno-function-cse"],
]
GFLAGS = ["-G0", "-G4", "-G8"]


def try_flags(src, flags):
    # "--flags=..." as one argv entry: argparse refuses a separate value that
    # starts with '-', and a single-flag sweep would hit that every time.
    r = subprocess.run(
        [PY, os.path.join(REPO, "tools", "match.py"), src,
         "--flags=" + " ".join(flags)],
        capture_output=True, text=True)
    out = r.stdout
    m = re.search(r"(\d+) matched, (\d+) differ", out)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()

    results = []
    combos = [list(o) + list(g) + list(t)
              for o, g, t in itertools.product([[o] for o in OPT],
                                               [[g] for g in GFLAGS],
                                               TOGGLES)]
    print("trying %d flag combinations..." % len(combos))
    for flags in combos:
        res = try_flags(args.src, flags)
        if res is None:
            continue
        ok, bad, _ = res
        results.append((ok, -bad, flags))

    results.sort(reverse=True)
    best = results[0][0] if results else 0
    print("\nbest: %d function(s) matched\n" % best)
    print("  matched  differ  flags")
    for ok, negbad, flags in results[:args.top]:
        print("  %7d  %6d  %s" % (ok, -negbad, " ".join(flags)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
