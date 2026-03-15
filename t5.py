#!/data/data/com.termux/files/usr/bin/env python
import ast
from multiprocessing import Pool
import os
from pathlib import Path
import sys

from dh import format_size, get_size
from tree_sitter import (
    Language,
    Parser,
    Query,
    QueryCursor,
)
import tree_sitter_python as tspython

QUERY_STRING = """
(comment) @comment
(block
  . (expression_statement
    (string)) @docstring)
(module
  . (expression_statement
    (string)) @docstring)
"""


class TSRemover:
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        self.query = Query(self.language, QUERY_STRING)

    def remove_comments(self, source: str):
        source_bytes = source.encode("utf-8")
        tree = self.parser.parse(source_bytes)
        cursor = QueryCursor(self.query)
        matches = cursor.matches(tree.root_node)
        deletions = []
        comment_count = 0
        docstring_count = 0
        for (
            _pattern_index,
            captures_dict,
        ) in matches:
            for (
                capture_name,
                node_list,
            ) in captures_dict.items():
                for node in node_list:
                    start = node.start_byte
                    end = node.end_byte
                    text = source_bytes[start:end].decode("utf-8")
                    if capture_name == "comment":
                        stripped = text.strip()
                        if (
                            stripped.startswith("# type:")
                            or stripped.startswith("# TODO")
                            or stripped.startswith("# noqa")
                            or stripped.startswith("#!")
                            or stripped.startswith("# fmt:")
                        ):
                            continue
                        comment_count += 1
                    else:
                        docstring_count += 1
                    if end < len(source_bytes) and source_bytes[end : end + 1] == b"\n":
                        end += 1
                    deletions.append((start, end))
        deletions = sorted(set(deletions), reverse=True)
        new_source = source_bytes
        for start, end in deletions:
            new_source = new_source[:start] + new_source[end:]
        cleaned = new_source.decode("utf-8")
        cleaned = self._cleanup_blank_lines(cleaned)
        return (
            cleaned,
            comment_count,
            docstring_count,
        )

    @staticmethod
    def _cleanup_blank_lines(text: str) -> str:
        lines = text.splitlines()
        cleaned = []
        blank_streak = 0
        for line in lines:
            if line.strip() == "":
                blank_streak += 1
                if blank_streak <= 2:
                    cleaned.append("")
            else:
                blank_streak = 0
                cleaned.append(line.rstrip())
        return "\n".join(cleaned) + "\n"


def process_file(fp):
    file_path = Path(fp)
    ts_rmc = TSRemover()
    code = file_path.read_text(encoding="utf-8", errors="ignore")
    ts_rmc.remove_comments(code)
    result, comments, docstrings = ts_rmc.remove_comments(code)
    if comments == 0 and docstrings == 0:
        print(f"[NO CHANGE] : {file_path.name}")
        return
    try:
        ast.parse(result)
        print(f"{file_path.name}: comments: {comments}   docstrings: {docstrings}")
        fp.write_text(result, encoding="utf-8")
    except:
        print(f"{file_path.name} : invalid code")


def main():
    before = get_size(".")
    args = sys.argv[1:]
    if args:
        files = [f for f in args if Path(f).is_file()]
    else:
        files = [os.path.join(r, f) for r, _, fs in os.walk(".") for f in fs if f.endswith(".py")]
    if not files:
        return
    print(f"Processing {len(files)} files using QueryCursor...")
    pool = Pool(8)
    for _ in pool.imap_unordered(process_file, files):
        pass
    pool.close()
    pool.join()
    diff_size = before - get_size(".")
    if diff_size != 0:
        print(format_size(diff_size))


if __name__ == "__main__":
    main()
