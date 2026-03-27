#!/data/data/com.termux/files/usr/bin/python
import sys
from pprint import pprint
from filecmp import dircmp
from pathlib import Path


if __name__ == "__main__":
    dir1 = Path.cwd()
    dir2 = Path(sys.argv[1])
    c = dircmp(dir1, dir2)
    pprint(c.report_full_closure())
