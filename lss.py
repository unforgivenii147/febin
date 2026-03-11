#!/data/data/com.termux/files/usr/bin/env python
import os
import sys
from pathlib import Path


def main():
    dir = Path.cwd()
    req = sys.argv[1].strip()
    found = []
    for f in os.listdir(dir):
        if f.startswith(req):
            found.append(f)
    for k in found:
        print(k)


if __name__ == "__main__":
    main()
