#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib

EXCLUDE_DIRS = {".git"}
OUTPUT_FILE = "merged.txt"


def read_file(path):
    try:
        with pathlib.Path(path).open(encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def collect_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            if (
                pathlib.Path(full).resolve() == pathlib.Path(OUTPUT_FILE).resolve()
                or fname == pathlib.Path(__file__).name
            ):
                continue
            yield full


def merge_files(root):
    files = list(collect_files(root))
    print(f"Found {len(files)} files")
    with pathlib.Path(OUTPUT_FILE).open("w", encoding="utf-8") as fo:
        for i, path in enumerate(files, 1):
            content = read_file(path)
            if content is None:
                continue
            fo.write(f"########### {path} ##########\n\n\n")
            fo.write(content)
            if i != len(files):
                fo.write("\n\n\n")
            print(f"Added: {path}")
    print(f"\nsaved as: {OUTPUT_FILE}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Merge files recursively into merged.txt")
    ap.add_argument(
        "--path",
        default=".",
        help="Directory to scan",
    )
    args = ap.parse_args()
    merge_files(args.path)
