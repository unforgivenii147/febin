from multiprocessing import get_context
from collections import deque
from pathlib import Path


def process_file(fp):
    return fp.stat().st_size


def mpf(process_file, files):
    with get_context("spawn").Pool(8) as p:
        pending = deque()
        for f in files:
            pending.append(p.apply_async(process_file, (f,)))
            if len(pending) >= MAX_IN_FLIGHT:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


if __name__ == "__main__":
    cwd = Path.cwd()
    files = [p for p in cwd.rglob("*")]
    mpf(process_file, files)
