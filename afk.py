#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path

from dh import fix_code, get_pyfiles
from termcolor import cprint


def process_file(fp):
    code = fp.read_text(encoding="utf-8")
    result = fix_code(code)
    diff_size = len(code) - len(result)
    if diff_size:
        print(f"{fp.name} ", end="")
        cprint(f"{diff_size}", "cyan")
        fp.write_text(result, encoding="utf-8")
    else:
        print(f"{fp.name} no change")


if __name__ == "__main__":
    cwd = Path.cwd()
    files = get_pyfiles(cwd)
    for f in files:
        process_file(f)
