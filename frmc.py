#!/data/data/com.termux/files/usr/bin/env python
import sys
from multiprocessing import Pool
from pathlib import Path
from dh import (SOURCE_CODE_EXT, format_size, get_size, is_binary,
                remove_blank_lines)
from fastwalk import walk_files
from termcolor import cprint
def process_file(fp):
    if is_binary(fp) or fp.suffix in SOURCE_CODE_EXT:
        print(f"[skip] {fp.name} is binary or source code")
        return
    initsize = get_size(fp)
    lines = []
    print(f"[Ok] {fp.name} ", end=" ")
    with open(fp, "r", encoding="utf-8") as fin:
        lines = fin.readlines()
        if not lines:
            return
    cleaned = []
    for line in lines:
        if line.startswith("#!"):
            cleaned.append(line)
            continue
        if "#" in line and not line.strip().startswith("#"):
            indx = line.index("#")
            cleaned.append(line[:indx] + "\n")
            continue
        if not line.strip().startswith("#"):
            cleaned.append(line)
    with open(fp, "w") as fout:
        for k in cleaned:
            fout.write(k)
    remove_blank_lines(fp)
    endsize = get_size(fp)
    diffsize = endsize - initsize
    cprint(f"{format_size(diffsize)}", "yellow")
def main() -> None:
    dir = Path.cwd()
    init_size = get_size(dir)
    args = sys.argv[1:]
    if args:
        files = [Path(arg) for arg in args]
    else:
        files = [Path(f) for f in walk_files(dir)]
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
    else:
        p = Pool(8)
        for _ in p.imap_unordered(process_file, files):
            pass
        p.close()
        p.join()
        end_size = get_size(dir)
        cprint(
            f"{format_size(init_size - end_size)}",
            "cyan",
        )
if __name__ == "__main__":
    main()
