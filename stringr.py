#!/data/data/com.termux/files/usr/bin/python
import sys
from multiprocessing import get_context
from pathlib import Path

from dh import format_size, get_files, get_size, is_binary, run_command


def process_file(fp):
    if not fp.exists() or not is_binary(fp):
        return
    print(f"processing {fp.name}")
    outfile = fp.with_name(f"{fp.stem}_strings")
    cmd = f"strings {fp!s}"
    _code, txt, _err = run_command(cmd)
    outfile.write_text(txt)
    return


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd)
    before = get_size(cwd)
    pool = get_context("spawn").Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    diff_size = before - get_size(cwd)
    print(f"space change : {format_size(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
