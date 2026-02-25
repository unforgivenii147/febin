#!/data/data/com.termux/files/usr/bin/env python3
from pathlib import Path


def to_lowercase(path):
    path = Path(path)
    for item in path.rglob("*"):
        if item.is_dir() or item.is_file():
            new_name = item.name.lower()
            new_path = item.with_name(new_name)

            if new_path != item and not new_path.exists():
                item.rename(new_path)
                print(f"Renamed: {item} -> {new_path}")
            else:
                print(f"Skipping {item} (already exists or no change)")


if __name__ == "__main__":
    current_dir = Path.cwd()
    print(f"Converting file and directory names to lowercase in: {current_dir}")
    to_lowercase(current_dir)
    print("Done!")
