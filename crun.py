#!/usr/bin/env python3
from collections import deque
from multiprocessing import Pool
from pathlib import Path
from sys import exit
from dh import format_size, get_size, run_command
from fastwalk import walk_files
def process_file(fp):
    if not fp.exists():
        return False
    if fp.suffix == ".c":
        cmd = f"clang {str(fp)} -o {str(fp.with_suffix(''))}"
    if fp.suffix == ".cpp":
        cmd = f"clang++ {str(fp)} -o {str(fp.with_suffix(''))}"
    ret, txt, err = run_command(cmd)
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
    end_size = get_size(dir)
    print(f"{format_size(abs(end_size - start_size))}")
if __name__ == "__main__":
    exit(main())
