#!/data/data/com.termux/files/usr/bin/python
"""Print the 30 most common 3+ letter words across text files.

Each target file is processed in a worker pool; for every file the 30 most
common lowercase words of at least three letters are printed space-separated.
Files given on the command line are used, otherwise every non-binary file in
the current directory (per :func:`dh.get_nobinary`) is scanned.

Usage::

    20most.py [file ...]
"""

import sys
from collections import Counter, deque
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from pathlib import Path

import regex as re
from dh import get_nobinary


def extract_words(text: str) -> list[str]:
    """Return all lowercase words of at least three ASCII letters in ``text``.

    Args:
        text: Arbitrary input text.

    Returns:
        List of matched words (already lowercased).
    """
    words: list[str] = re.findall(r"[a-z]{3,}", text.lower())
    return words


def process_file(path: Path) -> None:
    """Print the 30 most common qualifying words in ``path``.

    Args:
        path: Text file to analyse.
    """
    text: str = path.read_text(encoding="utf-8")
    words: list[str] = extract_words(text)
    filtered: list[str] = list(words)
    for word, _count in Counter(filtered).most_common(30):
        print(f"{word}", end=" ")


def main() -> None:
    """Dispatch :func:`process_file` across a multiprocessing pool."""
    args: list[str] = sys.argv[1:]
    cwd: Path = Path.cwd()
    files: list[Path] = [Path(arg) for arg in args] if args else get_nobinary(cwd)
    with Pool(8) as pool:
        pending: "deque[ApplyResult[None]]" = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > 16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


if __name__ == "__main__":
    main()
