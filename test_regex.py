#!/data/data/com.termux/files/usr/bin/env python3
import sys
from multiprocessing import Pool
from pathlib import Path

import regex as re
from dh import format_size, get_pyfiles, get_size


def process_file(file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    regex1 = re.compile(r"\"[^\"]*\"")
    re.compile(r"'[^']*'")
    matches = regex1.findall(content)
    print(matches)


def main():
    dir = Path.cwd()
    before = get_size(dir)
    args = sys.argv[1:]
    if args:
        files = [Path(f) for f in args]
        if len(files) == 1:
            process_file(files[0])
            return
        else:
            for f in files:
                process_file(f8)
    else:
        files = get_pyfiles(dir)
        p = Pool(8)
        for f in files:
            p.apply_async(process_file, (f, ))
        p.close()
        p.join()
    diff_size = before - get_size(dir)
    print(f"{format_size(diff_size)}")


if __name__ == "__main__":
    main()
