"""Read native Psy-Q `.LIB`/`.OBJ` files without converting them to ELF.

Only Psy-Q 4.7 was available pre-converted to ELF `.a` archives; 4.4/4.5/4.6
ship in Sony's own linker format ("LNK\\x02" objects, "LIB\\x01" archives).
Rather than build `psyq-obj-parser` just to answer "which release did the game
link against", this reads the format directly.  It produces exactly the tuple
shape `psyq_sigs.signatures_from_object` produces, so the same matcher runs
over either input.

Format, as verified against files that also exist in ELF form:

    archive: "LIB" 0x01, then per member
             char name[8]        space padded, uppercased basename
             u32 timestamp
             u32 obj_offset      from the start of this member header
             u32 member_length   to the *next* member header, not the obj size
             [u8 len, char name[len]]*  exported-symbol directory, 0 terminates

    object:  "LNK" 0x02, then a stream of u8-tagged records (below).

Record and expression tags match Sony's linker; the ones that matter here are
SECTION/SWITCH/BYTES/ZEROES/UNINIT/RELOCATION/XDEF.  Debug records (SLD line
numbers, function/block scopes) are skipped -- they carry no output bytes.

    py -3 tools/psyq_lib.py <dir-or-file>     dump what was parsed
"""
import os
import struct
import sys

# record opcodes
END, BYTES, SWITCH, ZEROES = 0x00, 0x02, 0x06, 0x08
RELOCATION, XDEF, XREF, SECTION = 0x0A, 0x0C, 0x0E, 0x10
LOCAL_SYM, FILENAME, PROGRAMTYPE, UNINIT = 0x12, 0x1C, 0x2E, 0x30
INC_SLD, INC_SLD_B, INC_SLD_W, SET_SLD = 0x32, 0x34, 0x36, 0x38
SET_SLD_F, END_SLD = 0x3A, 0x3C
FUNC_START, FUNC_END, BLOCK_START, BLOCK_END = 0x4A, 0x4C, 0x4E, 0x50
SECTION_DEF, SECTION_DEF2, FUNC_START2 = 0x52, 0x54, 0x56

# expression node tags
E_VALUE, E_SYMBOL, E_SECT_BASE = 0x00, 0x02, 0x04
E_SECT_START, E_SECT_END = 0x0C, 0x16
E_ADD, E_SUB, E_DIV = 0x2C, 0x2E, 0x32
# other arithmetic operators appear rarely (0x36 shows up once, in
# libsn's hand-written cache.obj); all take two sub-expressions.
E_BINARY = (0x2C, 0x2E, 0x30, 0x32, 0x34, 0x36, 0x38, 0x3A)

# Psy-Q relocation kind -> the ELF R_MIPS_* number psyq_sigs already masks with.
# Verified by checking the opcode of the instruction each relocation lands on:
# 82/84 always land on lui / a %lo-form instruction, 74 always on jal or j.
PSYQ_RELOC_TO_ELF = {
    16: 2,      # 32-bit absolute word        -> R_MIPS_32
    74: 4,      # 26-bit jump target          -> R_MIPS_26
    82: 5,      # %hi                         -> R_MIPS_HI16
    84: 6,      # %lo                         -> R_MIPS_LO16
    100: 7,     # $gp relative                -> R_MIPS_GPREL16
    30: 2,      # 32-bit, big-endian variant  -> treat as a whole-word address
    92: 2,
    98: 7,
}


class Reader(object):
    def __init__(self, data):
        self.d, self.p = data, 0

    def u8(self):
        v = self.d[self.p]
        self.p += 1
        return v

    def u16(self):
        v = struct.unpack_from("<H", self.d, self.p)[0]
        self.p += 2
        return v

    def u32(self):
        v = struct.unpack_from("<I", self.d, self.p)[0]
        self.p += 4
        return v

    def string(self):
        n = self.u8()
        s = self.d[self.p:self.p + n]
        self.p += n
        return s.decode("ascii", "replace")


