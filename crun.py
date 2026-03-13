#!/usr/bin/env python3
from multiprocessing import Pool
from pathlib import Path
from sys import exit

from dh import format_size, get_size, run_command
from fastwalk import walk_files


def process_file(fp):
    if not fp.exists():
        return False
    if fp.suffix == ".c":
        cmd = f"clang {fp!s} -o {fp.with_suffix('')!s}"
    if fp.suffix == ".cpp":
        cmd = f"clang++ {fp!s} -o {fp.with_suffix('')!s}"
    ret, txt, _err = run_command(cmd)
    print(txt)
    return ret
    return True


def main():
    dir = Path().cwd()
    start_size = get_size(dir)
    files = []
    for pth in walk_files(dir):
        path = Path(pth)
        if path.is_file() and path.suffix in {
                ".c",
                ".cpp",
        }:
            files.append(path)
    pool = Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    after = get_size(dir)
    print(f"{format_size(abs(after - start_size))}")


if __name__ == "__main__":
    exit(main())
