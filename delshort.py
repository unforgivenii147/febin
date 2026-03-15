#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from sys import exit
from time import perf_counter

from fastwalk import walk_files


def process_file(fp) -> None:
    if fp.stat().st_size < 100:
        fp.unlink()
    with open(fp) as f:
        lines = f.readlines()
        if len(lines) < 3:
            fp.unlink()
            print(f"{fp.name} removed")


def main() -> None:
    start = perf_counter()
    for pth in walk_files("."):
        path = Path(pth)
        process_file(path)

    print(f"{perf_counter() - start} seconds")


if __name__ == "__main__":
    exit(main())
