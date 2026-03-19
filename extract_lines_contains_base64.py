#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import sys

from dh import get_nobinary


def process_file(fp):
    lines = fp.read_text(encoding="utf-8").splitlines()
    nl = []
    found = 0
    for line in lines:
        if "base64," in line:
            found += 1
            indx = line.index("base64,") + 7
            cleaned = line[indx:]
            if '"' in cleaned:
                end_indx = cleaned.index('"')
                cleaned = cleaned[:end_indx]
            nl.append(cleaned)
    if found:
        print(f"{fp.name} : {found}")
        with open("b64", "a") as f:
            f.write("\n")
            for k in nl:
                f.write(f"{k}\n")


def main():
    args = sys.argv[1:]
    root_dir = Path.cwd()
    files = [Path(arg) for arg in args] if args else get_nobinary(root_dir)
    for f in files:
        process_file(f)


if __name__ == "__main__":
    sys.exit(main())
