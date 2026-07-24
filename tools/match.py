"""Compile a C file and check each function against the original bytes.

Comparison ignores exactly the fields the linker would patch -- jal targets,
%hi/%lo immediates, absolute words -- taken from our own object's relocation
table.  Everything else must be identical, so a reported match is a real one.

    py -3 tools/match.py src/gfx/prim.c
"""
import argparse
import io
import os
import re
import struct
import subprocess
import sys

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
from psyq_sigs import RELOC_MASK                                  # noqa: E402

VRAM = 0x80010000
PAYLOAD = open(os.path.join(REPO, "disc", "SLUS_014.11"), "rb").read()[0x800:]

LABEL = re.compile(r"^(?:glabel|dlabel)\s+(\S+)")
INSN = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8}) [0-9A-F]{8} \*/")


def asm_inventory():
    """name -> (vram, size) for every function in the disassembly."""
    out = {}
    asm_dir = os.path.join(REPO, "asm")
    for fn in sorted(os.listdir(asm_dir)):
        if not fn.endswith(".s"):
            continue
        cur, first, count = None, None, 0
        for line in open(os.path.join(asm_dir, fn)):
            m = LABEL.match(line)
            if m:
                if cur and count:
                    out[cur] = (first, count * 4)
                cur, first, count = m.group(1), None, 0
                continue
            m = INSN.match(line)
            if m and cur:
                if first is None:
                    first = int(m.group(1), 16)
                count += 1
        if cur and count:
            out[cur] = (first, count * 4)
    return out


def object_functions(obj_path):
    """name -> (bytes, masks) for functions defined in .text of an object."""
    blob = open(obj_path, "rb").read()
    elf = ELFFile(io.BytesIO(blob))
    text = elf.get_section_by_name(".text")
    if text is None:
        return {}
    text_idx = list(elf.iter_sections()).index(text)
    tdata = text.data()

    relocs = {}
    for sec in elf.iter_sections():
        if isinstance(sec, RelocationSection) and \
                sec.name in (".rel.text", ".rela.text"):
            for r in sec.iter_relocations():
                relocs[r["r_offset"]] = r["r_info_type"]

    syms = []
    for sec in elf.iter_sections():
        if not isinstance(sec, SymbolTableSection):
            continue
        for sym in sec.iter_symbols():
            if sym.name and sym["st_shndx"] == text_idx and \
                    sym["st_info"]["type"] == "STT_FUNC":
                syms.append((sym.name, sym["st_value"], sym["st_size"]))
    syms.sort(key=lambda s: s[1])

    out = {}
    for i, (name, val, size) in enumerate(syms):
        if size == 0:
            size = (syms[i + 1][1] if i + 1 < len(syms) else len(tdata)) - val
        words, masks = [], []
        for w in range(size // 4):
            off = val + w * 4
            words.append(struct.unpack("<I", tdata[off:off + 4])[0])
            masks.append(RELOC_MASK.get(relocs.get(off), 0xFFFFFFFF))
        out[name] = (words, masks)
    return out


def original_words(vram, size):
    off = vram - VRAM
    n = size // 4
    return list(struct.unpack("<%dI" % n, PAYLOAD[off:off + n * 4]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--keep", action="store_true", help="keep the built object")
    ap.add_argument("--flags", default="", help="extra CC1PSX flags")
    args = ap.parse_args()

    rel = os.path.relpath(os.path.abspath(args.src), REPO).replace("\\", "/")
    obj = os.path.join(REPO, "build", rel.replace("/", "_") + ".o")
    cmd = [sys.executable, os.path.join(REPO, "tools", "cc.py"), args.src, obj]
    if args.flags:
        cmd += ["--flags", args.flags]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return 1

    inv = asm_inventory()
    built = object_functions(obj)
    if not built:
        print("no functions found in %s" % obj)
        return 1

    ok = bad = 0
    for name in sorted(built):
        words, masks = built[name]
        if name not in inv:
            print("  ?     %-24s not in the disassembly (new symbol)" % name)
            continue
        vram, size = inv[name]
        if size != len(words) * 4:
            print("  DIFF  %-24s size %d, original %d" % (name, len(words) * 4, size))
            bad += 1
            continue
        orig = original_words(vram, size)
        mism = [i for i in range(len(words))
                if (words[i] & masks[i]) != (orig[i] & masks[i])]
        if not mism:
            print("  MATCH %-24s 0x%08X  %d insns" % (name, vram, len(words)))
            ok += 1
        else:
            print("  DIFF  %-24s 0x%08X  %d/%d instructions differ"
                  % (name, vram, len(mism), len(words)))
            for i in mism[:8]:
                print("        +0x%02X  built %08X  original %08X"
                      % (i * 4, words[i], orig[i]))
            bad += 1

    if not args.keep and os.path.exists(obj):
        for ext in ("", ".s", ".i"):
            try:
                os.remove(obj + ext)
            except OSError:
                pass

    print("\n%d matched, %d differ" % (ok, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
