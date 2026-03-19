#!/data/data/com.termux/files/usr/bin/env python
from bs4 import BeautifulSoup
import string
import random
import os
from collections import deque
from pathlib import Path
import sys

from dh import (
    cprint,
    format_size,
    get_files,
    get_size,
)
from multiprocessing import Pool
from termcolor import cprint

MAX_QUEUE = 16


def save_script(str1):
    fn = "js/"
    if not os.path.exists("js"):
        os.mkdir("js")
    for _i in range(0, 10):
        fn += random.choice(string.ascii_lowercase)
    fn += ".js"
    if os.path.exists(fn):
        cprint(f"[{fn}] exists.", "red")
        return False
    if not os.path.exists(fn):
        with open(fn, "w") as f:
            f.write("\n".join(list(str1)))
        cprint(f"{[fn]} created.", "cyan")
    return True


def process_file(fp):
    with open(fp, encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    scripts = soup.find_all("script")
    if scripts:
        cprint(
            f"{[fp.name]} : {len(scripts)} scripts found.",
            "magenta",
        )
        for script in scripts:
            save_script(script.contents)
    return True


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(root_dir, extensions=[".html", "htm"])
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(root_dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
