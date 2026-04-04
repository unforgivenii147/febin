#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from sys import argv


def main():
    fn = Path(argv[1])
    content = fn.read_text(encoding="utf-8")
    lower_content = content.lower()
    fn.write_text(lower_content, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
