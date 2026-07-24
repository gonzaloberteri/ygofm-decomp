"""Identify Psy-Q SDK functions inside the game's code by signature match.

The binary carries Psy-Q runtime RCS tags, so a large share of its code came
from the SDK rather than from Konami.  Those functions never need decompiling
by hand -- they only need naming.

Matching is exact, not fuzzy.  The trick is that the *mask* comes from the
library object's own relocation table: any field the linker would have patched
(jal targets, %hi/%lo immediates, absolute words) is excluded from the compare,
and every other byte must be identical.  So there is no similarity threshold to
tune and no false-positive class from "close enough" code.

    py -3 tools/psyq_sigs.py            report matches
    py -3 tools/psyq_sigs.py --write    also write config/symbol_addrs.txt
    py -3 tools/psyq_sigs.py --libdir D compare a different SDK release

`--libdir` accepts either ELF `.a` archives (Psy-Q 4.7, pre-converted) or
Sony's native `.LIB`/`.OBJ` files (4.4 through 4.6), which `tools/psyq_lib.py`
reads directly.  The default is unchanged.
"""
import argparse
import io
import json
import os
import struct
import sys
from collections import defaultdict

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBDIR = os.path.join(REPO, "tools", "bin", "psyq", "p47",
                      "psyq-4_7-converted", "lib")
VRAM = 0x80010000
MIN_INSNS = 5          # below this a signature is not discriminating

# relocation types -> bits the linker may rewrite
R_MIPS_16, R_MIPS_32, R_MIPS_REL32, R_MIPS_26 = 1, 2, 3, 4
R_MIPS_HI16, R_MIPS_LO16, R_MIPS_GPREL16, R_MIPS_LITERAL = 5, 6, 7, 8
R_MIPS_GOT16, R_MIPS_PC16, R_MIPS_CALL16 = 9, 10, 11

RELOC_MASK = {
    R_MIPS_32: 0x00000000,          # whole word is an address
    R_MIPS_REL32: 0x00000000,
    R_MIPS_26: 0xFC000000,          # keep the opcode, drop the target
    R_MIPS_HI16: 0xFFFF0000,
    R_MIPS_LO16: 0xFFFF0000,
    R_MIPS_GPREL16: 0xFFFF0000,
    R_MIPS_GOT16: 0xFFFF0000,
    R_MIPS_CALL16: 0xFFFF0000,
    R_MIPS_LITERAL: 0xFFFF0000,
    R_MIPS_16: 0xFFFF0000,
    R_MIPS_PC16: 0xFFFF0000,
}


def read_archive(path):
    """Yield (member_name, data) from a Unix ar archive."""
    data = open(path, "rb").read()
    if data[:8] != b"!<arch>\n":
        return
    off, longnames = 8, b""
    while off + 60 <= len(data):
        hdr = data[off:off + 60]
        name = hdr[0:16].decode("ascii", "replace").rstrip()
        try:
            size = int(hdr[48:58].decode("ascii").strip())
        except ValueError:
            break
        body = data[off + 60:off + 60 + size]
        off += 60 + size + (size & 1)

        if name.startswith("//"):
            longnames = body
            continue
        if name.startswith("/") and name[1:].isdigit():
            start = int(name[1:])
            end = longnames.find(b"\n", start)
            name = longnames[start:end].decode("ascii", "replace").rstrip("/")
        elif name.startswith("/"):
            continue                    # symbol index member
        name = name.rstrip("/")
        yield name, body


def signatures_from_object(blob, origin):
    """One signature per object: its whole .text section.

    Every symbol in these converted objects has st_size == 0, and the only
    per-function boundaries available are `$lib/file.rel.text@offset` local
    labels -- which are branch targets *inside* functions, not function starts.
    Deriving sizes from those produced dozens of 5-instruction signatures that
    matched everywhere.

    An object's .text is linked as one contiguous unit, so matching the whole
    section is both the faithful thing to do and far more discriminating.  The
    real function names are the defined STB_GLOBAL symbols, and their st_value
    gives the offset to name once the object is located.
    """
    try:
        elf = ELFFile(io.BytesIO(blob))
    except Exception:
        return []

    text = elf.get_section_by_name(".text")
    if text is None or text.data_size < MIN_INSNS * 4:
        return []
    text_idx = list(elf.iter_sections()).index(text)
    tdata = text.data()

    relocs = {}
    for sec in elf.iter_sections():
        if isinstance(sec, RelocationSection) and \
                sec.name in (".rel.text", ".rela.text"):
            for r in sec.iter_relocations():
                relocs[r["r_offset"]] = r["r_info_type"]

    exports = []
    for sec in elf.iter_sections():
        if not isinstance(sec, SymbolTableSection):
            continue
        for sym in sec.iter_symbols():
            if not sym.name or sym.name.startswith("$"):
                continue
            if sym["st_info"]["bind"] != "STB_GLOBAL":
                continue
            if sym["st_shndx"] != text_idx:
                continue
            exports.append((sym.name, sym["st_value"]))
    if not exports:
        return []
    exports.sort(key=lambda e: e[1])

    n = len(tdata) // 4
    words, masks = [], []
    for w in range(n):
        off = w * 4
        word = struct.unpack("<I", tdata[off:off + 4])[0]
        mask = RELOC_MASK.get(relocs.get(off), 0xFFFFFFFF)
        words.append(word & mask)
        masks.append(mask)

    if not any(m == 0xFFFFFFFF for m in masks):
        return []
    return [(exports[0][0], origin, words, masks, exports)]


