#!/data/data/com.termux/files/usr/bin/python
#!/data/data/com.termux/files/usr/bin/env python

import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

from brotlicffi import decompress
from dh import format_size, get_files, get_size
from termcolor import cprint

MAX_QUEUE = 16


def process_file(fp):
    fp = Path(fp)
    if not fp.exists() or fp.suffix != ".br":
        return
    before = get_size(fp)
    data = fp.read_bytes()
    outfile = Path(str(fp).replace(".br", ""))
    udata = decompress(data)
    outfile.write_bytes(udata)
    fp.unlink()
    after = get_size(outfile)
    ratio = round((before / after) * 100, 3)
    cprint(f"{outfile.name}", "green", end=" | ")
    cprint(f"{ratio}", "cyan")
    del data, udata, outfile, before, after, ratio
    return


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, recursive=True)
    with Pool(8) as pool:
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
