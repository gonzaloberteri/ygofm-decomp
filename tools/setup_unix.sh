#!/usr/bin/env bash
# Set up the toolchain on macOS or Linux.
#
#   tools/setup_unix.sh
#
# Installs into tools/bin/, which is gitignored, so nothing here ends up in the
# tree.  What it cannot install is the proprietary half: the Psy-Q SDK, the disc
# and a PlayStation BIOS are yours to supply.  See README.md.
#
# Two things are deliberately built from source rather than taken from a package
# manager, because this project's whole gate is byte-identity and the toolchain
# is part of the input:
#
#   * binutils is pinned to **2.40**, the version the tree was developed
#     against.  Homebrew's `mipsel-linux-gnu-binutils` is 2.46 and, worse, a
#     different target triple -- `-linux-gnu` is a hosted target with different
#     defaults from bare-metal `-none-elf`.  Assembler defaults are exactly the
#     kind of thing that moves bytes, so it is pinned rather than borrowed.
#   * the target triple is `mipsel-none-elf`, matching the PSn00bSDK bundle the
#     Windows side uses.
#
# wibo is fetched as a release binary: it is a loader, not part of the compiler,
# and does not affect the output bytes.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$REPO/tools/bin"
BINUTILS_VERSION=2.40
WIBO_VERSION=1.2.0
JOBS="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)"

mkdir -p "$BIN"
cd "$BIN"

# ---------------------------------------------------------------- wibo
# The PE loader for CC1PSX.EXE.  Only needed off Windows.
if [ "$(uname)" = "Darwin" ]; then WIBO_ASSET=wibo-macos; else WIBO_ASSET=wibo; fi
if [ ! -x "$BIN/wibo" ]; then
    echo "==> fetching wibo $WIBO_VERSION ($WIBO_ASSET)"
    curl -fsSL -o "$BIN/wibo" \
        "https://github.com/decompals/wibo/releases/download/$WIBO_VERSION/$WIBO_ASSET"
    chmod +x "$BIN/wibo"
fi
"$BIN/wibo" --help >/dev/null 2>&1 || true
echo "==> wibo: $("$BIN/wibo" --help 2>&1 | head -1)"

# macOS runs wibo's x86-64 code through Rosetta 2.  Without it the loader
# cannot start at all, and the failure is an opaque "bad CPU type".
if [ "$(uname)" = "Darwin" ] && ! /usr/bin/arch -x86_64 /usr/bin/true 2>/dev/null; then
    echo "!!  Rosetta 2 is not installed. Run:"
    echo "      softwareupdate --install-rosetta --agree-to-license"
    exit 1
fi

# ------------------------------------------------------------ binutils
if [ -x "$BIN/bin/mipsel-none-elf-as" ]; then
    echo "==> binutils already present: $("$BIN/bin/mipsel-none-elf-as" --version | head -1)"
else
    echo "==> building binutils $BINUTILS_VERSION for mipsel-none-elf (a few minutes)"
    work="$BIN/.build-binutils"
    rm -rf "$work"; mkdir -p "$work"; cd "$work"
    curl -fsSL -O "https://ftp.gnu.org/gnu/binutils/binutils-$BINUTILS_VERSION.tar.xz"
    tar xf "binutils-$BINUTILS_VERSION.tar.xz"
    mkdir build && cd build
    # --disable-nls and --disable-werror: this is an old release built with a
    # much newer clang, and its own -Werror trips on warnings that did not
    # exist in 2023.  Neither flag affects generated output.
    #
    # --with-system-zlib is not optional on macOS.  The zlib bundled with 2.40
    # predates the current SDK, fails to detect fdopen, and then `#define
    # fdopen(fd,mode) NULL` collides with the real declaration in <stdio.h> --
    # the build dies in zutil.c with "expected identifier or '('".  zlib is only
    # used for compressed debug sections, so the system one is equivalent here.
    "../binutils-$BINUTILS_VERSION/configure" \
        --target=mipsel-none-elf \
        --prefix="$BIN" \
        --disable-multilib --disable-nls --disable-werror \
        --disable-gdb --disable-sim --disable-readline \
        --with-system-zlib
    # MAKEINFO=true: binutils builds its own info manuals, macOS has no
    # `makeinfo`, and the build dies with "Error 127" from doc/bfd.info long
    # after the parts anyone here cares about have compiled.  `true` stubs the
    # doc build out; the binaries are unaffected.
    make -j"$JOBS" MAKEINFO=true
    make install MAKEINFO=true
    cd "$BIN"
    # The build tree is ~1 GB and nothing needs it once installed.
    rm -rf "$work"
    echo "==> binutils: $("$BIN/bin/mipsel-none-elf-as" --version | head -1)"
fi

# ----------------------------------------------------------------- cpp
# `cpp` ships with gcc, not binutils, and tools/cc.py needs it for the
# preprocessing stage.  Pinned to 12.3.0 to match the PSn00bSDK bundle the
# Windows side uses, rather than the newest release: preprocessor output is an
# input to the hash gate, so "a cpp" is not good enough, it has to be the same
# cpp.  (PCSX-Redux's Homebrew formula builds gcc 16 -- fine for their purposes,
# wrong for this one.)
#
# Only `make all-gcc` is built.  That produces the compiler proper, including
# cpp, and skips libgcc -- which would need target headers this bare-metal
# configuration deliberately does not have.
GCC_VERSION=12.3.0
if [ -x "$BIN/bin/mipsel-none-elf-cpp" ]; then
    echo "==> cpp already present: $("$BIN/bin/mipsel-none-elf-cpp" --version | head -1)"
else
    echo "==> building gcc $GCC_VERSION cpp for mipsel-none-elf (slow: ~20 min)"
    work="$BIN/.build-gcc"
    rm -rf "$work"; mkdir -p "$work"; cd "$work"
    curl -fsSL -O "https://ftp.gnu.org/gnu/gcc/gcc-$GCC_VERSION/gcc-$GCC_VERSION.tar.xz"
    tar xf "gcc-$GCC_VERSION.tar.xz"
    # gmp/mpfr/mpc, in-tree, so the build does not depend on what Homebrew
    # happens to have installed.
    (cd "gcc-$GCC_VERSION" && ./contrib/download_prerequisites)
    mkdir build && cd build
    PATH="$BIN/bin:$PATH" "../gcc-$GCC_VERSION/configure" \
        --target=mipsel-none-elf \
        --prefix="$BIN" \
        --without-headers --without-isl \
        --with-gnu-as --with-gnu-ld \
        --enable-languages=c \
        --disable-multilib --disable-nls --disable-werror \
        --disable-threads --disable-shared --disable-libssp \
        --disable-libgomp --disable-libatomic --disable-libquadmath
    make -j"$JOBS" all-gcc MAKEINFO=true
    make install-gcc MAKEINFO=true
    cd "$BIN"
    rm -rf "$work"
    echo "==> cpp: $("$BIN/bin/mipsel-none-elf-cpp" --version | head -1)"
fi

echo
echo "==> done. Check what resolved:"
echo "      python3 tools/toolchain.py"
