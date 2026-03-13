#!/data/data/com.termux/files/usr/bin/env python
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_pyfiles, get_size

MAX_QUEUE = 16


def process_file(path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        new_lines = []
        if lines[0].startswith("#!/"):
            new_lines = lines[1:]
            content = "\n".join(new_lines)
            path.write_text(content, encoding="utf-8")
            print(f"{path.name} updated.")
            return
        else:
            return
    except Exception:
        pass


def main() -> None:
    dir = Path.cwd()
    before = get_size(dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_pyfiles(dir)
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f, )))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    after = get_size(dir)
    print(f"space saved: {format_size(before - after)}")


if __name__ == "__main__":
    main()
