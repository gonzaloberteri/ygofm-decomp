# Yu-Gi-Oh! Forbidden Memories (SLUS-01411) — Decompilation Plan

Goal: a source tree that rebuilds a **byte-identical `SLUS_014.11`** and a **bootable CD image**,
verified automatically by booting to a duel in DuckStation.

---

## 0. Facts established from the disc (verified, not assumed)

Disc: `C:\Users\PC\Downloads\Yu-Gi-Oh! Forbidden Memories (USA)\*.bin/.cue`
517,872,768 bytes · 220,184 sectors · MODE2/2352 · single track.

```
/SYSTEM.CNF                68 B    BOOT = cdrom:\SLUS_014.11;1   STACK = 801FFF00
/SLUS_014.11        1,902,592 B    lba 24
/DATA/SU.MRG        2,537,472 B    lba 954
/DATA/SD_SE.DAT     1,521,664 B    lba 2193
/DATA/SD_BGM.DAT   14,675,968 B    lba 2936
/DATA/WA_MRG.MRG   37,748,736 B    lba 10102
/DATA/MODEL.MRG   351,019,008 B    lba 28534
/DATA/MASTER.XA     5,742,592 B    lba 199930
/DATA/MOVIE.STR    35,430,400 B    lba 202734
```

PS-EXE header:

| field | value |
|---|---|
| entry `pc0` | `0x800129D8` |
| load `t_addr` | `0x80010000` |
| size `t_size` | `0x001D0000` (1,900,544 B = 1856 KB) |
| `sp` | `0x801FFFF0` |
| `gp0` | `0x00000000` (no $gp addressing — simplifies everything) |

**The entire game is one flat 1.86 MB executable. There are no overlays.**
On a 2 MB console that means code + rodata + data are a single contiguous link unit,
and the only thing streamed from disc is assets. This is the single most important
structural fact: one splat config covers 100% of the executable code.

### Toolchain fingerprints found inside the binary

```
$Id: intr.c,v 1.75  1997/02/07 09:00:36 makoto Exp $
$Id: bios.c,v 1.86  1997/03/28 07:42:42 makoto Exp yos $
$Id: sys.c,v  1.140 1998/01/12 07:52:27 noda  Exp yos $
```

These are **Psy-Q runtime RCS tags**. This is worth a lot: every function that came from
`libapi/libgpu/libgte/libspu/libcd/libsn` can be identified by **signature match against
the real Psy-Q `.lib` objects** instead of being decompiled by hand.

> **Correction (see the status log).** This section originally claimed
> `sys.c v1.140 / 1998-01-12` "pins the SDK to the Psy-Q 4.x line (4.0–4.4
> window)". That was wrong. All three revisions are present verbatim in **both**
> 4.6 and 4.7 — 4.6's library members are all dated 1999-07-23 — so the RCS tags
> are a *lower bound only* and pin nothing. The release was established instead
> by measuring per-object coverage.

Leaked original source paths (from `assert` / debug format strings):

```
src/hirata/H_mctrl1.c     <- original tree layout: src/<programmer>/<module>.c
S3000000.C
```

`Assertion failed: file "%s", line %d` is present, so more `__FILE__` strings should
surface once the rodata is properly segmented — each one names a real translation unit.

### Prior art survey

There is **no existing decompilation** of this game (checked GitHub search API).
There is, however, a mature *data-format* community whose work removes a large amount of
guesswork about the asset side:

- `forbidden-memories-coding/fmlib-cpp` — reads the game's files and patches the disc
- `forbidden-memories-coding/fmscrambler` — randomizer; encodes card/drop table layouts
- `xan1242/YGOFM-BGEx` — background image format
- `GenericMadScientist/FM-Manip-Tool` — RNG routing (documents the PRNG)
- Data Crystal RAM map — known RAM addresses for game state

Reference PSX decomp projects to mirror in structure/tooling:
`Xeeynamo/sotn-decomp`, `Caesar0007/NFSHS-PSX-decomp`, `theMagicalKarp/open-spyro`.

---

## 1. Strategy — why "boots to duel" comes early, not late

The naive reading of this project is "write C until the game works", which would mean
nothing boots for months. That is the wrong architecture.

Instead: **the build is byte-identical and bootable from Milestone 2 onward**, because
every function not yet written in C stays in the tree as extracted assembly and gets
linked in. Progress is then measured as *percentage of the binary expressed as C*, while
the boot test stays green the entire time.

```
                     +-----------------------------------------+
  original EXE  -->  |  splat: disassemble to .s + .bin data    |
                     +-----------------------------------------+
                                       |
                     +-----------------------------------------+
                     |  assemble + link -> SLUS_014.11          |  <-- SHA-1 must equal original
                     +-----------------------------------------+
                                       |
                     +-----------------------------------------+
                     |  mkpsxiso -> .bin/.cue -> DuckStation    |  <-- boot-to-duel test
                     +-----------------------------------------+
                                       |
              loop:  pick a .s  ->  m2c  ->  hand-fix C  ->  compile
                     ->  asm-differ vs original  ->  match?  ->  commit
                     (SHA-1 gate re-runs every single time)
```

The SHA-1 equality gate is what makes unattended work safe. A decompiled function is
either bit-for-bit the same or it is rejected — there is no "looks right" failure mode
and no drift. "Pixel perfect" falls out of byte-perfect for free.

You said the final binaries don't need to match. I'm going to aim for matching anyway,
because it is the only cheap oracle available: without it, verifying 1.86 MB of
reimplemented gameplay logic means playing the game, and that does not scale to
unattended operation. Where matching proves impossible for a specific function, the
project falls back to an "equivalent" marker for that function only.

---

## 2. Milestones

### M0 — Environment
- Python 3.12 (`py -3`) is present and is enough for splat / spimdisasm / m2c / maspsx.
- Need: `mipsel-none-elf` binutils (as, ld, objcopy) for Windows.
- Need: Psy-Q 4.x compiler (`cc1psx` / `aspsx`) — these are native Win32 executables, so
  they run directly on Windows; this is the one place where Windows is *easier* than Linux.
- Fallback if Psy-Q binaries misbehave: GCC 2.95.2 + `maspsx`, which is the standard
  substitute used by sotn-decomp and reproduces Psy-Q output closely.
- No Docker/WSL required (WSL has no distro installed; not going to touch that).

**Exit:** `mipsel-none-elf-as --version` and the compiler both run.

### M1 — Repo skeleton + extraction
- `tools/extract_disc.py` — pulls all 9 files out of the MODE2/2352 image, records
  LBA + size + SHA-1 of each into `config/disc.json`.
- Baseline SHA-1 of `SLUS_014.11` recorded as the build oracle.

**Exit:** `py -3 tools/extract_disc.py` reproduces all files; hashes stored.

### M2 — 100% assembly byte-matching rebuild ← **first real gate**
- splat config: `rom 0x800 → 0x1D0800`, vram `0x80010000`, entry `0x800129D8`.
- Iterate on: code/data boundary, jump-table detection, `.rodata` vs `.data` vs `.bss`,
  `%hi/%lo` pairing. This is the fiddly part and where most of M2's time goes.
- `tools/make_exe.py` reattaches the 2048-byte PS-EXE header.

**Exit:** `SHA-1(build/SLUS_014.11) == SHA-1(original)`. Fully automatable, no judgement calls.

### M3 — CD image rebuild + boot
- `mkpsxiso` with an XML that pins every file to its **original LBA** (FM may read by
  raw LBA rather than by filename — pinning removes that entire risk class).
- Assets are `.incbin`'d unmodified from the extracted originals at this stage.

