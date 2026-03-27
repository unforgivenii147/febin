#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_size, format_size, get_nobinary
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
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(cwd)
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    lines_removed = 0
    results = []
    with get_context("spawn").Pool(processes=8) as p:
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
        f"total removed : {lines_removed}",
        "green",
    )
    diffsize = before - get_size(cwd)
    print("space freed: ", end="")
    cprint(
        f"{format_size(diffsize)}",
        "green",
    )


if __name__ == "__main__":
    sys.exit(main())
