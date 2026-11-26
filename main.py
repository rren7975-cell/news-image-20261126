#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 make.fun bounty entry.

Verifies entry.png rigorously with the standard library only, delivers it
to /output/entry.png, re-inspects the delivered copy, and repeats the whole
delivery once more, requiring byte-identical results both times.

Checks on the PNG:
  * file size <= 1 MiB
  * 8-byte PNG signature
  * first chunk is IHDR declaring 1024x1024
  * every chunk's stored CRC-32 matches zlib.crc32(type + data)
  * the joined IDAT payload zlib-decompresses cleanly
  * an IEND chunk is present and is the last chunk, with no trailing bytes

Exit code 0 and an OK line on success; non-zero with a stderr message on
any failure. No network access.
"""
import hashlib
import os
import shutil
import struct
import sys
import zlib

MAX_BYTES = 1024 * 1024  # 1 MiB
EXPECTED_W = 1024
EXPECTED_H = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
OUTPUT_PATH = "/output/entry.png"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def inspect_png(path):
    """Return (size, sha256_hex) after fully validating the PNG at path."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")

    if len(data) > MAX_BYTES:
        fail(f"{path}: {len(data)} bytes exceeds the 1 MiB limit")
    if not data.startswith(PNG_SIGNATURE):
        fail(f"{path}: missing PNG signature")

    pos = len(PNG_SIGNATURE)
    first = True
    idat = bytearray()
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            fail(f"{path}: truncated chunk header at offset {pos}")
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if pos + 12 + length > len(data):
            fail(f"{path}: truncated {ctype!r} chunk at offset {pos}")
        chunk_data = data[pos + 8:pos + 8 + length]
        (stored_crc,) = struct.unpack(
            ">I", data[pos + 8 + length:pos + 12 + length])
        if zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF != stored_crc:
            fail(f"{path}: CRC mismatch in {ctype!r} chunk at offset {pos}")
        if first:
            if ctype != b"IHDR":
                fail(f"{path}: first chunk is {ctype!r}, not IHDR")
            if length != 13:
                fail(f"{path}: IHDR length {length}, expected 13")
            w, h = struct.unpack(">II", chunk_data[:8])
            if (w, h) != (EXPECTED_W, EXPECTED_H):
                fail(f"{path}: dimensions {w}x{h}, expected "
                     f"{EXPECTED_W}x{EXPECTED_H}")
            first = False
        if ctype == b"IDAT":
            idat.extend(chunk_data)
        if ctype == b"IEND":
            if pos + 12 + length != len(data):
                fail(f"{path}: trailing bytes after IEND")
            seen_iend = True
            break
        pos += 12 + length
    if not seen_iend:
        fail(f"{path}: no IEND chunk")
    try:
        zlib.decompress(bytes(idat))
    except zlib.error as exc:
        fail(f"{path}: IDAT payload does not decompress: {exc}")
    return len(data), hashlib.sha256(data).hexdigest()


def deliver_once():
    """Copy entry.png next to this file to /output/entry.png, verified."""
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    size, digest = inspect_png(src)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(OUTPUT_PATH)
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    size2, digest2 = inspect_png(dst)
    if (size, digest) != (size2, digest2):
        fail("delivered copy differs from source")
    return size, digest


def main():
    size1, digest1 = deliver_once()
    size2, digest2 = deliver_once()
    if (size1, digest1) != (size2, digest2):
        fail("two deliveries differ: program is not deterministic")
    print(f"OK: entry.png {size1} bytes sha256={digest1}")


if __name__ == "__main__":
    main()
