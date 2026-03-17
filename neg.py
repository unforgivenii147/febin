#!/data/data/com.termux/files/usr/bin/env python
from collections import deque
from multiprocess import Pool
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
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > 16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    print("done.")


if __name__ == "__main__":
    sys.exit(main())
