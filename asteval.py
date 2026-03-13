#!/data/data/com.termux/files/usr/bin/env python
import ast
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_size, move_file

MAX_QUEUE = 16

dir = Path.cwd()
ok_dir = Path(f"{dir}/OK")
err_dir = Path(f"{dir}/ERROR")
ok_dir.mkdir(exist_ok=True)
err_dir.mkdir(exist_ok=True)


def process_file(fp) -> None:
    content = fp.read_text()
    try:
        ast.parse(content)
        newpath = ok_dir / fp.name
        move_file(fp, newpath)
        print(f"{fp.name} --> {newpath}")
    except:
        newpath = err_dir / fp.name
        move_file(fp, newpath)
        print(f"{fp.name} --> {newpath}")


def main():
    before = get_size(dir)
    args = sys.argv[1:]
    files = [Path(f)
             for f in args] if args else [Path(p) for p in dir.glob("*.py")]

    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f, )))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
