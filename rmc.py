#!/data/data/com.termux/files/usr/bin/env python
import ast
from collections import deque
from pathlib import Path
import sys

from dh import (
    DOC_TH1,
    DOC_TH2,
    cprint,
    format_size,
    get_files,
    get_size,
    rm_doc,
)
from multiprocessing import Pool
import regex as re
from termcolor import cprint
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

MAX_QUEUE = 16

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)
PRESERVED: dict = {
    "#!",
    "# type",
    "# fmt",
    "# pylint",
}


def preprocess(orig):
    cleaned = []
    lines = orig.splitlines()
    for line in lines:
        if line.startswith(DOC_TH1) and line.endswith(DOC_TH1) and line != DOC_TH1 * 2:
            continue
        if line.startswith(DOC_TH2) and line.endswith(DOC_TH2) and line != DOC_TH2 * 2:
            continue
        if any(pat in line for pat in PRESERVED):
            cleaned.append(line)
            continue
        if "#" in line and not line.startswith("#"):
            indx = line.index("#")
            cleaned.append(line[:indx] + "\n")
            continue
        if not line.startswith("#"):
            cleaned.append(line)

    code = "\n".join(cleaned)
    try:
        _ = ast.parse(code)
        del cleaned
        return code
    except:
        return orig


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
                    to_delete.append(
                        (
                            node.start_byte,
                            node.end_byte,
                        )
                    )
            elif node.type == "expression_statement":
                child = node.named_children[0] if node.named_children else None
                if child and child.type == "string":
                    parent = node.parent
                    if parent and parent.type == "block":
                        if parent.named_child_count == 1:
                            to_replace_with_pass.append(
                                (
                                    node.start_byte,
                                    node.end_byte,
                                )
                            )
                        else:
                            to_delete.append(
                                (
                                    node.start_byte,
                                    node.end_byte,
                                )
                            )
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
            working_code = working_code[:start] + replacement + working_code[end:]
        del tree
        return working_code
    except:
        del tree
        return source_code


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
    before = get_size(file_path)
    try:
        original = file_path.read_text(encoding="utf-8")
        code = preprocess(original)
        try:
            modified, removed = rm_ast(code)
        except:
            modified, _removed = rm_doc(code)

        try:
            finalcode = strip_code(modified)
            finalcode = cleanup_blank_lines(finalcode)
            ast.parse(finalcode)
            file_path.write_text(finalcode, encoding="utf-8")
            after = get_size(file_path)
            print(f"{file_path.name}", end=" ")
            cprint(
                f"{format_size(before - after)}",
                "blue",
            )
            return
        except:
            try:
                ast.parse(modified)
                finalcode = cleanup_blank_lines(modified)
                file_path.write_text(finalcode, encoding="utf-8")
                after = get_size(file_path)
                print(f"{file_path.name}", end=" ")
                cprint(
                    f"{format_size(before - after)}",
                    "blue",
                )
                return
            except:
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
