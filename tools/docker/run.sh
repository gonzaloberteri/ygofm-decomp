#!/usr/bin/env bash
# Run a repo command inside the toolchain container.
#
#   tools/docker/run.sh python3 tools/toolchain.py
#   tools/docker/run.sh python3 tools/match.py src/manual/func_8004B734.c
#   tools/docker/run.sh python3 tools/flagsweep.py src/globals.c
#
# The repo is bind-mounted rather than copied, so edits on the host are visible
# immediately and build artefacts land in the host's build/ -- which is what
# makes the container a place to *run* the toolchain rather than a place the
# work lives.
#
# The Psy-Q SDK is not in the image and never should be: it is proprietary.  It
# is mounted from wherever the host keeps it.  By default that is the usual
# tools/bin/psyq inside the repo, in which case the repo mount already covers it
# and no second mount happens.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE="${YGOFM_IMAGE:-ygofm:toolchain}"

args=(--rm -i
      --platform linux/amd64
      -v "$REPO:/work"
      -w /work
      -e YGOFM_BINUTILS=/opt/mipsel/bin)

# A tty only when there is one: without this, piping the output of a run into
# another command makes docker fail with "the input device is not a TTY".
[ -t 0 ] && args+=(-t)

# Let the host keep the SDK outside the repo.  tools/bin is gitignored, so a
# checkout that carries it inside the repo works with no extra configuration.
if [ -n "${YGOFM_PSYQ_DIR:-}" ]; then
    args+=(-v "$YGOFM_PSYQ_DIR:/work/tools/bin/psyq:ro")
fi

# Write build artefacts as the invoking user, not as root.  Without this every
# file the container creates in build/ is root-owned and the host's own tools
# cannot overwrite them on the next run.
if [ "$(uname)" != "Darwin" ]; then
    args+=(-u "$(id -u):$(id -g)" -e HOME=/tmp
           -e WINEPREFIX=/tmp/wineprefix)
fi

exec docker run "${args[@]}" "$IMAGE" "$@"
