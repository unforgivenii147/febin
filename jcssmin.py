#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

from dh import mpf
from fastwalk import walk_files
from rcssmin import cssmin


def process_file(path) -> str:
    try:
        content = Path(path).read_text(encoding="utf-8")
        if path.suffix == ".css" or ".min.css" in path.name:
            minified = cssmin(content)
        else:
            return f"SKIP (unknown type) → {path}"
        if len(minified) == len(content):
            return f"[NO CHANGE] {path.name}"
        Path(path).write_text(minified, encoding="utf-8")
        return f"[OK] {path.name}"
    except Exception as e:
        return f"[ERROR] ({path}): {e}"


def collect_files() -> list:
    targets = []
    root = Path.cwd()
    EXT = {".css", ".min.css"}
    for pth in walk_files(root):
        path = Path(pth)
        if path.is_file() and path.suffix in EXT:
            targets.append(path)
    return targets


def main() -> None:
    files = collect_files()
    if not files:
        print("No CSS files found.")
        return
    print(f"Found {len(files)} files. Starting multiprocessing...")
    for k in mpf(process_file, files):
        print(k)


if __name__ == "__main__":
    main()
