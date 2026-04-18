#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from datetime import datetime

EXCLUDED_DIRS = {".git", "__pycache__"}

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def main():
    root = Path(".")
    files = []

    for p in root.rglob("*"):
        # Skip paths that have excluded directories in their parents
        if any(part in EXCLUDED_DIRS for part in p.parts):
            continue

        if p.is_file():
            files.append(p)

    # Sort by modification time (oldest first)
    files.sort(key=lambda f: f.stat().st_mtime)

    print("\nTop 10 oldest files (excluding .git & __pycache__):\n")
    for f in files[:10]:
        mtime = f.stat().st_mtime
        print(f"{format_time(mtime)}  -  {f}")

if __name__ == "__main__":
    main()