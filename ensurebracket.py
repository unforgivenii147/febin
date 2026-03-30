#!/data/data/com.termux/files/usr/bin/python
import sys
import pathlib

# !/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_files


MAX_QUEUE = 16


def process_file(fn):
    text = ""
    text = pathlib.Path(fn).read_text(encoding="utf-8")
    stack = []
    mapping = {")": "(", "]": "[", "}": "{"}

    for char in text:
        if char in mapping:
            top_element = stack.pop() if stack else "#"  # Use '#' as a placeholder if stack is empty
            if mapping[char] != top_element:
                return False
        elif char in {"(", "[", "{"}:
            stack.append(char)
    if not stack:
        print(fn.name)
    return not stack


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".py"])
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)

    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


if __name__ == "__main__":
    main()
