#!/data/data/com.termux/files/usr/bin/python
import os
import sys
from multiprocessing import Pool
from pathlib import Path
from sys import exit

from bs4 import BeautifulSoup
from dh import format_size, get_files, get_random_name, get_size
from termcolor import cprint


def save_style(str1):
    if not str1:
        return None
    fn = "css/"
    if not Path("css").exists():
        Path("css").mkdir()
    fn = get_random_name(10)
    fn += ".css"
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
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(arg) for arg in args]
        if args
        else get_files(
            cwd,
            recursive=True,
            extensions=[".html", ".htm"],
        )
    )
    before = get_size(cwd)
    pool = Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    diffsize = before - get_size(cwd)
    print(f"{format_size(diffsize)}")


if __name__ == "__main__":
    exit(main())
