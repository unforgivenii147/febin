#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from typing import Int, Str

from dh import format_size, get_files, get_size, mpf


def _get_comments_symbol(text: Str, symbol: Str) -> list[Str]:
    comments: list = []
    i: Int = 0
    indexes: list = []
    for i in range(len(text)):
        if text[i] == symbol and len(text) > i + 2 and text[i] == text[i + 1] == text[i + 2]:
            if len(indexes) == 0:
                indexes.append(i)
            elif len(indexes) == 1:
                indexes.append(i + 2)
                comments.append(text[indexes[0] : indexes[1] + 1])
                indexes = []
    return comments


def _get_comments_simplequot(text: Str) -> list[str]:
    return _get_comments_symbol(text=text, symbol="'")


def _get_comments_doublequot(text: str) -> list[str]:
    return _get_comments_symbol(text=text, symbol='"')


def remove_comments(text: str) -> str:
    comments = _get_comments_simplequot(text=text)
    for comment in comments:
        text = text.replace(comment, "")
    comments = _get_comments_doublequot(text=text)
    for comment in comments:
        text = text.replace(comment, "")
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if "#" in line:
            line_without_comment = "#".join(line.split("#")[:1]).rstrip(" ")
            new_lines.append(line_without_comment)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def process_file(fp):
    data = fp.read_text()
    result = remove_comments(data)
    fp.write_text(result)


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".py"])

    mpf(process_file, files)
    diff_size = before - get_size(cwd)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
