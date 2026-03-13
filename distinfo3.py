#!/data/data/com.termux/files/usr/bin/env python
import os
from sys import exit
from pathlib import Path
import shutil
from termcolor import cprint


def process_dir(dr):
    print(dr.name)
    if "dist-info" in str(dr.name):
        for k in os.listdir(dr):
            if k == "top_level.txt" or k == "entry_points.txt":
                cprint(f"{dr} removed", "cyan")
                shutil.rmtree(dr)

    return

    return True


def main():

    dir = "/data/data/com.termux/files/usr/lib/python3.12/site-packages"
    for pth in os.listdir(dir):
        path = Path(os.path.join(dir, pth))

        if path.is_dir() and len(os.listdir(path)) == 1:
            process_dir(path)


if __name__ == "__main__":
    exit(main())
