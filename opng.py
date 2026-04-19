#!/data/data/com.termux/files/usr/bin/python

import subprocess
from pathlib import Path

from dh import get_filez
from termcolor import cprint


def process_file(file_path):
    try:
        subprocess.run(
            ["optipng", "-o7", str(file_path)],
            check=True,
        )
        return True, file_path
    except subprocess.CalledProcessError as e:
        return False, file_path, str(e)


def main():
    cwd = Path.cwd()
    png_num = len([p for p in cwd.rglob("*.png") if not p.is_symlink()])
    c = 0
    for path in get_filez(cwd):
        if path.is_symlink():
            continue
        if path.suffix.lower() != ".png":
            continue
        cprint(f"{c}/{png_num}|remained:{png_num - c}", "cyan")
        process_file(path)
        c += 1


if __name__ == "__main__":
    main()
