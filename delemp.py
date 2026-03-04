#!/data/data/com.termux/files/usr/bin/env python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path
from sys import exit
from time import perf_counter

from dh import format_size, get_nobinary, get_size, is_binary
from fastwalk import walk_files
from termcolor import cprint


def process_file(filepath):
    if filepath.is_symlink():
        return False
    try:
        before = get_size(filepath)
        print(f"[OK] {filepath.name}", end=" ")
        with filepath.open(
                "r+",
                encoding="utf-8",
                errors="ignore",
        ) as f:
            lines = (line for line in f if line.strip())
            content = "".join(lines)
            f.seek(0)
            f.write(content)
            f.truncate()
        after = get_size(filepath)
        cprint(f"{format_size(before-after)}", "cyan")
        return before != after
    except OSError:
        return False


def main():
    args = sys.argv[1:]
    if args:
        files = [Path(arg) for arg in args]
    else:
        dir = Path.cwd()
        start_size = get_size(dir)
        files = get_nobinary(dir)
    results = []
    with Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, ((f), )))
            if len(pending) > 16:
                results.append(pending.popleft().get())
        while pending:
            results.append(pending.popleft().get())
    changed = 0
    for r in results:
        if r:
            changed += 1
    end_size = get_size(dir)
    print("space freed: ", end=" ")
    cprint(f"{format_size(start_size - end_size)}", "cyan")


if __name__ == "__main__":
    sys.exit(main())
