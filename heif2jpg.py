#!/data/data/com.termux/files/usr/bin/env python
from multiprocessing import Pool
from pathlib import Path
from sys import exit

from dh import get_size
from fastwalk import walk_files
import pillow_heif as ph


def process_file(fp):
    if not fp.exists():
        return False
    print(f"[OK] {fp.name}")
    img = ph.open_heif(fp)
    outfile = fp.with_suffix(".jpg")
    img.save(outfile)
    return True


def main():
    dir = Path().cwd()
    start_size = get_size(dir)
    files = []
    for pth in walk_files(dir):
        path = Path(pth)
        if path.is_file() and path.suffix in {
            ".heif",
            ".heic",
        }:
            files.append(path)
    pool = Pool(8)
    pool.imap_unordered(process_file, files)
    pool.close()
    pool.join()
    after = get_size(dir)
    print(f"{fornat_size(abs(after - start_size))}")


if __name__ == "__main__":
    exit(main())
