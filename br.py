#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_size, get_files, format_size
from termcolor import cprint
from brotlicffi import compress


MAX_QUEUE = 16


def process_file(fp):
    fp = Path(fp)
    if not fp.exists() or fp.suffix == ".br":
        return
    before = get_size(fp)
    data = fp.read_bytes()
    outfile = fp.with_suffix(fp.suffix + ".br")
    cdata = compress(data, quality=11)
    outfile.write_bytes(cdata)
    fp.unlink()
    after = get_size(outfile)
    ratio = round((before / after) * 100, 3)
    cprint(f"{outfile.name}", "green", end=" | ")
    cprint(f"{ratio} | {format_size(before)} -> {format_size(after)}", "cyan")
    del data, cdata, outfile, before, after, ratio
    return


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd, recursive=True)
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    diff_size = before - get_size(cwd)
    print(f"space reduced: {format_size(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
