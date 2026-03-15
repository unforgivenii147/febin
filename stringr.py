#!/usr/bin/env python3
from multiprocessing import Pool
from pathlib import Path

from dh import (
    format_size,
    get_files,
    get_size,
    run_command,
)


def process_file(fp):
    if not fp.exists():
        return False
    outfile = fp.with_name(f"{fp.stem}_strings")
    cmd = f"strings {fp!s}"
    _code, txt, _err = run_command(cmd)
    outfile.write_text(txt)
    return None


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir)
    before = get_size(root_dir)
    pool = Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    diff_size = before - get_size(root_dir)
    print(f"{format_size(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
