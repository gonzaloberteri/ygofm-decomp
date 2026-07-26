# The toolchain, on a host that is not Windows.
#
# One thing in this build is not portable and cannot be made portable:
# CC1PSX.EXE is a 32-bit Windows PE, it is the compiler whose exact output the
# project reproduces byte for byte, and no native build of it exists.  So it
# runs under `wibo`, a small Win32 loader.
#
# This image is for a Linux box wanting a reproducible environment.  **On macOS
# use tools/setup_unix.sh instead** -- wibo runs natively there, and measured on
# an M4 the native path is ~9x faster to start and ~11x faster to run than
# anything containerised.  The reason is worth stating because it is a trap:
# Docker Desktop registers Rosetta for x86-64 ELF but falls back to QEMU for
# i386, so an "accelerated" amd64 container still emulates 32-bit code.  wibo is
# an x86-64 program that builds 32-bit segments for itself, so it stays on the
# fast path -- which is also why this image needs no i386 packages and no Wine.
#
# Nothing proprietary is baked in.  The Psy-Q SDK and the disc stay on the host
# and are bind-mounted; see tools/docker/run.sh.
FROM --platform=linux/amd64 debian:bookworm-slim

ARG BINUTILS_URL=https://github.com/Lameguy64/PSn00bSDK/releases/download/v0.24/gcc-mipsel-none-elf-12.3.0-linux.zip
ARG WIBO_VERSION=1.2.0

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates curl unzip git \
        python3 python3-pip python3-venv \
        build-essential cmake ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /usr/local/bin/wibo \
        "https://github.com/decompals/wibo/releases/download/${WIBO_VERSION}/wibo" && \
    chmod +x /usr/local/bin/wibo

# PSn00bSDK publishes this bundle for Windows and Linux only.  Inside a Linux
# container that is exactly what is wanted; on macOS there is nothing to unzip,
# which is why setup_unix.sh builds binutils from source instead.
RUN curl -fsSL "$BINUTILS_URL" -o /tmp/binutils.zip && \
    mkdir -p /opt/mipsel && unzip -q /tmp/binutils.zip -d /opt/mipsel && \
    rm /tmp/binutils.zip && \
    /opt/mipsel/bin/mipsel-none-elf-as --version | head -1

# mkpsxiso only rebuilds the disc image; the byte-identity gate on the
# executable does not need it, so a failure here must not fail the build.
RUN git clone --depth 1 --branch v2.30 --recurse-submodules \
        https://github.com/Lameguy64/mkpsxiso /tmp/mkpsxiso && \
    cmake -S /tmp/mkpsxiso -B /tmp/mkpsxiso/build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/mkpsxiso && \
    cmake --build /tmp/mkpsxiso/build --target install && \
    rm -rf /tmp/mkpsxiso || echo "mkpsxiso build failed -- disc rebuild unavailable"

RUN pip3 install --no-cache-dir --break-system-packages \
        splat64 spimdisasm rabbitizer pyelftools colorama ansiwrap watchdog \
        levenshtein n64img pygfxd tqdm intervaltree pylibyaml pyyaml crunch64 \
        pycparser pillow toml

# Read by tools/toolchain.py.  The Psy-Q path is left to the bind mount.
ENV YGOFM_BINUTILS=/opt/mipsel/bin \
    YGOFM_WINE=/usr/local/bin/wibo \
    PATH=/opt/mipsel/bin:/opt/mkpsxiso/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /work
