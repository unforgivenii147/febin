#!/data/data/com.termux/files/usr/bin/env python
from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from dh import get_nobinary, get_random_name
import regex as re

if TYPE_CHECKING:
    from collections.abc import Iterable

OUTPUT_DIR = Path("extracted_base64")
DATA_URL_RE = re.compile(
    r"\"data:(.*)+;base64,(?P<data>[A-Za-z0-9+/=\n\r]+)\"",
    re.IGNORECASE,
)


def decode_base64(data: str) -> bytes:
    cleaned = "".join(data.split())
    return base64.b64decode(cleaned, validate=False)


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_from_html(
    html: str,
) -> Iterable[tuple[str, bytes]]:
    for match in DATA_URL_RE.finditer(html):
        print(match.group("data"))
        #        mime = match.group("mime")
        raw_data = match.group("data")
        try:
            decoded = decode_base64(raw_data)
        except Exception:
            continue
        yield decoded


def save_asset(mime: str, data: bytes) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ext = infer_extension(mime)
    digest = content_hash(data)
    filename = f"{digest}.{ext}"
    path = OUTPUT_DIR / filename
    if not path.exists():
        path.write_bytes(data)
    return path


def main() -> None:
    root = Path.cwd()
    for html_file in iter_html_files(root):
        try:
            html = html_file.read_text(encoding="utf-8", errors="ignore")
            extract_from_html(html)
        except Exception:
            continue


"""
        for mime, data in extract_from_html(html):
            digest = content_hash(data)
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            save_asset(mime, data)
            extracted_count += 1
"""
if __name__ == "__main__":
    main()
