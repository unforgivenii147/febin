#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path

from dh import xorhash


def find_dups(root):
    file_hashes = {}
    for dirpath, _, files in os.walk(root):
        for name in files:
            full_path = os.path.join(dirpath, name)
            try:
                h = xorhash(full_path)
                file_hashes.setdefault(h, []).append(full_path)
            except Exception as e:
                print(f"Error hashing {full_path}: {e}")
    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


if __name__ == "__main__":
    root_dir = Path.cwd()
    dupes = find_dups(root_dir)

    for h, paths in dupes.items():
        print(f"Duplicate group ({h}):")
        for p in paths:
            print("  ", p)
