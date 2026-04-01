#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from dh import mpf, unique_path


def process_file(path):
    new_name = path.name.lower()
    if new_name == path.name:
        return
    new_path = path.with_name(new_name)
    if new_path.exists():
        new_path = unique_path(new_path)
    path.rename(new_path)


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else list(cwd.rglob("*"))
    mpf(process_file, files)
