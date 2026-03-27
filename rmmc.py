#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path
from multiprocessing import get_context

from dh import get_size, format_size, get_nobinary
import regex as re


def process_file(file_path: Path) -> None:
    if is_binary(file_path):
        return
    before = get_size(file_path)
    file_path.read_text(encoding="utf-8")
    orig = re.sub(r"#.*", "")
    orig = re.sub(r"\n\n*", "\n")
    if file_path.suffix == ".py":
        try:
            ast.parse(orig)
            file_path.write_text(orig, encoding="utf-8")
            after = get_size(file_path)
            print(f"{file_path.name} ", end=" ")
            print(format_size(before - after))
        except:
            return
    else:
        file_path.write_text(orig, encoding="utf-8")
        after = get_size(file_path)
        print(f"{file_path.name} ", end=" ")
        print(format_size(before - after))


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_nobinary(cwd)
    p = get_context("spawn").Pool(8)
    for f in files:
        p.apply_async(process_file, (f,))
    p.close()
    p.join()
    diff_size = before - get_size(cwd)
    print(f"space change: {format_size(diff_size)}")


if __name__ == "__main__":
    main()
