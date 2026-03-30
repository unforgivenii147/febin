#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_size, get_files, format_size, run_command
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
        diffsize = before - get_size(fp)
        if diffsize == 0:
            cprint("[NO CHANGE]", "white")
        elif diffsize < 0:
            cprint(
                f"[OK] + {format_size(diffsize)}",
                "yellow",
            )
        elif diffsize > 0:
            cprint(
                f"[OK] - {format_size(diffsize)}",
                "cyan",
            )
        return True
    cprint(f"[ERROR] {err}", "magenta")
    return False


def main():
    args = sys.argv[1:]
    cwd = Path.cwd()
    before = get_size(cwd)
    files = (
        [Path(p) for p in args] if args else get_files(cwd, extensions=[".js", ".ts", ".cjs", ".mjs", ".jsx", ".tsx"])
    )

    with get_context("spawn").Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, ((f),)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    cprint(f"space freed : {format_size(diff_size)}", "green")


if __name__ == "__main__":
    sys.exit(main())
