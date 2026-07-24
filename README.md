# ygofm-decomp

A matching decompilation of **Yu-Gi-Oh! Forbidden Memories** (PlayStation, NTSC-U,
`SLUS-01411`).

The build reproduces both the game executable and the complete 517 MB disc image
**byte for byte**. Functions that have been decompiled are compiled from C;
everything else is linked from extracted assembly. The binary is bit-identical
either way, so the game is always playable and the hash is always the test.

```
SLUS_014.11    84747e64f6da8e764206ec203e489acf8c9dcf7d
disc image     d5785a41900a10968d4a28a390666c4b9879b796
```

See [PLAN.md](PLAN.md) for the design, the reverse-engineering findings, and a
dated status log.

## Why byte-identity

Verifying reimplemented gameplay logic means playing the game, which does not
scale and cannot run unattended. Byte equality is the only cheap oracle: a
decompiled function either assembles to the same bytes or it is rejected. There
is no "looks correct" failure mode.

This is not theoretical. A single wrong byte at `0x80092B73` — caused by data
lines in the disassembly omitting the raw-word field, so a `.short` was dropped
when the assembly was split — was caught by nothing except the hash.

## Requirements

* **Windows.** The Psy-Q tools are 32-bit PE binaries and run natively under
  WOW64. This is the one place where Windows is easier than Linux for this work.
* Python 3.12 (`py -3`). The bare `python` on PATH may be the Microsoft Store
  stub, which does not work.
* A copy of the game disc as a `MODE2/2352` `.bin`/`.cue` pair. Nothing
  copyrighted is in this repository — the disc, the extracted assembly and the
  Psy-Q SDK are all gitignored.
* DuckStation, for the boot test only.

### One-time setup

```bash
py -3 -m venv .venv
.venv/Scripts/python.exe -m pip install splat64 spimdisasm rabbitizer pyelftools \
    colorama ansiwrap watchdog levenshtein n64img pygfxd tqdm intervaltree \
    pylibyaml pyyaml crunch64 pycparser pillow
```

Then fetch the toolchain into `tools/bin/`: `mipsel-none-elf` binutils and
`mkpsxiso` from their GitHub releases, and Psy-Q 4.6 and 4.7. Clone `maspsx`,
`asm-differ` and `m2c` into `tools/`.

## Building

```bash
py -3 tools/all.py
```

Runs the whole pipeline — extract the disc, classify regions, split, compile,
link, rebuild the image, verify, and render the progress map. Exits non-zero if
the output stops being byte-identical.

To skip launching the emulator:

```bash
py -3 tools/all.py --no-boot
```

## Toolchain

Recovered by search rather than assumption (`tools/flagsweep.py`), since none of
it is documented anywhere public:

| | |
|---|---|
| compiler | `CC1PSX.EXE` — GCC **2.95.2**, from Psy-Q 4.6 |
| assembler | ASPSX **2.86**, reproduced by `maspsx` |
| flags | `-O3 -G8` |

The assembler's `-G` is a **separate knob** from the compiler's and varies per
translation unit. It lives in [config/cflags.json](config/cflags.json).

## Layout of the binary

```
0x80010000 .. 0x80012800   data (opens with a jump table, not with .text)
0x80012800 .. 0x80073704   Konami game code      ~397 KB   <- the target
0x80073704 .. 0x80092C00   Psy-Q SDK             ~128 KB   identified, not decompiled
0x80092C00 .. 0x801E0000   data, and 1.09 MB of zero fill
$gp = 0x8009AF08           set by the startup code at 0x80012A54
```

The 1.86 MB executable is 71.6% zero fill. The real decompilation target is the
397 KB of code Konami actually wrote.

## Tools

| tool | purpose |
|---|---|
| `all.py` | run the whole pipeline |
| `extract_disc.py` | pull the 9 files out of the MODE2/2352 image, record SHA-1 baselines |
| `map_regions.py` | classify every 1 KB window as code / data / zero |
| `gen_splat_config.py` | emit `config/splat.yaml` from the region map |
| `build.py` | compile, assemble, link, and verify against the original |
| `split_asm.py` | carve the disassembly around functions that now exist in C |
| `make_iso.py` | rebuild the disc image with original LBAs |
| `verify_boot.py` | hash gate plus a DuckStation smoke test from a save state |
| `cc.py` | compile one C file the way the original build did |
| `match.py` | compare a compiled file against the original, per function |
| `flagsweep.py` | search the flag space for what makes a file match |
| `psyq_sigs.py` | identify Psy-Q SDK functions by relocation-masked signature |
| `gen_context.py` | build a Psy-Q type/signature context for m2c |
| `autodecomp.py` | run m2c → compile → compare unattended, keep what matches |
| `funcs.py` | function inventory and candidate selection |
| `progress_map.py` | render `progress.png` |
| `tu_detect.py`, `tu_own.py` | propose translation-unit boundaries (both still too weak to trust) |

## Measuring progress

`progress.png` shows one cell per function. Both metrics are printed, because
they disagree sharply — the automated pass matches the *smallest* functions, so
counting functions flatters the work by roughly 10x. **Instructions matched is
the number to watch.**

## What is not done

* Translation-unit boundaries are not reconstructed. Two heuristics have been
  tried and both are too weak to trust; see PLAN.md. This no longer blocks
  matching, only readability of the source tree.
* The boot test is a smoke test, not a frame comparison. That is sufficient
  while the build is byte-identical, and becomes load-bearing only when a
  function is accepted as equivalent-but-not-identical.
* The Psy-Q SDK region is still linked as extracted assembly rather than against
  the genuine library objects.
