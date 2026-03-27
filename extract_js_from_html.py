#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import string
from pathlib import Path
from collections import deque
from multiprocessing import Pool

from dh import get_size, get_files, format_size
from bs4 import BeautifulSoup
from termcolor import cprint


MAX_QUEUE = 16


def save_script(str1):
    fn = "js/"
    if not Path("js").exists():
        Path("js").mkdir()
    for _i in range(10):
        fn += random.choice(string.ascii_lowercase)
    fn += ".js"
    if Path(fn).exists():
        cprint(f"[{fn}] exists.", "red")
        return False
    if not Path(fn).exists():
        Path(fn).write_text("\n".join(list(str1)), encoding="utf-8")
        cprint(f"{[fn]} created.", "cyan")
    return True


def process_file(fp):
    html_content = Path(fp).read_text(encoding="utf-8")
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
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".html", "htm"])
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
