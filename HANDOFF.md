# Unattended work prompt — ygofm-decomp

Paste everything below the line into a fresh agent session.

---

You are continuing a matching decompilation of **Yu-Gi-Oh! Forbidden Memories**
(PlayStation, NTSC-U, `SLUS-01411`) at `C:\ygofm-decomp`.

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

## Machines — all three are set up and all three agree

Every machine below reproduces **all 340 source files byte-identically**
(`tools/verify_src.py`: 340 ok, 0 failing). `CC1PSX.EXE` is SHA256
`0755e509f148b6018e97e89e798493af37c290a44fc97ecd1ec661182ed56e65` on all
three. Do not re-derive this; it is measured.

| | address | cores | CC1PSX runs via |
|---|---|---|---|
| `.180` DESKTOP-9USQDG9 | 192.168.0.180 | 16 | WOW64 |
| `.209` DESKTOP-G51OOOE | 192.168.0.209 | 4 (Haswell) | WOW64 |
| `.201` MacBook Air M4 | 192.168.0.201 | 10 | **wibo under Rosetta 2** |

- **`.180` is where the interactive work goes**: matching, emulator runs,
  Ghidra. It is the only one with PCSX-Redux, the save states and the disc.
- **`.209`**: `ssh -o BatchMode=yes pc@192.168.0.209`, PowerShell, and the
  session is elevated. Python 3.13.7 from the python.org installer — **winget
  is broken there** (`0x8a15000f`, and `source reset` does not fix it).
- **`.201`**: `ssh gonza@192.168.0.201`, repo at
  `/Users/gonza/dev/ygofm-decomp`. It cannot rebuild the disc image (no
  mkpsxiso, no disc) and cannot boot anything (no Redux), but it compiles and
  matches, which is what batch work needs.

**Give the two remote machines batch work only** — `tools/flagsweep.py` and
`tools/permute.py` over `build/rejected/`. Use `--jobs 3` on `.209` and
`--jobs 8` on the Mac; `permute.py --jobs 14` reached 88 processes and 1.2 GB
on the 16-core box. Copy results back and re-verify with `tools/match.py` on
`.180`; **never trust a match that was not re-checked there.**

Three gitignored things have to be copied by hand to a new machine, over the
LAN and never through git or a cloud service: `tools/bin/psyq/p46` (the SDK,
proprietary), `disc/SLUS_014.11` and `asm/code_002800.s` (both generated, both
game-derived). About 22 MB. Plus the binutils tree — and note that
`tools/bin/bin` **alone is not enough**: `mipsel-none-elf-cpp` is a driver and
execs `cc1` out of `tools/bin/libexec/gcc/mipsel-none-elf/12.3.0/`, so
`libexec`, `lib` and `mipsel-none-elf` have to come too.

`tools/toolchain.py` reports what a machine can and cannot do; run it first on
any new host.

## Environment

- **Windows-native.** The Psy-Q tools are 32-bit PE and run under WOW64. There is
  no WSL distro and installing one is out of scope.
- **Leftover emulators lock `build/ygofm.bin`** and break `make_iso.py`. They do
  not always answer to `pcsx-redux` — look for **`pcsx-redux.main`** too. Kill
  strays before a full `all.py`.
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
PY tools/sample.py --state 4 --pad  # ...with the controller driven, for real logic
PY tools/sample.py --report         # reprint the last ranking
PY tools/trace.py --state 4         # breakpoint coverage (slow: ~4-10 s/frame)
PY tools/trace.py --state 4 --pad --batch 200   # coverage that actually finishes
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
2. **Unblock the sound driver — but read the 2026-07-25 split in PLAN.md first.**
   Counting calls in the nine blocked functions says this is **two** problems,
   not one. Seven of them (975 of the 1,102 instructions) contain calls, and for
   those the reload is ordinary C: a call may clobber a global, so naming
   `D_8009B458` directly at each use forces a re-read, while binding it to a
   local keeps it in a saved register across the call. No `-f` flag changes
   that, which is why the sweep below found nothing.

   **This is verified against CC1PSX, not argued.** `cc1_G=8` plus naming the
   global at each use emits a fresh `lui %hi / lw %lo` pair every iteration —
   the exact idiom. See the disassembly in PLAN.md and
   `build/scratch/hoist_test.c`. **Start the seven there.** Only `func_8004A0FC` (96)
   and `func_8004C84C` (31) have no calls at all, and those two are what the
   aliasing argument below actually describes. `func_8004C84C` is 1 instruction
   short and that instruction is the reload — the cheapest test case there is.

   The original framing, still accurate for those two:
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

