#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path

from dh import get_files, is_binary
from pbar import Pbar
from termcolor import cprint


def process_file(fn: Path, backup=False) -> bool:
    if is_binary(fn):
        return False
    try:
        content = fn.read_text(encoding="utf-8", errors="ignore")
        if backup:
            backup_file = fn.with_suffix(fn.suffix + ".bak")
            backup_file.write_text(content, encoding="utf-8")
        new_content = content
        if fn.suffix == ".py":
            try:
                tree = ast.parse(content)
                new_content = ast.unparse(tree)
                fn.write_text(new_content, encoding="utf-8")
                print(f"{fn.name} rewrited.")
                return True
            except:
                cprint(f"{fn.name} ast parse error", "cyan")
                return False
        else:
            new_content = unidecodedata.normalize("NFKD", content)
            fn.write_text(new_content, encoding="utf-8")
    except:
        return False


def main() -> None:
    cwd = Path.cwd()
    args = sys.argv[1:]
    backup = sys.argv[2] if len(sys.argv) > 2 else False
    files = [Path(arg) for arg in args] if args else get_files(cwd)
    with Pbar("") as pbar:
        for path in pbar.wrap(files):
            process_file(path, backup=backup)


if __name__ == "__main__":
    raise SystemExit(main())
