#!/data/data/com.termux/files/usr/bin/python
"""
Script to delete a range of lines from a file.
Gets filename and line numbers (x, y) from user input.
Deletes lines from x to y (inclusive) and updates file in place.
"""

import sys
from pathlib import Path


def delete_lines_from_file():
    filename = sys.argv[1]
    path = Path(filename)
    lines = path.read_text(encoding="utf-8").splitlines()

    if len(sys.argv) == 4:
        fromline = int(sys.argv[2])
        toline = int(sys.argv[3])

    if len(sys.argv) == 3:
        fromline = int(sys.argv[2])
        toline = len(lines)

    new_lines = lines[: fromline - 1] + lines[toline:]
    path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"remained: {len(new_lines)} lines")


if __name__ == "__main__":
    delete_lines_from_file()
