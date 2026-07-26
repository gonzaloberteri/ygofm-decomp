"""Decompile a function out of the Ghidra project, for type and struct recovery.

This is not a source of code to commit -- Ghidra's C does not recompile to the
same bytes, and byte equality is the gate.  It is a source of *shape*: what is a
struct, how wide each field is, which arguments are signed.  `size-differs` is
~49% of match failures and that is exactly the information missing.

Read it beside `tools/sidebyside.py` output, write the types into
`include/game.h`, and let m2c and cc1 settle whether the result matches.

    py -3 tools/ghidra_decomp.py func_8004B734
    py -3 tools/ghidra_decomp.py 8004B734 --raw   also dump the disassembly
"""
import argparse
import os
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
WORK = os.path.join(REPO, "build", "ghidra")
PAYLOAD = os.path.join(WORK, "SLUS_014.11.payload")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="function name (func_8004B734) or bare address")
    ap.add_argument("--project", default="ygofm")
    ap.add_argument("--raw", action="store_true", help="also print the disassembly")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    if not os.path.exists(PAYLOAD):
        sys.exit("no Ghidra project -- run tools/ghidra_import.py --analyze first")

    os.environ["GHIDRA_INSTALL_DIR"] = GHIDRA
    os.environ["JAVA_HOME"] = JDK

    import pyghidra
    pyghidra.start()

    from ghidra.app.decompiler import DecompInterface
    from ghidra.util.task import ConsoleTaskMonitor

    name = args.target
    addr_text = name[len("func_"):] if name.startswith("func_") else name

    with pyghidra.open_program(PAYLOAD, project_location=WORK,
                               project_name=args.project, analyze=False) as api:
        program = api.getCurrentProgram()
        # Addresses go in as hex strings: everything here is above 0x80000000 and
        # will not convert to a Java int.
        addr = api.toAddr(addr_text)
        fn = api.getFunctionAt(addr)
        if fn is None:
            fn = program.getFunctionManager().getFunctionContaining(addr)
        if fn is None:
            sys.exit("no function at %s -- was the project analysed?" % addr_text)

        print("// %s at %s, %d bytes"
              % (fn.getName(), fn.getEntryPoint(), fn.getBody().getNumAddresses()))

        if args.raw:
            listing = program.getListing()
            for insn in listing.getInstructions(fn.getBody(), True):
                print("//   %s  %s" % (insn.getAddress(), insn))
            print()

        iface = DecompInterface()
        iface.openProgram(program)
        try:
            res = iface.decompileFunction(fn, args.timeout, ConsoleTaskMonitor())
            if not res.decompileCompleted():
                sys.exit("decompilation failed: %s" % res.getErrorMessage())
            print(res.getDecompiledFunction().getC())
        finally:
            iface.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
