#!/data/data/com.termux/files/usr/bin/env python
import argparse
from collections import deque
from multiprocess import Pool
from pathlib import Path

from dh import format_size, get_size, run_command
from fastwalk import walk_files
from termcolor import cprint

MAX_IN_FLIGHT = 16
FILE_EXTENSIONS = {
    ".js",
    ".css",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".html",
    ".cjs",
    ".mjs",
}


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
    parser = argparse.ArgumentParser(description="Format files using Prettier.")
    parser.add_argument("file", nargs="?", help="File to format")
    args = parser.parse_args()
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found.")
            return
        if any(file_path.suffix == ext for ext in FILE_EXTENSIONS):
            format_file(file_path)
        else:
            print(f"Error: File '{args.file}' has an unsupported extension.")
    else:
        start = get_size(".")
        jfiles = []
        for pth in walk_files("."):
            path = Path(pth)
            if any(path.suffix == ext for ext in FILE_EXTENSIONS):
                if ".min." in path.name:
                    continue
                jfiles.append(path)
        if not jfiles:
            print("No files found.")
            return
        print(f"Formatting {len(jfiles)} files using mp...")
        with Pool(8) as p:
            pending = deque()
            for f in jfiles:
                pending.append(p.apply_async(format_file, (f,)))
                if len(pending) >= MAX_IN_FLIGHT:
                    pending.popleft().get()
            while pending:
                pending.popleft().get()
        end = get_size(".")
        print(f"{format_size(start - end)}")


if __name__ == "__main__":
    main()
