#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path

from dh import move_file

MAX_QUEUE = 16

cwd = Path.cwd()
ok_dir = Path(f"{cwd}/OK")
err_dir = Path(f"{cwd}/ERROR")
ok_dir.mkdir(exist_ok=True)
err_dir.mkdir(exist_ok=True)


def process_file(fp) -> None:
    content = fp.read_text()
    try:
        ast.parse(content)
        newpath = ok_dir / fp.name
        newpath = Path(newpath)
        move_file(fp, newpath)
        print(f"{fp.name} --> {newpath}")
    except:
        newpath = err_dir / fp.name
        newpath = Path(newpath)
        move_file(fp, newpath)
        print(f"{fp.name} --> {newpath}")


def main():
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else [Path(p) for p in cwd.glob("*.py")]
    for f in files:
        process_file(f)


"""
    with get_context('spawn').Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

"""

if __name__ == "__main__":
    sys.exit(main())