4. **Reach real duel logic. The pad driver works; save state 4 is the problem.**
   `tools/pad.lua` scripts controller input, wired into `sample.py` and
   `trace.py` as `--pad`. **Do not re-derive the following — it is measured**,
   batched coverage, 150 frames, same parameters throughout:

   | state | without `--pad` | with `--pad` | only with `--pad` |
   |---|---|---|---|
   | 3, deck build menu | 57 functions | **109** | **52 fn / 2,809 insns** |
   | 4, in a duel (first capture) | 125 functions | 125 | **0** |
   | 4, **recaptured** | 63 functions | **118** | **55 fn / 4,406 insns** |

   The first state 4 was captured at a non-interactive moment and was completely
   unmoved by input — which briefly looked like the driver being broken. It was
   not: recapturing at a point where the game is actually waiting on the player
   changed it from 0 to 4,406 instructions of input-dependent code.

   **Capture states where the game is waiting on input**, and confirm with the
   diff above before drawing conclusions from any of them.

   The recapture also reaches **40 functions no earlier run had ever executed**
   (5,250 instructions), among them `func_8001BD88` (1,326 insns),
   `func_80019D18` (1,261) and `func_80035E20` (875) — far larger than anything
   in the sound cluster, and evidence-backed as duel-path. These are new
   decompilation targets; `tools/funcs.py --candidates` does not know about them.

   Two traps, both of which produced a wrong conclusion here first:
   * `sample.py` cannot settle this and never could: it samples once per Vsync,
     always at the same phase, so a 16-instruction spin takes ~98.8% of samples
     either way. That is aliasing. Use `trace.py --pad --batch`, diff hit sets.
   * A single negative state is not a negative result. State 4 alone said "input
     does nothing"; state 3 disproved it in one run.

5. **The register-allocation class.** Parked in `build/rejected/`, all with
   correct structure: `func_8005F1B8` (3/49), `func_80018C34` (4/49),
   `func_80049FB4` (53/82). Try `-Os` first -- it is a distinct allocation mode,
   not a size heuristic. Do not sweep more flags. The permuter plateaus at score
   10 on this class and **some of its winning variants are semantically wrong**,
   so read anything it produces before using it.

6. **The delay-slot class: `func_8004B734` (71 of 72) and now `func_8004A43C`
   (54 of 55).** Both residuals are a single `nop` the original has and we do
   not. `func_8004B734`: the original leaves `nop` in the loop-back branch and
   materialises the return value after it, where GCC hoists the zeroing into the
   slot. `func_8004A43C`: the original leaves a load-delay `nop` after
   `lbu $v1,0x3($s0)`, where GCC schedules the `D_8009B458` load into it — see
   PLAN.md for the aligned listing. **The permuter cannot help — no rewriting of
   C adds a `nop`**, confirmed here: it was run over `func_8004A43C` and
   plateaued at score 500, against 0 for a match. `flagsweep.py` over all 105
   combinations also found nothing. `reorg.c` is the place to look, and one
   answer probably resolves both.

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
* **The duel save states exist**, in `tools/states/` (gitignored), and they are
  **PCSX-Redux** states, not DuckStation's. All four slots restore and pass the
  boot gate. This was the item marked "needs a human"; it is done.
* **Everything that runs the game is now PCSX-Redux.** `verify_boot.py` used to
  drive DuckStation with its own incompatible state format; it was ported, so
  there is one emulator and one set of states. It also counts Vsyncs delivered
  after the restore rather than checking the process is alive — the old check
  would have passed a black screen.
* **`tools/trace.lua` was removing each breakpoint from inside its own callback**,
  freeing it while Redux was still dispatching it. That corrupted the heap and
  killed the emulator (`0xC0000374`) the moment game code started, so *every*
  trace silently reported `0 of 1206`. Removal is now deferred to the Vsync
  handler. A boot trace reports 108 functions. `TRACE_NO_REMOVE=1` disables
  removal entirely if it is ever suspect again.
* **`tools/all.py` never staged `iso/` or `config/disc.xml`**, so a fresh clone
  died at `make_iso.py`. `tools/stage_iso.py` does it and is in the pipeline.
* **A leftover emulator locks `build/ygofm.bin`** and made mkpsxiso fail with
  nothing but "Cannot open or create output image file". `make_iso.py` now names
  the cause. Note the process does not always still answer to its own name —
  finding it took the Restart Manager API.
* **`tools/ref/gcc-2.95.2/`** is populated (gitignored), so `loop.c`, `gcse.c`,
  `reorg.c` and `local-alloc.c` are on disk for queue items 2 and 6.
