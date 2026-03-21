#!/data/data/com.termux/files/usr/bin/python
from collections import defaultdict
from pathlib import Path

from file_hash import hash_file
from termcolor import cprint


def find_duplicates():
    root_dir = Path.cwd()
    files_by_hash = defaultdict(list)
    duplicate_count = 0
    for path in root_dir.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            continue
        if path.is_file():
            files_by_hash[hash_file(path)].append(path)
    for (
            hash,
            paths,
    ) in files_by_hash.items():
        if len(paths) > 1:
            duplicate_count += len(paths) - 1
            print(f"hash {hash}:")
            for file_path in paths:
                relative_path = file_path.relative_to(root_dir)
                cprint(f"  {relative_path}", "cyan")
            print()


if __name__ == "__main__":
    find_duplicates()
