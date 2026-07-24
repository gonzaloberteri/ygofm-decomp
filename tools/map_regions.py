"""Classify every 1 KB window of the payload as code / data / zero and emit a
splat subsegment list.

This is only the *initial* guess.  tools/build.py compares the linked output
against the original byte-for-byte, and any region that fails to round-trip
gets demoted to data on the next pass, so mistakes here are self-correcting.
"""
import json
import os

import rabbitizer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(REPO, "disc", "SLUS_014.11")
HDR = 0x800
VRAM = 0x80010000
WIN = 0x400                     # 1 KB classification window

payload = open(EXE, "rb").read()[HDR:]
n = len(payload) // 4
end_vram = VRAM + len(payload)
words = [int.from_bytes(payload[i * 4:i * 4 + 4], "little") for i in range(n)]


def classify(base_word, count):
    """Return 'zero', 'code' or 'data' for a window of `count` words."""
    blk = words[base_word:base_word + count]
    if not blk:
        return "data"
    if all(w == 0 for w in blk):
        return "zero"

    nv = jr = pro = tgt = ntgt = branch = 0
    for i, w in enumerate(blk):
        vram = VRAM + (base_word + i) * 4
        insn = rabbitizer.Instruction(w, vram=vram)
        if not insn.isValid():
            continue
        nv += 1
        if insn.isJrRa():
            jr += 1
        nm = insn.getOpcodeName()
        if (nm == "addiu" and insn.rt == rabbitizer.RegGprO32.sp
                and insn.rs == rabbitizer.RegGprO32.sp
                and insn.getProcessedImmediate() < 0):
            pro += 1
        if insn.isJumpWithAddress():
            ntgt += 1
            if VRAM <= insn.getInstrIndexAsVram() < end_vram:
                tgt += 1
        if insn.isBranch():
            branch += 1

    valid = nv / len(blk)
    if valid < 0.90:
        return "data"
    # jump targets that leave the executable are a hard tell for data
    if ntgt and tgt / ntgt < 0.90:
        return "data"
    # real code always has control flow
    if (jr + branch) == 0:
        return "data"
    if jr == 0 and pro == 0 and branch / len(blk) < 0.02:
        return "data"
    return "code"


wpw = WIN // 4
raw = []
for b in range(0, n, wpw):
    raw.append((b * 4, classify(b, wpw)))

# merge contiguous runs
runs = []
start, cur = raw[0][0], raw[0][1]
for off, kind in raw[1:] + [(len(payload), None)]:
    if kind != cur:
        runs.append([start, off, cur])
        start, cur = off, kind

# Absorb small data pockets that sit *between* code into the code region.
# These are jump tables and inline rodata; spimdisasm detects them itself and
# emits .word for them.  Keeping them in the same file matters because branches
# and local .L labels must not cross a file boundary -- the linker cannot
# resolve a local label defined in another object.
GAP = 0x4000
absorbed = []
i = 0
while i < len(runs):
    r = runs[i]
    if r[2] != "code":
        # look ahead: is this a short non-code gap between two code runs?
        j = i
        while j < len(runs) and runs[j][2] != "code":
            j += 1
        gap_len = runs[j - 1][1] - r[0]
        between_code = (absorbed and absorbed[-1][2] == "code") and j < len(runs)
        if between_code and gap_len <= GAP:
            absorbed.append([r[0], runs[j - 1][1], "code"])
            i = j
            continue
    absorbed.append(list(r))
    i += 1

# Demote isolated code islands surrounded by data.  A `bin` region round-trips
# byte-for-byte, so this is the safe direction to be wrong in; anything that
# turns out to be real code gets promoted once symbol discovery finds callers.
ISLAND = 0x2000
for i, r in enumerate(absorbed):
    if r[2] != "code" or (r[1] - r[0]) > ISLAND:
        continue
    left_data = i == 0 or absorbed[i - 1][2] != "code"
    right_data = i + 1 >= len(absorbed) or absorbed[i + 1][2] != "code"
    if left_data and right_data:
        r[2] = "data"

# final pass: coalesce adjacent runs of the same kind
merged = []
for r in absorbed:
    if merged and merged[-1][2] == r[2]:
        merged[-1][1] = r[1]
    else:
        merged.append(r)

print("=== initial segmentation ===")
code = zero = dat = 0
for s, e, k in merged:
    print("  %-5s 0x%06X .. 0x%06X   vram %08X   %9d B"
          % (k, s, e, VRAM + s, e - s))
    if k == "code":
        code += e - s
    elif k == "zero":
        zero += e - s
    else:
        dat += e - s

tot = len(payload)
print("\n  code %9d B (%5.1f%%)" % (code, code / tot * 100))
print("  data %9d B (%5.1f%%)" % (dat, dat / tot * 100))
print("  zero %9d B (%5.1f%%)" % (zero, zero / tot * 100))

os.makedirs(os.path.join(REPO, "config"), exist_ok=True)
with open(os.path.join(REPO, "config", "regions.json"), "w") as fp:
    json.dump([{"start": s, "end": e, "kind": k} for s, e, k in merged], fp, indent=2)
print("\nwrote config/regions.json")
