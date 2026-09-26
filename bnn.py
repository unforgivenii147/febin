#!/data/data/com.termux/files/usr/bin/python
"""Turn literal ``\\n`` sequences in a file into real newlines.

Reads the given file, replaces every two-character ``backslash-n`` escape with
an actual line break, and writes the result back in place.

Usage::

    bnn.py <filename>
"""

import sys
from pathlib import Path


def main() -> None:
    """Replace literal ``\\n`` escapes with newlines in the file from argv."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)
    fname: str = sys.argv[1]
    content: str = Path(fname).read_text(encoding="utf-8")
    content = content.replace("\\n", "\n")
    Path(fname).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
