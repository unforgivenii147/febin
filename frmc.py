#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from multiprocessing import get_context
from pathlib import Path

from dh import (
    SOURCE_CODE_EXT,
    clean_blank_lines,
    format_size,
    get_nobinary,
    get_size,
    is_binary,
)
from termcolor import cprint


def process_file(fp):
    if fp.suffix == ".md":
        return
    removed: int = 0
    inline: int = 0
    if is_binary(fp) or fp.suffix in SOURCE_CODE_EXT:
        print(f"[skip] {fp.name} is binary or source code")
        return
    before: int = get_size(fp)
    lines: list[str] = []
    print(f"[Ok] {fp.name} ", end="")
    with Path(fp).open(encoding="utf-8") as fin:
        lines = fin.readlines()
        if not lines:
            return
    cleaned = []
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("#!"):
            cleaned.append(line)
            continue
        if "#" in line and not line.startswith("#"):
            indx = line.index("#")
            cleaned.append(line[:indx])
            inline += 1
            continue
        if not line.startswith("#"):
            cleaned.append(line)
        else:
            removed += 1
    code = "\n".join(cleaned)
    code = clean_blank_lines(code)
    if fp.suffix != ".py":
        Path(fp).write_text(code, encoding="utf-8")
        after = get_size(fp)
        diffsize = after - before
        cprint(
            f"{format_size(diffsize)} | removed : {removed} | inline : {inline}",
            "yellow",
        )
    else:
        try:
            _ = ast.parse(code)
            Path(fp).write_text(code, encoding="utf-8")
            after = get_size(fp)
            diffsize = after - before
            cprint(
                f"{format_size(diffsize)} | removed : {removed} | inline : {inline}",
                "yellow",
            )
        except:
            cprint("result code invalid.", "magenta")


def main() -> None:
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(cwd)
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    p = get_context("spawn").Pool(8)
    for _ in p.imap_unordered(process_file, files):
        pass
    p.close()
    p.join()
    diffsize = before - get_size(cwd)
    cprint(
        f"{format_size(diffsize)}",
        "cyan",
    )


if __name__ == "__main__":
    main()
