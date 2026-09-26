#!/data/data/com.termux/files/usr/bin/python

import sys
from multiprocessing import Pool
from pathlib import Path

from dh import fsz, get_nobinary, gsz

STRTOFIND = [
    "dist-info",
    ".so",
    ".py",
    ".pth",
    "__",
    ".zip",
]


def clean_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not any(s in line for s in STRTOFIND))


def clean_file(path: str | Path) -> None:
    """Strip unwanted lines from ``path`` in place."""
    try:
        original = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    cleaned = clean_text(original)
    if cleaned != original:
        Path(path).write_text(cleaned, encoding="utf-8")


def main() -> None:
    root = Path.cwd()
    isz = gsz(root)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(root)
    if len(files) == 1:
        clean_file(files[0])
        sys.exit(0)
    with Pool(8) as pool:
        for f in files:
            pool.apply_async(clean_file, (f,))
        pool.close()
        pool.join()
    esz = gsz(root)
    diffsize = isz - esz
    print(f"space freed : {fsz(diffsize)}")


if __name__ == "__main__":
    main()
