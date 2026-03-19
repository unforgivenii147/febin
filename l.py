#!/data/data/com.termux/files/usr/bin/python
import datetime
import os
from pathlib import Path
from dh import get_size,format_size
from termcolor import cprint

if __name__=="__main__":

    root_dir = Path.cwd()

    for path in sorted(root_dir.glob("*"),key=lambda e: e.stat().st_size,):
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%H:%M")
        if path.is_file() or path.is_dir():
            sz = str(format_size(get_size(path)))
            if len(sz)==7:
                sz="  "+sz
            if len(sz)==8:
                sz=" "+sz
        elif path.is_symlink():
            sz = " symlink "
        cprint(f"{path.name[:24]:25}","blue",end=" ")
        cprint(f"{sz}","cyan",end=" ")
        cprint(f"{mtime}","yellow")
