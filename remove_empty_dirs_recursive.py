#!/data/data/com.termux/files/usr/bin/env python
"""
find and remove empty dirs in current directory
"""
import os
from pathlib import Path
def main():
    count = 0
    for dirpath, dirnames, filenames in os.walk(Path.cwd(), topdown=False):
        if not dirnames and not filenames:
            print(f"removing empty dir: {dirpath}")
            os.rmdir(dirpath)
            count += 1
    print(f"total {count} empty dirs removed")
if __name__ == "__main__":
    main()
