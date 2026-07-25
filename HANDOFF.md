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
PY tools/sample.py --state 4        # hotness ranking from the in-duel state
PY tools/sample.py --report         # reprint the last ranking
PY tools/trace.py --state 4         # breakpoint coverage (slow: ~4 s/frame)
```

## Current state

```
1206 game functions, 99,265 instructions
 317 matched (26.29% of functions, 4.28% of instructions)
 321 todo functions use $gp (43,639 instructions, 43.96% of game code)
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
2. **The evidence-backed targets.** Sampling the in-duel save state named 11
   functions that actually execute, 1,179 instructions, none decompiled:
   `func_8004ADE8` (355), `func_8004C114` (195), `func_8004AAFC` (122),
   `func_8004C8C8` (102), `func_8004A0FC` (96), `func_800478EC` (95),
   `func_80049FB4` (82), `func_8004B374` (74), `func_8004B734` (72),
   `func_8004A43C` (55), `func_8004C84C` (31). They are one coherent module --
   the **sound driver** behind `D_8009B458` -- so they are worth doing together
   as a translation unit. `func_8005BFC8` (139) and `func_80043960` (155) came
   from the earlier boot sampling and still stand.
   `PY tools/sample.py --state 4 --report` reprints the list.

3. **The register-allocation class, now with better candidates.** ~12 known
   near-misses differ only by register allocation. Three fresh ones from this
   session are in `build/rejected/` with correct length and structure:
   `func_8005F1B8` (3/49 -- the best permuter candidate in the repo),
   `func_80018C34` (4/49), and `func_8004C84C`. Do not sweep more flags; a
   30-combination sweep separated none of them. `tools/ref/gcc-2.95.2/gcc/
   local-alloc.c` is on disk.

4. **Pad input under Lua, to reach duel logic.** The duel sampling above is the
   *idle* loop: no controller input is supplied, so summon, attack and fusion
   logic are still unmeasured. Driving the pad from `tools/sample.lua` is the
   cheapest way to extend coverage into the code this project most wants to read.

5. **`include/game.h`** exists with 17 machine-checked structs, plus
   `SoundVoice.unk_1E`. New work should use it. **Do not retrofit existing
   matching files onto it** -- `-G8` decides addressing from the *declaration's*
   size and `volatile` changes instruction count, so several files depend on
   their local declaration exactly as written.

6. **Execution coverage, the expensive half.** Breakpoint coverage under
   `-interpreter` still does not scale: ~4 s/frame with 1206 armed. Batching
   ~100 per pass over 13 passes would give true coverage of a restored state,
   which is now affordable per-pass because the state load skips the boot.
   Static call-graph reachability from `__SN_ENTRY_POINT` remains the cheap
   alternative and needs no emulator.

### Resolved since the last handoff, do not redo

* **`expand_div` works.** ASPSX's two-guard division macro is emitted, verified
  against target bytes. 38 game functions / 9,580 instructions (9.66%) are
  unblocked; nearly all are large.
* **Division by a literal is unmatchable by construction.** GCC 2.95.2
  strength-reduces it at every `-O` level. A real `div` on a constant proves the
  source named the divisor in a *variable*, declared at its point of use.
* **The duel save states exist**, in `tools/states/` (gitignored). This was the
  item marked "needs a human".

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
