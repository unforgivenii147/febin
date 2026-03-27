#!/data/data/com.termux/files/usr/bin/python
import sys
import pathlib


if __name__ == "__main__":
    try:
        with pathlib.Path(sys.argv[1]).open(encoding="utf-8", errors="ignore") as f:
            print(f.read(4096))
    except:
        with pathlib.Path(sys.argv[1]).open("rb") as f:
            print(f.read(4096))
