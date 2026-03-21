#!/data/data/com.termux/files/usr/bin/python
import json
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path

import xmltodict
from termcolor import cprint

MAX_QUEUE = 16


def process_file(path):
    try:
        jsonpath = path.with_suffix(".json")
        cprint(f"{jsonpath} created.", "cyan")
        xml_content = path.read_text(encoding="utf-8", errors="ignore")

        with open(jsonpath, "w") as f:
            data = xmltodict.parse(xml_content)
            json.dump(data, f, indent=4)
    except:
        print("error")


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else list(root_dir.rglob("*.xml"))

    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    print("done.")


if __name__ == "__main__":
    main()
