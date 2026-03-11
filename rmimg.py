#!/data/data/com.termux/files/usr/bin/env python
import ast
import sys
from multiprocessing import Pool
from pathlib import Path
from bs4 import BeautifulSoup

import regex as re
import tree_sitter_python as tspython
from dh import DOC_TH1, DOC_TH2, cprint, format_size, get_files, get_size, rm_doc
from termcolor import cprint
from tree_sitter import Language, Parser


def process_file(file_path: Path) -> None:
    before = get_size(file_path)
    try:
        original = file_path.read_text(encoding="utf-8")
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
            cprint(f"NO CHANGE", "yellow")
        elif diffsize > 0:
            cprint(f" + {format_size(diffsize)}")
        elif diffsize < 0:
            cprint(f" - {format_size(diffsize)}")
    except:
        pass


def main():
    dir = Path.cwd()
    before = get_size(dir)
    args = sys.argv[1:]
    if args:
        files = [Path(f) for f in args]
    else:
        files = get_files(dir, recursive=True, extensions=[".html", ".htm", ".md", ".rst", ".txt"])
    p = Pool(8)
    for f in files:
        p.apply_async(process_file, (f,))
    p.close()
    p.join()
    diff_size = before - get_size(dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