def build_signatures(libdir=None):
    libdir = libdir or LIBDIR
    sigs = []
    for fn in sorted(os.listdir(libdir)):
        if fn.endswith(".a"):
            for member, blob in read_archive(os.path.join(libdir, fn)):
                sigs += signatures_from_object(blob, "%s(%s)" % (fn, member))
        elif fn.upper().endswith((".LIB", ".OBJ")):
            # Sony's native linker format -- same tuple shape out.
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import psyq_lib
            for member, blob in psyq_lib.iter_members(os.path.join(libdir, fn)):
                sigs += psyq_lib.signatures_from_object(
                    blob, "%s(%s)" % (fn.lower(), member), MIN_INSNS)
    return sigs


def match_signatures(sigs, regions, payload):
    """-> (matches, ambiguous, ambiguous_exports) for the code regions.

    matches      addr -> (name, origin, size, exports)
    ambiguous    addr -> {origin, ...} where more than one object matched
    """
    # Index by the value of the first unmasked word, so each target word does a
    # single dict lookup instead of a sweep over every signature.
    index = defaultdict(list)
    for name, origin, words, masks, exports in sigs:
        first = next(i for i, m in enumerate(masks) if m == 0xFFFFFFFF)
        index[words[first]].append((first, name, origin, words, masks, exports))

    matches = {}
    ambiguous = {}
    ambiguous_exports = {}
    for r in regions:
        if r["kind"] != "code":
            continue
        base, end = r["start"], r["end"]
        nwords = (end - base) // 4
        target = struct.unpack("<%dI" % nwords, payload[base:base + nwords * 4])

        for i in range(nwords):
            for first, name, origin, words, masks, exports in index.get(target[i], ()):
                start = i - first
                if start < 0 or start + len(words) > nwords:
                    continue
                if all((target[start + w] & masks[w]) == words[w]
                       for w in range(len(words))):
                    addr = VRAM + base + start * 4
                    cand = (name, origin, len(words) * 4, exports)
                    prev = matches.get(addr)
                    if prev is None:
                        matches[addr] = cand
                        continue
                    if prev[1] == origin:
                        continue
                    ambiguous.setdefault(addr, set()).update({prev[1], origin})
                    # Different objects, same bytes.  If they agree on the
                    # exported names it does not matter which one we keep; if
                    # they disagree, prefer the longer match and let the
                    # name-agreement check below decide whether to emit it.
                    if len(words) * 4 > prev[2]:
                        matches[addr] = cand
                    ambiguous_exports.setdefault(addr, []).append(exports)
                    ambiguous_exports[addr].append(prev[3])

    return matches, ambiguous, ambiguous_exports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--libdir", default=None,
                    help="SDK library directory (ELF .a or native .LIB/.OBJ)")
    args = ap.parse_args()

    libdir = args.libdir or LIBDIR
    sigs = build_signatures(libdir)
    print("built %d signatures from %s" % (len(sigs), os.path.basename(libdir)))

    regions = json.load(open(os.path.join(REPO, "config", "regions.json")))
    payload = open(os.path.join(REPO, "disc", "SLUS_014.11"), "rb").read()[0x800:]

    matches, ambiguous, ambiguous_exports = match_signatures(sigs, regions, payload)

    total = sum(m[2] for m in matches.values())
    code_bytes = sum(r["end"] - r["start"] for r in regions if r["kind"] == "code")
    print("\nmatched %d functions, %d bytes of %d code bytes (%.1f%%)"
          % (len(matches), total, code_bytes, total / code_bytes * 100))

    if ambiguous:
        print("\n%d address(es) matched by more than one SDK name "
              "(aliases or identical stubs):" % len(ambiguous))
        for addr in sorted(ambiguous)[:10]:
            print("  %08X  %s" % (addr, ", ".join(sorted(ambiguous[addr]))))
        if len(ambiguous) > 10:
            print("  ... and %d more" % (len(ambiguous) - 10))

    # overlap check: two functions claiming the same bytes means a bad match
    overlaps = 0
    ordered = sorted(matches.items())
    for (a1, m1), (a2, _) in zip(ordered, ordered[1:]):
        if a1 + m1[2] > a2:
            overlaps += 1
    print("\noverlapping matches: %d %s"
          % (overlaps, "(clean)" if overlaps == 0 else "<-- investigate"))

    by_lib = defaultdict(lambda: [0, 0, 0])
    named = {}
    skipped = 0
    for addr, (name, origin, size, exports) in matches.items():
        # Only name an address when every object that matched it agrees on the
        # exported names; otherwise a wrong name is worse than no name.
        if addr in ambiguous_exports:
            sets = [frozenset(n for n, _ in e) for e in ambiguous_exports[addr]]
            if len(set(sets)) > 1:
                skipped += 1
                continue
        lib = origin.split("(")[0]
        by_lib[lib][0] += 1
        by_lib[lib][1] += size
        by_lib[lib][2] += len(exports)
        for ename, eoff in exports:
            named[addr + eoff] = (ename, origin)

    print("\n  library      objects   funcs    bytes")
    for lib in sorted(by_lib, key=lambda l: -by_lib[l][1]):
        o, b, f = by_lib[lib]
        print("  %-12s %7d %7d  %7d" % (lib, o, f, b))
    print("\nnamed %d SDK functions" % len(named))

    if args.write:
        path = os.path.join(REPO, "config", "symbol_addrs.txt")
        with open(path, "w") as fp:
            fp.write("// Psy-Q SDK symbols identified by tools/psyq_sigs.py.\n"
                     "// Whole-object .text match under the library's own\n"
                     "// relocation mask -- exact, not a similarity score.\n")
            for addr in sorted(named):
                name, origin = named[addr]
                fp.write("%s = 0x%08X; // type:func  %s\n" % (name, addr, origin))
        print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
