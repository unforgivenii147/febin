#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import sys


def process_file(path, text):
    content = path.read_text()
    target = "Requires-Dist: " + text
    if target in content:
        print(path.parent.name)


if __name__ == "__main__":
    root_dir = Path("/data/data/com.termux/files/usr/lib/python3.12/site-packages")
    target = sys.argv[1]
    for path in root_dir.rglob("METADATA"):
        process_file(path, target)
