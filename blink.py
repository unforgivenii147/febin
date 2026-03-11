#!/data/data/com.termux/files/usr/bin/env python
import os
from pathlib import Path

from dh import get_files

if __name__ == "__main__":
    dir = Path.cwd()
    files = get_files(dir)
    bcount = 0
    for path in files:
        if path.is_symlink() and not path.exists():
            try:
                path.unlink()
                bcount += 1
                print(f"{os.path.relpath(path)}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")
    if not bcount:
        print("no broken link found.")
