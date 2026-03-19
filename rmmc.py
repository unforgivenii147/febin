#!/data/data/com.termux/files/usr/bin/env python3
import ast
from pathlib import Path
import sys

from dh import format_size, get_nobinary, get_size
from multiprocessing import Pool
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
            file_path.write_text(orig)
            after = get_size(file_path)
            print(f"{file_path.name} ", end=" ")
            print(format_size(before - after))
        except:
            return
    else:
        file_path.write_text(orig)
        after = get_size(file_path)
        print(f"{file_path.name} ", end=" ")
        print(format_size(before - after))


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    if args:
        files = [Path(f) for f in args]
        for f in files:
            process_file(f)
    else:
        files = get_nobinary(root_dir)
        p = Pool(8)
        for f in files:
            p.apply_async(process_file, (f,))
        p.close()
        p.join()
    diff_size = before - get_size(root_dir)
    print(f"{format_size(diff_size)}")


if __name__ == "__main__":
    main()
