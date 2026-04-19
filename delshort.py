import sys
from pathlib import Path

from dh import is_binary
from fastwalk import walk_files


def process_file(fp) -> None:
    if not fp.exists():
        return
    if fp.exists() and fp.stat().st_size < 50 and len(fp.read_text().splitlines()) < 3:
        fp.unlink()
        print(f"{fp.name} removed")
    if fp.exists() and len(fp.read_text().splitlines()) < 2 and fp.suffix not in {".js", ".min.js", ".css", ".min.css"}:
        fp.unlink()
        print(f"{fp.name} removed")


def main() -> None:
    for pth in walk_files("."):
        path = Path(pth)
        if not is_binary(path) and path.exists():
            process_file(path)
        else:
            print(f"{path.name} is binary")


if __name__ == "__main__":
    sys.exit(main())
