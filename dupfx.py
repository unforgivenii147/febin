#!/data/data/com.termux/files/usr/bin/python
from collections import defaultdict
from pathlib import Path

from file_hash import hash_file


def remove_duplicates() -> None:
    root_dir = Path.cwd()
    files_by_hash = defaultdict(list)
    duplicate_count = 0
    deleted_count = 0
    for path in root_dir.rglob("*"):
        if path.is_file():
            files_by_hash[hash_file(path)].append(path)
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
                filetodel.unlink()
        else:
            continue

    print(f"dup found: {deleted_count}")


if __name__ == "__main__":
    remove_duplicates()
