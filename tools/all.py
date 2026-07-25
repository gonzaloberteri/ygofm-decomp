"""Run the whole pipeline: disc -> asm -> byte-identical exe -> disc -> verify.

    py -3 tools/all.py            full rebuild and verify (boots the emulator)
    py -3 tools/all.py --no-boot  same, minus the emulator launch
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")

STEPS = [
    ("extract disc",      [PY, "tools/extract_disc.py"]),
    # iso/ and config/disc.xml are gitignored and are what make_iso.py rebuilds
    # from, so a fresh clone has to produce them before it can get that far.
    ("stage iso",         [PY, "tools/stage_iso.py"]),
    ("classify regions",  [PY, "tools/map_regions.py"]),
    ("generate config",   [PY, "tools/gen_splat_config.py"]),
    ("split",             [PY, "-m", "splat", "split", "config/splat.yaml"]),
    # per-file check before the whole-binary one: build.py reports a hash
    # mismatch somewhere in the image, which does not say which file is at
    # fault. This names it.
    ("verify sources",    [PY, "tools/verify_src.py"]),
    ("build executable",  [PY, "tools/build.py"]),
    ("build disc image",  [PY, "tools/make_iso.py"]),
    ("progress map",      [PY, "tools/progress_map.py"]),
]


def main():
    extra = sys.argv[1:]
    for name, cmd in STEPS:
        print("\n=== %s ===" % name)
        r = subprocess.run(cmd, cwd=REPO)
        if r.returncode != 0:
            print("\nFAILED at: %s" % name)
            return r.returncode

    print("\n=== verify ===")
    return subprocess.run([PY, "tools/verify_boot.py"] + extra, cwd=REPO).returncode


if __name__ == "__main__":
    sys.exit(main())
