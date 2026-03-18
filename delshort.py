#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from sys import exit
from dh import is_binary
from fastwalk import walk_files


def process_file(fp) -> None:
    if fp.stat().st_size < 50 and len(fp.read_text().splitlines()) < 3:
        fp.unlink()
        print(f"{fp.name} removed")
    if len(fp.read_text().splitlines()) < 2:
        fp.unlink()
        print(f"{fp.name} removed")


def main() -> None:
    for pth in walk_files("."):
        path = Path(pth)
        if not is_binary(path):
            process_file(path)
        else:
            print(f"{path.name} is binary")


if __name__ == "__main__":
    exit(main())
