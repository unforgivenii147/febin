import argparse
import sys
from os import scandir as _scandir
from pathlib import Path

from autoflake import fix_code as fix_with_autoflake
from autopep8 import fix_code as fix_with_autopep
from black import Mode as _Mode
from black import TargetVersion as _tv
from black import format_str
from dh import get_filez
from isort import code as fix_with_isort
from termcolor import cprint
from yapf.yapflib.yapf_api import FormatCode as fix_with_yapf

CHUNK_SIZE = 32768

SKIP_DIRS = {".git", "__pycache__", ".ruff_cache", ".pytest_cachr"}


def is_binary(path: Path | str) -> bool:
    path = Path(path)
    try:
        with path.open("rb") as f:
            chunk = f.read(CHUNK_SIZE)
        if not chunk:
            return False  # empty file is text
        if b"\x00" in chunk:
            return True
        text_chars = bytearray(range(32, 127)) + b"\n\r\t\b"
        nontext = sum(1 for b in chunk if b not in text_chars)
        return nontext / len(chunk) > 0.30
    except Exception:
        return True


def get_lines(fp):
    return [p.strip() for p in fp.read_text(encoding="utf-8").splitlines() if p.strip()]


def is_python_file(path: str | Path) -> bool:
    path = Path(path)
    if path.is_symlink():
        return False
    if path.suffix == ".py":
        return True
    if not path.suffix:
        lines = get_lines(path)
        if not lines:
            return False
        first_line = lines[0]
        if first_line.startswith("#!") and ("python" in first_line):
            return True
        for line in lines:
            if line and (not line.startswith("#")):
                return line.startswith((
                    "import ",
                    "from ",
                    "class ",
                    "def ",
                ))
    return False


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def format_single_file(file_path, args) -> bool:
    before: int = gsz(file_path)
    after: int = before
    try:
        original_code: str = file_path.read_text(encoding="utf-8")
        if args.raui:
            code = fix_with_autoflake(
                original_code,
                remove_all_unused_imports=True,
            )
            file_path.write_text(code, encoding="utf-8")
        if args.isort:
            code = fix_with_isort(original_code)
            file_path.write_text(code, encoding="utf-8")
        if args.black:
            code = format_str(
                original_code,
                mode=_Mode(
                    target_versions={_tv.PY311, _tv.PY312, _tv.PY313},
                    line_length=120,
                ),
            )
            file_path.write_text(code, encoding="utf-8")
        elif args.autopep:
            code = fix_with_autopep(
                original_code,
                options={"aggressive": 2},
            )
            file_path.write_text(code, encoding="utf-8")
        else:
            code, _ = fix_with_yapf(original_code)
            file_path.write_text(code, encoding="utf-8")
        after = gsz(file_path)
        print(f"[OK] {file_path.name} ", end=" ")
        cprint(
            f"{fsz(before - after)}",
            "cyan",
        )
        return False
    except Exception as e:
        cprint("[ERROR]", "red", end=" ")
        print(f"{file_path.name}: {e}")
        return False


def main() -> None:
    p = argparse.ArgumentParser(description="Fast Python API-based formatter (Lazy Loading)")
    p.add_argument(
        "-b",
        "--black",
        action="store_true",
        help="Use black style",
    )
    p.add_argument(
        "-a",
        "--autopep",
        action="store_true",
        help="Use autopep8 style",
    )
    p.add_argument(
        "-i",
        "--isort",
        action="store_true",
        help="Sort imports",
    )
    p.add_argument(
        "-r",
        "--raui",
        action="store_true",
        help="Autoflake cleanup",
    )
    args = p.parse_args()
    cwd = Path.cwd()
    before = gsz(cwd)
    for f in get_filez(cwd):
        if is_binary(f):
            continue
        if is_python_file(f):
            format_single_file(f, args)
    diffsize = before - gsz(cwd)
    cprint(f"{fsz(diffsize)}", "cyan")


if __name__ == "__main__":
    main()
