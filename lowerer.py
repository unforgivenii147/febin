#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from sys import argv, exit


def main():
    fn = Path(argv[1])
    content = fn.read_text()
    lower_content = content.lower()
    fn.write_text(lower_content)


if __name__ == "__main__":
    exit(main())
