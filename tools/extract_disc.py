"""Extract every file from the Forbidden Memories MODE2/2352 disc image.

Writes the files to disc/ and records LBA, size and SHA-1 for each into
config/disc.json.  The SHA-1 of SLUS_014.11 recorded here is the build oracle
that every later milestone is checked against.
"""
import hashlib
import json
import os
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BIN = (r"C:\Users\PC\Downloads\Yu-Gi-Oh! Forbidden Memories (USA)"
               r"\Yu-Gi-Oh! Forbidden Memories (USA).bin")

RAW = 2352          # bytes per raw sector
USER_OFF = 24       # Mode 2 Form 1: 12 sync + 4 header + 8 subheader
USER_LEN = 2048


class Disc:
    def __init__(self, path):
        self.f = open(path, "rb")
        self.size = os.path.getsize(path)
        self.sectors = self.size // RAW

    def sector(self, lba):
        self.f.seek(lba * RAW + USER_OFF)
        return self.f.read(USER_LEN)

    def read(self, lba, nbytes):
        n = (nbytes + USER_LEN - 1) // USER_LEN
        data = b"".join(self.sector(lba + i) for i in range(n))
        return data[:nbytes]


def parse_dir_records(data):
    out, off = [], 0
    while off < len(data):
        rec_len = data[off]
        if rec_len == 0:
            # padding to the end of the current logical sector
            off = (off // USER_LEN + 1) * USER_LEN
            if off >= len(data):
                break
            continue
        rec = data[off:off + rec_len]
        extent = struct.unpack("<I", rec[2:6])[0]
        size = struct.unpack("<I", rec[10:14])[0]
        flags = rec[25]
        name_len = rec[32]
        name = rec[33:33 + name_len]
        out.append((name, extent, size, flags))
        off += rec_len
    return out


def walk(disc, lba, length, path=""):
    entries = []
    for name, extent, size, flags in parse_dir_records(disc.read(lba, length)):
        if name in (b"\x00", b"\x01"):      # '.' and '..'
            continue
        nm = name.decode("ascii")
        full = path + "/" + nm
        if flags & 2:
            entries += walk(disc, extent, size, full)
        else:
            entries.append({"path": full, "lba": extent, "size": size})
    return entries


def main():
    bin_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BIN
    disc = Disc(bin_path)

    pvd = disc.sector(16)
    if pvd[1:6] != b"CD001":
        sys.exit("no ISO9660 PVD at LBA 16 -- is this a MODE2/2352 image?")
    root = pvd[156:190]
    root_lba = struct.unpack("<I", root[2:6])[0]
    root_len = struct.unpack("<I", root[10:14])[0]

    files = walk(disc, root_lba, root_len)

    out_dir = os.path.join(REPO, "disc")
    os.makedirs(out_dir, exist_ok=True)

    for e in files:
        # strip the ISO9660 ';1' version suffix for the on-disk name
        name = e["path"].lstrip("/").replace(";1", "")
        dest = os.path.join(out_dir, name.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        h = hashlib.sha1()
        remaining, lba = e["size"], e["lba"]
        with open(dest, "wb") as fp:
            while remaining > 0:
                chunk = disc.read(lba, min(remaining, USER_LEN * 512))
                fp.write(chunk)
                h.update(chunk)
                remaining -= len(chunk)
                lba += (len(chunk) + USER_LEN - 1) // USER_LEN
        e["sha1"] = h.hexdigest()
        print("%-24s lba=%-8d %12d B  %s" % (name, e["lba"], e["size"], e["sha1"]))

    cfg = {
        "source_bin": bin_path,
        "image_sectors": disc.sectors,
        "files": files,
    }
    os.makedirs(os.path.join(REPO, "config"), exist_ok=True)
    with open(os.path.join(REPO, "config", "disc.json"), "w") as fp:
        json.dump(cfg, fp, indent=2)
    print("\nwrote config/disc.json (%d files)" % len(files))


if __name__ == "__main__":
    main()
