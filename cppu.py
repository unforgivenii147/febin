#!/data/data/com.termux/files/usr/bin/env python
import subprocess
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_size
from fastwalk import walk_files
from termcolor import cprint

FILE_EXTENSIONS = {
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
    init_size = file_path.stat().st_size
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
        end_size = file_path.stat().st_size
        size_diff = init_size - end_size
        if size_diff == 0:
            print(f"[NO CHANGE] {file_path.name}")
        elif size_diff > 0:
            print(f"[OK] {file_path.name} + {format_size(size_diff)}")
        elif size_diff < 0:
            print(f"[OK] {file_path.name} - {format_size(abs(size_diff))}")
        return True
    except (
            subprocess.CalledProcessError,
            FileNotFoundError,
    ):
        print(f"[ERR] {res.stderr!s} {file_path.name}")
        return False


def main() -> None:
    cfiles = []
    dir = str(Path().cwd().resolve())
    initsize = get_size(dir)
    for pth in walk_files(dir):
        path = Path(pth)
        if any(path.suffix == ext for ext in FILE_EXTENSIONS):
            cfiles.append(path)
    if not cfiles:
        cprint("No files found.", "red")
        return
    cprint(f"{len(cfiles)} files found...", "cyan")
    pool = Pool(6)
    for f in cfiles:
        pool.apply_async(format_file, ((f), ))
    pool.close()
    pool.join()
    endsize = get_size(dir)
    diffsize = initsize - endsize
    print(f"dir size changed: {format_size(abs(diffsize))}")


if __name__ == "__main__":
    main()
