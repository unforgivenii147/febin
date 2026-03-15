#!/data/data/com.termux/files/usr/bin/env python
import ast
from pathlib import Path
import sys

from dh import (
    format_size,
    get_files,
    get_size,
    rm_doc,
)
import regex as re
from termcolor import cprint


def rm_ast(content: str) -> tuple[str, int]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return rm_doc(content)
    lines = content.split("\n")
    ranges = find_docstring_ranges(tree)
    for start, end in sorted(ranges, reverse=True):
        del lines[start - 1 : end]
    return "\n".join(lines), len(ranges)


def find_docstring_ranges(
    node,
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for child in ast.walk(node):
        if (
            isinstance(
                child,
                (
                    ast.Module,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            )
            and child.body
            and isinstance(child.body[0], ast.Expr)
        ):
            value = child.body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                if child.body[0].lineno and child.body[0].end_lineno:
                    ranges.append(
                        (
                            child.body[0].lineno,
                            child.body[0].end_lineno,
                        )
                    )
    return ranges


def cleanup_blank_lines(content: str) -> str:
    content = re.sub(r"\n\n+", "\n", content)
    return "\n".join(line.rstrip() for line in content.split("\n"))


def process_file(file_path: Path) -> None:
    try:
        original = file_path.read_text(encoding="utf-8")
        try:
            modified, removed = rm_ast(original)
        except:
            modified, removed = rm_doc(original)
        modified = cleanup_blank_lines(modified)
        if removed:
            print(f"✓ {file_path.name} : ", end="")
            cprint(f"{removed}", "cyan")
            try:
                tree = ast.parse(modified)
                file_path.write_text(modified, encoding="utf-8")
                del tree
                return
            except:
                cprint(
                    f"{file_path.name} ast parse error",
                    "cyan",
                )
                return
    except Exception as exc:
        print(f"✗ Error processing {file_path}: {exc}")
        return


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(root_dir, extensions=[".py"])
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    diff_size = before - get_size(root_dir)
    print(f"space saved : {format_size(diff_size)}")


if __name__ == "__main__":
    main()
