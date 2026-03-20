#!/data/data/com.termux/files/usr/bin/python
import ast
from multiprocessing import Pool
from pathlib import Path
import sys

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
    with open(fp, encoding="utf-8") as fin:
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
        with open(fp, "w") as fout:
            fout.write(code)
        after = get_size(fp)
        diffsize = after - before
        cprint(
            f"{format_size(diffsize)} | removed : {removed} | inline : {inline}",
            "yellow",
        )
    else:
        try:
            _ = ast.parse(code)
            with open(fp, "w") as fo:
                fo.write(code)
            after = get_size(fp)
            diffsize = after - before
            cprint(
                f"{format_size(diffsize)} | removed : {removed} | inline : {inline}",
                "yellow",
            )
        except:
            cprint("result code invalid.", "magenta")


def main() -> None:
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(root_dir)
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    else:
        p = Pool(8)
        for _ in p.imap_unordered(process_file, files):
            pass
        p.close()
        p.join()
        after = get_size(root_dir)
        cprint(
            f"{format_size(before - after)}",
            "cyan",
        )


if __name__ == "__main__":
    main()
