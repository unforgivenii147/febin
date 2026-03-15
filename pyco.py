#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import shutil
import sysconfig

from dh import format_size
from fastwalk import walk_files, walk_dirs
from termcolor import cprint


def get_skip_dirs():
    skip = set()
    site_packages = Path(sysconfig.get_paths()["purelib"])
    for d in (
        "regex",
        "pip",
        "wheel",
        "setuptools",
        "packaging",
    ):
        skip.add(str(site_packages / d))
    return skip


def clean_pyc_and_pycache(
    start_dir: Path = Path.cwd(),
):
    total_size = 0
    dirs_removed = 0
    files_removed = 0
    d2r = []
    skip_dirs = get_skip_dirs()
    for pth in walk_files(start_dir):
        path = Path(pth)
        if path.is_file() and any(pat in str(path) for pat in skip_dirs):
            continue
        if path.is_file() and path.suffix == ".pyc":
            try:
                if path.parent.name != "__pycache__":
                    twin_path = path.with_suffix(".py")
                else:
                    parent_dir = path.parent.parent
                    twin_path = Path(str(parent_dir) + "/" + str(path.stem).replace(".cpython-312", "") + ".py")
                #                print(twin_path)
                if twin_path.exists():
                    size = path.stat().st_size
                    path.unlink()
                    total_size += size
                    files_removed += 1
                else:
                    cprint("lonely pyc file", "cyan")
            except Exception as e:
                print(f"⚠️ error deleting {path}: {e}")

    for dirp in walk_dirs(start_dir):
        path = Path(dirp)
        if path.is_dir() and path.name == "__pycache__":
            d2r.append(path)
        if path.is_dir() and ".git" in path.parts:
            continue
        if path.is_dir() and any(str(path).startswith(sd) for sd in skip_dirs):
            continue

    for d in d2r:
        if d.exists():
            try:
                shutil.rmtree(d)
                dirs_removed += 1
            except Exception as e:
                print(f"⚠️ Could not delete {path}: {e}")
    print(f"   • .pyc files removed: {files_removed}")
    print(f"   • Total size freed: {format_size(total_size)}")
    print(f"   • __pycache__ directories removed: {dirs_removed}")


if __name__ == "__main__":
    clean_pyc_and_pycache()
