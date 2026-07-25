# Unattended work prompt — ygofm-decomp

Paste everything below the line into a fresh agent session.

---

You are continuing a matching decompilation of **Yu-Gi-Oh! Forbidden Memories**
(PlayStation, NTSC-U, `SLUS-01411`) at `C:\Users\PC\Downloads\ygofm-decomp`.

**Work unattended. Do not ask questions — decide and proceed.** When a goal is
met, pick the next one yourself from the queue below or create a better one, and
keep going. Do not stop to check in; report progress as you land it.

## Read these first, in order

1. `README.md` — what the project is and how to build it.
2. `PLAN.md` — the authoritative record. Long, but it contains every finding,
   every compiler idiom, and **every retraction**. Read the status log entries
   from the bottom up; several early claims in it were later proven wrong and are
   marked as corrected. Do not act on an early claim without checking whether a
   later entry retracts it.
3. `HANDOFF.md` (this file, in the repo).

## The invariant that governs everything

Every commit must rebuild the game **byte-identically**:

```
SLUS_014.11    84747e64f6da8e764206ec203e489acf8c9dcf7d
disc image     d5785a41900a10968d4a28a390666c4b9879b796
```

Functions not yet decompiled are linked from extracted assembly, so the build is
always complete and the game always runs. A decompiled function either assembles
to the same bytes or it is rejected. There is no "looks correct".

**A non-matching file in `src/` is not harmless work-in-progress — it silently
replaces correct assembly with wrong code.** Never commit one.

## Environment

- **Windows-native.** The Psy-Q tools are 32-bit PE and run under WOW64. There is
  no WSL distro and installing one is out of scope.
- Python is `.venv/Scripts/python.exe` (call it `PY`). Bare `python` on PATH is
  the Microsoft Store stub and does not work.
- Run every command from the repo root. Several tools resolve paths relative to it.
- 16 cores. `tools/autodecomp.py`, `tools/build.py` and `tools/verify_src.py` are
  already parallel; use `--jobs`.

## Commands

```bash
PY tools/all.py                      # whole pipeline, ends byte-identical or non-zero
PY tools/verify_src.py               # per-file check — names the offending file
PY tools/verify_src.py --quarantine  # move failures to build/rejected/
PY tools/build.py                    # the hash gate, ~7 s
PY tools/progress_map.py             # progress.png + the honest numbers
PY tools/match.py src/manual/X.c     # one file, must print MATCH
PY tools/flagsweep.py src/manual/X.c # search the flag space for a file
PY tools/autodecomp.py --all --max-insns 250 --jobs 16
PY tools/permute.py func_XXXXXXXX --run   # decomp-permuter, for register diffs
PY tools/funcs.py --candidates       # pick targets
```

## Current state

```
1206 game functions, 99,265 instructions
 234 matched (19.40% of functions, 3.36% of instructions)
 404 use $gp (45.1% of game code)
 720 SDK functions, 409 named by signature, none decompiled
```

**Instructions matched is the metric. Function count flatters the work by ~6x**
because automation matched the smallest functions first. Quote both or quote
instructions.

## Toolchain — recovered, not guessed

`CC1PSX.EXE` = GCC **2.95.2** (Psy-Q 4.6), assembler ASPSX **2.86** via `maspsx`.
**Flags vary per translation unit.** Three independent knobs, set in a comment in
each source file:

```c
/* decomp-flags: opt=-O2 as_G=8 cc1_G=0 cc1_extra=-fno-schedule-insns2 */
```

- `opt` — **`-O2` dominates**, `-O1` common, `-O3` rare, and at least one function
  was built with **no `-O` at all** (`opt=-O0,-fomit-frame-pointer`, comma
  separated). `-Os` matched one function nothing else could.
- `as_G` — the *assembler's* `-G`: `offset($gp)` versus a `%hi/%lo` pair.
- `cc1_G` — the *compiler's* `-G`; changes register allocation independently.
- `cc1_extra` — e.g. `-fno-schedule-insns2`, `-fschedule-insns2`,
  `-fno-strength-reduce`. Comma separated.

