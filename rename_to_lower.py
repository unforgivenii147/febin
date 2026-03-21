#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

from dh import unique_path


def to_lowercase(path):
    path = Path(path)
    for item in path.rglob("*"):
        if item.is_dir() or item.is_file():
            if ".git" in item.parts:
                continue
            new_name = item.name.lower()
            new_path = item.with_name(new_name)
            if new_path != item and not new_path.exists():
                item.rename(new_path)
                print(f"[{item.name}] -> [{new_path.name}]")
            else:
                new_path = unique_path(new_path)
                item.rename(new_path)
                if "_1." in item.name:
                    new_name = item.stem.replace("_1", "") + item.suffix
                    new_path = item.with_name(new_name)
                    item.rename(new_path)


if __name__ == "__main__":
    current_dir = Path.cwd()
    print(
        f"Converting file and directory names to lowercase in: {current_dir}")
    to_lowercase(current_dir)
