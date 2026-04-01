#!/data/data/com.termux/files/usr/bin/python
import os
from sys import exit
import shutil
from pathlib import Path

from termcolor import cprint


ALLOWED = [
    "METADATA",
    "RECORD",
    "WHEEL",
    "top_level.txt",
]
NOT_ALLOWED = [
    "AUTHORS",
    "AUTHORS.md",
    "AUTHORS.rst",
    "AUTHORS.txt",
    "BSD-0-Clause.rst",
    "BSD-2-Clause.rst",
    "CONTRIBUTORS.txt",
    "COPYING",
    "COPYING.GPL",
    "COPYING.LESSER",
    "COPYING.LGPL",
    "COPYING.MPL",
    "COPYING.rst",
    "COPYING.txt",
    "DESCRIPTION.rst",
    "LICENCE",
    "LICENCE.rst",
    "LICENSE",
    "LICENSE-APACHE",
    "LICENSE.APACHE2",
    "LICENSE.markdown-it",
    "LICENSE.md",
    "LICENSE.rst",
    "LICENSE.txt",
    "LICENSE_numpy.txt",
    "LICENSE_scipy.txt",
    "NOTICE",
    "NOTICE.txt",
    "gpl-3-0.txt",
    "pbr.json",
    "toplevel.txt",
]


def process_lic(fp):
    lic_dir = Path(f"{fp}/licenses")
    if lic_dir.exists():
        shutil.rmtree(lic_dir)
        print(f"{lic_dir} removed.")

    rett = []
    for f in ALLOWED:
        nf = Path(f"{fp}/{f}")
        if not nf.exists() and f != "entry_points.txt":
            rett.append(nf)
    return rett


def main():
    missings = []
    cwd = Path("/data/data/com.termux/files/usr/lib/python3.12/site-packages")
    for pth in os.listdir(cwd):
        path = Path(os.path.join(cwd, pth))
        if path.is_dir() and "dist-info" in path.name:
            if len(os.listdir(path)) < 2:
                cprint(
                    f"{path.name} empty pkg",
                    "cyan",
                )
            missings.extend(process_lic(path))
    for k in missings:
        print(f"{k.parent.name}  ==>", end=" ")
        cprint(f"{k.name}", "yellow")


if __name__ == "__main__":
    exit(main())
