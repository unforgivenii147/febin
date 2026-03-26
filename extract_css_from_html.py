#!/data/data/com.termux/files/usr/bin/python
from multiprocessing import Pool
import os
from pathlib import Path
import sys
from sys import exit

from bs4 import BeautifulSoup
from dh import format_size, get_files, get_random_name, get_size
from termcolor import cprint


def save_style(str1):
    if not str1:
        return None
    fn = "css/"
    if not os.path.exists("css"):
        os.mkdir("css")
    fn = get_random_name(10)
    fn += ".css"
    if os.path.exists(fn):
        cprint(f"[{fn}] exists.", "red")
        return False
    if not os.path.exists(fn):
        Path(fn).write_text("\n".join(list(str1)), encoding="utf-8")
        cprint(f"{[fn]} created.", "cyan")
    return True


def process_file(fp):
    html_content = Path(fp).read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    styles = soup.find_all("style")
    if styles:
        cprint(
            f"{[fp.name]} : {len(styles)} styles found.",
            "magenta",
        )
        for style in styles:
            save_style(style.contents)
    return True


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(arg) for arg in args]
        if args
        else get_files(
            root_dir,
            recursive=True,
            extensions=[".html", ".htm"],
        )
    )
    before = get_size(root_dir)
    pool = Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    diffsize = before - get_size(root_dir)
    print(f"{format_size(diffsize)}")


if __name__ == "__main__":
    exit(main())
