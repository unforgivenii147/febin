#!/data/data/com.termux/files/usr/bin/python
from sys import exit
from time import perf_counter
from pathlib import Path
from multiprocessing import get_context

from fastwalk import walk_files


shebang = "#!/data/data/com.termux/files/usr/bin/python\n\n"


def process_file(fp):
    if not fp.exists() or fp.is_symlink():
        return
    print(f"processing {fp}")
    data = []
    newdata = []
    with Path(fp).open(encoding="utf-8") as fin:
        data = fin.readlines()
    if data[0].startswith("#!"):
        newdata.extend((data[0], "import regex as re\nimport os\n"))
        for k in data[1:]:
            newdata.append(k)
    else:
        newdata.extend((shebang, "import regex as re\nimport os\n"))
        for k in data:
            newdata.append(k)
    with Path(fp).open("w", encoding="utf-8") as fo:
        fo.writelines(newdata)
    return


def main():
    start = perf_counter()
    files = []
    for pth in walk_files("."):
        path = Path(pth)
        if path.is_file() and path.suffix == ".py":
            files.append(path)
    with get_context("spawn").Pool(8) as pool:
        pool.imap_unordered(process_file, files)
    print(f"{perf_counter() - start} sec")


if __name__ == "__main__":
    exit(main())
