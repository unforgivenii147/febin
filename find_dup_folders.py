#!/data/data/com.termux/files/usr/bin/python
import json
from collections import defaultdict
from pathlib import Path

from fastwalk import walk
from folder_hash import hash_folder


def is_nested(path1: Path, path2: Path) -> bool:
    try:
        path1.resolve().relative_to(path2.resolve())
        return True
    except ValueError:
        pass
    try:
        path2.resolve().relative_to(path1.resolve())
        return True
    except ValueError:
        pass
    return False


def hash_folder(folder_path):
    hasher = xxh64()
    files = []
    for pth in walk_files(str(folder_path)):
        path = Path(pth)
        if path.is_symlink():
            continue
        if path.is_file():
            files.append(path)
    if not files:
        return ""
    for file in sorted(files):
        rel = file.relative_to(folder_path)
        hasher.update(str(rel).encode())
        try:
            with file.open("rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
        except OSError:
            continue
    return hasher.hexdigest()


def find_duplicate_folders(cwd):
    folder_hashes = defaultdict(list)
    for ppth in walk(cwd):
        pth = Path(ppth)
        if pth.is_dir():
            folder_hash = hash_folder(str(pth), hash_algorithm="sha256")
            if folder_hash:
                folder_hashes[str(folder_hash)].append(str(pth))
    return {h: paths for h, paths in folder_hashes.items() if len(paths) > 1}


if __name__ == "__main__":
    cwd = "."
    duplicates = find_duplicate_folders(cwd)
    if duplicates:
        print("Duplicate folder groups:")
        for hsh, paths in duplicates.items():
            print(f"\nGroup (Hash: {hsh}):")
            for path in paths:
                print(f"  - {path}")
        cleaned = defaultdict(list)
        for hsh, paths in duplicates.items():
            for i in range(len(paths)):
                for j in range(i + 1, len(paths)):
                    p1 = Path(paths[i])
                    p2 = Path(paths[j])
                    if not is_nested(p1, p2):
                        cleaned[hsh].append(str(p1))
        with Path("/sdcard/dupdirs.json").open("w", encoding="utf-8") as fo:
            json.dump(cleaned, fo)
    else:
        print("No duplicate folders found.")
