"""Stage iso/ and config/disc.xml from the original disc image.

tools/make_iso.py rebuilds the image from iso/ using config/disc.xml, but until
now nothing in the pipeline produced either of them -- they were made by hand
with dumpsxiso and are gitignored, so a fresh clone got as far as make_iso.py
and died on a missing iso/SLUS_014.11.

--lba is the point of the whole thing: it writes every file's original LBA into
the XML so the rebuild pins each one to the sector it came from.  A game is free
to read sectors by raw address instead of by filename, and a relayout would
break it silently.

Idempotent: does nothing if both outputs already exist, unless --force.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toolchain

REPO = toolchain.REPO
DUMPSXISO = toolchain.dumpsxiso()
XML = os.path.join(REPO, "config", "disc.xml")
ISO_DIR = os.path.join(REPO, "iso")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", default=None,
                    help="path to the original .cue or .bin "
                         "(default: source_bin from config/disc.json)")
    ap.add_argument("--force", action="store_true",
                    help="re-extract even if iso/ and config/disc.xml exist")
    args = ap.parse_args()

    staged_exe = os.path.join(ISO_DIR, "SLUS_014.11")
    if not args.force and os.path.exists(XML) and os.path.exists(staged_exe):
        print("iso/ and config/disc.xml already staged")
        return 0

    image = args.image
    if image is None:
        cfg_path = os.path.join(REPO, "config", "disc.json")
        if not os.path.exists(cfg_path):
            sys.exit("config/disc.json missing -- run tools/extract_disc.py first")
        image = json.load(open(cfg_path))["source_bin"]
        # dumpsxiso wants the cue when there is one; it carries the track mode.
        cue = os.path.splitext(image)[0] + ".cue"
        if os.path.exists(cue):
            image = cue

    if not os.path.exists(image):
        sys.exit("disc image not found: %s" % image)
    if not os.path.exists(DUMPSXISO):
        sys.exit("dumpsxiso not found at %s -- see README Requirements"
                 % DUMPSXISO)

    os.makedirs(ISO_DIR, exist_ok=True)
    r = subprocess.run([DUMPSXISO, "-q", "-l", "-x", ISO_DIR, "-s", XML, image],
                       cwd=REPO)
    if r.returncode != 0:
        sys.exit("dumpsxiso failed")

    if not os.path.exists(staged_exe):
        sys.exit("dumpsxiso wrote no %s -- wrong image?" % staged_exe)
    print("staged iso/ and config/disc.xml from %s" % image)
    return 0


if __name__ == "__main__":
    sys.exit(main())
