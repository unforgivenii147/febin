#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from collections import deque
from multiprocessing import Pool

from dh import get_size, get_files, format_size
import regex as re


MAX_QUEUE = 16
image_re = re.compile(
    r"((.*)+ image::(.*)+)|((.*)+:target:(.*)+)|((.*)+:alt:(.*)+)",
    re.I,
)
blank_line = "\n"


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
            nl.append(blank_line)
            print(line)
            c += 1
    if not c:
        return
    newcontent = "\n".join(nl)
    path.write_text(newcontent, encoding="utf-8")
    print(f"{path.relative_to(path.parent)} updated.")


def main():
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = (
        [Path(f) for f in args]
        if args
        else get_files(
            cwd,
            recursive=True,
            extensions=[".metadata", ".md"],
        )
    )
    metafiles = list(cwd.rglob("METADATA"))
    if metafiles:
        files.extend(metafiles)
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(cwd)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
