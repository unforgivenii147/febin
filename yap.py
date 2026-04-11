#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
import argparse
from collections import deque
from multiprocessing import get_context
from dh import get_size, format_size, get_pyfiles
from termcolor import cprint

MAX_IN_FLIGHT = 16


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

            code = black.format_str(
                original_code,
                mode=black.Mode(
                    target_versions={black.TargetVersion.PY311, black.TargetVersion.PY311},
                    line_length=120,
                ),
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
    cwd = Path.cwd()
    before = get_size(cwd)
    files = get_pyfiles(cwd)
    if not files:
        print("No Python files detected.")
        return
    if len(files) == 1:
        format_single_file(files[0], args)
        sys.exit(0)
    with get_context("spawn").Pool(8) as p:
        pending = deque()
        for name in files:
            pending.append(
                p.apply_async(
                    format_single_file,
                    (
                        (name),
                        (args),
                    ),
                ),
            )
            if len(pending) >= MAX_IN_FLIGHT:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diffsize = before - get_size(cwd)
    cprint(f"{format_size(diffsize)}", "cyan")


if __name__ == "__main__":
    main()
