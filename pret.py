#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from dh import format_size, get_files, get_size, mpf, run_command
from termcolor import cprint

MAX_IN_FLIGHT = 16


def process_file(file_path):
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
    cprint(f"[ERROR] {file_path.name}", "red")
    return False


def main() -> None:
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = sorted(
        [Path(arg) for arg in args]
        if args
        else get_files(
            cwd,
            extensions=[
                ".md",
                ".js",
                ".css",
                ".ts",
                ".tsx",
                ".jsx",
                ".json",
                ".html",
                ".cjs",
                ".cts",
                ".mts",
                ".mjs",
                ".coffee",
                ".yaml",
                ".yml",
            ],
        )
    )
    before = get_size(cwd)
    lenbefore = len(files)
    if not files:
        print("no file found.")
        sys.exit(0)
    cprint(f"{lenbefore} files found.", "green")
    for i, file in enumerate(files, 0):
        if "node_modules" in file.parts:
            files.pop(i)
    lenafter = len(files)
    print(f"frocessing {lenafter} files.", end=" | ")
    cprint(f"{lenbefore - lenafter} files poped.", "cyan")
    mpf(process_file, files)
    diffsize = before - get_size(cwd)
    cprint(f"space change:{format_size(diffsize)}", "cyan")


if __name__ == "__main__":
    main()
