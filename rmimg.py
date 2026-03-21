#!/data/data/com.termux/files/usr/bin/python
import sys
from multiprocessing import Pool
from pathlib import Path

from bs4 import BeautifulSoup
from dh import (
    cprint,
    format_size,
    get_files,
    get_size,
)
from termcolor import cprint


def process_file(file_path: Path) -> None:
    before = get_size(file_path)
    try:
        file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        for img in soup.find_all("img"):
            img.decompose()

        for tag in soup.find_all(style=True):
            style = tag["style"]
            new_style = "; ".join(s for s in style.split(";") if "background-image" not in s).strip()
            if new_style:
                tag["style"] = new_style
            else:
                del tag["style"]

        clean_html = str(soup)
        file_path.write_text(clean_html)
        after = get_size(file_path)
        print(f"{file_path.name}", end=" ")
        diffsize = before - after
        if diffsize == 0:
            cprint("NO CHANGE", "yellow")
        elif diffsize > 0:
            cprint(f" + {format_size(diffsize)}")
        elif diffsize < 0:
            cprint(f" - {format_size(diffsize)}")
    except:
        pass


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    if args:
        files = [Path(f) for f in args]
    else:
        files = get_files(
            root_dir,
            recursive=True,
            extensions=[
                ".html",
                ".htm",
                ".md",
                ".rst",
                ".txt",
            ],
        )
    p = Pool(8)
    for f in files:
        p.apply_async(process_file, (f,))
    p.close()
    p.join()
    diff_size = before - get_size(root_dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
