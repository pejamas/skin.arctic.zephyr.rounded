"""List the texture directory of a Kodi Textures.xbt: path + frame dimensions.

Parses only the header/directory, not the pixel payload, so no LZO or DXT decoder is
needed. Field order follows Kodi's XBTFReader::ReadHeader.

Usage:  python .tools/xbt_list.py [substring-filter]
"""

import os
import struct
import sys

XBT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "media", "Textures.xbt")

FRAME = 12 + 16 + 4 + 8  # w,h,format | packed,unpacked | duration | offset


def read_directory(xbt=XBT):
    """Return [(path, width, height)] for every texture in the bundle."""
    with open(xbt, "rb") as f:
        blob = f.read()

    if blob[0:4] != b"XBTF":
        raise SystemExit("not an XBT bundle: magic=%r" % blob[0:4])

    off = 5
    (nfiles,) = struct.unpack_from("<I", blob, off)
    off += 4

    rows = []
    for _ in range(nfiles):
        path = blob[off:off + 256].split(b"\x00")[0].decode("utf-8", "replace")
        off += 256
        (_loop, nframes) = struct.unpack_from("<II", blob, off)
        off += 8
        if nframes:
            (w, h, _fmt) = struct.unpack_from("<III", blob, off)
            rows.append((path, w, h))
        off += FRAME * nframes

    sane = sum(1 for _, w, h in rows if 0 < w <= 8192 and 0 < h <= 8192)
    if sane < len(rows) * 0.9:
        raise SystemExit("dimensions look wrong - field order mismatch, do not trust output")
    return rows


def median_aspect_by_category(prefix):
    """Median width/height per immediate subfolder under `prefix` (e.g. flags/video/color/)."""
    cats = {}
    for path, w, h in read_directory():
        if not path.startswith(prefix) or not h:
            continue
        rest = path[len(prefix):]
        if "/" not in rest:
            continue
        cats.setdefault(rest.split("/")[0], []).append(w / float(h))
    return dict((c, sorted(v)[len(v) // 2]) for c, v in cats.items())


if __name__ == "__main__":
    filt = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    rows = read_directory()
    print("parsed %d entries" % len(rows))
    for path, w, h in sorted(rows):
        if filt in path.lower():
            print("%-70s %4dx%-4d  %.3f:1" % (path, w, h, w / float(h) if h else 0))
