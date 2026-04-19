import sys
from pathlib import Path

from fastwalk import walk_files

from dhh import fsz, gsz, mpf3, run_command


def process_file(fp):
    if not fp.exists():
        return False
    if fp.suffix == ".c":
        cmd = f"clang {fp!s} -o {fp.with_suffix('')!s}"
    if fp.suffix == ".cpp":
        cmd = f"clang++ {fp!s} -o {fp.with_suffix('')!s}"
    ret, txt, _err = run_command(cmd)
    print(txt)
    return ret
    return True


def main():
    cwd = Path().cwd()
    start_size = gsz(cwd)
    files = []
    for pth in walk_files(cwd):
        path = Path(pth)
        if path.is_file() and path.suffix in {
            ".c",
            ".cpp",
        }:
            files.append(path)
    mpf3(process_file, files)
    print(f"{fsz(start_size - gsz(cwd))}")


if __name__ == "__main__":
    sys.exit(main())
