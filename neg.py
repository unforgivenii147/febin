#!/data/data/com.termux/files/usr/bin/python
from multiprocessing import Pool
from pathlib import Path
import sys

import cv2 as cv
from dh import get_files


def process_file(fp):
    img = cv.imread(str(fp))
    if not img:
        return
    img = 255 - img
    cv.imwrite(str(fp), img)
    print(f"{fp} updated.")


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(arg) for arg in args]
        if args
        else get_files(
            root_dir,
            recursive=True,
            extensions=[".png", ".jpg"],
        )
    )

    pool = Pool(4)
    pool.map(process_file, files)
    pool.close()
    pool.join()
    print("done.")


if __name__ == "__main__":
    sys.exit(main())
