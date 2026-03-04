#!/data/data/com.termux/files/usr/bin/env python
import ast
from multiprocessing import Pool
from pathlib import Path

from dh import run_command
from fastwalk import walk_files


def process_file(path) -> bool:
    try:
        cmd = f"just-the-code -s --language=python {str(path)}"
        ret, new_code, _stderr = run_command(cmd)
        if ret == 0:
            try:
                ast.parse(new_code)
                path.write_text(new_code, encoding="utf-8")
                print(f"{path.name} updated.")
                return True
            except:
                print("result code is not valid")
                return False
    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        return False


def walk_directory(root) -> list[str]:
    files = []
    for pth in walk_files(root):
        path = Path(pth)
        if path.suffix == ".py":
            files.append(path)
    return files


def main():
    dir = Path.cwd()
    files = walk_directory(dir)
    for f in files:
        print(process_file(f))


if __name__ == "__main__":
    main()
