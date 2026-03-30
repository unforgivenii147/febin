#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path


def process_file(path):
    with path.open("r+", encoding="utf-8", errors="ignore") as f:
        lines = (line for line in f if line.strip())
        content = "".join(lines)
        f.seek(0)
        f.write(content)
        f.truncate()


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else get_nobinary(cwd)
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    for f in files:
        process_file(f)
