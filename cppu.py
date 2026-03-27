#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
import subprocess
from collections import deque
from multiprocessing import Pool

from dh import get_size, format_size
from fastwalk import walk_files
from termcolor import cprint


MAX_QUEUE = 16
FILE_EXTENSIONS = {
    ".java",
    ".c",
    ".cpp",
    ".cxx",
    ".cc",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".js",
    ".json",
}


def format_file(file_path):
    before = file_path.stat().st_size
    print(f"{file_path.name} ", end=" ")
    try:
        res = subprocess.run(
            [
                "clang-format",
                "-i",
                "--style=LLVM",
                str(file_path),
            ],
            check=True,
            capture_output=True,
        )
        after = file_path.stat().st_size
        size_diff = before - after
        if size_diff == 0:
            print("[NO CHANGE]")
        elif size_diff > 0:
            print(f"[OK] + {format_size(size_diff)}")
        elif size_diff < 0:
            print(f"[OK] - {format_size(size_diff)}")
        del res
        del size_diff
        del after
        del before
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
    ):
        del res
        del size_diff
        del after
        del before
        print(f"[ERR] {res.stderr!s}")
        return False


def main() -> None:
    cfiles: list = []
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    if args:
        cfiles = [Path(arg) for arg in args]
    else:
        for pth in walk_files(cwd):
            path = Path(pth)
            if any(path.suffix == ext for ext in FILE_EXTENSIONS):
                cfiles.append(path)
    if len(cfiles) == 1:
        format_file(cfiles[0])
        sys.exit(0)
    if not cfiles:
        cprint("No files found.", "red")
        sys.exit(0)
    all_count = len(cfiles)
    cprint(f"{all_count} files found...", "cyan")

    with Pool(8) as pool:
        pending = deque()
        for f in cfiles:
            pending.append(pool.apply_async(format_file, ((f),)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    after = get_size(cwd)
    diffsize = after - before
    print(f"space change: {format_size(diffsize)}")


if __name__ == "__main__":
    main()
