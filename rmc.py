#!/data/data/com.termux/files/usr/bin/python
import ast
import operator
import sys
from pathlib import Path

import tree_sitter_python as tspython
from dh import clean_blank_lines, fsz, get_pyfiles, gsz
from termcolor import cprint
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)
PRESERVED: set = {
    "#!",
    "# type",
    "# fmt",
}


def havedoc(code):
    tree = ast.parse(code)
    doc = ast.get_docstring(tree)
    has_doc = doc is not None
    has_comment = "#" in code
    return has_doc or has_comment


def should_preserve_comment(content):
    content = content.strip()
    return any(pat in content for pat in PRESERVED)


def strip_code(source_code):
    try:
        tree = parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        to_delete = []
        to_replace_with_pass = []

        def traverse(node):
            if node.type == "comment":
                comment_text = source_code[node.start_byte : node.end_byte]
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
        modifications.sort(key=operator.itemgetter(0), reverse=True)
        working_code = source_code
        for (
            start,
            end,
            replacement,
        ) in modifications:
            working_code = working_code[:start] + replacement + working_code[end:]
        return working_code
    except:
        return source_code


def rm_ast(content: str) -> tuple[str, int]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        del tree
        return content
    lines = content.split("\n")
    ranges = find_docstring_ranges(tree)
    for start, end in sorted(ranges, reverse=True):
        del lines[start - 1 : end]
    return "\n".join(lines), len(ranges)


def find_docstring_ranges(node) -> list[tuple[int, int]]:
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
            if (
                isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and child.body[0].lineno
                and child.body[0].end_lineno
            ):
                ranges.append((
                    child.body[0].lineno,
                    child.body[0].end_lineno,
                ))
    return ranges


def process_file(file_path: Path) -> bool:
    before = gsz(file_path)
    original = file_path.read_text(encoding="utf-8")
    if havedoc(original):
        modified, _removed = rm_ast(original)
        finalcode = strip_code(modified)
        wcode = clean_blank_lines(finalcode)
        try:
            _ = ast.parse(wcode)
            file_path.write_text(wcode, encoding="utf-8")
            dsz = before - gsz(file_path)
            print(f"{file_path.name}", end=" ")
            cprint(
                f"{fsz(dsz)}",
                "blue",
            )
            return True
        except:
            print("ast parse error")
            return False
    return None


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_pyfiles(cwd)
    print(f"{len(files)} files found.")
    for f in files:
        process_file(f)


if __name__ == "__main__":
    main()
