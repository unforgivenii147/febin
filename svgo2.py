#!/data/data/com.termux/files/usr/bin/python
import os
import sys
from pathlib import Path
import tempfile
import subprocess
from multiprocessing import Pool

from dh import get_size, get_files, move_file, format_size
from termcolor import cprint


MAX_QUEUE = 16


def process_file(in_file):
    if not in_file.exists():
        msg = f"Input file not found: {in_file.name}"
        raise FileNotFoundError(msg)
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    try:
        subprocess.run(
            [
                "svgcleaner",
                "--multipass",
                str(in_file),
                tmp_file_path,
            ],
            check=True,
            capture_output=True,
        )
        move_file(tmp_file_path, in_file, overwrite=True)
        print(f"{in_file.name} updated")
    except subprocess.CalledProcessError as e:
        print(f"Error running svgcleaner: {e.stderr.decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        if Path(tmp_file_path).exists():
            Path(tmp_file_path).unlink()


def main() -> None:
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd, extensions=[".svg"])
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    else:
        p = Pool(8)
        for _ in p.imap_unordered(process_file, files):
            pass
        p.close()
        p.join()
        after = get_size(cwd)
        cprint(
            f"{format_size(before - after)}",
            "cyan",
        )


if __name__ == "__main__":
    main()
