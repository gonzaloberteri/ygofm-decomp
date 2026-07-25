# ygofm-decomp

A matching decompilation of **Yu-Gi-Oh! Forbidden Memories** (PlayStation,
NTSC-U, `SLUS-01411`).

Every commit rebuilds the game executable **and the complete 517 MB disc image
byte for byte**. Functions that have been decompiled are compiled from C;
everything else is linked from extracted assembly. The result is bit-identical
either way, so the game is always playable and the SHA-1 is always the test.

```
SLUS_014.11    84747e64f6da8e764206ec203e489acf8c9dcf7d
disc image     d5785a41900a10968d4a28a390666c4b9879b796
```

**Nothing copyrighted is distributed here.** The disc, the extracted assembly
and data, and the Psy-Q SDK are all gitignored — you supply your own. See
[Requirements](#requirements).

## Progress

![Decompilation progress](progress.png)

**Rectangle area is proportional to instruction count**, not one cell per
function. Green is decompiled and byte-matching, amber is still assembly and
addresses through `$gp`, white is still assembly, grey-blue is the Psy-Q SDK
region. Functions stay in address order, so the picture is a map of the
executable rather than a sorted chart.

The area weighting is not cosmetic. Function sizes in this binary span three
orders of magnitude: **37 of 678 game functions hold roughly 48% of the code**,
the largest single function is **10,376 instructions** against a mean of 147,
and a 6-instruction leaf on an equal grid looks exactly like a 400-instruction
state machine. Since the automated pass matches the *smallest* functions first,
an equal-cell map overstated progress by more than 10x. With area weighting the
coloured fraction of the image *is* the fraction of the game that is done.

Current status, from `py -3 tools/progress_map.py`:

| | total | matched | |
|---|---|---|---|
| game functions | 678 | **131** | 19.32% |
| game instructions | 99,265 | **1,636** | **1.65%** |

```
todo, uses $gp:   224 functions   50,102 instructions (50.47%)
todo:             323 functions
Psy-Q SDK:        671 functions   409 identified by signature, none decompiled
```

**Instructions matched is the number to watch.** The two metrics disagree by
more than 10x for the reason given above, and function count is the flattering
one.

One caveat on the concentration figure: `tools/split_funcs.py` found that
spimdisasm had merged 320 functions into 146 labelled spans (unlabelled code
continuing past a `jr $ra`), and 27 of the 37 "500+ instruction" functions were
containers of that kind. So the code is real but somewhat less concentrated in
single functions than the raw distribution suggests.

## Why byte-identity

Verifying reimplemented gameplay logic means playing the game, which does not
scale and cannot run unattended. Byte equality is the only cheap oracle: a
decompiled function either assembles to the same bytes as the original or it is
rejected. There is no "looks correct" failure mode and no drift.

This is not theoretical. A single wrong byte at `0x80092B73` — caused by data
lines in the disassembly omitting the raw-word field, so a `.short` was dropped
when the assembly was split — was caught by nothing except the hash.

The gate is also cheap enough to leave on: a full parallel rebuild takes about
3.4 seconds.

What the hash does *not* prove is that the tree describes the program
correctly. Twice a wrong claim survived it — most notably the Psy-Q crt0 at
`0x800129D8`, which splat emits as raw `.word` data rather than instructions.
The bytes are right, so the hash never complained. See [PLAN.md](PLAN.md).

## Requirements

* **Windows.** The Psy-Q tools are 32-bit PE binaries and run natively under
  WOW64, with no emulation layer. This is the one place where Windows is
  genuinely easier than Linux for this work.
* **Python 3.12** (`py -3`). The bare `python` on PATH may be the Microsoft
  Store stub, which does not work.
* **Your own copy of the game disc**, as a `MODE2/2352` `.bin`/`.cue` pair
  (517,872,768 bytes, 220,184 sectors, single track). Not distributed.
* **Your own copy of the Psy-Q SDK**, releases 4.6 and 4.7. Proprietary SCE
  binaries; not distributed, and not redistributable.
* DuckStation, for the boot test only.

### Setup

```bash
git clone --recurse-submodules https://github.com/gonzaloberteri/ygofm-decomp
cd ygofm-decomp

py -3 -m venv .venv
.venv/Scripts/python.exe -m pip install splat64 spimdisasm rabbitizer pyelftools \
    colorama ansiwrap watchdog levenshtein n64img pygfxd tqdm intervaltree \
    pylibyaml pyyaml crunch64 pycparser pillow
```

If you cloned without `--recurse-submodules`, run
`git submodule update --init --recursive`.

Then populate `tools/bin/`, which is gitignored and which you assemble yourself:

```
tools/bin/bin/mipsel-none-elf-{as,ld,objcopy}.exe   PSn00bSDK binutils 2.40
tools/bin/mkpsxiso-2.30-win64/mkpsxiso.exe          mkpsxiso 2.30
tools/bin/psyq/p46/Psy-Q - 46/BIN/CC1PSX.EXE        Psy-Q 4.6 (also INCLUDE/)
```

Psy-Q 4.7's libraries are additionally used by `tools/psyq_sigs.py`, because
neither release is a superset of the other — the game links 4.6's `libgpu/font`
and 4.7's `libds`.

## Building

```bash
py -3 tools/all.py                                  # everything
py -3 tools/all.py --no-boot                        # skip the emulator
py -3 tools/extract_disc.py "path\to\game.bin"      # if the disc is elsewhere
```

`all.py` runs the whole pipeline: extract the disc, classify regions, generate
the splat config, split, compile, link, verify, rebuild the image, verify again,
render the progress map. It exits non-zero the moment the output stops being
byte-identical.

`tools/build.py` alone is the fast inner loop and prints:

```
  OK  byte-identical to the original SLUS_014.11
```

The disc rebuild reproduces the original image's SHA-1. Where it cannot —
mkpsxiso regenerates ECC/EDC and the volume descriptor timestamps — the gate
falls back to comparing the content of all nine files individually, which must
match exactly.

## Toolchain

Recovered by search rather than assumption, with `tools/flagsweep.py`, since
none of it is documented anywhere public:

| | |
|---|---|
| compiler | `CC1PSX.EXE` — GCC **2.95.2** (build 4.0), from Psy-Q 4.6 |
| assembler | ASPSX **2.86**, reproduced by [maspsx](https://github.com/mkst/maspsx) |
| linker | `mipsel-none-elf-ld`, with a generated script pinning every region to its exact VMA |

### Flags vary per translation unit

There is no single command line that reproduces this binary. Three knobs vary
independently per file:

* **`opt`** — the optimisation level. **`-O2` dominates**, `-O1` is common, and
  at least one function (`func_800136D4`) was built with **no `-O` at all**;
  only `-O0` produces its bare `addiu $sp,-16` / `addiu $sp,16` / `jr $ra` /
  `nop`. Across the 74 hand-decompiled files that carry their own flags: 57
  `-O2`, 15 `-O1`, 1 `-O3`, 1 with no `-O`. An earlier claim in PLAN.md that
  the build used `-O3` throughout was based on two tiny functions and is
  retracted.
* **`as_G`** — the *assembler's* `-G`, which decides whether a small-symbol
  reference is emitted as `offset($gp)` or as a `%hi/%lo` pair. This is a
  separate knob from the compiler's: turning `as -G8` on globally *breaks*
  functions that legitimately use `%hi/%lo` for a symbol small enough to have
  been gp-addressed.
* **`cc1_G`** — the compiler's `-G`, which decides which objects are *eligible*
  for the small-data area. With `cc1_G=0` GCC emits its own `lui`/`%lo` pair;
  with `cc1_G=8` it emits the `lw $r,sym` assembler macro, and the two allocate
  registers differently. Corollary: cc1 never allocates `$at`, so `$at` in the
  original proves an assembler macro rather than compiler output.

Flags live next to the code they describe, as a comment on the first line of
each file, read by `tools/cc.py`:

```c
/* decomp-flags: opt=-O2 as_G=8 */
```

Keeping them in the file rather than in a shared JSON is what lets parallel
workers run without contending on one config. `config/cflags.json` holds the
default and the machine-generated entries for `src/auto/`.

## Layout of the binary

```
0x80010000 .. 0x80012800   data (the image opens with a jump table, not .text)
0x800129D8 .. 0x80012B50   Psy-Q crt0
0x80012B50 .. 0x80073704   Konami game code      ~397 KB   <- the target
0x80073704 .. 0x80092C00   Psy-Q libraries       ~128 KB   identified, not decompiled
0x80092C00 .. 0x801E0000   data, and 1.09 MB of zero fill
$gp = 0x8009AF08           set by the crt0 at 0x80012A54
```

The 1.86 MB executable is 71.6% zero fill, and the SDK accounts for another
128 KB. Successive corrections took the real target from 1.86 MB (raw file) to
525 KB (code only) to **397 KB of code Konami actually wrote** — about 99,265
MIPS instructions.

The Psy-Q region is identified rather than decompiled, by relocation-masked
signature match against the real library objects: the mask comes from each
object's own relocation table, so every field the linker would have patched is
excluded and everything else must be identical. There is no similarity
threshold to tune. **99.33% of the SDK code is identified and the residual is
fully accounted for.** The genuine libraries are deliberately *not* linked; the
reasoning is in [PLAN.md](PLAN.md).

## Repository layout

```
config/           region map, splat config, symbol addresses, per-file flags
include/          types, macros, the generated assembler includes
linker_scripts/   the base linker script
src/manual/       hand-decompiled functions, one per file
src/auto/         functions matched by the unattended m2c pass
src/*.c           globals and early hand-written units
tools/            the pipeline (see below)
tools/bin/        gitignored: binutils, mkpsxiso, Psy-Q. Supply your own.
```

Three tools are git submodules:

| submodule | points at |
|---|---|
| `tools/maspsx` | [gonzaloberteri/maspsx](https://github.com/gonzaloberteri/maspsx), branch `extern-small-data-nop` |
| `tools/asm-differ` | [simonlindholm/asm-differ](https://github.com/simonlindholm/asm-differ), upstream |
| `tools/m2c` | [matt-kempster/m2c](https://github.com/matt-kempster/m2c), upstream |

The maspsx fork carries one patch, and it is load-bearing. Upstream learns
which symbols live in the small-data area only from `.sdata` blocks and
`.comm`/`.lcomm` — that is, from objects *defined in the same translation
unit*. Decompiled code references the game's globals as `extern`, for which cc1
emits `.extern sym, size`, so those were never recognised as small and the
load-delay `nop` was never forced. Meanwhile gas, given `-G8`, addressed them
gp-relative anyway. The two ends disagreed and every affected function came out
one word short per load/use pair — which made any function whose body is a
chain of `lhu $v0,off($gp); nop; sh $v0,off($gp)` unmatchable for tooling
reasons rather than source reasons. The patch honours the size operand of
`.extern`, which is exactly the test gas itself applies.

## Tools

| tool | purpose |
|---|---|
| `all.py` | run the whole pipeline |
| `extract_disc.py` | pull the 9 files out of the MODE2/2352 image, record SHA-1 baselines |
| `find_boundary.py` | locate `.text`/`.data` in the flat payload by structural scoring |
| `map_regions.py` | classify every 1 KB window as code / data / zero |
| `gen_splat_config.py` | emit `config/splat.yaml` from the region map |
| `build.py` | compile, assemble, link, and verify against the original |
| `split_asm.py` | carve the disassembly around functions that now exist in C |
| `split_funcs.py` | find functions the disassembly merged, and emit labels to split them |
| `make_iso.py` | rebuild the disc image with the original LBAs |
| `verify_boot.py` | hash gate plus a DuckStation smoke test from a save state |
| `cc.py` | compile one C file the way the original build did |
| `match.py` | compare a compiled file against the original, per function |
| `flagsweep.py` | search the flag space for what makes a file match |
| `psyq_sigs.py` | identify Psy-Q SDK functions by relocation-masked signature |
| `psyq_lib.py` | native `LIB`/`LNK` archive reader, for 4.6's unconverted libraries |
| `psyq_residual.py` | account for every unmatched byte of the SDK region; compare releases |
| `gen_context.py` | build a Psy-Q type/signature context for m2c |
| `autodecomp.py` | run m2c → compile → compare unattended, keep what matches |
| `funcs.py` | function inventory and candidate selection |
| `progress_map.py` | render `progress.png` (deterministic — no timestamps, everything sorted) |
| `tu_detect.py`, `tu_own.py` | propose translation-unit boundaries (both still too weak to trust) |

## Contributing

The loop is short and the gate is absolute.

```bash
py -3 tools/funcs.py --candidates       # pick a target
py -3 tools/match.py src/manual/foo.c   # compile and compare, per function
py -3 tools/flagsweep.py src/manual/foo.c   # when it does not match, search the flags
py -3 tools/build.py                    # whole-binary SHA-1 gate
```

Rules:

1. Iterate on `tools/match.py` until it prints `MATCH` for every function in
   the file. **Never commit a file that does not match.** A non-matching file
   either breaks the build or, worse, silently stops the tree from describing
   the program.
2. Then run `tools/build.py` and confirm `OK byte-identical`. `match.py`
   compares only `.text`, so a function dispatching through a jump table can
   report `MATCH` while its jump table lands at the wrong address. Only the
   whole-binary hash catches that.
3. Record the flags in the file's `decomp-flags` comment, not globally.
4. If a function genuinely cannot be matched, say so in the commit message
   rather than committing something approximate.

Notes that recur, collected in [PLAN.md](PLAN.md): GCC 2.95 inverts `if`
conditions; `sll/sra 16` at entry means the parameter was `s32`, not `s16`;
two induction variables in the assembly means two pointer variables in the
source; `i[array]` instead of `array[i]` flips which register accumulates an
address; the `$gp` hardware-state words need `volatile`.

## What is not done

* **Translation-unit boundaries are not reconstructed.** Two heuristics have
  been tried and both are too weak to trust — `tu_detect.py` proposes 111
  boundaries with a median implied unit of 4 functions, where real units are
  far larger. This no longer *blocks* matching (`R_MIPS_GPREL16` plus a
  `_gp` definition in the linker script dissolved that), but the source tree is
  one file per function instead of the `src/<programmer>/<module>.c` layout the
  original used.
* **The disassembly merges 320 functions** into 146 labelled spans, because
  spimdisasm only starts a function where it has a reason to.
  `tools/split_funcs.py` detects these conservatively, but the inventory still
  overstates sizes and understates the function count wherever they have not
  been split out.
* **The boot test is a smoke test, not a frame comparison.** It loads an
  in-duel save state on the rebuilt image and checks the emulator stays up. That
  is sufficient while the build is byte-identical, and becomes load-bearing only
  when a function is ever accepted as equivalent-but-not-identical.
* **Unedited m2c output is exhausted.** Widening the candidate pool from 80 to
  250 instructions and sweeping six flag combinations bought exactly one extra
  function. `size-differs` is ~49% of failures, which is per-function structure
  recovery — types, struct layouts, signedness — not a flag search.
* **Data is still `.incbin`'d.** The card database, fusion table, drop tables
  and text are raw blobs, not named C structures.
* **The Psy-Q region is linked as extracted assembly**, by design rather than by
  omission.

## Credits

This project is mostly glue around other people's tools:

* [splat](https://github.com/ethteck/splat) and
  [spimdisasm](https://github.com/Decompollaborate/spimdisasm) — disassembly and
  segmentation
* [maspsx](https://github.com/mkst/maspsx) — reproduces ASPSX behaviour on top
  of GNU as
* [m2c](https://github.com/matt-kempster/m2c) — MIPS to C decompiler
* [asm-differ](https://github.com/simonlindholm/asm-differ) — side-by-side
  assembly diffs
* [mkpsxiso](https://github.com/Lameguy64/mkpsxiso) — LBA-pinned CD image
  rebuild
* [PSn00bSDK](https://github.com/Lameguy64/PSn00bSDK) — the `mipsel-none-elf`
  binutils build
* [DuckStation](https://github.com/stenzek/duckstation) — the boot test

Structure and tooling patterns follow
[sotn-decomp](https://github.com/Xeeynamo/sotn-decomp),
[NFSHS-PSX-decomp](https://github.com/Caesar0007/NFSHS-PSX-decomp) and
[open-spyro](https://github.com/theMagicalKarp/open-spyro).

The Forbidden Memories data-format community removed a great deal of guesswork
about the asset side: [fmlib-cpp](https://github.com/forbidden-memories-coding/fmlib-cpp),
[fmscrambler](https://github.com/forbidden-memories-coding/fmscrambler),
[YGOFM-BGEx](https://github.com/xan1242/YGOFM-BGEx) and
[FM-Manip-Tool](https://github.com/GenericMadScientist/FM-Manip-Tool).

## License

The tooling, configuration and documentation in this repository are original
work and are released under the [MIT License](LICENSE).

That licence covers `tools/`, `config/`, `include/`, `linker_scripts/` and the
documentation. It does **not** cover:

* the decompiled C under `src/`, which is derived from the original game and is
  a work of reverse engineering — it carries whatever status the original does,
  and no licence is granted for it here;
* `tools/maspsx`, `tools/asm-differ` and `tools/m2c`, which are git submodules
  carrying their own upstream licences.

Yu-Gi-Oh! Forbidden Memories is © Konami. This project is not affiliated with
or endorsed by Konami or Sony Interactive Entertainment. No game code, game
data, disc image or SDK binary is distributed here, and none ever will be: you
must supply your own legally obtained copies. Nothing in this repository is
usable without them.
