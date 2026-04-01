#!/data/data/com.termux/files/usr/bin/python
import sys
import time
from pathlib import Path
from datetime import datetime
import operator


def parse_minutes() -> float:
    if len(sys.argv) == 1:
        return 60.0
    try:
        return float(sys.argv[1])
    except ValueError:
        print("Invalid argument. Usage: script.py [minutes]")
        sys.exit(1)


def main() -> None:
    minutes = parse_minutes()
    ctm = {}
    cwd = Path.cwd()
    cutoff = time.time() - (minutes * 60)
    for path in cwd.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir():
            continue
        stats = path.stat()
        created = stats.st_ctime
        modified = stats.st_mtime
        changed = stats.st_ctime
        if created <= cutoff or modified >= cutoff or changed >= cutoff:
            ctm[path] = created
    ctmsorted = dict(sorted(ctm.items(), key=operator.itemgetter(1)))
    newct = {}
    for pth, ct in ctmsorted.items():
        ctime = datetime.fromtimestamp(ct).strftime("%Y-%m-%d|%H:%M")
        newct[pth] = ctime
        path_str = str(pth.relative_to(cwd))

        max_path_len = max(len(path_str), 20)
        print(f"{path_str:<{max_path_len}} : {ctime}")


if __name__ == "__main__":
    main()
