#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path

if __name__ == "__main__":
    fn = "/data/data/com.termux/files/home/.bash_history"
    nl = []
    with Path(fn).open(encoding="utf-8") as f:
        nl.extend(line for line in f if 'cd "`printf' not in line)
    with Path(fn).open("w", encoding="utf-8") as fo:
        fo.writelines(nl)
    print("done.")
