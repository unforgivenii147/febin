#!/data/data/com.termux/files/usr/bin/python
import sys
import pathlib


def ensure_bracket(fn):
    open_parantez_count = 0
    close_parantez_count = 0
    open_braket_count = 0
    close_braket_count = 0
    open_cbraket_count = 0
    close_cbraket_count = 0
    with pathlib.Path(fn).open(encoding="utf-8") as f:
        content = f.read()
        lc = len(content)
        for i in range(lc):
            if content[i] == "(":
                open_parantez_count += 1
            if content[i] == ")":
                close_parantez_count += 1
            if content[i] == "[":
                open_braket_count += 1
            if content[i] == "]":
                close_braket_count += 1
            if content[i] == "{":
                open_cbraket_count += 1
            if content[i] == "}":
                close_cbraket_count += 1
    print(f"open_parantez_count : {open_parantez_count}\nclose_parantez_count : {close_parantez_count}")
    print(f"open_braket_count : {open_braket_count}\nclose_braket_count : {close_braket_count}")
    print(f"open_cbraket_count : {open_cbraket_count}\nclose_cbraket_count : {close_cbraket_count}")
    return bool(
        open_parantez_count == close_parantez_count
        and open_braket_count == close_braket_count
        and open_cbraket_count == close_cbraket_count
    )


def main():
    if len(sys.argv > 0):
        filename = sys.argv[1]
        if ensure_bracket(filename):
            print("ok")
        else:
            print("error")


if __name__ == "__main__":
    main()
