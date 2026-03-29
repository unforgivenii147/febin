#!/data/data/com.termux/files/usr/bin/python
import os
import mmap
import pathlib
from pathlib import Path
import tokenize

from dh import get_files
import regex as re


SIZE_THRESHOLD = 1 * 1024 * 1024
OLD_PRINT_RE = re.compile(r"(?m)^[ \t]*print[ \t]+[^(\n]")


def _open_source(filepath: str):
    size = pathlib.Path(filepath).stat().st_size
    f = pathlib.Path(filepath).open("rb")
    if size > SIZE_THRESHOLD:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    return f


def _read_text(filepath: str) -> str | None:
    try:
        with pathlib.Path(filepath).open(encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def _has_rich_print_import(text: str) -> bool:
    return "from rich import print" in text


def regex_flag(filepath: str) -> bool:
    text = _read_text(filepath)
    if not text:
        return False
    if _has_rich_print_import(text):
        return False
    return bool(OLD_PRINT_RE.search(text))


def tokenizer_confirm(
    filepath: str,
) -> str | None:
    try:
        src = _open_source(filepath)
        tokens = list(tokenize.tokenize(src.readline))
    except Exception:
        return None
    for i, tok in enumerate(tokens):
        if tok.type == tokenize.NAME and tok.string == "print":
            line = tok.line.rstrip()
            if line.strip() == "print":
                continue
            j = i + 1
            while j < len(tokens) and tokens[j].type in {
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
            }:
                j += 1
            if j < len(tokens) and tokens[j].string != "(":
                return line
    return None


def process_file(filepath):
    if not regex_flag(filepath):
        return None
    confirmed = tokenizer_confirm(filepath)
    if not confirmed:
        return None
    if confirmed:
        print(filepath)
    return confirmed


def main() -> None:
    cwd = Path.cwd()
    pool = get_context("spawn").Pool(8)
    for f in get_files(cwd, extensions=[".py"]):
        pool.apply_async(process_file, ((f),))
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