* **Ghidra is set up**, with its own JDK, both gitignored under `tools/bin/`.
  `tools/ghidra_import.py --analyze` builds the project at the real base
  `0x80010000` with all 1206 of our names on it; `tools/ghidra_decomp.py NAME`
  prints one function. It is **not** a second source of code — its C does not
  recompile to the same bytes — it is for the `size-differs` class: struct
  layout, field widths, signedness.
  First result, on `func_8004B734`: it renders the `D_8009B458` struct as
  offsets `0x500`, `0x501`, `0x508`, `0x509`, `0x50c`, `0x814`, and confirms
  **`0x50c` is a function pointer that is called inside the loop** — which
  item 7 had only marked as a guess. Note for item 2: this particular loop also
  contains three ordinary calls, and a call may clobber a global, so a reload
  here needs no special explanation. **Before assuming that answers item 2,
  check whether the actually-blocked functions contain calls at all** — PLAN's
  reasoning for the hoist is that only a *store* sits between reloads.
* **The register-allocation wall is explained.** `local-alloc.c` widens a
  quantity's lifetime to avoid reusing a just-dead register, gated on
  `flag_schedule_insns_after_reload && !optimize_size`. So there are **three**
  modes: `-O2` (sched2 + widening), `-Os` (sched2, no widening), and
  `-fno-schedule-insns2` (neither). PLAN's "no flag separates them" is retracted.
* **`tools/permute.py` was broken** -- it passed neither `cc1_G` nor
  `expand_div`, so anything not passed fell back to defaults. Base scores from
  before that fix are meaningless.
* **The permuter could not start at all on a fresh checkout**, and both causes
  were environmental rather than in the fork. `toml` was missing from the pip
  list (added to the README). And the permuter preprocesses with a bare `cpp`,
  which our gcc build only ships as `mipsel-none-elf-cpp` -- `tools/bin` is
  gitignored, so whatever alias existed locally was never reproducible.
  `permute.py` now creates the `cpp` alias itself, and puts Git's `bash` on PATH
  for the fork's `.sh` shim, which Windows cannot exec directly.
* **`tools/sidebyside.py` exists** for when `match.py` can only say the size is
  wrong. Use it rather than hand-rolling an objdump comparison (and note
  `objdump` hides `nop`s without `-z`).

## Hard rules

- **Verify before believing a negative result.** Five times in this project a
  mechanism was declared broken when the real cause was that the code under test
  never ran: a "verification" that counted the compiler's own guard rather than
  the feature's output; a `; echo "PUSHED"` after a broken `&&` chain; a permuter
  "plateau" that was an instant crash; a breakpoint "failure" caused by a
  missing `-fastboot` so the game never started; and a firewall "finding" where
  `Get-NetFirewallRule` returns an empty set rather than an error when run
  unelevated, so *every* rule query came back empty and "no rule allows TCP/22"
  was reported as measured fact. **Before concluding something does not work,
  prove it executed.** Run the control — for a query, that means confirming the
  query can return anything at all before trusting that it returned nothing.
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

Nothing right now.

Inbound SSH to `.180` **works in both directions** — verified end to end by
having the Mac `scp` `asm/code_002800.s` off `.180` and comparing SHA-1
(`fb45b794…`, matches). The key lives in
`C:\ProgramData\ssh\administrators_authorized_keys`, not
`C:\Users\PC\.ssh\authorized_keys`: `DESKTOP-9USQDG9\PC` is in Administrators,
so `sshd_config`'s `Match Group administrators` block redirects the lookup, and
appending to the `.ssh` one is a silent no-op for that account. That part is
real and worth remembering when adding a fourth machine.

**Retracted, and the way it was got wrong is the point.** This section
previously claimed, as a measured fact, that "no firewall rule references
TCP/22 in any direction". It was not measured. `Get-NetFirewallRule` and
`Get-NetFirewallPortFilter` return an **empty set, not an error**, when run
unelevated in this configuration — `Get-NetFirewallRule | Measure-Object`
reports **0 rules total** on a machine that has hundreds. Every "no rule
found" result was the tool being blind, and it was reported as evidence.

The control that would have caught it takes one line: *count all rules first.*
A query that finds nothing is only evidence if the same query can find
something. This is the fifth time in this project a negative result turned out
to be a mechanism that never ran — see the hard rule below, which already said
so.

If you find something that genuinely needs a human, put it here rather than
working around it, and say what you tried.

## Definition of done

There isn't one. Maximise **instructions matched** while the hash stays green.
When the queue empties, generate the next goals from what the evidence says is
blocking, and continue.
