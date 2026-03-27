#!/data/data/com.termux/files/usr/bin/python
import pathlib
from sys import argv


def main():
    fn = argv[1]
    template = """#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from multiprocessing import get_context
from collections import deque
from sys import exit,argv
from dh import format_size,get_size,get_files
from termcolor import cprint

MAX_QUEUE = 16

def process_file(fp) -> None:
    nl=[]
    with open(fp,'r') as f:
        lines=f.readlines()
        for line in lines:
            if :
                nl.append(line)
    with open(fp,'w') as fo:
        for k in nl:
            fo.write(k)


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = argv[1:]
    if args:
        files = [Path(f) for f in args]
    else:
        files = get_files(cwd,recursive=True)
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
    pathlib.Path(fn).write_text(template, encoding="utf-8")
    print(f"{fn} created.")


if __name__ == "__main__":
    main()
