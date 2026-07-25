"""Boot the rebuilt image in PCSX-Redux and confirm it reaches a duel.

Two layers of verification:

  1. Exact gate (always runs, no emulator needed): the rebuilt SLUS_014.11 and
     the rebuilt disc image must hash-match the originals.  While this holds,
     pixel-perfection is true by construction -- the console cannot tell the
     images apart.

  2. Smoke test: load the pre-duel save state on the *rebuilt* image and let it
     run.  This becomes the load-bearing check in M7, when decompiled C starts
     producing equivalent-but-not-identical code and layer 1 no longer applies.

Save state slots recorded from the original disc:
    1 = in-game start menu     2 = name input screen
    3 = first duel deck build  4 = in-game duel     <- acceptance target

The emulator is PCSX-Redux, the same one tools/trace.py and tools/sample.py use,
so the project needs exactly one emulator and one set of save states.  Redux is
the choice because its Lua API is what makes the analysis tools possible at all;
DuckStation, used here previously, has no scripting and forced this check to be
"the process did not exit", which a black screen or a spinning loop passes.  What
is measured now is Vsyncs delivered after the state is restored -- a hung game
stops producing frames even though the process stays alive.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDUX = os.path.join(REPO, "tools", "bin", "redux", "pcsx-redux.exe")
# The real BIOS.  Redux otherwise falls back to OpenBIOS, which is a
# reimplementation and not something to trust for judging whether the game boots.
BIOS = os.path.join(REPO, "tools", "bin", "redux", "SCPH1001.BIN")
# Shared with tools/trace.py and tools/sample.py -- one set of states, captured
# by hand in the Redux GUI (File -> Save state slots).
STATE_DIR = os.path.join(REPO, "tools", "states")
WORK = os.path.join(REPO, "build", "boot")

SLOT_NAMES = {
    1: "in-game start menu",
    2: "name input screen",
    3: "first duel deck build menu",
    4: "in-game duel",
}


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def exact_gate():
    """Rebuilt executable and disc image must be byte-identical."""
    cfg = json.load(open(os.path.join(REPO, "config", "disc.json")))
    ok = True

    exe_entry = next(e for e in cfg["files"] if e["path"].endswith("SLUS_014.11;1"))
    built_exe = os.path.join(REPO, "build", "SLUS_014.11")
    got = sha1_file(built_exe)
    print("  SLUS_014.11   %s  %s" % ("OK  " if got == exe_entry["sha1"] else "DIFF",
                                      got))
    ok &= got == exe_entry["sha1"]

    built_iso = os.path.join(REPO, "build", "ygofm.bin")
    got = sha1_file(built_iso)
    want = sha1_file(cfg["source_bin"])
    print("  disc image    %s  %s" % ("OK  " if got == want else "DIFF", got))
    ok &= got == want
    return ok


def boot(slot, frames, timeout):
    state = os.path.join(STATE_DIR, "SLUS01411.sstate%d" % slot)
    if not os.path.exists(state):
        print("  save state slot %d not found at %s" % (slot, state))
        print("  capture it in the Redux GUI first (File -> Save state slots)")
        return False

    image = os.path.join(REPO, "build", "ygofm.bin")
    if not os.path.exists(image):
        print("  %s missing -- run tools/make_iso.py first" % image)
        return False

    os.makedirs(WORK, exist_ok=True)
    result = os.path.join(WORK, "result.txt")
    if os.path.exists(result):
        os.remove(result)

    # -run is required: without it the emulator boots, sits paused and exits.
    # No -debugger/-interpreter here, unlike trace.py -- nothing is being
    # observed per instruction, so the dynarec is fine and much faster.
    cmd = [REDUX, "-no-ui", "-stdout", "-run", "-fastboot",
           "-bios", BIOS,
           "-iso", image,
           "-dofile", os.path.join("tools", "boot.lua"),
           "-logfile", os.path.join("build", "boot", "redux.log")]
    env = dict(os.environ, BOOT_STATE=state.replace("\\", "/"),
               BOOT_FRAMES=str(frames), BOOT_OUT=result)

    print("  launching: slot %d (%s), %d frames"
          % (slot, SLOT_NAMES.get(slot, "?"), frames))
    # stdin must stay open: with -no-ui the TUI reads stdin, and an immediate
    # EOF makes it quit before the game runs at all.
    proc = subprocess.Popen(cmd, cwd=REPO, stdin=subprocess.PIPE, env=env)
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("  emulator hit the %ds timeout; killing it" % timeout)
        proc.kill()
        proc.wait(timeout=30)
        return False

    if not os.path.exists(result):
        print("  emulator exited with code %s and wrote no result -- it died "
              "before finishing the run" % proc.returncode)
        return False

    line = open(result).read().strip()
    print("  %s" % line)
    # frame-limit is the pass: the game produced every frame asked of it after
    # the state was restored.  Any other reason means it stopped early.
    return "reason=frame-limit" in line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", type=int, default=4, choices=(1, 2, 3, 4))
    ap.add_argument("--frames", type=int, default=600,
                    help="frames to run after the state is restored (~10s)")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--no-boot", action="store_true",
                    help="run the exact gate only, skip launching the emulator")
    args = ap.parse_args()

    print("exact gate:")
    if not exact_gate():
        print("\nFAIL  rebuilt artifacts differ from the originals")
        return 1
    print("  -> rebuild is byte-identical; pixel-perfect by construction")

    if args.no_boot:
        return 0

    print("\nboot smoke test:")
    if not boot(args.slot, args.frames, args.timeout):
        print("\nFAIL  emulator did not stay up")
        return 1

    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
