#!/data/data/com.termux/files/usr/bin/python
import os
import shutil
from pathlib import Path

from packaging.tags import parse_tag
from packaging.utils import canonicalize_name
from packaging.version import Version


def is_valid_wheel_name(filename):
    try:
        basename = filename[:-4]
        parts = basename.split("-")
        if len(parts) != 5:
            return False
        (
            dist_name,
            version,
            build_tag,
            py_tag,
            abi_platform,
        ) = parts
        if canonicalize_name(dist_name) != dist_name.lower():
            return False
        try:
            Version(version)
        except Exception:
            return False
        if not build_tag[0].isdigit():
            return False
        try:
            parse_tag(py_tag + "-" + abi_platform + "-" + abi_platform.split("-")[-1])
        except Exception:
            return False
        return True
    except Exception:
        return False


def main():
    invalid_dir = Path("invalid_wheels")
    invalid_dir.mkdir(exist_ok=True)
    cwd = Path.cwd()
    for path in cwd.iterdir():
        if path.suffix == ".whl":
            if not is_valid_wheel_name(path):
                print(f"Invalid wheel name: {path}")
                dest = invalid_dir / path.name
                shutil.move(str(path), str(dest))
            else:
                print(f"Valid wheel name: {filename}")


if __name__ == "__main__":
    main()
