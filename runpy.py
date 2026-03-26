#!/data/data/com.termux/files/usr/bin/python
from multiprocessing import get_context
from pathlib import Path
import sys

from dh import format_size, get_pyfiles, get_size, run_command
from termcolor import cprint


def process_file(path):
    print(f"running {path.name}")
    try:
        cmd = f"python {path!s}"
        _, _, _ = run_command(cmd)
    except:
        print("error")


def main() -> None:
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_pyfiles(root_dir)
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
    diffsize = before - get_size(root_dir)
    cprint(
        f"{format_size(diffsize)}",
        "cyan",
    )


if __name__ == "__main__":
    main()
