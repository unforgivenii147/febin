import sys
from pathlib import Path

if __name__ == "__main__":
    try:
        with Path(sys.argv[1]).open(encoding="utf-8", errors="ignore") as f:
            print(f.read(4096))
    except:
        with Path(sys.argv[1]).open("rb") as f:
            print(f.read(4096))
