#!/data/data/com.termux/files/usr/bin/env python
import os
import shutil
from pathlib import Path
from sys import exit
from time import perf_counter

ALLOWED = ["METADATA", "RECORD", "WHEEL", "entry_points.txt", "top_level.txt"]
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
    "INSTALLER",
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
    "REQUESTED",
    "gpl-3-0.txt",
    "metadata.json",
    "namespace_packages.txt",
    "pbr.json",
    "toplevel.txt",
    "zip-safe",
]


def process_lic(fp):
    lic_dir = Path(f"{fp}/licenses")
    if lic_dir.exists():
        shutil.rmtree(lic_dir)
        print(f"{lic_dir} removed.")
    for f in NOT_ALLOWED:
        nf = Path(f"{fp}/{f}")
        if nf.exists():
            nf.unlink()
            print(f"{nf} removed")
    rett = []
    for f in ALLOWED:
        nf = Path(f"{fp}/{f}")
        if not nf.exists() and not f == "entry_points.txt":
            rett.append(nf)
    return rett


def main():
    missings = []
    dir = "/data/data/com.termux/files/usr/lib/python3.12/site-packages"
    for pth in os.listdir(dir):
        path = Path(os.path.join(dir, pth))
        if path.is_dir() and "dist-info" in path.name:
            missings.extend(process_lic(path))
    for k in missings:
        print(f"{k.parent.name}  ==> {k.name} missing")


if __name__ == "__main__":
    exit(main())
