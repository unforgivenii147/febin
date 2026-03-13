#!/data/data/com.termux/files/usr/bin/env python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import regex as re
from dh import format_size, get_files, get_size

MAX_QUEUE = 16

image_re = re.compile(
    r"((.*)+ image::(.*)+)|((.*)+:target:(.*)+)|((.*)+:alt:(.*)+)", re.I)


def process_file(path):
    content = path.read_text()
    c = 0
    lines = content.splitlines()
    nl = []
    for line in lines:
        matc = image_re.match(line)
        if not matc:
            nl.append(line)
        else:
            print(line)
            c += 1
    if not c:
        return
    newcontent = "\n".join(nl)
    path.write_text(newcontent, encoding="utf-8")
    print(f"{path.relative_to(path.parent)} updated.")


def main():
    dir = Path.cwd()
    before = get_size(dir)
    args = sys.argv[1:]

    files = ([Path(f) for f in args] if args else get_files(
        dir, recursive=True, extensions=[".metadata", ".md", ".txt", ".rst"]))
    metafiles = list(dir.rglob("METADATA"))
    if metafiles:
        files.extend(metafiles)

    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f, )))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
