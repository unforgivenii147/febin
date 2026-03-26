#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import sys


def main():
    root_dir = Path.cwd()
    req = sys.argv[1].strip()
    found = [f for f in os.listdir(root_dir) if f.startswith(req)]
    for k in found:
        print(k)


if __name__ == "__main__":
    main()
