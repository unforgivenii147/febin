#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
import compileall
from collections import deque
from multiprocessing import get_context

from dh import get_size, get_files, format_size


MAX_QUEUE = 16
REMOVE_ORIG = False


def process_file(fp):
    if not fp.exists():
        return False
    if ".git" in fp.parts:
        return None
    compileall.compile_file(fp, legacy=True, optimize=2)
    if REMOVE_ORIG:
        fp.unlink()
    return True


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".py"])
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    print(f"space changed : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
