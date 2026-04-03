#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

if __name__ == "__main__":
    cwd = Path.cwd()
    files = list(cwd.rglob("*"))
    bcount = 0
    for path in files:
        if path.is_symlink() and not path.exists():
            try:
                path.unlink()
                bcount += 1
                print(f"{path.relative_to(cwd)}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")
    if not bcount:
        print("no broken link found.")
        sys.exit(0)
    print(f"{bcount} broken link removed.")
