"""Set up (and optionally run) decomp-permuter for one function.

The permuter attacks the failure mode that flags cannot: a function that is
structurally correct but allocates one register differently. Roughly a third of
the near-misses from hand-decompilation are of that shape, and a 30-combination
flag sweep separated none of them -- the original wants `-fschedule-insns2`'s
instruction ordering together with the non-sched2 register allocation.

It works by randomly rewriting the C (introducing temporaries, reordering
statements, changing types) and scoring each variant against the target object,
which is exactly the search that cannot be expressed as a compiler flag.

    py -3 tools/permute.py func_800495A4            scaffold only
    py -3 tools/permute.py func_800495A4 --run      scaffold and run

The scaffold is `build/permute/<func>/` containing base.c, target.o and
compile.sh, per the permuter's documented contract (`./compile.sh in.c -o out.o`).
"""
import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import cc                                                        # noqa: E402

ASM = os.path.join(REPO, "asm", "code_002800.s")
AS = os.path.join(REPO, "tools", "bin", "bin", "mipsel-none-elf-as.exe")
PERMUTER = os.path.join(REPO, "tools", "permuter", "permuter.py")
WORK = os.path.join(REPO, "build", "permute")

def permuter_env():
    """PATH with our binutils visible under the names the permuter expects.

    It looks for `mips-linux-gnu-objdump` and friends; ours is
    `mipsel-none-elf-objdump`, the same binutils build, so tools/bin/bin carries
    an alias and simply needs to be on PATH.
    """
    env = dict(os.environ)
    env["PATH"] = (os.path.join(REPO, "tools", "bin", "bin") + os.pathsep
                   + env.get("PATH", ""))
    return env


PROLOGUE = ('.include "macro.inc"\n\n.set noat\n.set noreorder\n\n'
            '.section .text, "ax"\n\n')


def extract_asm(name):
    """The `glabel name ... endlabel` block, verbatim."""
    out, inside = [], False
    for line in open(ASM):
        if re.match(r"^glabel\s+%s\s*$" % re.escape(name), line):
            inside = True
        if inside:
            out.append(line)
            if re.match(r"^endlabel\s+%s\s*$" % re.escape(name), line):
                return out
    return None


def find_source(name):
    """An existing C file for this function, preferring curated over generated."""
    for rel in ("src/manual/%s.c" % name, "src/auto/%s.c" % name,
                "build/rejected/%s.c" % name):
        p = os.path.join(REPO, rel.replace("/", os.sep))
        if os.path.exists(p):
            return p
    return None


def m2c_draft(name, dest):
    """Fall back to a fresh m2c draft, with the gp rewrite applied."""
    import autodecomp
    body = autodecomp.run_m2c(name)
    if body is None:
        return None
    body, decls = autodecomp.rewrite_gp(body)
    if body is None:
        return None
    open(dest, "w").write(autodecomp.HEADER + decls + body)
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("func")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--keep-base", action="store_true",
                    help="do not overwrite an existing base.c (use to continue "
                         "from a variant the permuter already improved)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()
    name = args.func

    asm = extract_asm(name)
    if asm is None:
        sys.exit("%s not found in %s" % (name, os.path.basename(ASM)))

    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)

    # target.o -- the original bytes, obtained by assembling the disassembly of
    # this one function. Nothing is approximated: it is the same path build.py
    # uses for the assembly that is still in the tree.
    tgt_s = os.path.join(d, "target.s")
    with open(tgt_s, "w") as fp:
        fp.write(PROLOGUE)
        fp.writelines(asm)
    r = subprocess.run([AS, "-march=r3000", "-mabi=32", "-EL", "-no-pad-sections",
                        "-I", os.path.join(REPO, "build", "asm_parts"),
                        "-I", os.path.join(REPO, "include"),
                        "-o", os.path.join(d, "target.o"), tgt_s],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("assembling target.s failed:\n%s" % (r.stdout + r.stderr))

    src = find_source(name)
    if src is None:
        src = m2c_draft(name, os.path.join(d, "_draft.c"))
        if src is None:
            sys.exit("no existing C and m2c produced nothing usable for %s" % name)
        print("base: fresh m2c draft (no existing C found)")
    else:
        print("base: %s" % os.path.relpath(src, REPO))

    # The permuter needs preprocessed C -- it parses the file itself and cannot
    # follow #include. Preprocessing also strips the `decomp-flags` comment, so
    # the flags have to be baked into compile.sh rather than read from the source.
    fl = cc.flags_for(src)
    base_c = os.path.join(d, "base.c")
    cpp = [os.path.join(REPO, "tools", "bin", "bin", "mipsel-none-elf-cpp.exe"),
           "-undef", "-nostdinc", "-D__GNUC__=2", "-D__OPTIMIZE__",
           "-Dmips", "-D__mips__", "-D__PSX__", "-DPSX", "-P"]
    for inc in cc.INCLUDES:
        cpp += ["-I", inc]
    r = subprocess.run(cpp + [src, base_c], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("preprocessing failed:\n%s" % (r.stdout + r.stderr))

    extra = ",".join(fl.get("cc1_extra", []))
    sh = os.path.join(d, "compile.sh")
    with open(sh, "w", newline="\n") as fp:
        # Every knob has to be passed explicitly.  Preprocessing strips the
        # decomp-flags comment, so anything not on this command line silently
        # falls back to the *defaults* in cc.flags_for -- which is not the same
        # thing as the file's own flags.  Two were missing and both mattered:
        # cc1_G defaulted to 8 for a file needing 0, changing exactly the
        # register allocation the permuter is here to search, and expand_div
        # defaulted off, so a function containing a division started six
        # instructions short.  On func_8005F1B8 that showed as a base score of
        # 780 where match.py reported three differing registers.
        fp.write("#!/bin/bash\n"
                 "# Generated by tools/permute.py. Invoked as: ./compile.sh in.c -o out.o\n"
                 "# Flags are baked in because preprocessing removed the source's\n"
                 "# decomp-flags comment that tools/cc.py would otherwise read.\n"
                 'exec "%s" "%s" "$1" "$3" --as-g %d --cc1-g %d'
                 ' --expand-div %d%s%s\n'
                 % (sys.executable.replace("\\", "/"),
                    os.path.join(REPO, "tools", "cc.py").replace("\\", "/"),
                    fl["as_G"], fl["cc1_G"], int(fl.get("expand_div", 0) or 0),
                    ' "--flags=%s"' % fl["opt"] if fl.get("opt") else "",
                    ' "--flags=%s"' % extra if extra else ""))
    os.chmod(sh, 0o755)

    with open(os.path.join(d, "settings.toml"), "w", newline="\n") as fp:
        fp.write('func_name = "%s"\n' % name)

    print("scaffolded %s" % os.path.relpath(d, REPO))
    print("  flags: opt=%s as_G=%s cc1_G=%s expand_div=%s%s"
          % (fl["opt"], fl["as_G"], fl["cc1_G"],
             int(fl.get("expand_div", 0) or 0),
             " cc1_extra=" + extra if extra else ""))

    if args.run:
        print("\nrunning permuter (-j %d, stops on a zero score)..." % args.jobs)
        return subprocess.run([sys.executable, PERMUTER, d,
                               "-j", str(args.jobs), "--stop-on-zero",
                               "--better-only"], env=permuter_env()).returncode
    print("\nrun it with:\n  py -3 tools/permuter/permuter.py %s -j %d "
          "--stop-on-zero --better-only" % (os.path.relpath(d, REPO), args.jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
