import ast
import sys
from pathlib import Path

from dh import cpf, mpf3a

cwd = Path.cwd()
err_dir = Path(f"{cwd}/ERROR")
err_dir.mkdir(exist_ok=True)


def process_file(fp) -> None:
    content = fp.read_text(encoding="utf-8")
    try:
        ast.parse(content)
    except:
        newpath = err_dir / fp.name
        newpath = Path(newpath)
        cpf(fp, newpath)


def main():
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else [Path(p) for p in cwd.glob("*.py")]
    mpf3a(process_file, files)


if __name__ == "__main__":
    sys.exit(main())
