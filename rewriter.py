#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path

import astunparse
import unidecode
from dh import format_size, get_pyfiles, get_size, is_binary, mpf
from termcolor import cprint


def process_file(fn: Path) -> bool:
    if is_binary(fn):
        return False
    try:
        content = fn.read_text(encoding="utf-8", errors="ignore")
        backup_file=fn.with_suffix(fn.suffix+".bak")
        backup_file.write_text(content,encoding="utf-8")
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
    _ = mpf(process_file, files)
    diffsize = before - get_size(cwd)
    print(f"space change: {format_size(diffsize)}")


if __name__ == "__main__":
    sys.exit(main())
