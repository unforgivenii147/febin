#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import regex as re
from dh import format_size, get_files, get_size
from termcolor import cprint

MAX_QUEUE = 16


def process_file(fp) -> None:
    before = get_size(fp)
    src = fp.read_text(encoding="utf-8")
    pattern = re.compile(r"<!--[\s\S]*?-->", re.MULTILINE)
    out = pattern.sub("", src)
    if out != src:
        fp.write_text(out, encoding="utf-8")
    after = get_size(fp)
    print(f"[OK] {fp.name} ", end="")
    diffsize = before - after
    cprint(f"{format_size(diffsize)}", "cyan")


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = ([Path(f) for f in args] if args else get_files(
        root_dir,
        recursive=True,
        extensions=[".html", ".htm"],
    ))
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f, )))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(root_dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
