"""Locate the external tools, whatever the host OS is.

Every other tool used to hardcode `...\\mipsel-none-elf-as.exe`, which meant the
tree only built on Windows.  Almost nothing about the *pipeline* is actually
Windows-specific -- binutils, mkpsxiso, PCSX-Redux and Ghidra all build or ship
natively for macOS and Linux -- with exactly one exception:

    CC1PSX.EXE is a 32-bit Windows PE and there is no native build of it.

Its codegen is the thing being reproduced byte for byte, so it cannot be swapped
for a rebuilt-from-source GCC 2.95.2 even if one existed: the whole point is
that *this* compiler emits *these* bytes.  (Someone has done this for Psy-Q 4.4
-- nocato/homebrew-psyq -- but not for 4.6, which is what this tree uses.)  Off
Windows it therefore runs under a PE loader, and this module is where that
prefix is attached.  Everything else only needed the `.exe` suffix made
conditional.

Layout under `tools/bin/` is unchanged; only the file extensions move:

    tools/bin/bin/mipsel-none-elf-{as,ld,objcopy,cpp,objdump}[.exe]
    tools/bin/psyq/p46/Psy-Q - 46/BIN/CC1PSX.EXE       (always .EXE, always PE)
    tools/bin/mkpsxiso-*/[dump]mkpsxiso[.exe]
    tools/bin/redux/pcsx-redux[.exe]

Off Windows the binutils usually live outside the repo instead -- there is no
macOS PSn00bSDK bundle to unzip into `tools/bin/` -- so anything not found there
is looked up on PATH.  Three overrides cover the rest:

    YGOFM_BINUTILS=/opt/mipsel/bin     directory holding mipsel-none-elf-*
    YGOFM_WINE=/usr/local/bin/wibo     PE launcher for CC1PSX.EXE
    YGOFM_CC1=/path/to/CC1PSX.EXE      the compiler itself

A note on paths.  Both launchers map the host filesystem onto `Z:\\`, so an
absolute POSIX path handed to a Windows program resolves as long as the current
drive is Z: -- which it is here.  So `cc1 /abs/foo.i -o /abs/foo.s` works
unmodified and no path translation is needed.  What does *not* work is a path
that only exists inside a Wine prefix.
"""
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WINDOWS = os.name == "nt"
#: Suffix for *native* executables.  CC1PSX.EXE is not one of these -- it is a
#: Windows binary on every host, so its name is spelled out literally.
EXE = ".exe" if WINDOWS else ""

BIN = os.path.join(REPO, "tools", "bin")
BINUTILS_DIR = os.environ.get("YGOFM_BINUTILS") or os.path.join(BIN, "bin")
PSYQ = os.path.join(BIN, "psyq", "p46", "Psy-Q - 46")
PSYQ_INCLUDE = os.path.join(PSYQ, "INCLUDE")
PSYQ_P47_LIB = os.path.join(BIN, "psyq", "p47", "psyq-4_7-converted", "lib")


class MissingTool(Exception):
    """A required external tool is not where it should be.

    Raised rather than sys.exit() so a caller that has a fallback -- the boot
    test without an emulator, say -- can choose to carry on.
    """


#: Why nothing here raises when a tool is absent.  These are called at module
#: level by build.py and friends, exactly as the hardcoded paths they replace
#: were.  Raising on import would make `verify_src.py` -- which is largely
#: bookkeeping -- die on a host that has Python but no binutils yet, and would
#: turn a missing emulator into a failure of the byte-identity gate, which does
#: not use the emulator at all.  So resolution is best-effort and the checking
#: is a separate, explicit step: `python tools/toolchain.py`.


def binutil(name):
    """Absolute path to one of the mipsel-none-elf binutils.

        binutil("as")  ->  .../tools/bin/bin/mipsel-none-elf-as[.exe]

    PSn00bSDK publishes this bundle for Windows and Linux only -- there is no
    macOS build -- so on a Mac these come from PCSX-Redux's Homebrew formulae
    (`tools/macos-mips/` in that tree) or a source build, and land outside the
    repo.  Hence the PATH fallback and YGOFM_BINUTILS.  Either way it is a
    native binary on every host and needs no launcher.
    """
    exe = "mipsel-none-elf-" + name + EXE
    local = os.path.join(BINUTILS_DIR, exe)
    if os.path.exists(local):
        return local
    return shutil.which(exe) or local


def pe_launcher():
    """What runs a 32-bit Windows PE here, or None on Windows itself.

    `wibo` first, and by a wide margin.  It is a small Win32 loader -- not an
    emulator -- that maps the PE and calls it directly, which on an Apple
    Silicon Mac means the x86 code runs through Rosetta 2 in-process.  Measured
    on an M4 against the same 32-bit test binary:

        wibo, native macOS         30 ms start-up   0.25 s on the benchmark
        Wine in a linux/amd64      256 ms           2.7 s

    The gap is not Wine's fault.  Docker Desktop registers Rosetta for x86-64
    ELF but falls back to QEMU for i386, and `wine32` is an i386 ELF -- so a
    "Rosetta" container silently runs the compiler under QEMU.  wibo sidesteps
    that: it is an x86-64 Mach-O that builds 32-bit segments for itself, so
    Rosetta handles it.

    Wine is kept as the fallback because it is what works on an x86-64 Linux
    box, where it is native and fast.

    Neither needs path translation: wibo maps host paths onto `Z:\\` exactly as
    Wine does, and quotes arguments MSVCRT-style, so the space in `Psy-Q - 46`
    survives.
    """
    if WINDOWS:
        return None
    override = os.environ.get("YGOFM_WINE")
    if override:
        return override
    for cand in ("wibo", "wine", "wine64", "wine-stable"):
        found = shutil.which(cand)
        if found:
            return found
    vendored = os.path.join(BIN, "wibo" + EXE)
    if os.path.exists(vendored):
        return vendored
    # Named anyway when absent, so the failure surfaces as a plain "not found"
    # from the compile that needed it rather than as an import error in a tool
    # that was never going to run the compiler.
    return "wibo"


