#!/data/data/com.termux/files/usr/bin/python
import json
from pathlib import Path


def get_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def list_and_sort_by_size(path: Path = Path()):
    items = []
    for p in path.glob("*"):
        size = get_size(p)
        items.append({"name": p.name, "size": size})
    items.sort(key=lambda x: x["size"], reverse=True)
    return items


data = list_and_sort_by_size()

with open("directory_sizes.json", "w") as out:
    json.dump(data, out, indent=4)

print("Saved to directory_sizes.json")
