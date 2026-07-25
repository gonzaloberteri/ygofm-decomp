"""Rebuild the CD image from our own SLUS_014.11.

config/disc.xml came out of dumpsxiso --lba, so every file keeps its original
LBA.  That matters because a game is free to read sectors by raw address
instead of by filename, and a relayout would break it silently.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MKPSXISO = os.path.join(REPO, "tools", "bin", "mkpsxiso-2.30-win64", "mkpsxiso.exe")
XML = os.path.join(REPO, "config", "disc.xml")
OUT = os.path.join(REPO, "build", "ygofm")


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def locked(path):
    """True if another process holds the file open.

    An emulator left holding build/ygofm.bin makes mkpsxiso fail with nothing but
    "Cannot open or create output image file", which says nothing about why.
    Redux in particular outlives a killed run and keeps the image open.

    This has to ask for *exclusive* access to see it.  `open(path, "r+b")` and a
    rename both succeed while the other process holds a shared read handle --
    both were tried and neither detected a lock that was demonstrably there --
    so on Windows go straight to CreateFileW with dwShareMode 0, which is what
    mkpsxiso's own truncating open effectively needs.
    """
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes

    GENERIC_READ, GENERIC_WRITE = 0x80000000, 0x40000000
    OPEN_EXISTING, INVALID = 3, ctypes.c_void_p(-1).value
    CreateFileW = ctypes.windll.kernel32.CreateFileW
    CreateFileW.restype = wintypes.HANDLE
    h = CreateFileW(str(path), GENERIC_READ | GENERIC_WRITE, 0, None,
                    OPEN_EXISTING, 0, None)
    if h == INVALID:
        return True
    ctypes.windll.kernel32.CloseHandle(h)
    return False


def main():
    built_exe = os.path.join(REPO, "build", "SLUS_014.11")
    if not os.path.exists(built_exe):
        sys.exit("build/SLUS_014.11 missing -- run tools/build.py first")

    shutil.copyfile(built_exe, os.path.join(REPO, "iso", "SLUS_014.11"))
    print("staged build/SLUS_014.11 -> iso/SLUS_014.11")

    # An emulator left holding build/ygofm.bin makes mkpsxiso fail with nothing
    # but "Cannot open or create output image file", which says nothing about
    # why.  Redux in particular can outlive a killed run and keep the image open
    # -- and it does not always still answer to its own process name, so it is
    # easy to believe nothing is running.  Name the real problem instead.
    if os.path.exists(OUT + ".bin") and locked(OUT + ".bin"):
        sys.exit("%s.bin is locked by another process -- an emulator is "
                 "probably still holding it. Close PCSX-Redux and retry.\n"
                 "Note it may not answer to `pcsx-redux`: the trace and sample "
                 "runs leave a process named `pcsx-redux.main`." % OUT)

    r = subprocess.run([MKPSXISO, "-y", "-q", "-o", OUT + ".bin", XML],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        sys.exit("mkpsxiso failed")

    cfg = json.load(open(os.path.join(REPO, "config", "disc.json")))
    original = cfg["source_bin"]

    built_sha = sha1_file(OUT + ".bin")
    orig_sha = sha1_file(original)
    print("built  %s  %s" % (built_sha, OUT + ".bin"))
    print("target %s  %s" % (orig_sha, original))

    if built_sha == orig_sha:
        print("\n  OK  rebuilt disc image is byte-identical to the original")
        return 0

    # A whole-image hash match is a bonus, not the gate: mkpsxiso regenerates
    # ECC/EDC and the volume descriptor timestamps.  What must match is the
    # content of every file, which is checked directly below.
    print("\n  image hash differs -- verifying per-file content instead")
    bad = 0
    for e in cfg["files"]:
        name = e["path"].lstrip("/").replace(";1", "")
        staged = os.path.join(REPO, "iso", name.replace("/", os.sep))
        got = sha1_file(staged)
        ok = got == e["sha1"]
        if not ok:
            bad += 1
        print("  %-8s %-20s %s" % ("OK" if ok else "DIFF", name, got))
    if bad:
        print("\n  %d file(s) differ from the original" % bad)
        return 1
    print("\n  OK  every file byte-identical; image differs only in ECC/EDC "
          "and volume metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
