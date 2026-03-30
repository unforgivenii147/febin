#!/data/data/com.termux/files/usr/bin/python
from sys import exit
from pathlib import Path

from dh import unique_path
from fastwalk import walk_files
from termcolor import cprint


OUT_PATH = Path("/data/data/com.termux/files/home/tmp/metadata")


def process_file(fp) -> bool | None:
    pkgname = ""
    pkgversion = ""

    if not fp.exists():
        return False
    line1 = fp.read_text().splitlines()[1]
    line2 = fp.read_text().splitlines()[2]

    striped1 = line1.lower().strip()
    if striped1.startswith("name:"):
        pkgname = striped1.replace("name:", "").lstrip()

    striped2 = line2.lower().strip()
    if striped2.startswith("version:"):
        pkgversion = striped2.replace("version:", "").lstrip()

    if pkgversion and pkgname:
        outfn = Path(pkgname + "-" + pkgversion + ".metadata")
        outpath = OUT_PATH / outfn
        content = fp.read_text(encoding="utf-8")
        if outpath.exists():
            outpath = unique_path(outpath)
        outpath.write_text(content, encoding="utf-8")

        cprint(f"{outfn} created.", "green")
    elif pkgname and not pkgversion:
        outfn = Path(pkgname + ".metadata")
        outpath = OUT_PATH / outfn
        content = fp.read_text(encoding="utf-8")
        if outpath.exists():
            outpath = unique_path(outpath)

        content = fp.read_text(encoding="utf-8")
        outpath.write_text(content, encoding="utf-8")
        fp.unlink()
        cprint(f"{outfn} created.", "yellow")
    elif not pkgname and not pkgversion:
        cprint(f"no data{fp}", "cyan")
        input("what u wanna do?")
        return None
    return None


def main() -> None:
    dir = Path.cwd()
    for pth in walk_files(dir):
        path = Path(pth)
        if path.is_file() and (path.name == "METADATA" or path.suffix == ".metadata"):
            process_file(path)


if __name__ == "__main__":
    exit(main())
