#!/data/data/com.termux/files/usr/bin/env python
import os
import sys
from pathlib import Path
import cv2 as cv
from dh import get_files
from collections import deque
from multiprocessing import Pool

def process_file(fp):
    img = cv.imread(str(fp))
    if not img:
        return
    img = 255 - img
    cv.imwrite(str(fp), img)
    print(f"{fp} updated.")


def main():
    args=sys.argv[1:]
    if args:
        files=[Path(arg) for arg in args]
    else:
        files=get_files(dir,recursive=True,extensions=[".png",".jpg"])
    with Pool(8) as pool:
        pending=deque()
        for f in files:
            pending.append(pool.apply_async(process_file,(f,)))
            if len(pending)>16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    print("done.")



if __name__ == "__main__":
    sys.exit(main())
