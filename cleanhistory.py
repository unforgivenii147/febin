#!/data/data/com.termux/files/usr/bin/python
"""Strip noisy ``cd`` entries from the bash history file.

Lines produced by the shell's directory-tracking prompt (which contain
``cd "`printf``) are dropped; everything else is written back unchanged.
"""

from pathlib import Path

if __name__ == "__main__":
    fn: str = "/data/data/com.termux/files/home/.bash_history"
    nl: list[str] = []
    with Path(fn).open(encoding="utf-8") as f:
        nl.extend(line for line in f if 'cd "`printf' not in line)
    with Path(fn).open("w", encoding="utf-8") as fo:
        fo.writelines(nl)
    print("done.")
