import sys
from pathlib import Path

from dh import fsz, gsz
from fastwalk import walk_parallel


def empty_it(pth) -> None:
    Path(pth).write_text("", encoding="utf-8")


def remove_it(fp) -> None:
    if not fp.is_symlink():
        fp.unlink()


def load_junk():
    with Path("/sdcard/junk").open(encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    junk_files = load_junk()
    for pth in walk_parallel(cwd):
        path = Path(pth)
        if path.is_dir():
            continue
        if any(path.name.lower() == junk for junk in junk_files) and path.exists():
            remove_it(path)
            print(path.name)
    after = gsz(cwd)
    difsize = int(before - after)
    print(f"{fsz(difsize)}")


if __name__ == "__main__":
    sys.exit(main())
