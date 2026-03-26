#!/data/data/com.termux/files/usr/bin/python
from multiprocessing import Pool
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from dh import format_size, get_files, get_size, move_file
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
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


def main() -> None:
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, extensions=[".svg"])
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
        after = get_size(root_dir)
        cprint(
            f"{format_size(before - after)}",
            "cyan",
        )


if __name__ == "__main__":
    main()
