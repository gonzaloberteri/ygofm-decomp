"""Boot the rebuilt image in DuckStation and confirm it reaches a duel.

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
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUCKSTATION = (r"C:\Users\PC\AppData\Local\Programs\DuckStation"
               r"\duckstation-qt-x64-ReleaseLTCG.exe")
STATE_DIR = r"C:\Users\PC\AppData\Local\DuckStation\savestates"
SERIAL = "SLUS-01411"

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


def write_cue():
    cue = os.path.join(REPO, "build", "ygofm.cue")
    with open(cue, "w") as fp:
        fp.write('FILE "ygofm.bin" BINARY\n'
                 "  TRACK 01 MODE2/2352\n"
                 "    INDEX 01 00:00:00\n")
    return cue


def boot(slot, seconds):
    state = os.path.join(STATE_DIR, "%s_%d.sav" % (SERIAL, slot))
    if not os.path.exists(state):
        print("  save state slot %d not found at %s" % (slot, state))
        return False

    cue = write_cue()
    cmd = [DUCKSTATION, "-batch", "-fastboot", "-statefile", state, "--", cue]
    print("  launching: slot %d (%s)" % (slot, SLOT_NAMES.get(slot, "?")))
    proc = subprocess.Popen(cmd)

    deadline = time.time() + seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            print("  emulator exited early with code %s" % proc.returncode)
            return False
        time.sleep(0.5)

    alive = proc.poll() is None
    print("  ran %ds, process %s" % (seconds, "alive" if alive else "dead"))
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    return alive


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", type=int, default=4)
    ap.add_argument("--seconds", type=int, default=20)
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
    if not boot(args.slot, args.seconds):
        print("\nFAIL  emulator did not stay up")
        return 1

    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
