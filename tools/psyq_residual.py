"""Account for every byte of the Psy-Q SDK region, matched or not.

`tools/psyq_sigs.py` reports how much of the SDK region it identified.  This
reports the complement: what is left over, where it is, and why it did not
match.  It also runs two SDK releases head to head, per library object, which
is the only reliable way to tell which release the game actually linked --
the RCS `$Id:` tags in the binary are identical in 4.6 and 4.7.

    py -3 tools/psyq_residual.py
    py -3 tools/psyq_residual.py --libdir DIR
    py -3 tools/psyq_residual.py --compare DIR_A DIR_B
"""
import argparse
import json
import os
import re
import struct
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psyq_sigs
from psyq_sigs import VRAM, MIN_INSNS, LIBDIR, build_signatures, match_signatures

REPO = psyq_sigs.REPO
SDK_START = 0x80073704
SDK_END = 0x80092C00

ASM = os.path.join(REPO, "asm")
LABEL = re.compile(r"^(glabel|dlabel)\s+(\S+)")
LINE = re.compile(r"^\s+/\* [0-9A-F]+ ([0-9A-F]{8}) ")


def load_payload():
    return open(os.path.join(REPO, "disc", "SLUS_014.11"), "rb").read()[0x800:]


def load_regions():
    return json.load(open(os.path.join(REPO, "config", "regions.json")))


def asm_blocks():
    """-> sorted [(addr, kind, name, end)] for glabel/dlabel blocks."""
    blocks = []
    for fn in sorted(os.listdir(ASM)):
        if not fn.endswith(".s"):
            continue
        cur = None
        for line in open(os.path.join(ASM, fn)):
            m = LABEL.match(line)
            if m:
                cur = [None, m.group(1), m.group(2), None]
                blocks.append(cur)
                continue
            m = LINE.match(line)
            if m and cur is not None:
                a = int(m.group(1), 16)
                if cur[0] is None:
                    cur[0] = a
                cur[3] = a + 4
    blocks = [b for b in blocks if b[0] is not None]
    blocks.sort(key=lambda b: b[0])
    return blocks


def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def coverage(libdir, payload, regions):
    sigs = build_signatures(libdir)
    matches, ambiguous, amb_exports = match_signatures(sigs, regions, payload)
    return sigs, matches, ambiguous


def reject_stats(libdir):
    """Why were objects dropped before matching even started?"""
    import psyq_lib
    from elftools.elf.elffile import ELFFile
    import io

    stats = defaultdict(int)
    bytes_lost = defaultdict(int)
    for fn in sorted(os.listdir(libdir)):
        path = os.path.join(libdir, fn)
        if fn.endswith(".a"):
            members = list(psyq_sigs.read_archive(path))
            native = False
        elif fn.upper().endswith((".LIB", ".OBJ")):
            members = list(psyq_lib.iter_members(path))
            native = True
        else:
            continue
        for member, blob in members:
            if native:
                parsed = psyq_lib.parse_object(blob)
                if parsed is None:
                    stats["not an object"] += 1
                    continue
                sections, relocs, exports = parsed
                tnum = next((n for n, (nm, _) in sections.items()
                             if nm == ".text"), None)
                if tnum is None:
                    stats["no .text"] += 1
                    continue
                tlen = len(sections[tnum][1])
                exp = [e for e in exports if e[1] == tnum]
                offs = set(o for (s, o) in relocs if s == tnum)
            else:
                try:
                    elf = ELFFile(io.BytesIO(blob))
                except Exception:
                    stats["not an object"] += 1
                    continue
                t = elf.get_section_by_name(".text")
                if t is None:
                    stats["no .text"] += 1
                    continue
                tlen = t.data_size
                ti = list(elf.iter_sections()).index(t)
                exp = []
                for sec in elf.iter_sections():
                    from elftools.elf.sections import SymbolTableSection
                    if isinstance(sec, SymbolTableSection):
                        for sym in sec.iter_symbols():
                            if (sym.name and not sym.name.startswith("$")
                                    and sym["st_info"]["bind"] == "STB_GLOBAL"
                                    and sym["st_shndx"] == ti):
                                exp.append(sym.name)
                offs = set()
                from elftools.elf.relocation import RelocationSection
                for sec in elf.iter_sections():
                    if isinstance(sec, RelocationSection) and \
                            sec.name in (".rel.text", ".rela.text"):
                        offs = set(r["r_offset"] for r in sec.iter_relocations())

            if tlen == 0:
                stats["empty .text"] += 1
            elif tlen < MIN_INSNS * 4:
                stats["below MIN_INSNS (%d insns)" % MIN_INSNS] += 1
                bytes_lost["below MIN_INSNS (%d insns)" % MIN_INSNS] += tlen
            elif not exp:
                stats["no exported .text symbol"] += 1
                bytes_lost["no exported .text symbol"] += tlen
            elif len(offs) * 4 >= tlen:
                stats["every word relocated"] += 1
                bytes_lost["every word relocated"] += tlen
            else:
                stats["usable"] += 1
    return stats, bytes_lost


