#!/data/data/com.termux/files/usr/bin/python
import string
import sys
from pathlib import Path

from dh import mpf
from fastwalk import walk_files


def is_all_upper(str1):
    ln = len(str1)
    return all(str1[i] in string.ascii_uppercase for i in range(ln))


def process_file(fp):
    if not fp.exists() or fp.is_symlink():
        return None
    ext = fp.suffix[1:]
    if ext and is_all_upper(ext):
        print(fp)
        return True
    return False


def main():
    files = []
    for pth in walk_files("."):
        path = Path(pth)
        if path.is_file():
            files.append(path)
    mpf(process_file, files)


if __name__ == "__main__":
    sys.exit(main())
