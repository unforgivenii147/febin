#!/data/data/com.termux/files/usr/bin/python
import json
from collections import defaultdict
from pathlib import Path
from time import perf_counter as pff
from fastwalk import walk,walk_files
from folder_hash import hash_folder
from xxhash import xxh64
from termcolor import cprint


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


def hash_folder_xx(folder_path):
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
            start=pff()
            folder_hash_h = hash_folder(str(pth))
            ht=start-pff()

            start=pff()
            folder_hash_x = hash_folder_xx(str(pth))
            hx=start-pff()
            if hx<ht:
                cprint(f"xxhash was faster {hx:.6f}:{ht:.6f}","green")
            else:
                cprint(f"hhhash was faster {hx:.6f}:{ht:.6f}","cyan")
            if folder_hash_h:
                folder_hashes[str(folder_hash_h)].append(str(pth))
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
