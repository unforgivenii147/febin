#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path

if __name__ == "__main__":
    fn = Path(sys.argv[1])
    lines = fn.read_text(encoding="utf-8").splitlines()
    nl = [line for line in lines if line.strip() and ("mkv" in line or "mp4" in line) and "480" in line]
    if nl:
        fn.write_text("\n".join(nl), encoding="utf-8")
    print(f"{len(nl)} links found.")
