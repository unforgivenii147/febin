#!/data/data/com.termux/files/usr/bin/python
"""
python script to read an extension name via sys.argv[1] and reports:
    - how many files with that extension are there in current dir recursively and total size of them
"""

import sys
from pathlib import Path

from dh import format_size


def main():
    ext = sys.argv[1]
    total_size = 0
    count = 0
    root_dir = Path.cwd()
    for f in root_dir.rglob(f"*.{ext}"):
        total_size += f.stat().st_size
        count += 1
    print(f"Total number of .{ext} files: {count}")
    print(f"Total size of .{ext} files: {format_size(total_size)}")


if __name__ == "__main__":
    main()
