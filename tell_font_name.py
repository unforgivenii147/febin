#!/data/data/com.termux/files/usr/bin/python
from multiprocessing import Pool
from pathlib import Path
import sys

from dh import get_files, unique_path
from fontTools.ttLib import TTFont
import regex as re
from termcolor import cprint

MAX_QUEUE = 16


def is_ascii_printable(s: str) -> bool:
    return all(32 <= ord(c) <= 126 for c in s)


def clean_filename(s: str) -> str:
    s = re.sub(r"[^\w\-\.]", "", s)
    return s.strip("_-.")


def get_best_name(font, name_id):
    fallback = None
    for rec in font["name"].names:
        if rec.nameID != name_id:
            continue
        try:
            name = rec.toUnicode().strip()
        except Exception:
            continue
        if rec.platformID == 3 and rec.langID == 0x0409:
            return name
        if is_ascii_printable(name):
            fallback = name
    return fallback


def get_font_names(path):
    font = TTFont(path)
    family = get_best_name(font, 1)
    subfamily = get_best_name(font, 2)
    if not family:
        return None, None
    family = clean_filename(family)
    subfamily = "Regular" if not subfamily else clean_filename(subfamily)
    if subfamily.lower() == family.lower():
        subfamily = "Regular"
    return family, subfamily


def process_file(fn):
    try:
        family, style = get_font_names(fn)
    except Exception as e:
        cprint(f"error: {e}", "magenta")
        return 1
    if not family:
        cprint("name not found", "magenta")
        return 1
    ext = fn.suffix.lower()
    new_path = Path(fn.parent / f"{family}-{style}{ext}")
    if new_path.exists():
        new_path = unique_path(new_path)
    if fn.name == new_path.name:
        cprint("no change", "blue")
        return 0
    fn.rename(new_path)
    cprint(f"{fn.name} -> {new_path.name}", "green")
    return 0


def main() -> None:
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, extensions=[".ttf", ".woff", ".woff2"])
    if not files:
        print("no files found")
        return
    p = Pool(8)
    for _ in p.imap_unordered(process_file, files):
        pass
    p.close()
    p.join()


if __name__ == "__main__":
    main()
