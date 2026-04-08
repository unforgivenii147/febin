#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dh import get_filez


def process_file(fp):
    if not fp.exists():
        return (False, fp)
    ret = subprocess.run(
        [
            "prettier",
            "-w",
            str(fp).replace("/storage/emulated/0", "/sdcard"),
        ],
        check=True,
    )
    if ret:
        return (True, fp)
    return (False, fp)


def main():
    cwd = str(Path.cwd())
    args = sys.argv[1:]
    files = (
        [Path(f) for f in args]
        if args
        else get_filez(cwd, exts=[".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".css", ".md", ".jsm", ".scss"])
    )
    with ThreadPoolExecutor(8) as executor:
        futures = [executor.submit(process_file, fp) for fp in files]
    for future in as_completed(futures):
        s = future.result()
        if not s[0]:
            print(s[1])


if __name__ == "__main__":
    sys.exit(main())
