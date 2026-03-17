#!/data/data/com.termux/files/usr/bin/env python
from collections import deque
from multiprocess import Pool
from pathlib import Path
import sys

from dh import format_size, get_nobinary, get_size
from termcolor import cprint


def process_file(filepath) -> int:
    non_empty_lines: list[str] = []
    lines: list[str] = []
    removed: int = 0
    content: str = ""
    line: str = ""
    if filepath.is_symlink() or filepath.suffix == ".bak" or not get_size(filepath):
        return 0
    try:
        print(f"[OK] {filepath.name}", end=" ")
        with filepath.open(
            "r+",
            encoding="utf-8",
            errors="replace",
        ) as f:
            lines = f.readlines()
            for line in lines:
                if line.strip():
                    non_empty_lines.append(line)
                else:
                    removed += 1
            content = "".join(non_empty_lines)
            if not removed:
                cprint(f" {removed}", "green")
                del (
                    lines,
                    line,
                    removed,
                    content,
                    non_empty_lines,
                )
                return 0
            f.seek(0)
            f.write(content)
            f.truncate()
            cprint(f" {removed}", "cyan")
        del lines, line, content, non_empty_lines
        return removed
    except OSError:
        return 0


def main():
    files = []
    root_dir = Path.cwd()
    start_size = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(root_dir)
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    lines_removed = 0
    results = []
    with Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, (f,)))
            if len(pending) > 16:
                results.append(pending.popleft().get())
        while pending:
            results.append(pending.popleft().get())
    for result in results:
        if result:
            lines_removed += result
    cprint(
        f"total empty lines removed : {lines_removed}",
        "green",
    )
    after = get_size(root_dir)
    print("space freed: ", end=" ")
    cprint(
        f"{format_size(start_size - after)}",
        "green",
    )


if __name__ == "__main__":
    sys.exit(main())
