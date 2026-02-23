#!/data/data/com.termux/files/usr/bin/env python3
"""
python script to sort lines of a given
file and write back unique lines
- reads filename via sys.argv[1]
- updates the file in-place
- uses mmap for files larger than 10MB
"""

import sys
import os


def sort_uniq(filename):
    unsorted_lines = []
    file_size = os.path.getsize(filename)
    if file_size > 10 * 1024 * 1024:  # If file is larger than 10MB
        import mmap

        with open(filename, "r") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                lines = mm.read().decode("utf-8").splitlines()
    else:
        with open(filename, "r") as f:
            lines = f.readlines()
            # Remove whitespace and sort lines
            unique_lines = sorted(set(line.strip() for line in lines))
    # Write back unique lines to the file
    with open(filename, "w") as f:
        for line in unique_lines:
            f.write(line + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sort_uniq.py <filename>")
        sys.exit(1)
    sort_uniq(sys.argv[1])
