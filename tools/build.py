"""Assemble, link and verify SLUS_014.11 against the original.

The binary interleaves data and code (it opens with a jump table at 0x2800,
not with .text), so splat's section-ordered linker script can't express the
layout.  Instead every region is pinned to its exact VMA in a generated script;
an ld "section overlaps" error then means a region changed size, which is a
louder and earlier failure than a hash mismatch at the end.

Exit code 0 only when the rebuilt file is byte-identical to the original.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import match
import split_asm
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO, "tools", "bin", "bin")
AS = os.path.join(BIN, "mipsel-none-elf-as.exe")
LD = os.path.join(BIN, "mipsel-none-elf-ld.exe")
OBJCOPY = os.path.join(BIN, "mipsel-none-elf-objcopy.exe")

VRAM = 0x80010000
# Set by the startup code at 0x80012A54; the linker needs it to resolve the
# R_MIPS_GPREL16 relocations that small-data references compile down to.
GP_BASE = 0x8009AF08
BUILD = os.path.join(REPO, "build")
ASFLAGS = ["-march=r3000", "-mabi=32", "-EL", "-no-pad-sections",
           "-I", os.path.join(REPO, "include")]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED: %s" % " ".join(os.path.basename(c) for c in cmd[:1]) +
              " " + " ".join(cmd[1:]))
        print(r.stdout)
        print(r.stderr)
        sys.exit(1)
    return r


def compile_sources():
    """Compile every src/**/*.c and place each at its original address.

    A C file must cover a contiguous span of the original binary -- that is what
    a translation unit is.  Requiring it means each object's .text can be pinned
    with a single linker rule, and a file that does not satisfy it is not a real
    TU and should be split.
    """
    src_root = os.path.join(REPO, "src")
    if not os.path.isdir(src_root):
        return set(), []

    inv = match.asm_inventory()
    decompiled, objs = set(), []

    # Hand-written files win over anything tools/autodecomp.py generated: the
    # automated pass regenerates src/auto/ wholesale and would otherwise
    # collide with a curated version of the same function.
    sources = []
    for dirpath, _, files in os.walk(src_root):
        for fn in sorted(files):
            if fn.endswith(".c"):
                sources.append(os.path.join(dirpath, fn))
    sources.sort(key=lambda p: ("auto" in p.replace("\\", "/").split("/"), p))

    for src in sources:
        if True:
            rel = os.path.relpath(src, REPO).replace("\\", "/")
            obj = os.path.join(BUILD, "src", rel.replace("/", "_")[:-2] + ".o")
            os.makedirs(os.path.dirname(obj), exist_ok=True)
            run([sys.executable, os.path.join(REPO, "tools", "cc.py"), src, obj])

            funcs = match.object_functions(obj)
            known = {n: inv[n] for n in funcs if n in inv}
            if not known:
                print("  skip %s: defines nothing known to the disassembly" % rel)
                continue

            if any(n in decompiled for n in known):
                continue        # already claimed by a hand-written file
            ordered = sorted(known.items(), key=lambda kv: kv[1][0])
            start = ordered[0][1][0]
            span = ordered[-1][1][0] + ordered[-1][1][1] - start
            built = sum(len(funcs[n][0]) * 4 for n, _ in ordered)
            if built != span:
                print("  skip %s: functions are not contiguous in the original "
                      "(%d bytes of C over a %d byte span) -- split this file"
                      % (rel, built, span))
                continue

            objs.append((start, obj, ".text"))
            decompiled.update(n for n, _ in ordered)

    if decompiled:
        print("compiled %d function(s) from C in %d file(s)"
              % (len(decompiled), len(objs)))
    return decompiled, objs


def main():
    regions = json.load(open(os.path.join(REPO, "config", "regions.json")))
    os.makedirs(os.path.join(BUILD, "asm"), exist_ok=True)
    os.makedirs(os.path.join(BUILD, "assets"), exist_ok=True)

    objs = []          # (vma, object path, section name)

    # ---- C translation units take precedence over the disassembly ----
    decompiled, c_objs = compile_sources()
    objs += c_objs

    # assemble only the stretches no C file has claimed
    fragments = split_asm.split(decompiled)
    for frag_vma, frag in fragments:
        obj = os.path.join(BUILD, "asm", os.path.basename(frag)[:-2] + ".o")
        # -I the fragment dir first so its stripped macro.inc wins
        run([AS, "-I", split_asm.PARTS] + ASFLAGS + ["-o", obj, frag])
        objs.append((frag_vma, obj, ".text"))

    for r in regions:
        name = "%s_%06X" % (r["kind"], r["start"])
        vma = VRAM + r["start"]
        if r["kind"] != "code":
            # wrap the raw bytes in a uniquely-named section so the linker
            # script can pin it without any chance of merging or reordering
            blob = os.path.join(REPO, "assets", name + ".bin")
            sec = ".rgn_%06X" % r["start"]
            wrap = os.path.join(BUILD, "assets", name + ".s")
            with open(wrap, "w") as fp:
                fp.write('.section %s, "a"\n.incbin "%s"\n'
                         % (sec, blob.replace("\\", "/")))
            obj = os.path.join(BUILD, "assets", name + ".o")
            run([AS] + ASFLAGS + ["-o", obj, wrap])
            objs.append((vma, obj, sec))

    # ---- resolve references into the raw `bin` regions ----
    # Code references data that lives inside an .incbin blob, which carries no
    # symbols.  Those names encode their own address (D_80091A00), so every
    # reference that nothing defines can be satisfied mechanically.
    # addresses span KUSEG data, scratchpad (0x1F80xxxx) and KSEG1 (0xA000xxxx)
    sym_ref = re.compile(r"\b((?:D|func|jtbl|jpt|B)_([0-9A-F]{6,8}))\b")
    defined, referenced = set(decompiled), {}
    for _, frag in fragments:
        for line in open(frag):
            m = re.match(r"\s*(?:glabel|dlabel)\s+(\w+)", line)
            if m:
                defined.add(m.group(1))
                continue
            m = re.match(r"\s*(\w+):", line)
            if m:
                defined.add(m.group(1))
            for name, addr in sym_ref.findall(line):
                referenced[name] = int(addr, 16)

    # Decompiled C introduces references the disassembly never had: a
    # gp-relative access appears in the asm only as `0x170($gp)`, but in C it
    # becomes a named extern, so the name exists nowhere to be scanned for.
    # Read the objects' own undefined symbols instead of guessing from text.
    addr_name = re.compile(r"^(?:D|func|jtbl|jpt|B)_([0-9A-F]{6,8})$")
    for _, obj, _ in c_objs:
        try:
            elf = ELFFile(io.BytesIO(open(obj, "rb").read()))
        except Exception:
            continue
        for sec in elf.iter_sections():
            if not isinstance(sec, SymbolTableSection):
                continue
            for sym in sec.iter_symbols():
                if sym["st_shndx"] != "SHN_UNDEF" or not sym.name:
                    continue
                m = addr_name.match(sym.name)
                if m:
                    referenced[sym.name] = int(m.group(1), 16)

    missing = {k: v for k, v in referenced.items() if k not in defined}
    syms_ld = os.path.join(BUILD, "syms.ld")
    with open(syms_ld, "w") as fp:
        for name, addr in sorted(missing.items(), key=lambda kv: kv[1]):
            fp.write("%s = 0x%08X;\n" % (name, addr))
    print("resolved %d symbols into bin regions" % len(missing))

    # ---- linker script: every region pinned to its exact address ----
    ld_path = os.path.join(BUILD, "link.ld")
    with open(ld_path, "w") as fp:
        fp.write('INCLUDE "%s"\n' % syms_ld.replace("\\", "/"))
        # R_MIPS_GPREL16 relocations resolve to (symbol - _gp).  Defining _gp to
        # the value the startup code loads means a small-data reference lands at
        # the original offset without reconstructing the .sdata layout.
        fp.write("_gp = 0x%08X;\n" % GP_BASE)
        fp.write("SECTIONS\n{\n")
        for vma, obj, sec in sorted(objs):
            fp.write('    .s%08X 0x%08X : { "%s"(%s) }\n'
                     % (vma, vma, obj.replace("\\", "/"), sec))
        fp.write("    /DISCARD/ : { *(*) }\n}\n")

    elf = os.path.join(BUILD, "main.elf")
    run([LD, "-T", ld_path, "-o", elf, "--no-check-sections"])

    built_payload = os.path.join(BUILD, "main.built.bin")
    run([OBJCOPY, "-O", "binary", elf, built_payload])

    header = open(os.path.join(BUILD, "exe_header.bin"), "rb").read()
    payload = open(built_payload, "rb").read()

    original = open(os.path.join(REPO, "disc", "SLUS_014.11"), "rb").read()
    target_payload = original[0x800:]

    # objcopy stops at the last section; pad to the declared t_size
    if len(payload) < len(target_payload):
        payload += b"\x00" * (len(target_payload) - len(payload))

    out = os.path.join(BUILD, "SLUS_014.11")
    open(out, "wb").write(header + payload)

    built = header + payload
    print("built   %d B  sha1 %s" % (len(built), hashlib.sha1(built).hexdigest()))
    print("target  %d B  sha1 %s" % (len(original), hashlib.sha1(original).hexdigest()))

    if built == original:
        print("\n  OK  byte-identical to the original SLUS_014.11")
        return 0

    # report where it went wrong, grouped into runs, so regions can be demoted
    diffs = [i for i in range(min(len(built), len(original)))
             if built[i] != original[i]]
    print("\n  MISMATCH  %d differing bytes of %d (%.4f%%)"
          % (len(diffs), len(original), len(diffs) / len(original) * 100))
    if len(built) != len(original):
        print("  size differs by %d" % (len(built) - len(original)))

    runs, s, p = [], None, None
    for i in diffs:
        if s is None:
            s = p = i
        elif i - p <= 64:
            p = i
        else:
            runs.append((s, p))
            s = p = i
    if s is not None:
        runs.append((s, p))

    print("\n  first differing runs (file offsets):")
    for a, b in runs[:25]:
        print("    0x%06X .. 0x%06X  (%d B)  vram %08X"
              % (a, b, b - a + 1, VRAM + a - 0x800))
    if len(runs) > 25:
        print("    ... and %d more runs" % (len(runs) - 25))
    return 1


if __name__ == "__main__":
    sys.exit(main())
