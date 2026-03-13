#!/data/data/com.termux/files/usr/bin/env python
import sys
from pathlib import Path


def process_file(path, text):
    content = path.read_text()
    target = "Requires-Dist: " + text
    if target in content:
        lines = content.splitlines()
        nl = []
        for line in lines:
            if target not in line:
                nl.append(line)
        newcontent = "\n".join(nl)
        path.write_text(newcontent, encoding="utf-8")
        print(f"{path.parent.name} updated.")


if __name__ == "__main__":
    dir = Path("/data/data/com.termux/files/usr/lib/python3.12/site-packages")
    target = sys.argv[1]
    for path in dir.rglob("METADATA"):
        process_file(path, target)
