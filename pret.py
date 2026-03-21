#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_files, get_size, run_command
from termcolor import cprint

MAX_IN_FLIGHT = 16


def format_file(file_path):
    before = get_size(file_path)
    cmd = f"prettier -w {file_path!s}"
    code, _out, _err = run_command(cmd)
    if code == 0:
        diffsize = before - get_size(file_path)
        if not diffsize:
            cprint("[NO CHANGE] ", "green", end="")
            cprint(f"{file_path.name}", "white")
        elif diffsize < 0:
            cprint(
                f"[OK] {file_path.name} ",
                "white",
                end="",
            )
            cprint(
                f" + {format_size(diffsize)}",
                "green",
            )
        elif diffsize > 0:
            cprint(
                f"[OK] {file_path.name} ",
                "white",
                end="",
            )
            cprint(
                f" - {format_size(diffsize)}",
                "cyan",
            )
        return True
    else:
        cprint(f"[ERROR] {file_path.name}", "red")
        return False


def main() -> None:
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = ([Path(arg) for arg in args] if args else get_files(
        root_dir,
        extensions=[
            ".js",
            ".css",
            ".ts",
            ".tsx",
            ".jsx",
            ".json",
            ".html",
            ".cjs",
            ".mjs",
        ],
    ))
    if len(files) == 1:
        process_file(files[0])
        return

    before = get_size(root_dir)
    with Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(format_file, (f, )))
            if len(pending) >= MAX_IN_FLIGHT:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diffsize = before - get_size(root_dir)
    print(f"space change:{format_size(diffsize)}")


if __name__ == "__main__":
    main()
