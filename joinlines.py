#!/data/data/com.termux/files/usr/bin/python
import pathlib
from sys import argv


def main():
    nl = ""
    with open(argv[1], encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip():
                nl += line.strip("\n")
    pathlib.Path(argv[1]).write_text(nl + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
