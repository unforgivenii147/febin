#!/data/data/com.termux/files/usr/bin/python
import pathlib
import sys

INVISIBLE_CHARS = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u00a0",
    "\u00ad",
    "\ufeff",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
}


def clean_text(text: str) -> str:
    cleaned = ""
    for c in text:
        if ord(c) == 8204:
            continue
        if c == "\n":
            cleaned += c
            continue
        if c in INVISIBLE_CHARS:
            continue
        cleaned += c
    return cleaned


def main():
    text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
    cleaned = clean_text(text)
    removed = len(text) - len(cleaned)
    if removed:
        print(f"{removed} invisible characters removed")
    else:
        print("No invisible characters found")
    pathlib.Path(sys.argv[1]).write_text(cleaned, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
