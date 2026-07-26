"""Import SLUS_014.11 into Ghidra at its real load address, with our names on it.

Ghidra is not a second decompiler for this project -- m2c is, because matching is
the gate and Ghidra's output is not built to recompile byte-identically.  What
Ghidra is good at is the thing that actually blocks matching: `size-differs` is
~49% of failures, which is types, struct layouts and signedness.  It is also the
cheap way to read the still-`.incbin`'d data (card database, fusion table) and to
get static call-graph reachability without paying for breakpoints.

The PSX-EXE header is 0x800 bytes and is not part of the image, so it is stripped
before import; the payload then sits at t_addr from the header, 0x80010000.
Getting that base wrong silently produces a database where every pointer,
cross-reference and jump table lands somewhere plausible but wrong.

    py -3 tools/ghidra_import.py             import + name functions, no analysis
    py -3 tools/ghidra_import.py --analyze   ...and run auto-analysis (slow)
"""
import argparse
import os
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import glob

def _versioned(parent, prefix):
    """The one directory under `parent` starting with `prefix`.

    Ghidra and Temurin both unpack to a name carrying the version and,
    for the JDK, the platform -- `jdk-21.0.11+10` on one host is not the
    name on another.  Matching a prefix keeps this working across hosts
    without pinning a build number that was only ever right locally.
    """
    hits = sorted(glob.glob(os.path.join(parent, prefix + "*")))
    return hits[0] if hits else os.path.join(parent, prefix)

GHIDRA = _versioned(os.path.join(REPO, "tools", "bin", "ghidra"), "ghidra_")
JDK = _versioned(os.path.join(REPO, "tools", "bin", "jdk"), "jdk-")
EXE = os.path.join(REPO, "build", "SLUS_014.11")
FUNCS_TXT = os.path.join(REPO, "build", "trace", "funcs.txt")
WORK = os.path.join(REPO, "build", "ghidra")
PAYLOAD = os.path.join(WORK, "SLUS_014.11.payload")

PSX_EXE_HEADER = 0x800
LANGUAGE = "MIPS:LE:32:default"


def strip_header():
    """Write the loadable payload, and return (entry, base, size) from the header."""
    with open(EXE, "rb") as fp:
        head = fp.read(PSX_EXE_HEADER)
        if head[:8] != b"PS-X EXE":
            sys.exit("%s is not a PS-X EXE" % EXE)
        entry, _gp, base, size = struct.unpack("<IIII", head[0x10:0x20])
        body = fp.read()
    if len(body) < size:
        sys.exit("payload is %d bytes but the header claims %d" % (len(body), size))
    os.makedirs(WORK, exist_ok=True)
    with open(PAYLOAD, "wb") as fp:
        fp.write(body[:size])
    return entry, base, size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyze", action="store_true",
                    help="run Ghidra auto-analysis after import (slow: the image "
                         "is 1.9 MB and 71.6%% of it is zero fill)")
    ap.add_argument("--project", default="ygofm")
    args = ap.parse_args()

    for path, what in ((GHIDRA, "Ghidra"), (JDK, "the JDK")):
        if not os.path.isdir(path):
            sys.exit("%s not found at %s -- see README Requirements" % (what, path))
    if not os.path.exists(EXE):
        sys.exit("%s missing -- run tools/build.py first" % EXE)

    entry, base, size = strip_header()
    print("PS-X EXE  entry %08X  base %08X  size %08X" % (entry, base, size))

    os.environ["GHIDRA_INSTALL_DIR"] = GHIDRA
    os.environ["JAVA_HOME"] = JDK

    import pyghidra
    pyghidra.start()

    from ghidra.program.model.symbol import SourceType

    with pyghidra.open_program(PAYLOAD, project_location=WORK,
                               project_name=args.project, analyze=False,
                               language=LANGUAGE,
                               loader="ghidra.app.util.opinion.BinaryLoader") as api:
        program = api.getCurrentProgram()
        tx = program.startTransaction("rebase and name")
        try:
            # Addresses go in as hex strings, not ints: these are all above
            # 0x80000000, and a Python int that large will not convert to a
            # Java int.
            program.setImageBase(api.toAddr("%08X" % base), True)

            named = 0
            if os.path.exists(FUNCS_TXT):
                for line in open(FUNCS_TXT):
                    bits = line.split()
                    if len(bits) < 2:
                        continue
                    addr = api.toAddr(bits[0])
                    # createFunction returns None if one is already there, which
                    # is fine -- the label below is what we actually want.
                    api.createFunction(addr, bits[1])
                    api.createLabel(addr, bits[1], True, SourceType.USER_DEFINED)
                    named += 1
                print("applied %d function names from %s"
                      % (named, os.path.relpath(FUNCS_TXT, REPO)))
            else:
                print("no %s -- run tools/trace.py once to generate it"
                      % os.path.relpath(FUNCS_TXT, REPO))

            entry_addr = api.toAddr("%08X" % entry)
            api.addEntryPoint(entry_addr)
            api.createLabel(entry_addr, "__SN_ENTRY_POINT", True,
                            SourceType.USER_DEFINED)
        finally:
            program.endTransaction(tx, True)

        if args.analyze:
            print("running auto-analysis; this takes a while...")
            pyghidra.analyze(program)
            print("analysis done")

        print("\nproject: %s (%s)" % (os.path.join(WORK, args.project + ".gpr"),
                                      program.getName()))
        print("open it with: %s" % os.path.join(
            GHIDRA, "ghidraRun.bat" if os.name == "nt" else "ghidraRun"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
