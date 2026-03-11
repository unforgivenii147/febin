#!/data/data/com.termux/files/usr/bin/env python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_files, get_size, run_command
from termcolor import cprint

MAX_QUEUE = 16


def process_file(fp):
    before = get_size(fp)
    if not fp.exists():
        return False
    print(f"{fp.name}", end=" ")
    cmd = f"terser {fp}"
    code, output, err = run_command(cmd)
    if code == 0:
        fp.write_text(output)
        after = get_size(fp)
        diffsize = after - before
        if diffsize == 0:
            cprint("[NO CHANGE]", "white")
        elif diffsize < 0:
            cprint(f"[OK] - {format_size(diffsize)}", "cyan")
        elif diffsize > 0:
            cprint(f"[OK] + {format_size(diffsize)}", "yellow")
        return True
    else:
        cprint(f"[ERROR] {err}", "magenta")
        return False


def main():
    args = sys.argv[1:]
    dir = Path.cwd()
    before = get_size(dir)
    files = [Path(arg) for arg in args] if args else get_files(dir, recursive=True, extensions=[".js"])
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)

    with Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, ((f),)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    after = get_size(dir)
    print(f"{format_size(before - after)}")


if __name__ == "__main__":
    sys.exit(main())
