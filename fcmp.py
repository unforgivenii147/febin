#!/data/data/com.termux/files/usr/bin/python
from filecmp import dircmp
from pathlib import Path
from pprint import pprint
import sys

if __name__ == "__main__":
    dir1 = Path.cwd()
    dir2 = Path(sys.argv[1])
    c = dircmp(dir1, dir2)
    pprint(c.report_full_closure())
