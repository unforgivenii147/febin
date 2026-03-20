#!/data/data/com.termux/files/usr/bin/python
import datetime
from pathlib import Path

from dh import format_size, get_size

if __name__ == "__main__":
    root_dir = Path.cwd()
    dirz = []
    otherz = []

    for path in sorted(
        root_dir.glob("*"),
        key=lambda e: e.stat().st_size,
    ):
        if path.is_dir():
            dirz.append(path)

        else:
            otherz.append(path)

    for f in otherz:
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M")
        if f.is_symlink():
            sz = " \033[05;95msymlink "
            print(f"\033[05;95m{f.name[:24]:25}\033[0m", end=" ")
        else:
            sz = str(format_size(get_size(f)))
            if len(sz) == 7:
                sz = "  " + sz
            if len(sz) == 8:
                sz = " " + sz
            print(f"\033[05;92m{f.name[:24]:25}\033[0m", end=" ")
        print(f"\033[05;96m{sz}\033[0m", end=" ")
        print(f"\033[05;93m{mtime}\033[0m")

    for dr in dirz:
        mtime = datetime.datetime.fromtimestamp(dr.stat().st_mtime).strftime("%H:%M")
        sz = str(format_size(get_size(dr)))
        if len(sz) == 7:
            sz = "  " + sz
        if len(sz) == 8:
            sz = " " + sz
        print(f"\033[05;94m{dr.name[:24]:25}\033[0m", end=" ")
        print(f"\033[05;96m{sz}\033[0m", end=" ")
        print(f"\033[05;93m{mtime}\033[0m")
