#!/usr/bin/env python3
"""Deliver the news-image-20261126 entry to /output/entry.png.

Reads entry.png from beside this file, validates it end to end with the
standard library only, copies it to the output directory, validates the
copy again, and then does the whole delivery a second time, requiring
both runs to produce identical bytes (the bounty runs the program
twice and requires identical output).

Validation covers: the file is at most 1 MiB; it starts with the PNG
signature; its first chunk is an IHDR declaring 1024x1024; every chunk
carries a CRC-32 that matches its type and data; the joined IDAT
payload decompresses cleanly; an IEND chunk is present and is the last
thing in the file, with no trailing bytes.

Exit code 0 with an OK line on success; non-zero with a message on
stderr on any failure. No network access, deterministic.
"""
import hashlib
import os
import shutil
import struct
import sys
import zlib

LIMIT_BYTES = 1024 * 1024
SIZE_W, SIZE_H = 1024, 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


class EntryError(Exception):
    """Raised for any validation or delivery problem."""


def read_chunks(data):
    """Yield (type, payload) for each chunk of a PNG byte string.

    Stops at IEND (which must be the last chunk) and raises EntryError
    on any structural problem: bad signature, truncation, CRC mismatch,
    missing IEND, or bytes after IEND.
    """
    if not data.startswith(MAGIC):
        raise EntryError("missing PNG signature")
    pos = len(MAGIC)
    while pos < len(data):
        if pos + 8 > len(data):
            raise EntryError(f"truncated chunk header at offset {pos}")
        (size,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        end = pos + 12 + size
        if end > len(data):
            raise EntryError(f"truncated {kind!r} chunk at offset {pos}")
        payload = data[pos + 8:pos + 8 + size]
        (crc,) = struct.unpack(">I", data[pos + 8 + size:end])
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise EntryError(f"CRC mismatch in {kind!r} chunk at offset {pos}")
        yield kind, payload
        pos = end
        if kind == b"IEND":
            if pos != len(data):
                raise EntryError("trailing bytes after IEND")
            return
    raise EntryError("no IEND chunk")


def validate_png(path):
    """Return (size, sha256) of the PNG at path after full validation."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        raise EntryError(f"cannot read {path}: {exc}")
    if len(data) > LIMIT_BYTES:
        raise EntryError(f"{path}: {len(data)} bytes exceeds the 1 MiB limit")
    chunks = list(read_chunks(data))
    if not chunks or chunks[0][0] != b"IHDR":
        raise EntryError(f"{path}: first chunk is not IHDR")
    width, height = struct.unpack(">II", chunks[0][1][:8])
    if (width, height) != (SIZE_W, SIZE_H):
        raise EntryError(f"{path}: dimensions {width}x{height}, "
                         f"expected {SIZE_W}x{SIZE_H}")
    try:
        zlib.decompress(b"".join(p for k, p in chunks if k == b"IDAT"))
    except zlib.error as exc:
        raise EntryError(f"{path}: IDAT payload does not decompress: {exc}")
    return len(data), hashlib.sha256(data).hexdigest()


def deliver():
    """Copy entry.png to the output directory, verified both sides."""
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    before = validate_png(source)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    after = validate_png(target)
    if before != after:
        raise EntryError("delivered copy differs from source")
    return before


def run():
    first = deliver()
    second = deliver()
    if first != second:
        raise EntryError("two deliveries differ: program is not deterministic")
    size, digest = first
    print(f"OK: entry.png {size} bytes sha256={digest}")


if __name__ == "__main__":
    try:
        run()
    except EntryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
