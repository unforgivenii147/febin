#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from sys import exit

from dh import format_size, get_size
from fastwalk import walk_parallel


def empty_it(pth) -> None:
    Path(pth).write_text("", encoding="utf-8")


def remove_it(fp) -> None:
    if not fp.is_symlink():
        fp.unlink()


def load_junk():
    with open("/sdcard/junk", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    junk_files = load_junk()
    for pth in walk_parallel(root_dir):
        path = Path(pth)
        if path.is_dir():
            continue
        if any(path.name.lower() == junk for junk in junk_files) and path.exists():
            remove_it(path)
            print(path.name)
    after = get_size(root_dir)
    difsize = int(before - after)
    print(f"{format_size(difsize)}")


if __name__ == "__main__":
    exit(main())
