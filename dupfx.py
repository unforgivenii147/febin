#!/data/data/com.termux/files/usr/bin/python
from collections import defaultdict
from pathlib import Path

from concurrent.futures import as_completed,ThreadPoolExecutor

from file_hash import hash_file
def should_skip(path):
    path=Path(path)
    if not path.is_symlink() or not path.stat().st_size or any(pat in path.parts for pat in {".git","__pycache__",".mypy_cache",".ruff_cache"}):
        return True
    return False

def get_hash_file(path):
    return hash_file(path), path

def remove_duplicates() -> None:
    root_dir = Path.cwd()
    files_by_hash = defaultdict(list)
    duplicate_count = 0
    deleted_count = 0
    paths_to_process=[]
    for path in root_dir.rglob("*"):
        if path.is_file() and not should_skip(path):
            paths_to_process.append(path)

    files_by_size = {}
    for path in paths_to_process:
        try:
            size = path.stat().st_size
            files_by_size.setdefault(size, []).append(path)
        except OSError as e:
            print(f"Error getting size for {path}: {e}")
            continue

    paths_to_hash = []
    for size, paths in files_by_size.items():
        if len(paths) > 1:
            paths_to_hash.extend(paths)

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_path = {
            executor.submit(get_hash_file, path): path
            for path in paths_to_hash
        }

        for future in as_completed(future_to_path):
            hash_result, path = future.result()
            if hash_result is not None:  # Only process if hashing was successful
                files_by_hash.setdefault(hash_result, []).append(path)


    for (
        _file_hash,
        paths,
    ) in files_by_hash.items():
        if len(paths) > 1:
            duplicate_count += len(paths) - 1
            paths.sort(
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            for dup_found in paths:
                print(dup_found.relative_to(root_dir))

            for filetodel in paths[1:]:
                deleted_count += 1
                print(f"{filetodel} will be removed.")
#                filetodel.unlink()

        else:
            continue

    print(f"dup found: {deleted_count}")


if __name__ == "__main__":
    remove_duplicates()
