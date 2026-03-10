#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
from sys import argv
import tarfile
import zipfile

from dh import unique_path, get_files


def tar_xz_to_whl(tar_path: Path):
    target = tar_path.with_suffix(".whl")
    tt = str(target).replace(".tar", "")
    target = Path(tt)
    if target.exists():
        print(f"[SKIP] {target.name} already exists")
        target = unique_path(target)
    print(f"[TAR.XZ → WHL] {tar_path.name}")
    try:
        with (
            tarfile.open(tar_path, "r:xz") as tf,
            zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf,
        ):
            for member in tf.getmembers():
                if member.isdir():
                    continue
                extracted = tf.extractfile(member)
                if extracted is None:
                    continue
                zf.writestr(member.name, extracted.read())
        print(f"[OK] {target.name}")
    except Exception as e:
        print(f"[ERROR] {tar_path.name}: {e}")


def main():
    args = sys.argv[1:]
    dir = Path().cwd()
    if args:
        files = [Path(arg) for arg in args]
    else:
        files = get_files(dir, recursive=False, extensions=[".tar.xz", ".xz"])

    for f in files:
        tar_xz_to_whl(f)


if __name__ == "__main__":
    sys.exit(main())
