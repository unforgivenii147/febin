#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_size, get_files, format_size
from termcolor import cprint


MAINBLOCK = r'if __name__ == "__main__":'
MAX_QUEUE = 16


def process_file(filepath):
    if filepath.is_symlink():
        return
    content = filepath.read_text(encoding="utf-8")
    content.splitlines()
    if MAINBLOCK not in content:
        print(f"{filepath.name} dont have main block")


"""
        initial_indent = ""
        lines_to_write = []
        if content_lines and not content_lines[-1].endswith("\n"):
            lines_to_write.append("\n")
        lines_to_write.append(f"{initial_indent}if __name__ == '__main__':\n")
        lines_to_write.append(f"{initial_indent}    # Placeholder for main execution logic\n")
        lines_to_write.append(f"{initial_indent}    pass\n")
        with open(filepath, "a", encoding="utf-8") as f:
            f.writelines(lines_to_write)
    else:
        print(f"__main__ block already present in: {filepath.name}")
"""


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".py"])
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    cprint(f"space saved : {format_size(diff_size)}", "cyan")


if __name__ == "__main__":
    main()
