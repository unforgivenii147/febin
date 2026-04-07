#!/data/data/com.termux/files/usr/bin/python
"""
split_nltk.py
Split a text file into parts up to max_chars (default 5000), preferring sentence boundaries
(using NLTK). If a single sentence exceeds the limit, fall back to splitting by words.
Skip the file if it appears binary or has fewer than max_chars characters.
Output file naming: <basename>_(<counter>)<extension>  (counter starts at 1)
Requires: nltk (pip install nltk)
"""

import sys
from pathlib import Path

import nltk
import regex as re
from binaryornot import is_binary
from nltk.tokenize import sent_tokenize

DEFAULT_MAX = 5000
BINARY_SAMPLE = 4096  # bytes to sample to detect binary


def split_long_by_words(segment: str, max_chars: int = DEFAULT_MAX):
    words = re.findall(r"\S+\s*", segment, flags=re.S)
    parts = []
    cur = ""
    for w in words:
        if len(cur) + len(w) <= max_chars:
            cur += w
        else:
            if cur:
                parts.append(cur)
            if len(w) > max_chars:
                # Forced break of an extremely long token
                i = 0
                while i < len(w):
                    slice_ = w[i : i + max_chars]
                    parts.append(slice_)
                    i += max_chars
                cur = ""
            else:
                cur = w
    if cur:
        parts.append(cur)
    return parts


def chunk_text_with_nltk(text: str, max_chars: int):
    sentences = sent_tokenize(text)  # returns list of sentence strings (no trailing whitespace)
    chunks = []
    cur = ""
    for sent in sentences:
        # ensure there's a single space between sentences when joining
        sent_to_add = sent
        if cur and not cur.endswith((" ", "\n")) and not sent_to_add.startswith((" ", "\n")):
            sent_to_add = " " + sent_to_add
        if len(cur) + len(sent_to_add) <= max_chars:
            cur += sent_to_add
        else:
            if cur:
                chunks.append(cur)
                cur = ""
            if len(sent_to_add) <= max_chars:
                cur = sent_to_add
            else:
                parts = split_long_by_words(sent_to_add, max_chars)
                for p in parts[:-1]:
                    chunks.append(p)
                cur = parts[-1] if parts else ""
    if cur:
        chunks.append(cur)
    return chunks


def write_chunks(chunks, input_path: Path, out_dir: Path, encoding: str):
    stem = input_path.stem
    ext = "".join(input_path.suffixes)  # preserve multi-suffix like .tar.gz
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(chunks, start=1):
        out_name = f"{stem}_({i}){ext}"
        out_path = out_dir / out_name
        out_path.write_text(chunk, encoding=encoding)
        print(f"Wrote {out_path} ({len(chunk)} chars)")


def main():
    inp = Path(sys.argv[1])
    if not inp.exists() or not inp.is_file() or is_binary(inp):
        print(f"Input file not found or is binary: {inp.name}", file=sys.stderr)
        sys.exit(2)
    try:
        text = inp.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"Failed to read input file with encoding {args.encoding}: {exc}", file=sys.stderr)
        sys.exit(2)
    if len(text) < DEFAULT_MAX:
        print(f"File has fewer than {DEFAULT_MAX} characters ({len(text)}). Skipping.", file=sys.stderr)
        sys.exit(0)
    chunks = chunk_text_with_nltk(text, DEFAULT_MAX)
    if not chunks:
        print("No chunks produced. Exiting.", file=sys.stderr)
        sys.exit(0)
    out_dir = inp.parent
    write_chunks(chunks, inp, out_dir, "utf-8")
    print(f"Finished: {len(chunks)} files created")


if __name__ == "__main__":
    main()