`PLAN.md` has ~30 verified compiler idioms (branch inversion, loop reversal,
`i[array]`, float-constant register copies, `volatile` on `$gp` words). **Read
them before hand-decompiling anything** — four parallel workers rediscovered the
same ones independently, which was wasted effort.

## Work queue — start at the top, reorder if you have reason

1. **Hand-decompile from `tools/funcs.py --candidates`.** The reliable earner:
   four workers averaged ~12–20 matches each. The technique that actually works is
   disassembling your own object with `mipsel-none-elf-objdump -d` and reading it
   beside `asm/code_002800.s` — not sweeping flags blind.
2. **`func_8005BFC8` (139 insns) and `func_80043960` (155 insns).** The only
   *evidence-backed* targets so far: PC sampling under PCSX-Redux showed they
   actually execute. Prefer functions known to run.
3. **The register-allocation class.** ~12 known near-misses differ by exactly one
   register because the original wants `-fschedule-insns2`'s ordering with the
   non-sched2 allocation. `tools/permute.py` took one from score 40 to 10 in
   45,000 iterations, then plateaued. `tools/ref/gcc-2.95.2/gcc/local-alloc.c` is
   on disk — reading why sched2 changes allocation either answers this or closes
   it. Do not sweep more flags; a 30-combination sweep separated none of them.
4. **`expand_div` is broken and known-broken.** ASPSX's division macro is still
   not emitted, so any function with `/` or `%` cannot match. `maspsx`'s `div`/`rem`
   handler returns early for a `$zero` destination *before* the expansion block,
   and the expansion assumes the destination register is in the `div` line whereas
   GCC emits a separate `mfhi`. Fixing it needs that split form handled in
   `tools/maspsx` (our fork).
5. **`include/game.h`** exists with 17 machine-checked structs. New work should use
   it. **Do not retrofit existing matching files onto it** — `-G8` decides
   addressing from the *declaration's* size and `volatile` changes instruction
   count, so several files depend on their local declaration exactly as written.
6. **Execution coverage (optional, expensive).** Breakpoints work but 1206 of them
   slow the interpreter to frame 400 in 45 minutes. Batching ~100 per pass over 13
   passes would give true boot coverage. Sampling is fast but aliases against the
   60 Hz loop. Static call-graph reachability from `__SN_ENTRY_POINT` needs no
   emulator and is the cheap alternative.

## Hard rules

- **Verify before believing a negative result.** Four times in this project a
  mechanism was declared broken when the real cause was that the code under test
  never ran: a "verification" that counted the compiler's own guard rather than
  the feature's output; a `; echo "PUSHED"` after a broken `&&` chain; a permuter
  "plateau" that was an instant crash; and a breakpoint "failure" caused by a
  missing `-fastboot` so the game never started. **Before concluding something
  does not work, prove it executed.** Run the control.
- Run `PY tools/verify_src.py` before every commit. Never `git add -A` while
  something else is writing to `src/`.
- Never commit a file that does not print `MATCH`. Quarantine, do not delete.
- Do not rewrite pushed git history. Keep `tools/ref/` and `tools/bin/` out of
  git — a 12.9 MB tarball was committed once and had to be reset.
- Third-party tools we patched are **forks pinned as submodules**
  (`gonzaloberteri/maspsx`, `gonzaloberteri/decomp-permuter`). Patch there, commit
  with an explanation, advance the pin — do not vendor loose copies.
- Byte equality does not mean the C is *correct*. One worker found that swapping a
  call's arguments byte-matched but was semantically wrong, and declined. Do the
  same.
- Push to `gonzaloberteri/ygofm-decomp` as you go. Update `PLAN.md` with findings
  **and with retractions** — the record's value is that it says where it was wrong.

## Needs a human, do not try to work around

Duel-path execution coverage needs a **PCSX-Redux save state** at a duel;
DuckStation's format is not portable and the existing slots 1–4 are DuckStation's.
Note it and move on.

## Definition of done

There isn't one. Maximise **instructions matched** while the hash stays green.
When the queue empties, generate the next goals from what the evidence says is
blocking, and continue.
