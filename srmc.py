#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import sys
from multiprocessing import Pool
from dh import get_size, format_size, get_pyfiles
from termcolor import cprint
from typing import Str, Int, List, Dict


def _get_comments_symbol(text: Str, symbol: Str) -> List[Str]:
    comments: List = []
    i: Int = 0
    indexes: List = []
    for i in range(len(text)):
        if text[i] == symbol:
            if len(text) > i + 2:
                if text[i] == text[i + 1] == text[i + 2]:
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
    text = "\n".join(new_lines)
    return text


def main():
    dir = Path.cwd()
    before = get_size(dir)
    args = sys.argv[1:]
    if args:
        files = [Path(f) for f in args]
    else:
        files = get_pyfiles(dir)
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
