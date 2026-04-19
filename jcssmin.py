import sys
from pathlib import Path

from dh import get_files, gext, mpf
from rcssmin import cssmin


def process_file(path) -> str:
    try:
        ext = gext(path)
        content = Path(path).read_text(encoding="utf-8")
        if ext in {".css", ".min.css"}:
            minified = cssmin(content)

        else:
            return f"SKIP (unknown type) → {path}"
        if len(minified) == len(content):
            return f"[NO CHANGE] {path.name}"
        Path(path).write_text(minified, encoding="utf-8")
        return f"[OK] {path.name}"
    except Exception as e:
        return f"[ERROR] ({path}): {e}"


def main() -> None:
    cwd = Path.cwd()
    files = get_files(cwd, extensions=[".css", ".min.css"])
    if not files:
        print("No CSS files found.")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    print(f"Found {len(files)} files. Starting multiprocessing...")
    for k in mpf(process_file, files):
        print(k)


if __name__ == "__main__":
    main()
