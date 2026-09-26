#!/data/data/com.termux/files/usr/bin/python
"""Recursively build wheels for every project under the current directory.

Walks the tree looking for ``setup.py`` (built with ``bdist_wheel``) and
``pyproject.toml`` (built with ``python -m build -w``, skipped when a wheel
already exists), then reports how many ``*.whl`` files ended up present.
"""

import os
from pathlib import Path

from dh import run_command

if __name__ == "__main__":
    cwd: Path = Path.cwd()

    # Legacy setuptools projects.
    for path in cwd.rglob("setup.py"):
        pardir: Path = path.parent
        os.system(f"cd {pardir!s}")
        os.chdir(str(pardir))
        cmd: str = f"python {path!s} bdist_wheel"
        ret, _, _ = run_command(cmd)
        if ret != 0:
            print("ok")

    # PEP 517 projects, skipping any that already produced a wheel.
    for path in cwd.rglob("pyproject.toml"):
        pardir = path.parent
        distdir: Path = pardir / "dist"
        whlfile: list[Path] = list(pardir.rglob("*.whl"))
        if whlfile:
            continue
        os.system(f"cd {pardir!s}")
        os.chdir(str(pardir))
        cmd = "python -m build -w"
        ret, _, _ = run_command(cmd)
        if not ret:
            print("ok")
            continue

    allwhl: list[Path] = list(cwd.rglob("*.whl"))
    print(f"done {len(allwhl)} wheels crwated.")
