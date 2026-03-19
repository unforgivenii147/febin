#!/data/data/com.termux/files/usr/bin/python
import datetime
from pathlib import Path

from dh import format_size, get_size


if __name__=="__main__":

    root_dir = Path.cwd()

    for path in sorted(root_dir.glob("*"),key=lambda e: e.stat().st_size,):
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%H:%M")

        if path.is_symlink():
            sz = " \033[05;95msymlink "

        if path.is_file() or path.is_dir():
            sz = str(format_size(get_size(path)))
            if len(sz)==7:
                sz="  "+sz
            if len(sz)==8:
                sz=" "+sz
        if path.is_symlink():
            print(f"\033[05;95m{path.name[:24]:25}\033[0m",end=" ")
        elif path.is_dir():
            print(f"\033[05;94m{path.name[:24]:25}\033[0m",end=" ")
        elif path.is_file():
            print(f"\033[05;92m{path.name[:24]:25}\033[0m",end=" ")

        print(f"\033[05;96m{sz}\033[0m",end=" ")
        print(f"\033[05;93m{mtime}\033[0m")
