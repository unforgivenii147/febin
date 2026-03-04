#!/data/data/com.termux/files/usr/bin/env python3
import ast
import sys
from multiprocessing import Pool
from pathlib import Path

import regex as re
import tree_sitter_python as tspython
from dh import cprint, format_size, get_pyfiles, get_size, rm_doc
from termcolor import cprint
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def should_preserve_comment(content):
    content = content.strip()
    return content.startswith("#!") or content.startswith("# fmt:")


def strip_code(source_code):
    try:
        tree = parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        to_delete = []
        to_replace_with_pass = []

        def traverse(node):
            if node.type == "comment":
                comment_text = source_code[node.start_byte:node.end_byte]
                if not should_preserve_comment(comment_text):
                    to_delete.append((
                        node.start_byte,
                        node.end_byte,
                    ))
            elif node.type == "expression_statement":
                child = node.named_children[0] if node.named_children else None
                if child and child.type == "string":
                    parent = node.parent
                    if parent and parent.type == "block":
                        if parent.named_child_count == 1:
                            to_replace_with_pass.append((
                                node.start_byte,
                                node.end_byte,
                            ))
                        else:
                            to_delete.append((
                                node.start_byte,
                                node.end_byte,
                            ))
            for child in node.children:
                traverse(child)

        traverse(root_node)
        modifications = [(s, e, "") for s, e in to_delete]
        modifications += [(s, e, "pass") for s, e in to_replace_with_pass]
        modifications.sort(key=lambda x: x[0], reverse=True)
        working_code = source_code
        for (
                start,
                end,
                replacement,
        ) in modifications:
            working_code = working_code[:start] + replacement + working_code[
                end:]
        return working_code
    except:
        return source_code


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
    before = get_size(file_path)
    try:
        original = file_path.read_text(encoding="utf-8")
        try:
            modified, removed = rm_ast(original)
        except:
            modified, removed = rm_doc(original)
        modified = cleanup_blank_lines(modified)
        if removed:
            try:
                modified = strip_code(modified)
                ast.parse(modified)
                file_path.write_text(modified, encoding="utf-8")
                after = get_size(file_path)
                print(f"{file_path.name}", end=" ")
                cprint(f"{format_size(before - after)}", "blue")
                return
            except:
                cprint(f"{file_path.name} ast parse error", "cyan")
                return
    except Exception as exc:
        print(f"✗ Error processing {file_path}: {exc}")
        return


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
            for f in files:
                process_file(f8)
    else:
        files = get_pyfiles(dir)
        p = Pool(8)
        for f in files:
            p.apply_async(process_file, (f, ))
        p.close()
        p.join()
    diff_size = initsize - get_size(dir)
    print(f"{format_size(diff_size)}")


if __name__ == "__main__":
    main()
