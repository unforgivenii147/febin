#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_size, is_binary, format_size, get_pyfiles
from termcolor import cprint
import unidecode
import astunparse


MAX_QUEUE = 16


def process_file(fn: Path) -> bool:
    if is_binary(fn):
        return False
    try:
        content = fn.read_text(encoding="utf-8", errors="ignore")
        new_content = content
        if fn.suffix == ".py":
            try:
                tree = ast.parse(content)
                new_content = astunparse.unparse(tree)
                fn.write_text(new_content, encoding="utf-8")
                print(f"{fn.name} rewrited.")
                return True
            except:
                cprint(f"{fn.name} ast parse error", "cyan")
                return False
        else:
            new_content = unidecode.normalize(content)
            fn.write_text(new_content, encoding="utf-8")
    except:
        return False


def main() -> None:
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_pyfiles(cwd)
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    results = []
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                results.append(pending.popleft().get())
        while pending:
            results.append(pending.popleft().get())
    diffsize = before - get_size(cwd)
    print(f"space change: {format_size(diffsize)}")


if __name__ == "__main__":
    sys.exit(main())
