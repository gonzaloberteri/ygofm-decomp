"""Sample the program counter under PCSX-Redux and rank game code by hotness.

Companion runner for tools/sample.lua, which until now had none and was invoked
by hand -- so its results could not be reproduced from the repository.

Why sampling as well as tools/trace.py: breakpoint coverage answers "did this
function ever run", which is the better question, but 1206 execution breakpoints
are only observed by the interpreter and cost seconds per frame there.  Sampling
needs no breakpoints, so it runs under the x86-64 dynarec at full speed and can
afford thousands of frames.

    py -3 tools/sample.py                    from boot, 3600 frames
    py -3 tools/sample.py --state 4          from the in-duel save state
    py -3 tools/sample.py --report

Two caveats that the output cannot express and that matter for how it is used:

* The sample rate is one per Vsync, which **aliases against a 60 Hz game loop**.
  Treat the result as a ranking of hot code, not as coverage: a function absent
  from the samples has not been shown to be unused.
* No controller input is supplied, so a restored state runs its *idle* loop.
  Sampling the duel state shows the duel's per-frame update and render path, not
  the logic behind summoning or attacking.
"""
import argparse
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import funcs as funcs_mod                                        # noqa: E402
import trace as trace_mod                                        # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toolchain
REDUX = toolchain.redux()
BIOS = toolchain.bios()
IMAGE = os.path.join(REPO, "build", "ygofm.bin")
WORK = os.path.join(REPO, "build", "trace")
SAMPLES_TXT = os.path.join(WORK, "samples.txt")


def report(index, path):
    if not os.path.exists(path):
        print("no samples at %s" % path)
        return 1

    header, counts = "", {}
    for line in open(path):
        if line.startswith("#"):
            header = line.strip()
            continue
        parts = line.split()
        if len(parts) >= 2:
            counts[int(parts[0], 16)] = int(parts[1])

    done = set()
    for sub in ("manual", "auto"):
        d = os.path.join(REPO, "src", sub)
        if os.path.isdir(d):
            done |= {os.path.splitext(f)[0]
                     for f in os.listdir(d) if f.endswith(".c")}

    print(header)
    ranked = sorted(((c, index[a]) for a, c in counts.items() if a in index),
                    key=lambda t: -t[0])
    print("\n%-20s %-12s %8s %7s  %s"
          % ("function", "address", "samples", "insns", "decompiled"))
    for c, f in ranked:
        print("%-20s 0x%08X %8d %7d  %s"
              % (f["name"], f["addr"], c, f["insns"],
                 "yes" if f["name"] in done else "NO"))

    todo = [f for c, f in ranked if f["name"] not in done]
    print("\n%d of %d sampled functions are not yet decompiled "
          "(%d instructions)"
          % (len(todo), len(ranked), sum(f["insns"] for f in todo)))
    print("Sampling aliases against the 60 Hz loop -- this is a hotness "
          "ranking, not coverage.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=3600)
    ap.add_argument("--warmup", type=int, default=600,
                    help="frames to boot before restoring a save state; the "
                         "game EXE has not started before roughly 400")
    ap.add_argument("--state", type=int, default=None, choices=(1, 2, 3, 4),
                    help="sample from a save state slot instead of from boot")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--pad", nargs="?", const="", default=None,
                    metavar="SCRIPT",
                    help="drive the controller from tools/pad.lua, so a restored "
                         "state runs real logic instead of its idle loop; "
                         "optionally a comma-separated button list "
                         "(default: down,cross,right,cross,up,cross,left,cross)")
    ap.add_argument("--pad-hold", type=int, default=4,
                    help="frames to hold each button")
    ap.add_argument("--pad-gap", type=int, default=8,
                    help="frames released between buttons")
    args = ap.parse_args()

    out = os.path.join(WORK, args.out) if args.out else SAMPLES_TXT
    index = trace_mod.write_function_list()
    if args.report:
        return report(index, out)

    if not os.path.exists(IMAGE):
        sys.exit("%s missing -- run tools/make_iso.py first" % IMAGE)
    if os.path.exists(out):
        os.remove(out)

    env = dict(os.environ, SAMPLE_FRAMES=str(args.frames),
               SAMPLE_WARMUP=str(args.warmup), SAMPLE_OUT=out)
    if args.state:
        state = os.path.join(trace_mod.STATE_DIR,
                             "SLUS01411.sstate%d" % args.state)
        if not os.path.exists(state):
            sys.exit("%s missing -- capture the save states in the Redux GUI "
                     "first (File -> Save state slots)" % state)
        env["SAMPLE_STATE"] = state.replace("\\", "/")
        print("sampling %d frames from state %d (%s), after %d boot frames..."
              % (args.frames, args.state, trace_mod.SLOT_NAMES[args.state],
                 args.warmup))
    else:
        print("sampling %d frames from boot..." % args.frames)

    # The dynarec is deliberate here: it does not observe execution breakpoints,
    # but sampling does not use any, so there is nothing to lose and the speed is
    # what makes thousands of frames affordable.
    cmd = [REDUX, "-no-ui", "-stdout", "-run", "-fastboot",
           "-bios", BIOS, "-iso", IMAGE,
           "-dofile", os.path.join("tools", "sample.lua"),
           "-logfile", os.path.join("build", "trace", "sample.log")]

    if args.pad is not None:
        # pad.lua counts absolute Vsyncs and cannot see sample.lua's phases, so
        # it is told when to start.  A few frames after the restore, not on it:
        # the first frames back are the game reacting to the load.
        env["PAD_START"] = str((args.warmup + 30) if args.state else 30)
        env["PAD_HOLD"] = str(args.pad_hold)
        env["PAD_GAP"] = str(args.pad_gap)
        if args.pad:
            env["PAD_SCRIPT"] = args.pad
        at = cmd.index("-logfile")
        cmd[at:at] = ["-dofile", os.path.join("tools", "pad.lua")]
        print("  driving the controller from tools/pad.lua")
    # stdin must stay open: with -no-ui the TUI reads stdin, and an immediate EOF
    # makes it quit before the game runs at all.
    proc = subprocess.Popen(cmd, cwd=REPO, stdin=subprocess.PIPE, env=env)
    try:
        proc.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print("emulator hit the %ds timeout; killing it" % args.timeout)
        proc.kill()
        proc.wait(timeout=30)

    return report(index, out)


if __name__ == "__main__":
    sys.exit(main())
