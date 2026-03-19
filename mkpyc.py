#!/data/data/com.termux/files/usr/bin/env python
from collections import deque
import compileall
import os
from pathlib import Path
from sys import exit

from multiprocessing import Pool


def process_file(fp):
    if not fp.exists():
        return False
    compileall.compile_file(fp, legacy=True, optimize=2)
    return True


def process_dir(dr):
    compileall.compile_dir(dr, legacy=True, optimize=2)


def main():
    files = []
    dirs = []
    root_dir = Path.getcwd()
    for pth in os.listdir(root_dir):
        path = Path(os.path.join(root_dir, pth))
        if path.is_symlink():
            continue
        if path.is_file():
            files.append(path)
        if path.is_dir() and path.name != ".git":
            dirs.append(path)
    with Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, ((f),)))
            if len(pending) > 16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    for _dir in dirs:
        process_dir(root_dir)


if __name__ == "__main__":
    exit(main())
