#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from sys import exit

from dh import format_size, get_size
from fastwalk import walk_parallel


def empty_it(pth) -> None:
    with open(pth, "w") as f:
        f.write("")


def remove_it(fp) -> None:
    if not fp.is_symlink():
        fp.unlink()
    else:
        pass


def load_junk():
    with open("/sdcard/junk") as f:
        return [line.strip().lower() for line in f if line.strip()]


def main():
    dir = Path.cwd()
    before = get_size(dir)
    junk_files = load_junk()
    for pth in walk_parallel(dir):
        path = Path(pth)
        if path.is_dir():
            continue
        if any(path.name.lower() == junk for junk in junk_files) and path.exists():
            remove_it(path)
            print(path.name)
    after = get_size(dir)
    difsize = int(before - after)
    print(f"{format_size(difsize)}")


if __name__ == "__main__":
    exit(main())
