#!/data/data/com.termux/files/usr/bin/env python
import os
from pathlib import Path
import sys

from dh import format_size, get_files

ROOT_DIR = Path.cwd()


def get_sizes():
    sz = []
    for file_path in get_files(ROOT_DIR):
        sz.append((file_path.relative_to(ROOT_DIR), file_path.stat().st_size))
    return sz


def main() -> None:
    sizez = get_sizes()
    if not sizez:
        print("No files found or unable to access directory.")
        return
    sizez.sort(key=lambda x: x[1], reverse=True)
    top_files = sizez[:10]
    print("\n" + "=" * 60)
    print(f"TOP 10 LARGEST FILES (in {os.getcwd()})")
    print("=" * 60)
    if not top_files:
        print("No files found.")
        return
    max_path_len = max(len(str(path)) for path, size in top_files)
    max_path_len = min(max_path_len, 80)
    print(f"{'No.':<4} {'File Path':<{max_path_len}} {'Size':>12}")
    print("-" * (max_path_len + 20))
    for i, (file_path, size) in enumerate(top_files, 1):
        path_str = str(file_path)
        if len(path_str) > max_path_len:
            path_str = "..." + path_str[-(max_path_len - 3) :]
        size_str = format_size(size)
        print(f"{i:<4} {path_str:<{max_path_len}} {size_str:>12}")
    total_files = len(sizez)
    print("-" * (max_path_len + 20))
    print(f"Total files scanned: {total_files}")
    if total_files > 10:
        print(f"Showing top 10 out of {total_files} files")


def alternative_version_with_details() -> None:
    sizez = get_sizes()
    if not sizez:
        print("No files found.")
        return
    sizez.sort(key=lambda x: x[1], reverse=True)
    top_files = sizez[:10]
    print("\nTOP 10 LARGEST FILES (Detailed View)")
    print("=" * 70)
    for i, (file_path, size) in enumerate(top_files, 1):
        size_str = format_size(size)
        print(f"{i:2d}. {size_str:>10} - {file_path}")


if __name__ == "__main__":
    main()
#    alternative_version_with_details()
