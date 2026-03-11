#!/data/data/com.termux/files/usr/bin/env python
import sys
from collections import Counter, deque
from multiprocessing import Pool
from pathlib import Path

import regex as re
from dh import get_nobinary


def extract_words(text):
    return re.findall(r"[a-z]{3,}", text.lower())


def process_file(path: Path):
    text = path.read_text()
    words = extract_words(text)
    filtered = [w for w in words]
    for word, count in Counter(filtered).most_common(30):
        print(f"{word}", end=" ")


def main():
    args = sys.argv[1:]
    dir = Path.cwd()
    if args:
        files = [Path(arg) for arg in args]
    else:
        files = get_nobinary(dir)

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
