"""Attempt every candidate function automatically: m2c -> compile -> compare.

m2c's `--valid-syntax` mode emits C that compiles without human intervention,
so a large share of small functions can be matched with no hand-editing at all.
Whatever matches is kept; whatever does not is left for manual work, with the
mismatch recorded so the hard cases can be triaged by shape rather than one at
a time.

    py -3 tools/autodecomp.py --limit 50
    py -3 tools/autodecomp.py --all
"""
import argparse
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import funcs as funcs_mod                                        # noqa: E402
from match import asm_inventory, object_functions, original_words  # noqa: E402

M2C = os.path.join(REPO, "tools", "m2c", "m2c.py")
CC = os.path.join(REPO, "tools", "cc.py")
ASM = os.path.join(REPO, "asm", "code_002800.s")
OUTDIR = os.path.join(REPO, "src", "auto")
GAME_END = funcs_mod.GAME_END

HEADER = '#include "types.h"\n#include "m2c_macros.h"\n\n'


def run_m2c(name):
    r = subprocess.run(
        [sys.executable, M2C, "--target", "mipsel-gcc-c", "--valid-syntax",
         "--function", name, ASM],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    body = r.stdout
    if "M2C_ERROR" in body or "GLOBAL_ASM" in body:
        return None
    return body


def attempt(name, inv, tmpdir):
    src = os.path.join(tmpdir, name + ".c")
    obj = os.path.join(tmpdir, name + ".o")

    body = run_m2c(name)
    if body is None:
        return "m2c-failed", None

    open(src, "w").write(HEADER + body)

    r = subprocess.run([sys.executable, CC, src, obj],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return "compile-failed", None

    try:
        built = object_functions(obj)
    except Exception:
        return "objread-failed", None
    if name not in built:
        return "not-emitted", None

    words, masks = built[name]
    vram, size = inv[name]
    if size != len(words) * 4:
        return "size-differs", None

    orig = original_words(vram, size)
    mism = sum(1 for i in range(len(words))
               if (words[i] & masks[i]) != (orig[i] & masks[i]))
    if mism == 0:
        return "match", open(src).read()
    return "differs:%d/%d" % (mism, len(words)), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max-insns", type=int, default=60)
    args = ap.parse_args()

    all_funcs = funcs_mod.parse()
    inv = asm_inventory()

    cands = [f for f in all_funcs
             if f["addr"] < GAME_END
             and f["name"] in inv
             and f["insns"] <= args.max_insns
             and f["name"].startswith("func_")
             and not f["gp"]]        # $gp needs the sdata layout first
    cands.sort(key=lambda f: f["insns"])
    if not args.all:
        cands = cands[:args.limit]

    os.makedirs(OUTDIR, exist_ok=True)
    tmpdir = os.path.join(REPO, "build", "auto")
    os.makedirs(tmpdir, exist_ok=True)

    stats = {}
    matched = []
    for i, f in enumerate(cands, 1):
        name = f["name"]
        status, text = attempt(name, inv, tmpdir)
        key = status.split(":")[0]
        stats[key] = stats.get(key, 0) + 1
        if status == "match":
            open(os.path.join(OUTDIR, name + ".c"), "w").write(text)
            matched.append((name, f["insns"]))
        if i % 25 == 0 or i == len(cands):
            print("  %d/%d attempted, %d matched"
                  % (i, len(cands), len(matched)), flush=True)

    print("\n=== results over %d candidates ===" % len(cands))
    for k in sorted(stats, key=lambda k: -stats[k]):
        print("  %-16s %d" % (k, stats[k]))

    insns = sum(n for _, n in matched)
    print("\nmatched %d functions, %d instructions (%d bytes)"
          % (len(matched), insns, insns * 4))
    print("written to src/auto/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
