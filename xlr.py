#!/data/data/com.termux/files/usr/bin/python
"""Rewrite a text file so every line is followed by extra blank lines.

Each original line is padded with four newlines and the lines are re-joined,
producing a very loosely "spread out" version of the file (handy for diff /
review tooling).  The file is modified in place.

Usage::

    xlr.py <file>
"""

import sys
from pathlib import Path


def process_file(fp: Path) -> None:
    """Expand the vertical spacing of ``fp`` in place.

    Args:
        fp: Path to the text file to rewrite.
    """
    con: str = fp.read_text()
    nl: list[str] = [line + "\n\n\n\n" for line in con.splitlines()]
    newconn: str = "\n".join(nl)
    fp.write_text(newconn)


if __name__ == "__main__":
    fn: Path = Path(sys.argv[1])
    process_file(fn)
