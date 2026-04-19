#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path

from dh import is_binary

THRESHOLD = 10485760


def sort_uniq(filename):
    sz = filename.stat().st_size
    if not sz:
        return None
    if sz > THRESHOLD:
        import mmap

        with (
            Path(filename).open("r+", encoding="utf-8", errors="ignore") as f,
            mmap.mmap(
                f.fileno(),
                0,
                access=mmap.ACCESS_READ,
            ) as mm,
        ):
            lines = mm.read().decode("utf-8").splitlines()
    else:
        lines = filename.read_text(encoding="utf-8", errors="ignore").splitlines()
    unique_lines = sorted({p.strip() for p in lines if p.strip()})
    original_count = len(lines)
    new_count = len(unique_lines)
    lines_removed = original_count - new_count
    filename.write_text("\n".join(unique_lines), encoding="utf-8")
    return lines_removed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sort_uniq.py <filename>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if is_binary(path):
        print(f"{path.name} is binary")
        sys.exit(0)
    lines_removed = sort_uniq(path)
    if lines_removed > 0:
        print(f"Removed {lines_removed} duplicate lines.")
    else:
        print("No change.")
