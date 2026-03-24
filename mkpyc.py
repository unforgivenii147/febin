#!/data/data/com.termux/files/usr/bin/python
from collections import deque
import compileall
from multiprocessing import get_context
from pathlib import Path
import sys

from dh import format_size, get_files, get_size

MAX_QUEUE = 16


def process_file(fp):
    if not fp.exists():
        return False
    if ".git" in fp.parts:
        return None
    compileall.compile_file(fp, legacy=True, optimize=2)
    return True


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(root_dir, extensions=[".py"])
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(root_dir)
    print(f"space changed : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
