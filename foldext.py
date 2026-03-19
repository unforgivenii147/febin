#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import shutil

from dh import unique_path

NO_EXT_DIR = "no_ext"


def folderize_by_extension():
    base_dir = Path.cwd()
    for path in base_dir.rglob("*"):
        if path.is_dir():
            continue
        if path.is_file() and not path.is_symlink():
            _name = path.stem
            ext = path.suffix.lower().lstrip(".")
            target_dir = ext if ext else NO_EXT_DIR
            target_path = base_dir / target_dir
            if not target_path.exists():
                target_path.mkdir(exist_ok=True)
            dest_path = target_path / path.name
            if dest_path.exists():
                dest_path = unique_path(dest_path)
            shutil.move(path, dest_path)


if __name__ == "__main__":
    folderize_by_extension()
