#!/data/data/com.termux/files/usr/bin/python
from collections import Counter, deque
from multiprocessing import Pool
from pathlib import Path
import sys

from dh import get_nobinary
import regex as re


def extract_words(text):
    return re.findall(r"[a-z]{3,}", text.lower())


def process_file(path: Path):
    text = path.read_text()
    words = extract_words(text)
    filtered = list(words)
    for word, _count in Counter(filtered).most_common(30):
        print(f"{word}", end=" ")


def main():
    args = sys.argv[1:]
    root_dir = Path.cwd()
    files = [Path(arg) for arg in args] if args else get_nobinary(root_dir)

    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > 16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


if __name__ == "__main__":
    main()
