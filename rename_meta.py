#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import shutil
from sys import exit

from dh import unique_path
from fastwalk import walk_files

OUT_PATH = Path("/data/data/com.termux/files/home/tmp/metadata")
OUT_PATH.mkdir(parents=True, exist_ok=True)


def process_file(fp):
    if not fp.exists():
        return False
    line1 = fp.read_text().splitlines()[1]
    striped = line1.lower().strip()
    if striped.startswith("name:"):
        pkgname = striped.replace("name:", "").lstrip()
        outfn = pkgname + ".metadata"
        outpath = Path(OUT_PATH) / outfn
        if outpath.exists():
            outpath = unique_path(outpath)
        shutil.copy2(fp, outpath)
        print(f"{outpath} created.")
    return None


def main():
    root_dir = Path.cwd()
    for pth in walk_files(root_dir):
        path = Path(pth)
        if path.is_file() and (path.name == "METADATA" or path.suffix in {".metadata", ".md"}):
            process_file(path)


if __name__ == "__main__":
    exit(main())
