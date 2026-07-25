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
PY tools/sidebyside.py src/manual/X.c   # our output aligned against the original
```

**Watch what you leave running.** `tools/permute.py --jobs N` spawns roughly 6N
processes once cc1 and maspsx children are counted -- `--jobs 14` reached 88
processes and 1.2 GB. Use `--jobs 4` unless the machine is idle, and stop it when
it plateaus rather than leaving it going across a whole session.

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
2. **Unblock the sound driver: why does the original reload `D_8009B458`?**
   This is the highest-leverage unknown in the project. Nine of the eleven
   evidence-backed duel targets reload that pointer from memory *inside* their
   loops; GCC 2.95.2 hoists the load out under everything tried (all three
   allocation modes, both `cc1_G` values, eight `-fno-*` pass flags, a volatile
   pointer, capturing it in the loop condition). **1,102 of 1,279 instructions
   sit behind it** -- six times more code than any individual near-miss.
   GCC is not wrong to hoist: a `u16` store through a `SoundVoice *` cannot
   alias a `SoundWork *` variable. So the question is what the original build
   did differently. `loop.c` / `gcse.c` in `tools/ref/gcc-2.95.2/` is the place
   to look, the same way `local-alloc.c` answered the `-Os` question.

3. **The two tractable duel targets**, which do *not* have that blocker:
   `func_800478EC` (95 insns, untouched) and `func_80049FB4` (82, parked at the
   exact length and instruction sequence, 53 words differing on registers).
   `PY tools/sample.py --state 4 --report` reprints the ranking.

4. **Pad input under Lua, to reach real duel logic.** Today's duel coverage is
   the *idle* loop -- no controller input is supplied, so it is the sound
   driver and the per-frame render path. Summon, attack and fusion logic are
   still unmeasured. Driving the pad from `tools/sample.lua` is the cheapest way
   into the code this project most wants to read.

5. **The register-allocation class.** Parked in `build/rejected/`, all with
   correct structure: `func_8005F1B8` (3/49), `func_80018C34` (4/49),
   `func_80049FB4` (53/82). Try `-Os` first -- it is a distinct allocation mode,
   not a size heuristic. Do not sweep more flags. The permuter plateaus at score
   10 on this class and **some of its winning variants are semantically wrong**,
   so read anything it produces before using it.

6. **`func_8004B734` is 71 of 72 and is a different problem.** The single
   residual is a delay slot: the original leaves `nop` in the loop-back branch
   and materialises the return value after it, where GCC hoists the zeroing into
   the slot. The permuter cannot help -- no rewriting of C adds a `nop`.
   `reorg.c` is the place to look.

7. **`include/game.h`** has 17 machine-checked structs, plus `SoundVoice.unk_1E`
   and `SoundWork.unk_50C` as a function pointer. New work should use it. **Do
   not retrofit existing matching files onto it** -- `-G8` decides addressing
   from the *declaration's* size and `volatile` changes instruction count.

8. **Execution coverage, the expensive half.** Breakpoints under `-interpreter`
   cost ~4 s/frame with 1206 armed. Batching ~100 per pass is now affordable
   per-pass because a save state skips the boot. Static call-graph reachability
   from `__SN_ENTRY_POINT` remains the cheap alternative.

### Resolved since the last handoff, do not redo

* **`expand_div` works.** ASPSX's two-guard division macro is emitted, verified
  against target bytes. 38 game functions / 9,580 instructions (9.66%) are
  unblocked; nearly all are large.
* **Division by a literal is unmatchable by construction.** GCC 2.95.2
  strength-reduces it at every `-O` level. A real `div` on a constant proves the
  source named the divisor in a *variable*, declared at its point of use.
* **The duel save states exist**, in `tools/states/` (gitignored). This was the
  item marked "needs a human".
* **The register-allocation wall is explained.** `local-alloc.c` widens a
  quantity's lifetime to avoid reusing a just-dead register, gated on
  `flag_schedule_insns_after_reload && !optimize_size`. So there are **three**
  modes: `-O2` (sched2 + widening), `-Os` (sched2, no widening), and
  `-fno-schedule-insns2` (neither). PLAN's "no flag separates them" is retracted.
* **`tools/permute.py` was broken** -- it passed neither `cc1_G` nor
  `expand_div`, so anything not passed fell back to defaults. Base scores from
  before that fix are meaningless.
* **`tools/sidebyside.py` exists** for when `match.py` can only say the size is
  wrong. Use it rather than hand-rolling an objdump comparison (and note
  `objdump` hides `nop`s without `-z`).

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
