#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path
from dh import format_size, get_pyfiles, get_size, run_command
from termcolor import cprint


def process_file(path):
    print(f"running {path.name}")
    try:
        cmd = f"python -I {path!s}"
        _, _, _ = run_command(cmd)
    except:
        print("error")


def main() -> None:
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_pyfiles(cwd)
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    with get_context("spawn").Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, (f,)))
            if len(pending) > 8:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


if __name__ == "__main__":
    main()
