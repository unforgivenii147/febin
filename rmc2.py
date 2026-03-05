#!/data/data/com.termux/files/usr/bin/env python
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path
import tree_sitter_python
from tree_sitter import Language, Parser

from dh import get_size, cleanup_blank_lines, get_pyfiles, format_size

EXCLUDE_PREFIXES = (b"#!/", b"# fmt:", b"# type:")

parser = Parser()
parser.language = Language(tree_sitter_python.language())


def _collect_docstrings(node, source: bytes, deletions: list):
    def first_named_child(block):
        for child in block.children:
            if child.is_named:
                return child
        return None

    if node.type == "module":
        first = first_named_child(node)
        if first and first.type == "expression_statement":
            string_node = first.child_by_field_name("expression")
            if string_node and string_node.type == "string":
                deletions.append((first.start_byte, first.end_byte))
    if node.type in (
        "class_definition",
        "function_definition",
    ):
        body = node.child_by_field_name("body")
        if body:
            first = first_named_child(body)
            if first and first.type == "expression_statement":
                string_node = first.child_by_field_name("expression")
                if string_node and string_node.type == "string":
                    deletions.append((first.start_byte, first.end_byte))
    for child in node.children:
        _collect_docstrings(child, source, deletions)


def process_file(path: Path) -> None:
    try:
        source = path.read_bytes()
        tree = parser.parse(source)
        deletions = []

        def walk_comments(node):
            if node.type == "comment":
                text = source[node.start_byte : node.end_byte]
                if not text.lstrip().startswith(EXCLUDE_PREFIXES):
                    deletions.append((node.start_byte, node.end_byte))
            for child in node.children:
                walk_comments(child)

        walk_comments(tree.root_node)
        _collect_docstrings(tree.root_node, source, deletions)
        cleaned = bytearray(source)
        for start, end in sorted(deletions, reverse=True):
            del cleaned[start:end]
        cleaned_text = cleaned.decode("utf-8")
        cleaned_text = cleanup_blank_lines(cleaned_text)
        cleaned = cleaned_text.encode("utf-8")
        parser.parse(cleaned)
        path.write_bytes(cleaned)
        print(f"[OK] {path}")
    except Exception as e:
        print(f"[FAIL] {path} -> {e}")


def main() -> None:

    root = Path.cwd()
    isz = get_size(root)
    args = sys.argv[1:]
    if args:
        files = [Path(arg) for arg in args]
    else:
        files = get_pyfiles(root)

    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)

    with Pool(8) as pool:
        pool.map(process_file, files)
    esz = get_size(root)
    print(f"space freed: {format_size(isz - esz)}")


if __name__ == "__main__":
    main()
