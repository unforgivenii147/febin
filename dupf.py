#!/data/data/com.termux/files/usr/bin/env python
from collections import defaultdict
import os
from pathlib import Path
from file_hash import hash_file


def find_duplicates():
    root_dir=Path.cwd()
    files_by_hash = defaultdict(list)
    duplicate_count = 0
    for path in root_dir.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_file():
            files_by_hash[file_hash(path)].append(path)
    for (
            hash,
            paths,
    ) in files_by_hash.items():
        if len(paths) > 1:
            duplicate_count += len(paths) - 1
            print(f"Duplicate files found for hash {hash}:")
            for file_path in paths:
                relative_path = file_path.relative_to(root_dir)
                print(f"  {relative_path}")
            print()


if __name__ == "__main__":
    find_duplicates()
