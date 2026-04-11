#!/data/data/com.termux/files/usr/bin/python
import sys
import tempfile
from pathlib import Path
from dh import format_size, get_nobinary, get_size, mpf
from termcolor import cprint


def process_file(path: Path) -> int:
    if path.is_symlink() or path.suffix == ".bak" or get_size(path) == 0:
        return 0
    removed_count = 0
    try:
        temp_file_path = None
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp"
        ) as temp_f:
            temp_file_path = Path(temp_f.name)
            with path.open("r", encoding="utf-8", errors="replace") as original_f:
                for line in original_f:
                    if line.strip():
                        temp_f.write(line)
                    else:
                        removed_count += 1
        if not removed_count:
            temp_file_path.unlink()
            cprint(f"[NOCHANGE] {path.name}", "green")
            return 0
        Path(temp_file_path).replace(path)
        print(f"[OK] {path.name}", end=" | ")
        cprint(f"{removed_count}", "cyan")
        return removed_count
    except OSError:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        return 0
    except Exception as e:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        print(f"An unexpected error occurred processing {path.name}: {e}")
        return 0


def main():
    files = []
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(cwd)
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    lines_removed = 0
    results = mpf(process_file, files)
    for result in results:
        if result:
            lines_removed += result
    cprint(
        f"total removed : {lines_removed}",
        "green",
    )
    diffsize = before - get_size(cwd)
    print("space freed: ", end="")
    cprint(
        f"{format_size(diffsize)}",
        "cyan",
    )


if __name__ == "__main__":
    sys.exit(main())
