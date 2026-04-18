#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from binaryornot import is_binary
from dh import get_filez
from termcolor import cprint


def process_file(path):
    if is_binary(path):
        return
    removed = 0
    with path.open("r+", encoding="utf-8", errors="ignore") as f:
        orig_len = len(f)
        lines = (line for line in f if line.strip())
        final_len = len(lines)
        removed = orig_len - final_len
        if removed:
            print(f"{path.name}", end=" | ")
            cprint(f"{removed}", "blue")
            content = "".join(lines)
            f.seek(0)
            f.write(content)
            f.truncate()
        else:
            print(f"{path.name}", end=" | ")
            cprint("NO CHANGE", "grey")


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    if args:
        files = [Path(p) for p in args]
        for f in files:
            process_file(f)
    else:
        for f in get_filez(cwd):
            if not is_binary(f):
                process_file(f)
