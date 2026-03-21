#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path

from dh import format_size, get_files, get_size

MAX_QUEUE = 16


def process_file(fp):
    if not fp.exists():
        return False
    if not fp.stat().st_size:
        fp.unlink()
        print(f"{fp.name} removed.")
    return True


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, recursive=True)
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    diff_size = before - get_size(root_dir)
    print(f"{format_size(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
