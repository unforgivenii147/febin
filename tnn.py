#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from dh import get_pyfiles, mpf
import regex as re

TABCHAR = re.compile(r"\t")
SPACE = " "


def pf(path):
    content = path.read_text(encoding="utf-8")
    if not TABCHAR in content:
        print(f"no tab char in {path.name}")
    new_content = TABCHAR.sub(SPACE * 4, content)
    path.write_text(new_content, encoding="utf-8")
    print(f"{path.name} updated")


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = sorted([Path(f) for f in args] if args else get_pyfiles(cwd))
    if not files:
        print("no python files")
        sys.exit(0)
    mpf(pf, files)


if __name__ == "__main__":
    main()
