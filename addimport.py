import sys
from pathlib import Path

from dh import mpf
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
    files = []
    for pth in walk_files("."):
        path = Path(pth)
        if path.is_file() and path.suffix == ".py":
            files.append(path)
    mpf(process_file, files)


if __name__ == "__main__":
    sys.exit(main())
