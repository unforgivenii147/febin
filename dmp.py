#!/data/data/com.termux/files/usr/bin/python
from os.path import relpath
from pathlib import Path


EXCLUDED = {
    "tmp",
    "cache",
    "bin",
}
EXCLUDED2 = {
    "Android",
    ".git",
    "etc",
    "config",
    "var",
}
COUNT = 0
REMOVED_DIRS = []


def delete_empty_dirs(root: Path) -> None:
    global COUNT, REMOVED_DIRS
    for path in list(root.iterdir()):
        if path.is_dir():
            if path.name in EXCLUDED:
                continue
            if path.name.startswith("mc") and path.parent.name == "tmp":
                continue
            if any(pat in path.parts for pat in EXCLUDED2):
                continue
            delete_empty_dirs(path)
            try:
                if not any(path.iterdir()):
                    path.rmdir()
                    COUNT += 1
                    REMOVED_DIRS.append(relpath(path))
            except PermissionError:
                print(f"[ERR] {relpath(path)}")
            except OSError as e:
                print(f"[ERROR] {relpath(path)}: {e}")


if __name__ == "__main__":
    root = Path.cwd()
    delete_empty_dirs(root)
    if COUNT:
        print("\nRemoved directories:")
        for d in REMOVED_DIRS:
            print(f"- {d}")
        print(f"count: {COUNT}")
    else:
        print("no empty dirs found.")
