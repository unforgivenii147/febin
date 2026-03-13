#!/data/data/com.termux/files/usr/bin/env python
import json
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import xmltodict

MAX_QUEUE = 16


def process_file(path):
    jsonpath = path.with_suffix(".json")
    with open(jsonpath, "w") as f:
        data = xmltodict.parse(path.read_text(encoding="utf-8"))
        json.dump(data, f)
    print(f"{jsonpath} created.")


def main():
    dir = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else list(dir.rglob("*.xml"))

    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f, )))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    print("done.")


if __name__ == "__main__":
    main()
