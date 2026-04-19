#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path


def main():
    path = Path(sys.argv[1])
    template = """#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import sys,argv
from dh import get_files,mpf
def process_file(fp) -> None:
def main():
    cwd = Path.cwd()
    args = argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd)
    mpf(process_file,files)
if __name__ == "__main__":
    sys.exit(main())
"""
    path.write_text(template, encoding="utf-8")
    print(f"{path.name} created.")


if __name__ == "__main__":
    sys.exit(main())