def _skip_expr(r):
    tag = r.u8()
    if tag == E_VALUE:
        r.u32()
    elif tag in (E_SYMBOL, E_SECT_BASE, E_SECT_START, E_SECT_END):
        r.u16()
    elif tag in E_BINARY:
        _skip_expr(r)
        _skip_expr(r)
    else:
        raise ValueError("unknown expression tag 0x%02X" % tag)


def parse_object(blob):
    """-> (sections, relocs, exports) or None if this is not a Psy-Q object.

    sections  {secnum: [name, bytearray]}
    relocs    {(secnum, offset): psyq_reloc_type}
    exports   [(name, secnum, offset)]   STB_GLOBAL equivalents, .text or not
    """
    if blob[:4] != b"LNK\x02":
        return None
    r = Reader(blob)
    r.p = 4
    sections, relocs, exports = {}, {}, []
    cur = None
    pos = {}

    while r.p < len(blob):
        op = r.u8()
        if op == END:
            break
        elif op == SECTION:
            num = r.u16()
            r.u16()                     # group
            r.u8()                      # alignment
            name = r.string()
            sections[num] = [name, bytearray()]
            pos[num] = 0
        elif op == SWITCH:
            cur = r.u16()
        elif op == BYTES:
            n = r.u16()
            data = blob[r.p:r.p + n]
            r.p += n
            sec = sections.setdefault(cur, ["?", bytearray()])
            if pos.get(cur, 0) != len(sec[1]):
                sec[1].extend(b"\x00" * (pos[cur] - len(sec[1])))
            sec[1].extend(data)
            pos[cur] = len(sec[1])
        elif op == ZEROES:
            n = r.u32()
            sec = sections.setdefault(cur, ["?", bytearray()])
            sec[1].extend(b"\x00" * n)
            pos[cur] = len(sec[1])
        elif op == RELOCATION:
            kind = r.u8()
            off = r.u16()
            _skip_expr(r)
            relocs[(cur, off)] = kind
        elif op == XDEF:
            r.u16()                     # symbol number
            sec = r.u16()
            off = r.u32()
            exports.append((r.string(), sec, off))
        elif op == XREF:
            r.u16()
            r.string()
        elif op == UNINIT:
            r.u16()
            r.u16()
            r.u32()
            r.string()
        elif op == LOCAL_SYM:
            r.u16()
            r.u32()
            r.string()
        elif op in (FILENAME,):
            r.u16()
            r.string()
        elif op == PROGRAMTYPE:
            r.u8()
        elif op in (INC_SLD,):
            pass
        elif op in (INC_SLD_B,):
            r.u8()
        elif op in (INC_SLD_W,):
            r.u16()
        elif op == SET_SLD:
            r.u32()
        elif op == SET_SLD_F:
            r.u32()
            r.u16()
        elif op == END_SLD:
            pass
        elif op == FUNC_START:
            r.u16()                     # section
            r.u32()                     # offset
            r.u16()                     # file
            r.u32()                     # start line
            r.u16()                     # frame reg
            r.u32()                     # frame size
            r.u16()                     # return pc reg
            r.u32()                     # mask
            r.u32()                     # mask offset
            r.string()                  # name
        elif op == FUNC_END:
            r.u16()
            r.u32()
            r.u32()
        elif op == BLOCK_START:
            r.u16()
            r.u32()
            r.u32()
        elif op == BLOCK_END:
            r.u16()
            r.u32()
            r.u32()
        elif op == SECTION_DEF:
            r.u16()
            r.u16()
            r.u16()
            r.string()
        elif op == SECTION_DEF2:
            r.u16()
            r.u16()
            r.u16()
            r.u32()
            r.u16()
            n = r.u16()
            for _ in range(n):
                r.string()
            r.string()
        elif op == FUNC_START2:
            r.u16()
            r.u32()
            r.u16()
            r.u32()
            r.u16()
            r.u32()
            r.u16()
            r.u32()
            r.u32()
            r.string()
        else:
            raise ValueError("unknown record 0x%02X at 0x%X" % (op, r.p - 1))

    return sections, relocs, exports


