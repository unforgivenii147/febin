#!/data/data/com.termux/files/usr/bin/python
import datetime
from pathlib import Path
from dh import format_size, get_size

if __name__ == "__main__":
    cwd = Path.cwd()
    dirz = []
    otherz = []
    for path in sorted(cwd.glob("*"), key=lambda e: e.stat().st_size, reverse=True):
        if path.is_dir():
            dirz.append(path)
        else:
            otherz.append(path)
    for f in otherz:
        ctime = datetime.datetime.fromtimestamp(f.stat().st_ctime).strftime("%H:%M")
        if f.is_symlink():
            sz = " \033[05;95msymlink "
            print(f"\033[05;95m{f.name[:24]:25}\033[0m", end=" ")
        else:
            sz = str(format_size(get_size(f)))
            match len(sz):
                case 3:
                    sz = "      " + sz
                case 4:
                    sz = "     " + sz
                case 5:
                    sz = "    " + sz
                case 6:
                    sz = "   " + sz
                case 7:
                    sz = "  " + sz
                case 8:
                    sz = " " + sz
            print(f"\033[05;92m{f.name[:24]:25}\033[0m", end=" ")
        print(f"\033[05;96m{sz}\033[0m", end=" ")
        print(f"\033[05;93m{ctime}\033[0m")
    for dr in dirz:
        ctime = datetime.datetime.fromtimestamp(dr.stat().st_ctime).strftime("%H:%M")
        sz = str(format_size(get_size(dr)))
        if len(sz) == 7:
            sz = "  " + sz
        if len(sz) == 8:
            sz = " " + sz
        print(f"\033[05;94m{dr.name[:24]:25}\033[0m", end=" ")
        print(f"\033[05;96m{sz}\033[0m", end=" ")
        print(f"\033[05;93m{ctime}\033[0m")
