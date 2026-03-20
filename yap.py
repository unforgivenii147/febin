#!/data/data/com.termux/files/usr/bin/python

import argparse
from collections import deque
import contextlib
from multiprocessing import Pool
from pathlib import Path

from dh import format_size, get_size
from fastwalk import walk_files
from termcolor import cprint

MAX_IN_FLIGHT = 16
IGNORED_DIRS = {
    ".git",
    "__pycache__",
}


def is_python_file(path: Path) -> bool:
    if path.suffix in {".py", ".pyi"}:
        return True
    try:
        with path.open("rb") as f:
            line = f.readline(100)
            return line.startswith(b"#!") and b"python" in line.lower()
    except Exception:
        return False


def format_single_file(file_path: Path, args) -> bool:
    before: int = get_size(file_path)
    after: int = before
    try:
        original_code: str = file_path.read_text(encoding="utf-8")
        if args.raui:
            import autoflake

            code = autoflake.fix_code(
                original_code,
                remove_all_unused_imports=True,
            )
            file_path.write_text(code, encoding="utf-8")
        if args.isort:
            import isort

            code = isort.code(original_code)
            file_path.write_text(code, encoding="utf-8")

        if args.black:
            import black

            with contextlib.suppress(black.report.NothingChanged):
                code = black.format_str(
                    original_code,
                    mode=black.Mode(line_length=120),
                )
                file_path.write_text(code, encoding="utf-8")

        elif args.autopep:
            import autopep8

            code = autopep8.fix_code(
                original_code,
                options={"aggressive": 2},
            )
            file_path.write_text(code, encoding="utf-8")
        else:
            from yapf.yapflib import yapf_api

            code, _ = yapf_api.FormatCode(original_code)
            file_path.write_text(code, encoding="utf-8")
        after = get_size(file_path)
        print(f"[OK] {file_path.name} ", end=" ")
        cprint(
            f"{format_size(before - after)}",
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
    root_dir = Path().cwd()
    files = []
    before = get_size(root_dir)
    for pth in walk_files(root_dir):
        path = Path(pth)
        if (
            path.is_file()
            and not any(part in IGNORED_DIRS for part in path.parts)
            and is_python_file(path)
            and not path.is_symlink()
        ):
            files.append(path)
    if not files:
        print("No Python files detected.")
        return
    print(f"Formatting {len(files)} files...")
    with Pool(8) as p:
        pending = deque()
        for name in files:
            pending.append(
                p.apply_async(
                    format_single_file,
                    (
                        (name),
                        (args),
                    ),
                )
            )
            if len(pending) >= MAX_IN_FLIGHT:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

    after = get_size(root_dir)
    diffsize = before - after
    cprint(f"{format_size(diffsize)}", "cyan")


if __name__ == "__main__":
    main()
