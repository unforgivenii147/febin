#!/data/data/com.termux/files/usr/bin/env python
import importlib.metadata
import sys
from pathlib import Path


def get_installed_packages():
    return {
        dist.metadata["Name"].lower()
        for dist in importlib.metadata.distributions()
    }


def read_requirements(filename):
    req_file = Path(filename)
    if not req_file.exists():
        raise FileNotFoundError("file not found in current directory")
    with open(req_file) as f:
        return [
            line.strip().replace("-", "_").lower() for line in f
            if line.strip() and not line.startswith("#")
        ]


def write_requirements(lines, filename):
    with open(filename, "w") as f:
        f.write("\n".join(lines) + "\n")


def strip_installed_from_requirements(fname):
    installed = get_installed_packages()
    lines = read_requirements(fname)
    new_lines = [line for line in lines if line not in installed]
    write_requirements(new_lines, fname)
    removed = len(lines) - len(new_lines)
    print(f"Removed {removed} installed package(s).")


if __name__ == "__main__":
    fn = sys.argv[1]
    strip_installed_from_requirements(fn)