def gap_report(libdir, payload, regions, blocks, top=40):
    sigs, matches, ambiguous = coverage(libdir, payload, regions)

    covered = merge([[a, a + m[2]] for a, m in matches.items()])
    in_sdk = [(max(s, SDK_START), min(e, SDK_END)) for s, e in covered
              if e > SDK_START and s < SDK_END]
    cov_bytes = sum(e - s for s, e in in_sdk)
    sdk_bytes = SDK_END - SDK_START

    print("SDK region %08X..%08X  %d bytes" % (SDK_START, SDK_END, sdk_bytes))
    print("matched  %7d bytes  %5.1f%%" % (cov_bytes, 100 * cov_bytes / sdk_bytes))
    print("residual %7d bytes  %5.1f%%\n"
          % (sdk_bytes - cov_bytes, 100 * (sdk_bytes - cov_bytes) / sdk_bytes))

    gaps = []
    pos = SDK_START
    for s, e in sorted(in_sdk):
        if s > pos:
            gaps.append((pos, s))
        pos = max(pos, e)
    if pos < SDK_END:
        gaps.append((pos, SDK_END))

    # attribute each gap to a library using the matched objects either side
    ordered = sorted((a, m[1]) for a, m in matches.items())
    def neighbour(addr, before):
        best = None
        for a, origin in ordered:
            if before and a < addr:
                best = origin
            if not before and a >= addr:
                return origin
        return best

    # Classify gap bytes as code or data using the disassembly's own labels.
    # Blocks can overlap (splat emits a dlabel inside a function's span for
    # inline tables), so assign each 4-byte word to the innermost block that
    # covers it rather than summing block intersections.
    owner = {}
    for a, kind, name, end in blocks:
        if end is None:
            continue
        for w in range(a, end, 4):
            prev = owner.get(w)
            if prev is None or (end - a) <= prev[1]:
                owner[w] = (kind, end - a, name)

    def kinds(s, e):
        code = data = 0
        names = []
        for w in range(s, e, 4):
            o = owner.get(w)
            if o is None:
                continue
            if o[0] == "glabel":
                code += 4
            else:
                data += 4
            if o[2] not in names:
                names.append(o[2])
        return code, data, names

    # best partial alignment of any object against the gap
    index = []
    for name, origin, words, masks, exports in sigs:
        index.append((origin, words, masks))

    print("%d residual runs, largest first:" % len(gaps))
    print("  %-19s %7s %6s %6s  %-22s %-22s %s"
          % ("range", "bytes", "code", "data", "prev matched object",
             "next matched object", "closest object (word agreement)"))
    rows = []
    for s, e in gaps:
        code, data, names = kinds(s, e)
        rows.append((e - s, s, e, code, data, names))
    rows.sort(reverse=True)

    tot_code = sum(r[3] for r in rows)
    tot_data = sum(r[4] for r in rows)

    for size, s, e, code, data, names in rows[:top]:
        n = (e - s) // 4
        tgt = struct.unpack_from("<%dI" % n, payload, s - VRAM)
        best = ("-", 0.0)
        for origin, words, masks in index:
            k = min(len(words), n)
            if k < MIN_INSNS or abs(len(words) - n) > max(8, n // 2):
                continue
            agree = sum(1 for w in range(k)
                        if (tgt[w] & masks[w]) == words[w])
            frac = agree / k
            if frac > best[1]:
                best = (origin, frac)
        print("  %08X..%08X %7d %6d %6d  %-22s %-22s %s %.0f%%"
              % (s, e, size, code, data,
                 (neighbour(s, True) or "-")[:22],
                 (neighbour(e, False) or "-")[:22],
                 best[0][:34], 100 * best[1]))

    print("\nresidual bytes inside glabel (code) blocks: %d" % tot_code)
    print("residual bytes inside dlabel (data) blocks: %d" % tot_data)
    print("residual bytes in no labelled block:        %d"
          % (sum(r[0] for r in rows) - tot_code - tot_data))

    # which libraries do the residual runs sit between?
    by_lib = defaultdict(lambda: [0, 0])
    for size, s, e, code, data, names in rows:
        p = (neighbour(s, True) or "?").split("(")[0]
        q = (neighbour(e, False) or "?").split("(")[0]
        key = p if p == q else "%s / %s" % (p, q)
        by_lib[key][0] += 1
        by_lib[key][1] += size
    print("\nresidual grouped by the libraries bracketing it:")
    for k in sorted(by_lib, key=lambda k: -by_lib[k][1]):
        print("  %-34s %4d runs  %7d bytes" % (k, by_lib[k][0], by_lib[k][1]))
    return matches, sigs


def compare(dir_a, dir_b, payload, regions):
    """Per-object head to head: which release's variant does the game contain?"""
    res = {}
    for tag, d in (("A", dir_a), ("B", dir_b)):
        sigs = build_signatures(d)
        matches, ambiguous, _ = match_signatures(sigs, regions, payload)
        hit = set(m[1] for m in matches.values())
        for s in ambiguous.values():
            hit |= s
        table = {}
        for name, origin, words, masks, exports in sigs:
            lib, member = origin.split("(")
            key = (os.path.splitext(lib)[0].lower(),
                   os.path.splitext(member.rstrip(")"))[0].lower())
            table[key] = (tuple(words), tuple(masks), origin in hit, len(words) * 4)
        res[tag] = table
        print("%s %-46s %5d objects, %5d matched"
              % (tag, d, len(table), sum(1 for v in table.values() if v[2])))

    a, b = res["A"], res["B"]
    both = set(a) & set(b)
    same_code = sum(1 for k in both if a[k][0] == b[k][0] and a[k][1] == b[k][1])
    print("\nobjects in both releases: %d   byte-identical .text: %d (%.1f%%)"
          % (len(both), same_code, 100 * same_code / len(both)))
    print("only in A: %d   only in B: %d" % (len(set(a) - both), len(set(b) - both)))

    differ = [k for k in both if a[k][0] != b[k][0] or a[k][1] != b[k][1]]
    a_only = [k for k in differ if a[k][2] and not b[k][2]]
    b_only = [k for k in differ if b[k][2] and not a[k][2]]
    agree = [k for k in differ if a[k][2] and b[k][2]]
    print("\nof the %d objects whose code differs between releases:" % len(differ))
    print("  the game contains A's variant only: %3d objects, %6d bytes"
          % (len(a_only), sum(a[k][3] for k in a_only)))
    print("  the game contains B's variant only: %3d objects, %6d bytes"
          % (len(b_only), sum(b[k][3] for k in b_only)))
    print("  both variants match (mask hides the difference): %d" % len(agree))
    if a_only:
        print("\n  A-only:", ", ".join("%s/%s" % k for k in sorted(a_only)[:25]))
    if b_only:
        print("\n  B-only:", ", ".join("%s/%s" % k for k in sorted(b_only)[:25]))

    # objects present in only one release but matched -- also decisive
    for tag, t, other in (("A", a, b), ("B", b, a)):
        uniq = [k for k in set(t) - set(other) if t[k][2]]
        if uniq:
            print("\n  matched and present only in %s: %d objects, %d bytes: %s"
                  % (tag, len(uniq), sum(t[k][3] for k in uniq),
                     ", ".join("%s/%s" % k for k in sorted(uniq)[:20])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--libdir", default=LIBDIR)
    ap.add_argument("--compare", nargs=2, metavar=("DIR_A", "DIR_B"))
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--rejects", action="store_true")
    args = ap.parse_args()

    payload = load_payload()
    regions = load_regions()

    if args.compare:
        compare(args.compare[0], args.compare[1], payload, regions)
        return 0

    if args.rejects:
        stats, lost = reject_stats(args.libdir)
        print("object triage for %s:" % args.libdir)
        for k in sorted(stats, key=lambda k: -stats[k]):
            print("  %-34s %5d objects  %8d .text bytes"
                  % (k, stats[k], lost.get(k, 0)))
        return 0

    gap_report(args.libdir, payload, regions, asm_blocks(), args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
