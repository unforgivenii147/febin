#!/data/data/com.termux/files/usr/bin/env python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_size, run_command
from fastwalk import walk_files
from termcolor import cprint


def process_file(fp):
    start = get_size(fp)
    if not fp.exists():
        return False
    print(f"{fp.name}", end=" ")
    cmd = f"terser {str(fp)}"
    code, output, err = run_command(cmd)
    if code == 0:
        fp.write_text(output)
        result = get_size(fp) - start
        if int(result) == 0:
            cprint("[OK]", "white")
        elif result < 0:
            cprint(f"[OK] - {format_size(abs(result))}", "cyan")
        elif result > 0:
            cprint(f"[OK] + {format_size(abs(result))}", "yellow")
        return True
    else:
        cprint(f"[ERROR] {err}", "magenta")
        return False


def main():
    args = sys.argv[1:]
    if args:
        filepaths = []
        for arg in args:
            path = Path(arg)
            if path.is_file() and path.suffix == ".js":
                filepaths.append(path)
        for fp in filepaths:
            process_file(fp)
        return 0
    else:
        init_size = get_size(".")
        files = []
        for pth in walk_files("."):
            path = Path(pth)
            if path.is_file() and path.suffix == ".js":
                files.append(path)
    with Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, ((f), )))
            if len(pending) > 16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    end_size = get_size(".")
    print(f"{format_size(init_size - end_size)}")
    return None


if __name__ == "__main__":
    sys.exit(main())
