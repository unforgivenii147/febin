#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import shutil
from sys import exit

from termcolor import cprint


def process_dir(dr):
    print(dr.name)
    if "dist-info" in str(dr.name):
        for k in os.listdir(dr):
            if k in {
                "top_level.txt",
                "entry_points.txt",
            }:
                cprint(f"{dr} removed", "cyan")
                shutil.rmtree(dr)

    return None

    return True


def main():

    root_dir = "/data/data/com.termux/files/usr/lib/python3.12/site-packages"
    for pth in os.listdir(root_dir):
        path = Path(os.path.join(root_dir, pth))

        if path.is_dir() and len(os.listdir(path)) == 1:
            process_dir(path)


if __name__ == "__main__":
    exit(main())
