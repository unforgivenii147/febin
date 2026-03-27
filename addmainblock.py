#!/data/data/com.termux/files/usr/bin/python
import os
import regex as re
import sys
from pathlib import Path
from dh import get_pyfiles, get_size, format_size
from multiprocessing import get_context
from collections import deque
from termcolor import cprint
def process_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content_lines = f.readlines()


        main_block_found = False
        for i, line in enumerate(content_lines):
            if re.match(r'^\s*if\s+__name__\s*==\s*="__main__":', line):

                if not line.startswith((" ", "\t")):
                    main_block_found = True
                    break


                main_block_found = True
                break
        if not main_block_found:
            print(f"{filepath} dont have main block")
            return




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
            print(f"__main__ block already present in: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
def main() -> None:
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_pyfiles(cwd)
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    p = get_context("spawn").Pool(8)
    for _ in p.imap_unordered(process_file, files):
        pass
    p.close()
    p.join()
    diffsize = before - get_size(cwd)
    cprint(
        f"{format_size(diffsize)}",
        "cyan",
    )
if __name__ == "__main__":
    main()
