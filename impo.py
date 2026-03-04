#!/data/data/com.termux/files/usr/bin/env python
import shutil
import subprocess
import sys
from os.path import exists
from pathlib import Path

from dh import move_file

if __name__ == "__main__":
    dir = Path.cwd()
    if "dist-info" in str(dir):
        print("dist-info dir.")
        sys.exit(0)
    if exists("importz.txt"):
        print("importz.txt exists")
        sys.exit(0)
    subprocess.run(["eximports"])
    subprocess.run(["imports", "output"])
    if exists("output/importz.txt"):
        move_file("output/importz.txt", "importz.txt")
    shutil.rmtree("output")
