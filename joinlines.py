#!/data/data/com.termux/files/usr/bin/python
from sys import argv
import pathlib


def main():
    nl = ""
    with pathlib.Path(argv[1]).open(encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip():
                nl += line.strip("\n")
    pathlib.Path(argv[1]).write_text(nl + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
