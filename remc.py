#!/data/data/com.termux/files/usr/bin/env python
import ast
import sys
from pathlib import Path
import regex as re
from dh import cprint, format_size, get_pyfiles, get_size, rm_doc
def rm_ast(content: str) -> tuple[str, int]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return rm_doc(content)
    lines = content.split("\n")
    ranges = find_docstring_ranges(tree)
    for start, end in sorted(ranges, reverse=True):
        del lines[start - 1:end]
    return "\n".join(lines), len(ranges)
def find_docstring_ranges(node) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for child in ast.walk(node):
        if isinstance(
                child,
            (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if child.body and isinstance(child.body[0], ast.Expr):
                value = child.body[0].value
                if isinstance(value, ast.Constant) and isinstance(
                        value.value, str):
                    if child.body[0].lineno and child.body[0].end_lineno:
                        ranges.append(
                            (child.body[0].lineno, child.body[0].end_lineno))
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
        if removed > 0:
            print(f"✓ {file_path.name} d : {removed}")
        if modified != original:
            try:
                ast.parse(modified)
                file_path.write_text(modified, encoding="utf-8")
                return
            except:
                cprint(f"{file_path.name} ast parse error", "cyan")
                return
    except Exception as exc:
        print(f"✗ Error processing {file_path}: {exc}")
        return
def process_directory(directory: str) -> dict:
    files = get_pyfiles(directory)
    if not files:
        print("No Python files found")
        return
    for file_path in files:
        process_file(file_path)
def main():
    dir = Path.cwd()
    initsize = get_size(dir)
    args = sys.argv[1:]
    if args:
        files = [Path(f) for f in args]
        if len(files) == 1:
            process_file(files[0])
            return
    else:
        process_directory(dir)
    diff_size = initsize - get_size(dir)
    print(f"{format_size(diff_size)}")
if __name__ == "__main__":
    main()
