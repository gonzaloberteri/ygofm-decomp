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
# preprocessing stage.  It is satisfied with a *host* GNU cpp rather than a
# cross-built one, and that is a measured claim, not a convenience:
#
#   tools/cc.py invokes cpp with `-undef -nostdinc` and supplies every macro
#   explicitly (-D__GNUC__=2 -Dmips -D__mips__ -DPSX ...).  `-undef` discards
#   the built-in target macros, which is the only thing that makes a cpp
#   target-specific.  What is left is macro expansion and #include handling,
#   which are standardised.
#
#   Verified rather than assumed: PSn00bSDK's own mipsel-none-elf-cpp 12.3.0 and
#   a host GNU cpp 16 were run over a file exercising stringification, token
#   pasting, __VA_ARGS__, nested expansion and conditionals, with cc.py's exact
#   flags.  The output was byte-identical once the input pathname was
#   normalised.  Re-run that comparison if this ever looks suspect.
#
# Building a real cross gcc was tried first and abandoned: gcc 12.3.0's C++
# sources do not compile against the macOS 26 SDK's libc++ (hundreds of errors
# in <__locale> from attribute and macro handling), and moving to a gcc new
# enough to build would defeat the point of pinning 12.3.0 anyway -- at which
# point the host cpp, shown equivalent above, is the simpler answer.
#
# It must be a *GNU* cpp.  Apple's /usr/bin/cpp is clang's, which differs in
# ways that would matter here, so it is rejected rather than used silently.
if [ -x "$BIN/bin/mipsel-none-elf-cpp" ]; then
    echo "==> cpp already present: $("$BIN/bin/mipsel-none-elf-cpp" --version | head -1)"
else
    gnu_cpp=""
    for cand in cpp-16 cpp-15 cpp-14 cpp-13 cpp-12 cpp; do
        p="$(command -v "$cand" 2>/dev/null)" || continue
        if "$p" --version 2>&1 | head -1 | grep -qi "gcc\|GNU"; then
            gnu_cpp="$p"; break
        fi
    done
    if [ -z "$gnu_cpp" ]; then
        echo "!!  no GNU cpp found. Install one:"
        echo "      brew install gcc      # macOS"
        echo "      apt install cpp       # Debian/Ubuntu"
        echo "    Apple's /usr/bin/cpp is clang's and is not a substitute."
        exit 1
    fi
    echo "==> using GNU cpp: $gnu_cpp ($("$gnu_cpp" --version | head -1))"
    mkdir -p "$BIN/bin"
    # A wrapper rather than a symlink: argv[0] steers gcc's driver, and a name
    # like `mipsel-none-elf-cpp` pointing at a host cpp would make it look for a
    # cross toolchain that is not there.
    cat > "$BIN/bin/mipsel-none-elf-cpp" <<WRAP
#!/bin/sh
# Generated by tools/setup_unix.sh -- a host GNU cpp standing in for the
# cross-built one.  See that script for why this is sound.
exec "$gnu_cpp" "\$@"
WRAP
    chmod +x "$BIN/bin/mipsel-none-elf-cpp"
fi

echo
echo "==> done. Check what resolved:"
echo "      python3 tools/toolchain.py"
