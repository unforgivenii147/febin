#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from multiprocessing import get_context

from dh import get_size, get_files, format_size, get_random_name
from bs4 import BeautifulSoup
from termcolor import cprint


def save_style(str1):
    if not str1 or len(str(str1)) < 2:
        return
    fn = "css/"
    fn += get_random_name(10)
    fn += ".css"
    path = Path(fn)
    if path.exists():
        cprint(f"[{fn}] exists.", "red")
        path = unique_path(path)
    path.write_text("\n".join(list(str1)), encoding="utf-8")
    cprint(f"{[fn]} created.", "cyan")
    return


def process_file(fp):
    html_content = fp.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    styles = soup.find_all("style")
    if styles:
        cprint(
            f"{[fp.name]} : {len(styles)} styles found.",
            "green",
        )
        for style in styles:
            save_style(style.contents)
    return True


def main():
    outpath = Path("css")
    if not outpath.exists():
        outpath.mkdir(exists_ok=True)
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
    pool = get_context("spawn").Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    diffsize = before - get_size(cwd)
    cprint(f"space change : {format_size(diffsize)}", "blue")


if __name__ == "__main__":
    sys.exit(main())