def iter_members(path):
    """Yield (member_name, object_bytes) for a .LIB, or the file for a .OBJ."""
    data = open(path, "rb").read()
    if data[:4] == b"LNK\x02":
        yield os.path.basename(path).lower(), data
        return
    if data[:4] != b"LIB\x01":
        return
    off = 4
    while off + 20 <= len(data):
        name = data[off:off + 8].decode("ascii", "replace").strip()
        obj_off = struct.unpack_from("<I", data, off + 12)[0]
        member_len = struct.unpack_from("<I", data, off + 16)[0]
        if obj_off == 0 or member_len <= obj_off:
            break
        start = off + obj_off
        yield name.lower() + ".obj", data[start:off + member_len]
        off += member_len


def signatures_from_object(blob, origin, min_insns=5):
    """Same tuple shape as psyq_sigs.signatures_from_object.

    -> [(first_export_name, origin, words, masks, exports)] with exports as
    [(name, offset_in_text)], words already masked, masks per word.
    """
    from psyq_sigs import RELOC_MASK

    parsed = parse_object(blob)
    if parsed is None:
        return []
    sections, relocs, exports = parsed

    tnum = None
    for num, (name, body) in sections.items():
        if name == ".text":
            tnum = num
            break
    if tnum is None:
        return []
    tdata = bytes(sections[tnum][1])
    if len(tdata) < min_insns * 4:
        return []

    exp = sorted([(n, o) for n, s, o in exports if s == tnum], key=lambda e: e[1])
    if not exp:
        return []

    words, masks = [], []
    for w in range(len(tdata) // 4):
        off = w * 4
        word = struct.unpack_from("<I", tdata, off)[0]
        kind = relocs.get((tnum, off))
        elf = PSYQ_RELOC_TO_ELF.get(kind) if kind is not None else None
        mask = RELOC_MASK.get(elf, 0xFFFFFFFF) if elf is not None else 0xFFFFFFFF
        words.append(word & mask)
        masks.append(mask)

    if not any(m == 0xFFFFFFFF for m in masks):
        return []
    return [(exp[0][0], origin, words, masks, exp)]


def build_signatures(libdir, min_insns=5):
    sigs = []
    names = sorted(os.listdir(libdir)) if os.path.isdir(libdir) else [libdir]
    for fn in names:
        if not fn.upper().endswith((".LIB", ".OBJ")):
            continue
        path = fn if os.path.isabs(fn) else os.path.join(libdir, fn)
        for member, blob in iter_members(path):
            sigs += signatures_from_object(blob, "%s(%s)" % (fn.lower(), member),
                                           min_insns)
    return sigs


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    target = sys.argv[1]
    files = ([os.path.join(target, f) for f in sorted(os.listdir(target))]
             if os.path.isdir(target) else [target])
    tot_obj = tot_text = tot_rel = bad = 0
    for path in files:
        if not path.upper().endswith((".LIB", ".OBJ")):
            continue
        n = t = rl = 0
        for member, blob in iter_members(path):
            try:
                parsed = parse_object(blob)
            except Exception as exc:
                bad += 1
                print("  !! %s(%s): %s" % (os.path.basename(path), member, exc))
                continue
            if parsed is None:
                continue
            sections, relocs, exports = parsed
            n += 1
            for num, (name, body) in sections.items():
                if name == ".text":
                    t += len(body)
            rl += len(relocs)
        print("%-16s %4d objects  %8d .text bytes  %6d relocs"
              % (os.path.basename(path), n, t, rl))
        tot_obj += n
        tot_text += t
        tot_rel += rl
    print("total: %d objects, %d .text bytes, %d relocations, %d unparsable"
          % (tot_obj, tot_text, tot_rel, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
