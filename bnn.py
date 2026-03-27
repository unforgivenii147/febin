#!/data/data/com.termux/files/usr/bin/python
import sys
import pathlib


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)
    fname = sys.argv[1]
    content = pathlib.Path(fname).read_text(encoding="utf-8")
    content = content.replace("\\n", "\n")
    pathlib.Path(fname).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