**Exit:** rebuilt `.bin/.cue` boots in DuckStation to the title screen.

### M4 — Automated boot-to-duel harness ← **the acceptance test you asked for**
- DuckStation CLI batch launch against the rebuilt image.
- A save state captured just before a duel starts is loaded into the rebuilt build;
  since the binary is byte-identical, the state is valid.
- Capture N frames at fixed frame numbers, compare perceptual hashes against frames
  captured from the original disc. Any divergence fails the build.
- Per your standing preference, I automate launch + frame capture; **you do the one-time
  manual navigation** to record the "just before a duel" save state and the reference
  frame set. That's the only step in the whole plan that needs a human.

**Exit:** `py -3 tools/verify_boot.py` returns 0 on a rebuilt image and non-zero on a
deliberately corrupted one.

### M5 — Psy-Q library identification
- Signature-match against real Psy-Q 4.x `.lib` objects (`psyq-obj-parser` → ELF → symbol
  hashing) to auto-name every SDK function.
- On comparable PSX titles this accounts for **15–25% of the binary**, resolved without
  writing a single line of C.

**Exit:** `progress.py` reports the SDK share; those functions are named and excluded from
the hand-decompilation queue.

### M6 — Translation-unit segmentation
- Infer TU boundaries from function ordering, `.rodata` block ordering, alignment padding,
  and recovered `__FILE__` strings. Reconstruct the `src/<programmer>/<module>.c` layout
  hinted at by `src/hirata/H_mctrl1.c`.

**Exit:** splat config split into named segments; each maps to one future `.c` file.

### M7 — The decompilation grind (unattended loop)
Per function, fully mechanical:
1. `m2c` first pass on the `.s`
2. clean the C until it compiles
3. `asm-differ` against the original assembly
4. iterate; `decomp-permuter` on stubborn register/stack-slot mismatches
5. match → commit; SHA-1 gate re-runs

Order of attack: leaf functions first, then callers; boot path and duel path prioritised
so the most meaningful code is readable earliest.

**Exit:** continuous. Tracked as a percentage, reported per session.

### M8 — Data & assets
Use `fmlib-cpp` / `fmscrambler` / `YGOFM-BGEx` knowledge to convert raw `.bin` data blobs
into named, typed C structures (card DB, fusion table, drop tables, text). This is where
the source becomes genuinely *readable* rather than merely correct.

---

## 3. Honest scope assessment

M0–M4 — a byte-identical, bootable, automatically-verified build — is days of work and is
almost entirely mechanical. **That is when the game boots to duel from this repo.**

M5–M8 — 1.86 MB fully expressed as C — is community-scale. sotn-decomp has had dozens of
contributors over several years for a comparable binary. I can grind it down function by
function indefinitely and the percentage will climb steadily, but I'm not going to
represent "100% decompiled" as something that arrives on a schedule.

The plan is built so that the valuable, verifiable part lands first and never regresses.

---

## 4. Risks

| Risk | Mitigation |
|---|---|
| Psy-Q Win32 binaries fail on Win10 | fall back to GCC 2.95.2 + maspsx |
| Code/data boundary misdetection in a 1.86 MB flat blob | SHA-1 gate catches it immediately; iterate |
| Game reads assets by raw LBA | pin LBAs in mkpsxiso XML from the start |
| DuckStation not scriptable enough for frame capture | fall back to PCSX-Redux (Lua API, headless) for CI only |
| Non-matching functions (compiler flag drift per-TU) | per-TU flag search; mark `NON_MATCHING` and move on |

---

## 5. Status log

### 2026-07-24 — M0 through M4 complete

| Milestone | Result |
|---|---|
| M0 toolchain | binutils 2.40 (`mipsel-none-elf`), mkpsxiso 2.30, splat 0.41.1 / spimdisasm 1.42.2, Psy-Q 4.6 + 4.7 archived for M5 |
| M1 extraction | all 9 files extracted, SHA-1 baselines in `config/disc.json` |
| M2 exe rebuild | **byte-identical** — `84747e64f6da8e764206ec203e489acf8c9dcf7d` |
| M3 disc rebuild | **byte-identical, whole 517 MB image** — `d5785a41900a10968d4a28a390666c4b9879b796` |
| M4 boot test | loads the in-duel save state on the rebuilt image and runs |

### Revised scope — the binary is much smaller than it looks

The 1.86 MB executable is **71.6% zero-fill**.  A single 1.09 MB `.bss`-style
block sits at `0x8009B400..0x8013A000`, with more zero padding after it.  The
actual content:

| | bytes | share |
|---|---|---|
| code | 525,312 | 27.6% |
| data | 200,704 | 10.6% |
| zero | 1,174,528 | 61.8% |

So the decompilation target is **~525 KB / ~129,000 MIPS instructions**, not
1.86 MB.  That is a materially smaller project than the original estimate in
section 3 — comparable to a mid-size PSX decomp rather than an
sotn-scale one.

### Layout recovered

```
0x000000..0x002800  data   (10 KB)
0x002800..0x082C00  code   (525 KB, one contiguous region)
0x082C00..0x1C9400  data + zero  (mostly the 1.09 MB bss block)
0x1C9400..0x1D0000  zero
```

Two notes worth carrying forward:

* The image **opens with a jump table at 0x2800**, not with `.text`.  splat's
  section-ordered linker script cannot express data-before-code, so
  `tools/build.py` generates its own script pinning every region to its exact
  VMA.  An ld "section overlaps" error now catches a size regression earlier
  and more clearly than a hash mismatch would.
* Region boundaries must never cut a function.  Branches and `.L` local labels
  cannot cross an object file, so short data pockets between code runs (jump
  tables, inline rodata) are absorbed into the code region and left for
  spimdisasm to classify internally.

### Next: M5

Psy-Q library identification, using the archived 4.6/4.7 SDK.  The RCS tags in
the binary (`sys.c v1.140`, 1998-01-12) pin the SDK generation, so SDK
functions can be named by signature match rather than decompiled.

### 2026-07-24 — M5 complete: Psy-Q SDK identified

254 library objects matched, **401 SDK functions named**, covering 114,924 bytes
= 21.9% of all code.  Build re-verified byte-identical after the re-split.

Matching is exact, not fuzzy: the mask comes from each library object's own
relocation table, so every field the linker would have patched (jal targets,
%hi/%lo immediates, absolute words) is excluded and everything else must be
identical.  There is no similarity threshold to tune.

Two corrections were needed along the way, both worth recording:

