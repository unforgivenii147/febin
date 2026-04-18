#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from datetime import datetime

EXCLUDED_DIRS = {".git", "__pycache__"}


def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def main():
    cwd = Path.cwd()
    files = []
    opt = sys.argv[1] if len(sys.argv) > 1 else "-g"
    if opt == "-g":
        for p in cwd.glob("*"):
            if any(part in EXCLUDED_DIRS for part in p.parts):
                continue

            if p.is_file() or p.is_dir():
                files.append(p)
    elif opt == "-r":
        for p in cwd.rglob("*"):
            if any(part in EXCLUDED_DIRS for part in p.parts):
                continue

            if p.is_file():
                files.append(p)

    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    print("\nTop 10 oldest files (excluding .git & __pycache__):\n")
    for f in files[:1000]:
        mtime = f.stat().st_mtime
        print(f"{format_time(mtime)}  -  {f.relative_to(cwd)}")


if __name__ == "__main__":
    main()
