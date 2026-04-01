#!/data/data/com.termux/files/usr/bin/python
import os
import sys
from pathlib import Path
import operator
from collections import defaultdict


def scan_directory(path="."):
    total_size = 0
    file_count = 0
    folder_count = 0
    extensions = set()
    size_by_ext = defaultdict(int)
    for root, dirs, files in os.walk(path):
        folder_count += len(dirs)
        for filename in files:
            file_count += 1
            full_path = Path(root) / filename
            try:
                size = full_path.stat().st_size
            except OSError:
                size = 0
            total_size += size

            ext = full_path.suffix
            ext = ext.lower() if ext else "(no extension)"
            extensions.add(ext)
            size_by_ext[ext] += size
    return (
        total_size,
        file_count,
        folder_count,
        extensions,
        size_by_ext,
    )


def write_summary(filename: Path) -> None:
    (
        total_size,
        file_count,
        folder_count,
        extensions,
        size_by_ext,
    ) = scan_directory()
    with filename.open("w", encoding="utf-8") as f:
        f.write(f"total size: {total_size} bytes\n")
        f.write(f"extensions:\n{'\n   - '.join(sorted(extensions))}\n")
        f.write(f"number of files: {file_count}\n")
        f.write(f"number of folders: {folder_count}\n")
        f.write("size by extension:\n")
        for ext, size in sorted(size_by_ext.items(), key=operator.itemgetter(1), reverse=True):
            f.write(f"  {ext}: {size} bytes\n")


if __name__ == "__main__":
    outf = Path(".dirinfo")
    if outf.exists():
        print("remove .dirinfo and run again")
        sys.exit(1)
    write_summary(outf)
    print("Summary saved to .dirinfo")
