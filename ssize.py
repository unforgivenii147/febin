#!/data/data/com.termux/files/usr/bin/python

import operator
from pathlib import Path


def gsz(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def list_and_sort_by_size(path: Path = Path()):
    items = []
    for p in path.glob("*"):
        size = gsz(p)
        items.append({"name": p.name, "size": size})
    items.sort(key=operator.itemgetter("size"), reverse=False)
    return items


data = list_and_sort_by_size()
for k in data:
    print(f"{k['name']}:{k['size']}")
