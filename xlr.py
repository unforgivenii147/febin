#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys


def process_file(fp):
    con = fp.read_text()
    nl = []
    for line in con.splitlines():
        nl.append(line + "\n\n\n\n")
    newconn = "\n".join(nl)
    fp.write_text(newconn)


if __name__ == "__main__":
    fn = Path(sys.argv[1])
    process_file(fn)
