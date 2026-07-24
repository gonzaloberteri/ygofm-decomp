"""Locate .text/.data regions in the flat SLUS_014.11 payload.

Raw "does this word decode as a valid MIPS instruction" is a weak signal --
random data decodes cleanly ~70% of the time.  Real code has structure that
data does not:

  * `jr $ra` roughly every 30-60 instructions (one per function)
  * `addiu $sp, $sp, -N` prologues at function entry
  * branch/jump targets that land inside the executable

Scoring on those three gives a clean separation.
"""
import os

import rabbitizer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(REPO, "disc", "SLUS_014.11")
HDR = 0x800
VRAM = 0x80010000

data = open(EXE, "rb").read()[HDR:]
n = len(data) // 4
end_vram = VRAM + len(data)
words = [int.from_bytes(data[i * 4:i * 4 + 4], "little") for i in range(n)]

BLOCK = 0x4000 // 4          # 16 KB blocks

print("payload %d B, vram %08X..%08X\n" % (len(data), VRAM, end_vram))
print("  offset      vram       valid%%  jr$ra/1k  prologue/1k  target%%  verdict")

rows = []
for b in range(0, n, BLOCK):
    blk = words[b:b + BLOCK]
    nv = jr = pro = tgt = ntgt = 0
    for i, w in enumerate(blk):
        vram = VRAM + (b + i) * 4
        insn = rabbitizer.Instruction(w, vram=vram)
        if not insn.isValid():
            continue
        nv += 1
        if insn.isJrRa():
            jr += 1
        name = insn.getOpcodeName()
        if name == "addiu" and insn.rt == rabbitizer.RegGprO32.sp \
                and insn.rs == rabbitizer.RegGprO32.sp:
            imm = insn.getProcessedImmediate()
            if imm < 0:
                pro += 1
        if insn.isJumpWithAddress():
            ntgt += 1
            t = insn.getInstrIndexAsVram()
            if VRAM <= t < end_vram:
                tgt += 1

    k = len(blk) / 1000.0
    valid_pct = nv / len(blk) * 100
    jr_k, pro_k = jr / k, pro / k
    tgt_pct = (tgt / ntgt * 100) if ntgt else 0.0

    # code needs both a high decode rate AND real function structure
    is_code = valid_pct > 90 and jr_k > 3 and tgt_pct > 90
    verdict = "CODE" if is_code else "data"
    rows.append((b * 4, verdict))
    print("  0x%06X  0x%08X  %5.1f  %8.1f  %10.1f  %7.1f  %s"
          % (b * 4, VRAM + b * 4, valid_pct, jr_k, pro_k, tgt_pct, verdict))

# collapse into contiguous runs
print("\n=== regions ===")
runs, cur, start = [], rows[0][1], 0
for off, v in rows[1:] + [(n * 4, None)]:
    if v != cur:
        runs.append((start, off, cur))
        start, cur = off, v
for s, e, v in runs:
    print("  %-4s 0x%06X .. 0x%06X  (vram %08X .. %08X)  %8d B"
          % (v, s, e, VRAM + s, VRAM + e, e - s))
