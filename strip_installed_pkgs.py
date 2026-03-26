#!/data/data/com.termux/files/usr/bin/python
from importlib.metadata import distributions
from pathlib import Path
import sys

from dh import STDLIB


def get_installed_packages():
    return {dist.metadata["Name"] for dist in distributions()}


def read_requirements(filename):
    req_file = Path(filename)
    if not req_file.exists():
        msg = "file not found in current directory"
        raise FileNotFoundError(msg)
    with open(req_file, encoding="utf-8") as f:
        return [line.strip().replace("-", "_").lower() for line in f if line.strip() and not line.startswith("#")]


def write_requirements(lines, filename):
    Path(filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def strip_installed_from_requirements(fname):
    installed = get_installed_packages()
    installed = [p.lower().replace("-", "_") for p in installed if p]
    lines = read_requirements(fname)
    new_lines = [line for line in lines if line not in installed]
    stdlib = list(STDLIB)
    new_lines = [line for line in new_lines if line not in stdlib]
    write_requirements(new_lines, fname)
    removed = len(lines) - len(new_lines)
    print(f"Removed {removed} installed package(s).")


if __name__ == "__main__":
    fn = sys.argv[1]
    strip_installed_from_requirements(fn)
