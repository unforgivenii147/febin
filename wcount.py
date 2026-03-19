#!/data/data/com.termux/files/usr/bin/env python
from collections import deque
import json
from pathlib import Path
import sys

from dh import get_nobinary
from loguru import logger
from multiprocessing import Pool
from toolz import compose, frequencies
from toolz.curried import map

MAX_QUEUE = 16


def stem(word):
    return word.lower().rstrip(",.|;:'\"").lstrip("'\"")


def process_file(fp):
    if fp.is_symlink():
        logger.info(f"skipping symlink {fp.name}")
    logger.info(f"{fp.name}")
    word_count = compose(frequencies, map(stem), str.split)
    content = fp.read_text(encoding="utf-8")
    return word_count(content)
    #    logger.info(sorted(result))


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_nobinary(root_dir)
    results = {}
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                result = pending.popleft().get()
                for x in result:
                    if x not in results:
                        results[x] = result.get(x)
                    else:
                        results[x] += result.get(x)
        while pending:
            result = pending.popleft().get()
            for x in result:
                if x not in results:
                    results[x] = result.get(x)
                else:
                    results[x] += result.get(x)

    outfile = Path("word_count.json")
    wsorted = []
    for key in results:
        wsorted.append(results.get(key))
    wsorted = sorted(wsorted, reverse=True)
    word_sorted = {}
    for item in wsorted:
        word_sorted[item] = results.get(item)
    with open(outfile, "w") as fo:
        json.dump(word_sorted, fo, ensure_ascii=False, indent=2)


#        for v in results.keys():
#            fo.write(f"{str(v)} : {str(results.get(v))}\n")

if __name__ == "__main__":
    main()
