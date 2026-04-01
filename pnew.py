#!/data/data/com.termux/files/usr/bin/python
from sys import argv, exit
from pathlib import Path


def main():
    path = Path(argv[1])
    template = """#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from multiprocessing import get_context
from collections import deque
from sys import exit,argv
from dh import format_size,get_size,get_files
from termcolor import cprint
MAX_QUEUE = 16
def process_file(fp) -> None:
def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd,recursive=True)
    with get_context('spawn').Pool(8) as pool:
        pending=deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending)>MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    print(f"space saved : {format_size(diff_size)}")
if __name__ == "__main__":
    exit(main())
"""
    path.write_text(template, encoding="utf-8")
    print(f"{path.name} created.")


if __name__ == "__main__":
    exit(main())
