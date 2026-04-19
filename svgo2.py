import subprocess
import sys
import tempfile
from multiprocessing import Pool
from pathlib import Path

from termcolor import cprint

from dhh import fsz, get_files, gsz, move_file

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
    before = gsz(cwd)
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
        after = gsz(cwd)
        cprint(
            f"{fsz(before - after)}",
            "cyan",
        )


if __name__ == "__main__":
    main()
