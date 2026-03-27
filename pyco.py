#!/data/data/com.termux/files/usr/bin/python
import sys
import shutil
from pathlib import Path

from dh import format_size
from termcolor import cprint


def clean_pyc_and_pycache():
    cwd = Path.cwd()
    total_size = 0
    dirs_removed = 0
    files_removed = 0
    for path in cwd.rglob("*.pyc"):
        pyfile_samedir = path.with_name(
            path.name
            .replace(".cpython-312", "")
            .replace(".opt-1", "")
            .replace(".opt-2", "")
            .replace("-pytest-9.0.2", "")
        ).with_suffix(".py")
        pyfile_parentdir = path.parent.parent / pyfile_samedir.name
        if not pyfile_samedir.exists() and not pyfile_parentdir.exists():
            cprint(f"{pyfile_samedir} {pyfile_parentdir} does not exists so {path.name} is lonely pyc", "cyan")
            continue
        if pyfile_parentdir.exists() or pyfile_samedir.exists():
            sz = path.stat().st_size
            path.unlink()
            total_size += sz
            files_removed += 1

    d2r = [dirp for dirp in cwd.rglob("__pycache__") if dirp.is_dir()]

    for d in d2r:
        if d.exists():
            try:
                d.rmdir()
                dirs_removed += 1
            except Exception:
                try:
                    shutil.rmtree(str(d))
                    dits_temoved += 1
                except:
                    print(f"ertor removing {d}")

    if not files_removed and not dirs_removed:
        print("nothing found")
        sys.exit(0)
    print(f"files removed: {files_removed}")
    print(f"dirs  removed: {dirs_removed}")
    print(f"Total size: {format_size(total_size)}")


if __name__ == "__main__":
    clean_pyc_and_pycache()
