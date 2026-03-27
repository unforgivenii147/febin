#!/data/data/com.termux/files/usr/bin/python
import sys
import pathlib


def split_file_by_delimiter(fname, delimiter) -> None:
    content = pathlib.Path(fname).read_text(encoding="utf-8")
    parts = content.split(delimiter)
    with pathlib.Path(fname).open("w", encoding="utf-8") as f:
        f.writelines(part.strip() + f"{delimiter}\n" for part in parts)


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename> <delimiter>")
        sys.exit(1)
    fname = sys.argv[1]
    delimiter = sys.argv[2]
    if delimiter == "":
        print("Error: delimiter cannot be empty")
        sys.exit(1)
    split_file_by_delimiter(fname, delimiter)
    print(f"{sys.argv[1]} updated.")


if __name__ == "__main__":
    main()
