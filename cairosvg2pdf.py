#!/data/data/com.termux/files/usr/bin/python
from collections import deque
from multiprocessing import get_context
from pathlib import Path
import sys

import cairosvg
from dh import format_size, get_files, get_size
from termcolor import cprint

MAX_QUEUE = 16


def process_file(path):
    outfile = path.with_suffix(".pdf")
    cairosvg.svg2pdf(url=str(path), write_to=str(outfile))


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".svg"])
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    cprint(f"space saved : {format_size(diff_size)}", "cyan")


if __name__ == "__main__":
    main()
