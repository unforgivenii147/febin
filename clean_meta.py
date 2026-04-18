#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import deque
from multiprocessing import Pool
from os import scandir as _scandir
from pathlib import Path

import regex as re

from dhh import get_files

SKIP_DIRS = {".git", "__pycache__"}


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


MAX_QUEUE = 16
image_re = re.compile(
    r"((.*)+ image::(.*)+)|((.*)+:target:(.*)+)|((.*)+:alt:(.*)+)",
    re.I,
)
blank_line = "\n"


def process_file(path):
    content = path.read_text()
    c = 0
    lines = content.splitlines()
    nl = []
    for line in lines:
        matc = image_re.match(line)
        if not matc:
            nl.append(line)
        else:
            nl.append(blank_line)
            print(line)
            c += 1
    if not c:
        return
    newcontent = "\n".join(nl)
    path.write_text(newcontent, encoding="utf-8")
    print(f"{path.relative_to(path.parent)} updated.")


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    args = sys.argv[1:]
    files = (
        [Path(f) for f in args]
        if args
        else get_files(
            cwd,
            recursive=True,
            extensions=[".metadata", ".md"],
        )
    )
    metafiles = list(cwd.rglob("METADATA"))
    if metafiles:
        files.extend(metafiles)
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - gsz(cwd)
    print(f"space saved : {fsz(diff_size)}")


if __name__ == "__main__":
    main()