* The converted Psy-Q objects report `st_size == 0` for every symbol, and the
  only other labels are `$lib/file.rel.text@offset` locals — which are *branch
  targets inside* functions, not function starts.  Deriving sizes from them
  produced ~5-instruction signatures that matched everywhere: 610 ambiguous
  addresses and 165 overlaps.  Matching **whole object `.text` sections**
  instead (an object's text is linked contiguously) dropped that to 32 and 6.
* Where several objects still match the same bytes and disagree on the exported
  names, no name is emitted.  27 addresses are deliberately left unnamed; a
  wrong name is worse than no name.

### The game/SDK boundary is now exact

Every one of the 401 SDK symbols lies above `0x80073704`, and none below it.
A false positive would almost certainly have landed somewhere in the game code,
so this clean split is also the best evidence the matching is sound.

```
0x80012800 .. 0x80073704   Konami game code   ~397 KB   <- the real target
0x80073704 .. 0x80092C00   Psy-Q SDK          ~128 KB   89.6% identified
```

**The decompilation target is ~397 KB, not 1.86 MB.** Successive corrections
have taken it from 1.86 MB (raw file) to 525 KB (code only) to 397 KB (code
Konami actually wrote).

### 2026-07-24 — M7a/M7b complete: the decompilation loop works

**The original build configuration has been recovered:**

| | |
|---|---|
| compiler | `CC1PSX.EXE` — GCC **2.95.2** (build 4.0), from Psy-Q 4.6 |
| assembler | ASPSX **2.86**, reproduced by `maspsx` |
| flags | **`-O3 -G8`** |

The Psy-Q tools are 32-bit PE binaries, so they run natively under WOW64 with
no emulation — the one place where Windows is genuinely easier than Linux for
this work.

Flags were recovered by search, not guesswork: `tools/flagsweep.py` compiles a
file under 84 flag combinations and reports which byte-match. `-O2` gets simple
leaf functions right but allocates a different register when loading a global
through `%hi/%lo`; `-O3` is what the original used. Four functions across three
files now match byte-for-byte.

**Correction to section 0:** the claim that the game does no `$gp` addressing
was wrong. It was inferred from `gp0 = 0` in the PS-EXE header, but the game
sets `$gp` itself at startup rather than letting the loader do it — code such as
`lw $v0, 0x554($gp)` is common. This is consistent with the recovered `-G8`,
which places small objects in the small-data area. Expect `.sdata`/`.sbss`
layout to matter when whole translation units start being linked.

### Function inventory

```
1345 functions total
 676 game   (below 0x80073704)   99,265 instructions   397,060 bytes
 669 sdk    (above 0x80073704)   named by signature match
 208 game leaf functions (no jal/jalr) -- the natural starting set
```

### The loop, as it now stands

```
tools/funcs.py --candidates     pick a target
tools/match.py src/foo.c        compile and compare, per function
tools/flagsweep.py src/foo.c    when it does not match, search the flag space
tools/build.py                  whole-binary SHA-1 gate, must stay green
```

### 2026-07-24 — M7 scaling, and the $gp constraint

`tools/autodecomp.py` runs the whole loop unattended: m2c `--valid-syntax`
emits compilable C, which is compiled and compared per function, and anything
that byte-matches is kept in `src/auto/`.

The first run surfaced a structural problem worth stating plainly.

**`$gp = 0x8009AF08`**, set by the startup code at `0x80012A54`:

```
80012A54  3C1C800A   lui   $gp, 0x800A
80012A58  279CAF08   addiu $gp, $gp, -0x50F8
```

(The other 22 `$gp`-defining instructions the scan found are all inside data
regions -- data misread as instructions, not real code.)

**50.8% of game code addresses through `$gp`** (259 of 676 functions, 50,436 of
99,265 instructions). Those functions cannot be matched yet, and the reason is
not a missing tool:

* `-G8` puts objects of 8 bytes or less in the small-data area, addressed as
  `offset($gp)` rather than `%hi/%lo`.
* GCC only does this for variables it can see the *definition* of. An `extern`
  declaration always gets `%hi/%lo` -- which is exactly why `src/globals.c`
  matched: its global genuinely is addressed that way in the original.
* So matching a `$gp` function means defining its globals in the same
  translation unit, in the original order, so `.sdata`/`.sbss` land at the same
  offsets. That is a whole-program constraint, not a per-function one.

**This makes M6 (translation-unit segmentation) a hard prerequisite for half of
the remaining work, rather than the refinement step it was originally listed
as.** The revised order is M6 first, then the `$gp` half of M7.

Reachable without touching `$gp`: 417 functions, 48,829 instructions, 49.2%.

### 2026-07-24 — decompiled C is now part of the byte-identical build

**32 functions build from C, and the whole binary still hashes to
`84747e64f6da8e764206ec203e489acf8c9dcf7d`.** Until now the C was only compared
against the original; it is now actually linked in, and the assembly it
replaced is gone from the build.

How it works: `tools/split_asm.py` carves the monolithic disassembly into the
runs still made of assembly, leaving holes where C has taken over, and
`tools/build.py` pins each C object and each assembly fragment at its exact
original address. A C file must cover a *contiguous* span of the original --
which is simply what a translation unit is. `src/globals.c` failed that test
and was split in two; the check refuses to guess.

Three problems this shook out, all of which would have been silent:

* `endlabel`/`enddlabel` expand to `.size sym, . - sym`. Once split, a symbol's
  start and its closing `.` can land in different files and the expression
  stops being constant. Fragments now use a generated macro.inc with `.size`
  removed -- it is metadata and never reaches the output bytes.
* Standalone data labels sitting outside any function were dropped when
  fragments were cut, because the fragment splitter only recognised the
  instruction comment format. Data lines omit the raw word:
  `/* 82B72 80092B72 */ .short 0xC000` versus
  `/* 82B74 80092B74 00000000 */ .word 0x0`. That cost exactly one byte
  (0x80092B73) and was caught only by the hash.
* Undefined-symbol resolution has to scan the *fragments*, not the original
  disassembly. Anything the split drops must be resolved like any other
  reference into a bin region.

The one-byte failure is the argument for the hash gate in miniature: no test
short of byte equality would have noticed it.

### 2026-07-24 — automated pass results, and a weak signal reported as weak

`tools/autodecomp.py` over all 302 non-`$gp` candidates up to 80 instructions:

| outcome | count | share |
|---|---|---|
| size-differs | 157 | 52% |
| differs | 62 | 21% |
| compile-failed | 47 | 16% |
| **match** | **32** | **11%** |
| m2c-failed | 4 | 1% |

An 11% hit rate on untouched m2c output is roughly what this approach yields;
the value is that it costs nothing and clears the trivial cases, not that it
scales to the whole binary. `size-differs` dominating says most of these need
real structure recovery (types, struct layouts, signedness) before the compiler
will emit the same instruction count.

**Progress, stated the honest way.** `tools/progress_map.py` renders
`progress.png` and prints both metrics, because they disagree sharply:

```
game functions:    676 total    matched 32   (4.73%)
game instructions: 99265 total  matched 340  (0.34%)
```

Function count flatters the work by more than 10x -- the automated pass matched
the smallest functions in the binary, averaging 10 instructions each against a
147-instruction mean. **Instructions matched is the metric to track.**

### The TU detector is not good enough yet

`tools/tu_detect.py` looks for translation-unit boundaries where the band of
data a function references jumps backwards, tracking `.data`/`.bss`, `.rodata`
and `$gp` offsets as separate bands (mixing them was useless -- a single
function touches both a static at `0x8009xxxx` and a table at `0x801Bxxxx`).

It proposes 111 boundaries, only 14 corroborated by more than one signal, with
a median implied unit of 4 functions. Real translation units are far larger
than that, so **this is a candidate generator for review, not an answer.** The
underlying assumption -- that a function mostly touches its own unit's data --
is weaker in this binary than hoped.

Better signals to try next: per-function `.rodata` *ownership* (a table
referenced by exactly one function is almost certainly in that function's unit),
alignment padding between objects, and the `__FILE__` strings from `assert`.

### 2026-07-24 — the $gp blocker is solved, and it did not need M6

The earlier conclusion that half the binary was blocked behind translation-unit
reconstruction was **wrong**, and pleasantly so.

`R_MIPS_GPREL16` relocations resolve to `symbol - _gp`. So the small-data layout
does not have to be rebuilt at all -- it is enough to

1. assemble with `-G8` so a small-symbol reference is emitted as `offset($gp)`
   plus a `GPREL16` relocation rather than a `%hi/%lo` pair, and
2. define `_gp = 0x8009AF08` in the linker script, the value the startup code
   loads.

The linker then computes the offset, and because each symbol is already pinned
to its true absolute address, it comes out right. First `$gp` function matched:

```
ours:      80015d0c:  a3800239   sb  zero,569(gp)
original:  80015D0C:  390280A3   sb  $zero, 0x239($gp)
```

**33 functions now build from C, `$gp` included, and the binary still hashes
`84747e64f6da8e764206ec203e489acf8c9dcf7d`.**

Two traps on the way:

* **maspsx injects `-G0` unless you pass `--dont-force-G0`**, which silently
  cancels the small-data area and turns every gp-relative access back into a
  `%hi/%lo` pair. This looked like a compiler problem for a while; it was a
  wrapper default.
* **The assembler's `-G` is a separate knob from the compiler's, and the
  original build did not use one value throughout.** Turning on `as -G8`
  globally *broke* functions that legitimately use `%hi/%lo` for a symbol small
  enough to have been gp-addressed -- they got shorter by an instruction. So `-G`
  is per translation unit, now configured in `config/cflags.json` with
  `tools/flagsweep.py` to recover it per file.

The practical consequence: **M6 is no longer a prerequisite for anything.** It
stays useful for producing a readable source tree organised the way Konami's
was, but it is no longer blocking matching. M8 is largely dissolved.

### 2026-07-24 — function size distribution sets a hard ceiling on automation

| size (instructions) | functions | instructions | share of code |
|---|---|---|---|
| 0-9 | 59 | 325 | 0.3% |
| 10-24 | 153 | 2,606 | 2.6% |
| 25-49 | 130 | 4,681 | 4.7% |
| 50-99 | 130 | 8,772 | 8.8% |
| 100-249 | 118 | 17,800 | 17.9% |
| 250-499 | 49 | 17,167 | 17.3% |
| **500+** | **37** | **47,914** | **48.3%** |

**37 functions -- 5.5% of them -- hold 48.3% of the code.** The largest,
`func_80061A84`, is 10,376 instructions on its own.

The consequence for planning is blunt: `tools/autodecomp.py` works on functions
of at most 80 instructions, which is 65.8% of all functions but only **14.1% of
instructions**. Even a perfect automated pass caps there. Conversely the 86
functions above 250 instructions carry 65.6% of the code.

So the shape of the remaining work is not "grind through 600 small functions".
It is **a few dozen very large functions**, each of which needs real structure
recovery -- types, struct layouts, control flow -- and none of which m2c will
hand over for free. That is worth knowing before mistaking a rising
function-count percentage for progress.

### 2026-07-24 — Psy-Q release pinned; two earlier claims retracted

**Verdict: do not link the genuine SDK libraries.** Reasons below.

#### Which release

The RCS tags do not identify it — all three revisions appear in both 4.6 and 4.7
(4.6's members are dated 1999-07-23). Measuring coverage of the SDK region
instead, with a native `LIB\x01`/`LNK\x02` reader (`tools/psyq_lib.py`) so 4.6's
unconverted archives could be used:

| release | objects | bytes | share of region |
|---|---|---|---|
| 4.7 (ELF) | 254 | 114,684 | 89.4% |
| 4.6 (native) | 258 | 109,044 | 85.0% |
| **union** | **281** | **117,948** | **92.0%** |

**Neither release is a superset.** Of 1,942 objects in both, 34 differ, and the
game contains 4.6's variant of some (`libgpu/font`, `libspu/s_sr`, 100% of words)
and 4.7's of others (`libds/dssys_1`, `dssys_2`, 9,520 B, 100% of words — 4.6
scores 4.5%). So Konami's `LIB` directory was a base release with individual
libraries updated in place, which is also what rules out 4.4/4.5: they are
strictly older than 4.7's libds. `config/symbol_addrs.txt` now uses the union:
**412 named functions**, 22.6% of all code.

#### The residual is fully accounted for

Of 10,304 bytes unmatched, **9,504 are not code at all** — trailing rodata at
`0x800906E0..0x80092C00` (69% zeros, containing `\DATA\WA_MRG.MRG;1` and the SCE
copyright string) that the region classifier absorbed into the code region. The
remaining **800 bytes are 50 individual 16-byte library objects**, all BIOS
trampolines and GTE register accessors, excluded solely by `MIN_INSNS = 5`.

So **99.33% of the actual SDK code is identified and the rest is explained.**
Nothing is missing from the archives and nothing was customised by Konami.

#### Retraction: SDK code does exist below 0x80073704

An earlier entry claimed "every one of the 401 SDK symbols lies above
`0x80073704`, and none below it". **Wrong.** `noheap.obj` matches at
`0x800129D8` — the PS-EXE entry point — at 94/94 words, giving
`__SN_ENTRY_POINT`, `__main` and `__do_global_dtors`. Corroboration: the `$gp`
setup at `0x80012A54` is `__SN_ENTRY_POINT + 0x7C`. The real layout is crt0
first, then the game, then the libraries:

```
0x800129D8 .. 0x80012B50   Psy-Q crt0
0x80012B50 .. 0x80073704   Konami game code
0x80073704 .. 0x80092C00   Psy-Q libraries
```

Worse, splat emits those 376 bytes as `dlabel D_800129C4` raw `.word` data
rather than instructions — verified by hand: `0x800129D8` decodes as
`lui/addiu/lui/addiu/sw/addiu/sltu`, a `.bss`-clearing loop. The bytes are right
so the hash never complained, but **the disassembly is wrong about the program's
entry stub.** This is the second time a claim of mine survived the hash gate
while being false; the gate proves byte equality, not that the tree describes
the program correctly.

#### Why not to link the real libraries

1. **Zero information gain** — the region is already named and excluded from the
   decomp queue; a `.a` member is no more readable than the assembly.
2. **It would not even remove the assembly** — 800 B of stubs and 9,504 B of
   rodata stay regardless, so the result is a hybrid with more moving parts.
3. **Quantified byte-identity risk** — 5,851 relocations would have to resolve
   exactly, and 67 of the matched objects carry 49,048 B of `.data`/`.bss`/
   `.rdata`/`.sbss` that would also have to land at their original addresses,
   with one SHA-1 bit as the only oracle for a layout search that size.
4. **No single archive reproduces it** — 3,072 B exist only in 4.6, 9,520 B only
   in 4.7, so the tree would link a hand-curated two-release mixture, which is
   *less* honest about the original build, not more.
5. **Licensing and self-containment** — proprietary SCE binaries; the build would
   stop being reproducible from a clone.
6. **Maintenance asymmetry** — a symbol file and deterministic asm, versus an SDK
   provisioning step, version checks, a link-order search, and a failure mode
   that surfaces only as a hash mismatch.

### 2026-07-24 — $gp automated; 54 functions from C

`tools/autodecomp.py` now rewrites m2c's undeclared `saved_reg_gp` into a real
extern at `gp + offset` (since `$gp` is a known constant) and tries both
assembler `-G` values, keeping whichever reproduces the bytes. Over all 436
candidates up to 80 instructions:

| outcome | count |
|---|---|
| size-differs | 229 |
| compile-failed | 69 |
| **match** | **54** |
| differs | 44 |
| gp-unhandled | 32 |
| m2c-failed | 8 |

**54 functions build from C (up from 32), 22 of them needing `as_G 8`**, and both
the executable and the full disc image remain byte-identical. Boot from the
in-duel save state still passes.

One more fix this forced: decompiled C introduces symbol references the
disassembly never contained. A gp-relative access appears in the asm only as
`0x170($gp)`, so scanning assembly text for names could never find `D_8009B078`.
Symbol resolution now reads each object's own undefined-symbol table instead of
inferring names from text.

Progress, both metrics:

```
game functions:    678    matched  54  (7.96%)
game instructions: 99265  matched 495  (0.50%)
```

The gap between 7.96% and 0.50% is the point made in the size-distribution entry
above: what is matched so far is almost entirely the small end of the binary.

### 2026-07-24 — automation plateaus at ~0.5%; failures diagnosed

Parallelised `autodecomp` and `build.py` across 16 cores (all the work is
subprocess-bound, so threads scale nearly linearly and the GIL is irrelevant).
**The full build now takes 3.4 seconds**, down from around 40, which makes the
hash gate cheap enough to run constantly.

That made it affordable to widen the candidate pool from 80 to 250 instructions
and sweep `-O1/-O2/-O3` against both assembler `-G` values. The result is a
plateau, and it is worth stating plainly:

| | candidates | matched | instructions |
|---|---|---|---|
| ≤80 insns, single -O | 445 | 55 | 468 |
| ≤250 insns, -O swept | 580 | **56** | **510 (0.51%)** |

**135 extra candidates and a six-way flag sweep bought one function.** Unedited
m2c output is exhausted. Breakdown over the 580:

| outcome | count | share |
|---|---|---|
| size-differs | 283 | 49% |
| compile-failed | 132 | 23% |
| gp-unhandled | 55 | 9% |
| differs | 45 | 8% |
| **match** | **56** | **10%** |
| m2c-failed | 9 | 2% |

Sampling 60 of the compile failures gives the causes, which are not exotic:

| count | cause |
|---|---|
| 30 | **`NULL` undeclared** -- generated files include only `types.h` and `m2c_macros.h`, neither of which defined it |
| 7 | invalid unary `*` on an unknown type |
| 5 | too few arguments -- m2c emits a prototype with one parameter then calls with none |
| 4 | parse error |
| rest | assorted pointer/integer conversion warnings |

`NULL` was half the bucket and is a one-line fix. The "too few arguments" case is
an m2c limitation: it declares `s32 func_8004BAE4(s32);` and then emits
`func_8004BAE4()`. Relaxing those prototypes to unprototyped form would compile,
but the call still passes no argument, so it would move the function from
`compile-failed` to `size-differs` rather than to `match` -- not a real win.

`size-differs` at 49% is the honest wall. Those compile fine and produce the
wrong instruction count, which means the C is not yet expressing what the
original expressed -- wrong integer widths, wrong struct layouts, wrong
signedness. No flag search fixes that; it is per-function structure recovery.

#### The NULL fix, measured

Defining `NULL` did what it was supposed to and almost nothing for the score:

| | before | after |
|---|---|---|
| compile-failed | 132 | **107** |
| size-differs | 283 | 303 |
| differs | 45 | 49 |
| **match** | **56** | **57** |
| instructions | 510 | **540 (0.54%)** |

25 files that would not compile now compile, and **24 of them landed in
`size-differs` or `differs`** -- one became a match. This is exactly the outcome
predicted for the prototype-relaxation idea, which is why that one was not
implemented: unblocking the compiler does not make the C correct.

The lesson generalises. Every remaining failure bucket is downstream of the same
thing -- the C does not yet say what the original said -- and moving a function
between buckets is not progress. The only thing that moves `matched` is getting
the types and structures right, one function at a time.

### 2026-07-24 — parallel hand-decompilation; two tooling bugs found

Six workers on disjoint batches of the 260 unmatched functions in the 4-45
instruction range (6,246 instructions). Per-file flags moved into a
`/* decomp-flags: opt=-O2 as_G=8 */` comment read by `tools/cc.py`, so
concurrent workers never contend on `config/cflags.json`.

First batch back: **10 of 43 matched, 148 instructions.** Three of the ten needed
**`-O1`**, which the default config never used. Its fingerprint in the original
assembly is a `nop` after every load and no interleaving of independent
instructions -- i.e. scheduling off.

#### Two tooling bugs, each blocking a whole class of functions

**1. maspsx does not emit the load-delay `nop` for `.extern` small-data symbols.**
`func_8003CDF8` is `lhu $v0,off($gp); nop; sh $v0,off($gp)` six times over. cc1
emits a placeholder `#nop`, and maspsx only forces a real one when it believes
the next instruction touches `$gp` -- a decision it makes from `.comm`/`.lcomm`/
`.sdata` symbols declared *in the same translation unit*. A `.extern sym, size`
is never recognised as small, so no nop is emitted and the function comes out six
instructions short. **Any function whose body is a chain of gp load -> gp store
is currently unmatchable for tooling reasons, not source reasons.**

**2. Several `glabel ... endlabel` spans contain more than one function.** After
the first `jr $ra` and its delay slot, unlabelled code continues -- e.g.
`func_80035668` is 6 instructions, then a second function begins at
`0x80035680`. `asm_inventory()` measures the whole span, so a correct
single-function file is reported as `size N, original N+k` and can never match.
This also means the function inventory **overstates sizes and understates the
function count** everywhere it happens.

#### Per-function idioms worth reusing

* The `-G8` threshold applies to **your declaration**, not the real object. An
  8-byte struct declaration made gas emit `sb $v0,6($gp)` where the original used
  `%hi/%lo`; padding past 8 bytes fixed it. Conversely an incomplete type
  (`extern u16 D_8009AF74[];`) never gets gp-relative addressing -- it needs a
  size of 8 bytes or less for cc1 to mark it small.
* `i[array]` instead of `array[i]` flips which register an address accumulates
  into, and turned one 2-instruction miss into a match.
* Two induction variables in the assembly means two pointer variables in the
  source; a struct-array index always collapses to one. Declaration *order* of
  the locals mattered for the last two instructions.
* Loop shapes map predictably: `bne v0,-1` is `while (n-- != 0)`; `bgez` with
  `li N-1` is `for (i = 0; i < N; i++)`. Getting it wrong is a size error, not a
  register error.
* `sll/sra 16` at entry means the parameter was declared `s32`, not `s16`.
  Declaring `s16` cost four spurious instructions.
* GCC 2.95 inverts `if` conditions -- write the source condition to match the
  branch in the assembly and expect the blocks to come out swapped.

The residual misses are almost all register allocation or scheduling: correct
instruction count, one register pair swapped or one instruction in a different
delay slot.

#### Batches 0, 2, 4, 5 — 51 functions matched, and what they proved

| batch | matched / total | instructions |
|---|---|---|
| 0 | 14 / 44 | 211 |
| 2 | 16 / 43 | 231 |
| 4 | 10 / 43 | 148 |
| 5 | 11 / 43 | ~171 |

**`-O2` won nearly every case, not `-O3`.** The earlier claim that the build used
`-O3` throughout was based on two tiny functions and does not hold: `-O2` and
`-O1` dominate, and `func_800136D4` needs **no `-O` at all** (`addiu $sp,-16` /
`addiu $sp,+16` / `jr $ra` / `nop`, which only `-O0` produces).

**Three independent batches converged on `-fno-schedule-insns2`.** No `-O` level
reproduces some functions: `-O1` gives the original's epilogue order but the
wrong prologue, `-O2` the reverse. The difference is the post-reload scheduler
hoisting `lw $ra` above trailing stores. Batch 5 verified two functions reach
MATCH with `-O2` plus that flag. It is now expressible as `cc1_extra=`, so those
are reclaimable.

**`cc1_G` is a third real knob, independent of `as_G`.** With `cc1_G=0` GCC emits
its own `lui/%lo` pair; with `cc1_G=8` it emits the `lw $r,sym` assembler macro,
and the two allocate registers differently. A binary-wide scan found 837
different-register `%hi`/`%lo` pairs, 46 of them loads with a non-`$at` base,
clustered in 29 functions -- all `cc1_G=0` candidates. Corollary worth
remembering: **cc1 never allocates `$at`, so `$at` in the original proves an
assembler macro rather than compiler output.**

**The `-G` threshold is a property of your declaration, not the real object.**
cc1 emits `.extern sym, size` and gas honours it, so declaring a symbol as an
array or oversized struct keeps it out of small data. That is how a function that
mixes `offset($gp)` and `%hi/%lo` for same-sized globals becomes expressible --
otherwise it is a dead end for any single `as_G`.

**`volatile` is required for the `$gp` state words.** `x &= 0x3FFC; x |= 2;` on
`gp+0x20A` reloads between the two operations in the original; without
`volatile` GCC merges them and the function is three instructions short. These
look like pad/hardware state.

**One recurring near-miss with a single cause:** the 6-argument stack-push idiom.
The original emits `li $v0,argN; sw $v0,0x10($sp)` reusing `$v0`; this cc1
materialises both constants first into `$v0`/`$v1`. That is the *only* remaining
difference in four functions, and is very likely the same scheduler flag.

**A verification gap worth naming:** `match.py` compares only `.text`. A function
that dispatches through a jump table would report MATCH while its jump table
landed at the wrong address. Whole-binary SHA-1 still catches it, but the
per-function check alone would not.

Data structures recovered across batches (a shared header once TU segmentation
lands): `D_8009B45C` (gp+0x554) main game state, `D_8009B458` (gp+0x550) sound
driver work area with 16 x 24-byte channel records and a `SpuVoiceAttr`,
`D_800F2C40[]` 0xE20-byte per-duelist records, `D_800E9EC8` pad block,
`D_801A7AD8[]` 28-byte card records with bit 15 of `+0x16` as occupied.

### 2026-07-25 — 320 merged functions split; the inventory was wrong

`tools/split_funcs.py --write` now emits `config/split_syms.txt` (a file of its
own, because `psyq_sigs.py --write` rewrites `symbol_addrs.txt` wholesale and
would erase the splits), splat reads both, and the build stays byte-identical
with all 131 C functions.

**The corrected inventory, against what was previously reported:**

| | before | after |
|---|---|---|
| game functions | 678 | **966** |
| functions ≥500 insns | 37 | **23** |
| share of code in those | 48.3% | **31.8%** |
| largest function | 10,376 | **9,532** |
| functions using `$gp` | 259 (50.8%) | 331 (45.8%) |

```
  0-9           68 funcs     390 insns    0.4%
  10-24        244 funcs    4071 insns    4.1%
  25-49        234 funcs    8312 insns    8.4%
  50-99        191 funcs   13202 insns   13.3%
  100-249      155 funcs   23239 insns   23.4%
  250-499       51 funcs   18444 insns   18.6%
  500+          23 funcs   31607 insns   31.8%
```

**Retraction.** The earlier claim that "37 functions hold 48.3% of the code" was
an artefact of merged spans and is withdrawn. It is 23 functions and 31.8%, and
the work is correspondingly less concentrated and more tractable than stated.
The automation ceiling claim also moves: candidates up to 250 instructions now
cover **49.6% of instructions**, against the 14.1% quoted when the ceiling was
computed over an 80-instruction pool of merged functions.

This is the third time a claim of mine survived the SHA-1 gate while being wrong
about the program's structure. The gate proves bytes, not understanding.

#### Re-run after the splits: automation 57 -> 87 functions

With the 320 splits applied, the maspsx `.extern` nop fix in place and
`cc1_extra` available, the automated pass over 880 candidates (≤250 instructions)
matched **87 functions / 947 instructions**, against 57 / 540 before. For
comparison, the previous attempt to move that number by widening the candidate
pool and sweeping `-O` gained exactly one function -- so the gain here came from
fixing the tooling and the disassembly, not from searching harder.

Combined with the hand-decompiled set: **161 functions, 2,043 instructions
(2.06%)**, executable and full disc image both byte-identical, boot from the
in-duel save state passing.

| outcome | count | share |
|---|---|---|
| size-differs | 452 | 51% |
| compile-failed | 148 | 17% |
| differs | 90 | 10% |
| **match** | **87** | **10%** |
| gp-unhandled | 85 | 10% |
| m2c-failed | 18 | 2% |

`size-differs` still dominates and still means the same thing: the C compiles
but does not express what the original expressed. That is per-function work.

### 2026-07-25 — the gp-unhandled bucket is gone, and a verification hole

`rewrite_gp()` in `tools/autodecomp.py` handled exactly one syntactic form. Over
644 candidates, 173 m2c outputs mention `saved_reg_gp`, in three families:

| shape | occurrences | was |
|---|---|---|
| `M2C_FIELD(saved_reg_gp, T *, off)` | 458 | handled |
| `M2C_FIELD(saved_reg_gp, T **, off)` | 51 | **unhandled** |
| `M2C_FIELD(saved_reg_gp, M2C_UNK (**)(args), off)` | 5 | **unhandled** |
| `saved_reg_gp + off` (bare address, from `addiu $r, $gp, off`) | 10 | **unhandled** |

The old regex allowed exactly one `*` in the type and only ever looked inside
`M2C_FIELD`. Parsing is now a balanced-paren scan, because function-pointer
types contain top-level-looking commas, and offsets are resolved innermost-first
so nested `M2C_FIELD` still works. There are no negative or computed offsets and
no `volatile`/`const` forms in this binary.

**`gp-unhandled`: 42 -> 0.** Matches 87 -> 90, instructions 947 -> 992. The 42
redistribute as 3 match / 29 size-differs / 6 differs / 4 compile-failed, and the
deltas sum to exactly 42, so nothing that matched before regressed.

#### The gp offset is not verified by the byte comparison

`R_MIPS_GPREL16` is masked `0xFFFF0000`, because the linker owns the low half --
so **a wrong gp offset would produce a false MATCH.** It is correct by
construction here: the offset is what picks the extern's name, and the name is
what the link resolves back to `gp+off`. But that is an invariant to hold
deliberately, not something the check enforces. The opcode and base register are
*not* masked, so a wrong load *width* does still show up.

This is the second known hole of the same shape, after the jump-table one: a
function dispatching through a jump table can report MATCH with its table
misplaced. **Both are closable** -- these symbol names encode their own
addresses, so the expected `%hi`, `%lo` and `gp_rel` values can be computed and
compared instead of masked. Worth doing; `match.py` is currently treated as
authoritative and is not quite.

Also learned: the gp bucket was largely hiding unrelated m2c defects. Of the four
that now fail to compile, one references a static comparator m2c never declares,
one emits a bare `sp`, one emits `*((int) + D_80090DF8)(arg)` for a jump-table
call. Those block manual work on those functions too.

### 2026-07-25 — include/game.h, and corrections to struct claims recorded here

`include/game.h` (1183 lines) declares 17 structs and ~70 `$gp` globals, derived
from the byte-matching files — whose declarations are evidence, because
byte-equality verifies them. All 17 sizes and 26 key offsets are **machine
checked** with negative-width-bitfield assertions (GCC 2.95.2 has no
`_Static_assert`), and the check was deliberately broken once to confirm it
actually fails. Sizes are not eyeballed.

Two structures turned out not to exist as separate objects:

* **`D_800F0548` is `&D_800EFE48[0x10]`** — `0x800F0548 - 0x800EFE48 = 0x700 =
  0x10 * 0x70`. One pool of 0x60 records with two allocators, not two arrays.
* **`D_800F39B0` is `D_800F2C40 + 0xD70`** — it names a field inside the record,
  not a separate table.

`GameState` is at a *fixed* address, not allocated: `0x80046788` stores
`0x801E0000` into `gp+0x554`, and `gp+0x558` holds `0x801E1650 == state+0x1650`,
which is also its size.

#### Corrections to claims recorded earlier in this document

These came from previous workers' reports and I wrote them down without
independent checking. They are wrong or unsupported:

* **"`D_800E9EC8` is a pad/controller block" is unsupported.** Nothing in the
  module touches the pad. The evidence — the enclosing module calls
  `GsSortBoxFill`, `+0x00` holds a 24-bit value with sentinel `0xFFFFFF`, RGB-
  looking byte triples are written nearby, `func_80015998` spins on bit 7 of
  `+0x06` — points to a screen fade/flash controller. Two earlier workers named
  the same struct `Pad800E9EC8` and `Sound` respectively; neither is supported,
  and the header keeps it as `Unk800E9EC8` with the evidence recorded.
* **"master volumes at +0x514/+0x516"** are offsets *inside `SoundWork`*, not
  `$gp` offsets. Easy to misread as written.
* **"`D_800F2C40[]` per-duelist records"** is unconfirmed; the type is
  `Rec800F2C40`.
* A field pair named `key`/`value` in one existing file is an interpretive error:
  `func_800601D0` keys on `+0x00` and returns `+0x04`, `func_80060170` keys on
  `+0x04` and writes `+0x00`, and both byte-match — so it is a two-way pair
  table, not a key/value map.

Genuine disagreements between byte-matching files, left unresolved rather than
guessed: offset `0x34` is an s16 `z` coordinate in one module and a u16 bitfield
in another; `SoundWork+0x500` is either `SpuVoiceAttr.adsr2` or a single flag
byte written 22 times; `D_800EB184` is both a pointer variable and
`&D_800EB0F8[1].unk_28`; four globals disagree about `volatile` (all match either
way, but `D_8009B112` genuinely needs it).

**The header is additive reference material for new work only.** Retrofitting
existing files onto it would break matches: `-G8` decides small-data addressing
from the *declaration's* size, and `volatile` changes instruction count, so
several matching files depend on their local declaration being exactly what it
is. Note also that padding in existing files is **not** evidence — most of those
"struct maps" are arbitrary filler around the few offsets actually addressed.

### 2026-07-25 — wave 2 batch 1: 20 functions, and two structural gaps

20 matched / 360 instructions. `-O2` dominated again; `-O1` only where the
original's body order is unscheduled.

**Highest-yield new idiom: two identical zero arguments passed as floats.** Two
identical *integer* constants get re-materialised (`li $a2,0; li $a3,0`); two
identical *float* constants CSE into one pseudo and are copied (`move $a3,$a2`).
Declaring those parameters `f32` and passing `0.0f, 0.0f` matched four functions
in this batch alone.

Other idioms worth reusing:

* `((Rec *)(off + (u8 *)array))->field` — an int on the *left* of the `+` flips
  the `addu` operand order, and keeping the struct field access preserves the
  `lw 0x28(reg)` displacement, where `off + base + 0x28` folds `0x28` into the
  `%lo`. Note `match.py` masks the `%lo`, so that fold is invisible there but
  shows up as a wrong displacement on the load.
* `a > 0 && a < 4` folds to `addiu -1; sltiu 3`; two *nested* `if`s keep the
  original's `blez` + `slti` pair.
* `x < 0 ? -x : x` must be a ternary — the `if` form adds a `move`.
* `sll 16; sra 16` on a *return value* means an `s32`-returning callee assigned
  to an `s16` local.
* **`cc1_G` signature corrected.** `lui %hi / sw %lo` without `$at` is *not*
  proof of `cc1_G=0`: with `cc1_G=8` cc1 still emits its own pair for symbols it
  knows are not small. The real `cc1_G=0` tell is the `%hi` and the loaded
  *value* landing in **different registers**.
* Mixing `$gp` and `%hi/%lo` in one function works by sizing declarations:
  gp-side as ≤8-byte scalars, `%hi/%lo`-side wrapped in a struct >8 bytes, with
  `as_G=8`.

#### Gap 1 — a third tooling-side blocker

**ASPSX duplicates a branch target into the delay slot; GNU as does not.** The
original fills a `bnez` delay slot with a *copy* of the branch target's
instruction (a loop-counter `addiu $s0,$s0,-1`) and retargets to target+4. cc1
leaves the slot to the assembler in `.set reorder` mode, and maspsx/GNU as emits
`nop`. **Any `continue` whose target is a loop-counter update is currently
unmatchable for tooling reasons**, not source reasons — the same class as the
`.extern` load-delay bug, and likewise fixable in principle.

#### Gap 2 — split_funcs.py misses leaf-tail functions

Four more merged spans in this batch that the detector did not find:
`func_80059208` (3+3), `func_80024E24` (10+3), `func_80035668` (6+8),
`func_80040424` (10+7). All are **leaf functions with no stack frame**, and the
detector requires an `addiu $sp,$sp,-N` prologue to propose a split. That
conservatism was deliberate and is now shown to cost real functions.

A decisive signal is available and does not require guessing: **is the address
the target of a `jal` anywhere in the binary?** If something calls it, it is a
function. Implemented below.

#### Also noted

`-fno-schedule-insns2` changes register *allocation*, not just ordering — GCC
2.95's local_alloc avoids reusing a just-dead register when post-reload
scheduling is on. Five functions sit exactly between the two settings: sched2 off
gives the original's register reuse but loses the prologue interleave and the
load-delay filling. No flag separates them.

And a trap worth recording: in one function, swapping the call's arguments
byte-matches but is *semantically wrong*. The worker declined to do it. Byte
equality does not imply the C says the right thing.

#### split_funcs.py rewritten: the rule was unsound in both directions

The prologue-based rule was wrong twice over. It **missed leaf functions**, which
have no `addiu $sp` to recognise — and it was only accidentally safe against the
opposite error, because a MIPS function may legitimately have **several `jr $ra`
returns**, and splitting at each one would have cut single functions apart.

The sound test uses splat's own analysis: splat emits a local label for every
internal branch/jump target it found, so **an unlabelled instruction after a
return is unreachable from the preceding code** and therefore begins something
new. Verified on two spans:

* `func_80059208` is genuinely two 3-instruction getters, one returning
  `gp+0x570` and the other `&D_800F56A0`. Split.
* `func_80040424` has an internal `.L80040444` target, so *that* return is not a
  boundary — correctly left alone — while the unlabelled code after the second
  return is split off.

**435 further game-region functions** are hidden this way, beyond the 320 already
applied. Applying them is pending: re-splitting the disassembly while
hand-decompilation workers are mid-task would change the spans under them.

### 2026-07-25 — wave 2 batch 3: 17 functions, and a feature of mine that never worked

17 matched / 298 instructions.

**`-Os` is a real optimisation level and was missing from every sweep.** One
function matched *only* at `-Os`, and it brought two others closer than any other
level did. Now in `flagsweep.py` and `autodecomp.py`.

#### Correction: `expand_div` was a no-op, and my verification of it was bad

I added an `expand_div` flag to reproduce ASPSX's division macro and reported it
working. **It did nothing.** Proven by comparing `.text` with and without it:
byte-identical.

The verification was the real failure. I compiled one file, saw a `break` in the
output, and concluded the macro was being emitted — but that `break` is **cc1's
own** zero-division guard, present either way. I checked a symptom that could not
distinguish the hypothesis, and never ran the control.

Two separate gates, both found by a worker and confirmed here:

1. `div_needs_expanding()` returns False for a `$zero` destination, and GCC
   2.95.2 always prints `div $0,%1,%2` — the destination field is unused because
   MIPS `div` writes hi/lo. So the check rejected every division this compiler
   produces. Now gated on the flag instead.
2. The `div`/`rem` handler *also* returns early for a `$zero` destination, before
   reaching the expansion block, and the expansion assumes the destination
   register appears in the `div` line — whereas GCC emits a separate `mfhi`
   afterwards.

`-mno-check-zero-division` now correctly suppresses cc1's own guard, so half of
it is right. **The macro is still not emitted, so `expand_div` remains
non-functional** and any function containing `/` or `%` is still unmatchable.
Fixing it properly means teaching maspsx the split `div`/`mfhi` form, which is a
design change in that tool, not a one-liner. Recorded as open rather than fixed.

#### Other findings

* **Nested `if`s defeat `fold_truthop`.** `(f & 0x8000) && !(f & 0x4000)` folds to
  `andi 0xC000; xori 0x8000; sltiu`; nesting the tests reproduces the original's
  two-branch form. Same for `r == 0 || r == -1`, which folds to `addiu 1; sltiu 2`.
* **New `cc1_G=0` trigger:** a `%hi/%lo` pair *split across basic blocks* — the
  original hoists `lui %hi` into two different branch delay slots. The `cc1_G=8`
  `$at` macro cannot be split. (Not merely "two different registers".)
* Accumulate into the existing variable (`c += g[1]`) rather than a fresh one, or
  GCC allocates another register.
* Cache a pointer loaded out of a struct in a local, or GCC reloads it after any
  intervening store.
* The **register-copy-of-a-constant** pattern (`li $a1,0; move $a2,$a1`) is now
  the single largest 1–2 instruction blocker, hit in six functions, immune to
  ~20 flags and to shared locals. Same phenomenon as the "6-argument stack-push"
  note above. This needs decomp-permuter or reading cc1's source, not more
  flag guessing.

**A bytecode VM occupies `0x800709xx`–`0x800714xx`**: `D_800F5B98[]` is an `s32`
register file, `D_800F5BE8` its state (u8 stack pointer at `+0x14`, `s32` stack at
`+0x18`), and every `func_800709xx`/`func_8007
13xx`/`func_800714xx` is one opcode.
Worth decompiling as a single translation unit rather than piecemeal.

### 2026-07-25 — I committed a broken state; added the check that would have caught it

I committed with `git add -A` while a worker was still running, having said
explicitly that I would not, and the committed tree was **not byte-identical** —
34 bytes wrong. Removing the offending file exposed three more behind it.

Eight files across `src/manual/` were non-matching drafts left on disk. Workers
were told to delete anything that did not match; some did not, and one file
matched per its author but conflicted with a generated `src/auto/` file covering
the same span.

Whack-a-mole was the wrong response. `tools/verify_src.py` now checks **every**
file individually and can quarantine failures to `build/rejected/` (moved, not
deleted, so the work survives). It runs in `tools/all.py` *before* `build.py`,
because `build.py` reports a hash mismatch somewhere in a 1.9 MB image without
saying which file caused it — the per-file check names it.

After quarantining the eight: **234 functions from C, byte-identical.**

The lesson is about the gate, not the workers. A non-matching file is not
harmless work-in-progress — it silently replaces correct assembly with wrong
code — and until now nothing checked for one except a whole-binary hash that
cannot localise the fault.

### 2026-07-25 — wave 2 complete: 234 functions, 3.36% of instructions

All six workers in. Wave 2 hand-decompilation: 20 + 18 + 17 + 18 = **73
functions**. Combined with automation and wave 1:

| | |
|---|---|
| functions from C | **234** |
| instructions | **3,334 / 99,265 (3.36%)** |
| executable | `84747e64…` byte-identical |
| disc image | `d5785a41…` byte-identical |
| boot from in-duel state | passes |

#### Two bugs of mine in split_funcs.py, found by the verifier

**1. The output must accumulate, not be rewritten.** The tool reads `asm/`, which
already reflects previously applied splits, so a freshly computed set contains
only what is *still* merged. Writing it verbatim erased the 320 splits that made
the current disassembly what it is, and left 104 source files referring to
functions that no longer existed. It now unions with the existing file and is
re-run to a fixed point.

**2. The local-label regex never matched anything.** Those lines are *indented*
(`  .L800708B0:`) and the pattern was anchored `^\.L`. So every internal branch
target looked unlabelled, and 205 of 462 proposed splits were cutting real
functions in half. Once a bad symbol exists splat renders that address as
`func_X` rather than `.L X`, so the error is self-justifying on the next run.

**My spot-check missed it because I picked the wrong example.** In
`func_80040424` the label sits *on* the return instruction, not after it, so that
case never exercised the broken path — it passed for the wrong reason. Two
examples that both look convincing can still leave the actual code path untested.

With the regex fixed, **257** genuine splits, not 462. Final inventory after
iterating to a fixed point:

```
1206 game functions (from 678 originally reported, then 966)
 404 use $gp (45.1% of game code)
 436 leaf functions
```

`tools/verify_src.py` is what caught both bugs — it names the failing file, where
the whole-binary hash only says something is wrong somewhere in 1.9 MB.

### 2026-07-25 — three tools added; decomp-permuter working on Windows

Installed to attack the named blockers rather than to have more tools:

| tool | what it is for |
|---|---|
| **decomp-permuter** | the register-allocation wall — randomly rewrites C and scores each variant against the target object, which is the search no compiler flag can express |
| **PCSX-Redux** (44.8 MB) | runtime observability: Lua API and GDB stub for execution tracing and real frame comparison. DuckStation has neither |
| **GCC 2.95.2 source** | `local-alloc.c`, `sched.c`, `regclass.c`, `reload1.c`, `mips.md` — to explain *why* sched2 changes allocation |

A bonus in the Redux archive: **`psyq-obj-parser.exe`**, the exact tool an earlier
worker had to hand-write a replacement for in order to read native Psy-Q `.LIB`
files.

`tools/permute.py` scaffolds a permuter directory per function: `target.o` is the
original bytes, obtained by assembling that one function's disassembly with the
same path `build.py` uses, so nothing is approximated. `base.c` comes from
`src/manual`, `src/auto`, `build/rejected` or a fresh m2c draft, preprocessed
because the permuter parses C itself. Flags are baked into `compile.sh`, since
preprocessing strips the `decomp-flags` comment that `cc.py` would otherwise read.

#### Four Windows assumptions in the permuter, all patched in our fork

1. It required the POSIX owner-execute bit on `compile.sh`; Windows cannot
   represent it, so every scaffold was rejected. Skipped where unsatisfiable.
2. It looks for `mips-linux-gnu-objdump`; ours is `mipsel-none-elf-objdump`, the
   same binutils build — aliased.
3. It shells out to bare `cpp` — aliased to `mipsel-none-elf-cpp.exe`.
4. It `exec`s `compile.sh` directly, which Windows refuses (WinError 193). Now
   routed through bash for `.sh` on `nt`.

#### The permuter corroborates the diagnosis independently

On `func_80044278`, its own penalty breakdown is:

```
Stack Differences:      0
Branch Differences:     0
Register Differences:   8      <- the entire score
Reorderings:            0
Insertions/Deletions:   0
base score = 40
```

Nothing structural, nothing reordered — purely register allocation. That is a
second, independent confirmation of what four workers reported by hand, from a
tool with no knowledge of their conclusions.
