#!/data/data/com.termux/files/usr/bin/python
import subprocess
from multiprocessing import get_context
from pathlib import Path

from dh import get_filez


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
    for path in get_filez(cwd):
        if path.is_symlink():
            continue
        if not path.suffix.lower() == ".png":
            continue
        process_file(path)


if __name__ == "__main__":
    main()
