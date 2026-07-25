"""Run the game under PCSX-Redux and record which functions actually execute.

Function choice for decompilation has so far been driven by size and address
order.  That is a poor proxy: a 20-instruction function that never runs on the
way to a duel is worth less than a 200-instruction one that runs every frame.
This produces the coverage set, so effort can follow execution.

PCSX-Redux is used rather than DuckStation because it has a Lua API; DuckStation
has no scripting at all, which is why the existing boot check could only assert
that the process stayed alive.

    py -3 tools/trace.py                    trace from boot, 1800 frames
    py -3 tools/trace.py --frames 600
    py -3 tools/trace.py --report           just re-report the last trace
"""
import argparse
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import funcs as funcs_mod                                        # noqa: E402

REDUX = os.path.join(REPO, "tools", "bin", "redux", "pcsx-redux.exe")
# The real BIOS, copied from DuckStation. Redux otherwise falls back to
# OpenBIOS, which is a reimplementation and not something to trust for running a
# commercial game -- a trace taken under it would not be evidence about the real
# boot path.
BIOS = os.path.join(REPO, "tools", "bin", "redux", "SCPH1001.BIN")
IMAGE = os.path.join(REPO, "build", "ygofm.bin")
WORK = os.path.join(REPO, "build", "trace")
FUNCS_TXT = os.path.join(WORK, "funcs.txt")
HITS_TXT = os.path.join(WORK, "hits.txt")


def write_function_list():
    """Addresses of every game function, for the Lua side to breakpoint."""
    fns = [f for f in funcs_mod.parse() if f["addr"] < funcs_mod.GAME_END]
    fns.sort(key=lambda f: f["addr"])
    os.makedirs(WORK, exist_ok=True)
    with open(FUNCS_TXT, "w") as fp:
        for f in fns:
            fp.write("%08X %s %d\n" % (f["addr"], f["name"], f["insns"]))
    return {f["addr"]: f for f in fns}


def report(index):
    if not os.path.exists(HITS_TXT):
        print("no trace results at %s" % HITS_TXT)
        return 1

    header, hits = "", {}
    for line in open(HITS_TXT):
        if line.startswith("#"):
            header = line.strip()
            continue
        parts = line.split()
        if len(parts) >= 2:
            hits[int(parts[0], 16)] = int(parts[1])

    print(header)
    total_ins = sum(f["insns"] for f in index.values())
    hit_ins = sum(index[a]["insns"] for a in hits if a in index)
    print("\nexecuted %d of %d functions (%.1f%%)"
          % (len(hits), len(index), 100.0 * len(hits) / max(1, len(index))))
    print("covering %d of %d instructions (%.1f%%)"
          % (hit_ins, total_ins, 100.0 * hit_ins / max(1, total_ins)))

    # The useful output: executed functions, largest first.  These are the ones
    # where decompilation effort buys the most understanding of what the game
    # actually does.
    ranked = sorted((index[a] for a in hits if a in index),
                    key=lambda f: -f["insns"])
    print("\nlargest executed functions (decompile these first):")
    print("  %-20s %-12s %6s  %s" % ("function", "address", "insns", "first seen"))
    for f in ranked[:25]:
        print("  %-20s 0x%08X %6d  frame %d"
              % (f["name"], f["addr"], f["insns"], hits[f["addr"]]))

    never = [f for a, f in index.items() if a not in hits]
    never_ins = sum(f["insns"] for f in never)
    print("\n%d functions never executed (%d instructions, %.1f%% of game code)"
          % (len(never), never_ins, 100.0 * never_ins / max(1, total_ins)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=1800)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    index = write_function_list()
    if args.report:
        return report(index)

    if not os.path.exists(IMAGE):
        sys.exit("%s missing -- run tools/make_iso.py first" % IMAGE)
    if os.path.exists(HITS_TXT):
        os.remove(HITS_TXT)

    # -run is required: without it the emulator boots, sits paused, and exits.
    # -debugger and -interpreter: the x86-64 dynarec does not check breakpoints,
    # so 1206 armed breakpoints produced zero hits while the game demonstrably
    # ran. The interpreter is slower but is the only mode that observes them.
    cmd = [REDUX, "-no-ui", "-stdout", "-run", "-debugger", "-interpreter",
           "-bios", BIOS,
           "-iso", IMAGE,
           "-dofile", os.path.join("tools", "trace.lua"),
           "-logfile", os.path.join("build", "trace", "redux.log"),
]
    print("tracing %d frames under PCSX-Redux..." % args.frames)
    # stdin must stay open: with -no-ui the TUI reads stdin, and an immediate EOF
    # makes it quit before the game runs at all. That looked exactly like the Lua
    # script failing.
    env = dict(os.environ, TRACE_FRAMES=str(args.frames))
    proc = subprocess.Popen(cmd, cwd=REPO, stdin=subprocess.PIPE, env=env)
    try:
        proc.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print("emulator hit the %ds timeout; killing it" % args.timeout)
        proc.kill()
        proc.wait(timeout=30)

    return report(index)


if __name__ == "__main__":
    sys.exit(main())