#: Kept so that anything still calling the old name keeps working.
wine = pe_launcher


def psyq_cc1():
    """Argv *prefix* that runs the Psy-Q compiler -- a list, not a string.

    A list because off Windows it is two words (`wine`, then the exe) and
    callers must splice rather than concatenate:

        subprocess.run(psyq_cc1() + flags + [src, "-o", asm])
    """
    cc1 = os.environ.get("YGOFM_CC1") or os.path.join(PSYQ, "BIN", "CC1PSX.EXE")
    launcher = pe_launcher()
    return ([launcher, cc1] if launcher else [cc1])


def _first_existing(*paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def _iso_tool(name):
    """mkpsxiso / dumpsxiso, whose release directory is named per platform.

    Upstream ships `mkpsxiso-2.30-win64`, `-linux`, `-macos` and so on, so the
    directory name cannot be hardcoded the way the binutils one can.
    """
    for entry in sorted(os.listdir(BIN)) if os.path.isdir(BIN) else []:
        if not entry.startswith("mkpsxiso"):
            continue
        cand = _first_existing(os.path.join(BIN, entry, name + EXE),
                               os.path.join(BIN, entry, "bin", name + EXE))
        if cand:
            return cand
    return shutil.which(name) or os.path.join(
        BIN, "mkpsxiso-2.30", name + EXE)


def mkpsxiso():
    return _iso_tool("mkpsxiso")


def dumpsxiso():
    return _iso_tool("dumpsxiso")


def redux():
    """PCSX-Redux, for the boot test and the sampling/coverage tools.

    macOS ships it as an .app bundle, so the executable is not simply
    `pcsx-redux` in the directory the archive unpacks to.
    """
    d = os.path.join(BIN, "redux")
    return _first_existing(
        os.path.join(d, "pcsx-redux" + EXE),
        os.path.join(d, "PCSX-Redux.app", "Contents", "MacOS", "PCSX-Redux"),
        shutil.which("pcsx-redux")) or os.path.join(d, "pcsx-redux" + EXE)


def bios():
    return os.path.join(BIN, "redux", "SCPH1001.BIN")


def ghidra_run():
    """Ghidra's headless launcher -- `.bat` on Windows, extensionless elsewhere."""
    root = os.path.join(BIN, "ghidra", "ghidra_12.1.2_PUBLIC")
    name = "analyzeHeadless.bat" if WINDOWS else "analyzeHeadless"
    return os.path.join(root, "support", name)


def venv_python():
    """The project interpreter, for tools that re-exec a sibling script.

    Prefer the interpreter already running: if `all.py` was started with the
    venv's Python then every child inherits it, and hardcoding a path only
    matters when someone runs it with a bare `python`.
    """
    if os.path.basename(os.path.dirname(sys.executable)).lower() in (
            "scripts", "bin"):
        return sys.executable
    sub = "Scripts" if WINDOWS else "bin"
    cand = os.path.join(REPO, ".venv", sub, "python" + EXE)
    return cand if os.path.exists(cand) else sys.executable


#: (label, path, required-for-the-hash-gate).  The emulator and the ISO tools
#: are not required: `build.py` reaches byte-identity without either, and a host
#: kept purely for batch flagsweep/permuter work needs neither.
def describe():
    cc1 = psyq_cc1()
    rows = [("cpp", binutil("cpp"), True),
            ("as", binutil("as"), True),
            ("ld", binutil("ld"), True),
            ("objcopy", binutil("objcopy"), True),
            ("objdump", binutil("objdump"), True),
            ("cc1", cc1[-1], True)]
    if len(cc1) > 1:
        rows.append(("pe-launcher", cc1[0], True))
    rows += [("mkpsxiso", mkpsxiso(), False),
             ("dumpsxiso", dumpsxiso(), False),
             ("redux", redux(), False),
             ("bios", bios(), False)]
    return rows


def main():
    print("host:   %s / %s" % (sys.platform, "windows (native PE)" if WINDOWS
                               else "CC1PSX.EXE needs a PE launcher"))
    print("python: %s" % venv_python())
    missing = 0
    for label, path, required in describe():
        # The launcher may be a bare name resolved from PATH, not a path.
        found = os.path.exists(path) or (
            os.sep not in path and shutil.which(path) is not None)
        if not found and required:
            missing += 1
        mark = "ok  " if found else ("MISS" if required else "--  ")
        print("  %-10s %s  %s" % (label, mark, path))
    if missing:
        print("\n%d required tool(s) missing. See README.md, "
              "'Building off Windows'." % missing)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
