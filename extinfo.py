#!/data/data/com.termux/files/usr/bin/env python3
"""
python script to read an extension name via sys.argv[1] and reports:
    - how many files with that extension are there in current dir recursively and total size of them
"""

import sys
from pathlib import Path


def format_size(sb):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if sb < 1024:
            return f"{sb:.2f} {unit}"
        sb /= 1024
    return f"{sb:.2f} PB"


def main():
    ext = sys.argv[1]
    total_size = 0
    count = 0
    dir = Path.cwd()
    for f in dir.rglob(f"*.{ext}"):
        total_size += f.stat().st_size
        count += 1
    print(f"Total number of .{ext} files: {count}")
    print(f"Total size of .{ext} files: {format_size(total_size)}")


if __name__ == "__main__":
    main()
