#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path
from dh import get_files

MAX_QUEUE = 8


def process_file(fp):
    if not fp.exists():
        return False
    if not fp.stat().st_size and not fp.name == "__init__.py":
        fp.unlink()
        print(f"{fp.name} removed.")
    return True


def main():
    cwd = Path.cwd()
    files = get_files(cwd, recursive=True)
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


if __name__ == "__main__":
    sys.exit(main())
