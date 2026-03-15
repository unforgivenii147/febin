#!/data/data/com.termux/files/usr/bin/env python
from collections import deque
from multiprocessing import Pool
from pathlib import Path
import sys

from dh import format_size, get_files, get_size

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
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, extensions=[".py"])
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diffsize = before - get_size(root_dir)
    print(f"space saved: {format_size(diffsize)}")


if __name__ == "__main__":
    main()
