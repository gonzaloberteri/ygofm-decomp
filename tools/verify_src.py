"""Check every C file against the original, and optionally quarantine failures.

`tools/build.py` links everything in `src/` and compares the whole binary, so one
bad file shows up as a hash mismatch somewhere in the image -- which tells you
that something is wrong but not which file.  This checks each file individually,
so a failure names itself.

That matters because a non-matching file is not a harmless work-in-progress: it
silently replaces correct assembly with wrong code.  A file either matches or it
does not belong in `src/`.

    py -3 tools/verify_src.py               report
    py -3 tools/verify_src.py --quarantine  move failures to build/rejected/
"""
import argparse
import concurrent.futures as cf
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import cc                                                        # noqa: E402
from match import asm_inventory, object_functions, original_words  # noqa: E402

REJECTED = os.path.join(REPO, "build", "rejected")


def sources():
    out = []
    for dirpath, _, files in os.walk(os.path.join(REPO, "src")):
        for fn in sorted(files):
            if fn.endswith(".c"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def check(src, inv):
    """(rel, ok, detail) for one source file."""
    rel = os.path.relpath(src, REPO).replace("\\", "/")
    obj = os.path.join(REPO, "build", "verify",
                       rel.replace("/", "_")[:-2] + ".o")
    os.makedirs(os.path.dirname(obj), exist_ok=True)
    try:
        cc.compile_c(src, obj)
    except SystemExit:
        return rel, False, "compile failed"
    except Exception as exc:                                     # noqa: BLE001
        return rel, False, "compile error: %s" % exc

    try:
        built = object_functions(obj)
    except Exception as exc:                                     # noqa: BLE001
        return rel, False, "unreadable object: %s" % exc

    known = [n for n in built if n in inv]
    if not known:
        return rel, False, "defines nothing in the disassembly"

    for name in sorted(known):
        words, masks = built[name]
        vram, size = inv[name]
        if size != len(words) * 4:
            return rel, False, ("%s size %d, original %d"
                                % (name, len(words) * 4, size))
        orig = original_words(vram, size)
        bad = sum(1 for i in range(len(words))
                  if (words[i] & masks[i]) != (orig[i] & masks[i]))
        if bad:
            return rel, False, "%s %d/%d instructions differ" % (name, bad, len(words))
    return rel, True, "%d function(s)" % len(known)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quarantine", action="store_true",
                    help="move failing files to build/rejected/")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()

    inv = asm_inventory()
    srcs = sources()
    print("checking %d source file(s)" % len(srcs))

    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda s: check(s, inv), srcs))

    bad = [r for r in results if not r[1]]
    for rel, _, detail in bad:
        print("  FAIL  %-40s %s" % (rel, detail))

    print("\n%d ok, %d failing" % (len(results) - len(bad), len(bad)))

    if bad and args.quarantine:
        os.makedirs(REJECTED, exist_ok=True)
        for rel, _, _ in bad:
            src = os.path.join(REPO, rel.replace("/", os.sep))
            shutil.move(src, os.path.join(REJECTED, os.path.basename(src)))
        print("moved %d file(s) to build/rejected/ -- kept, not deleted, so the "
              "work is not lost" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
