#!/data/data/com.termux/files/usr/bin/env python
import ast
from collections import deque
import importlib
import inspect
import os
from pathlib import Path
import sys
from textwrap import dedent

from dh import get_files, unique_path
from loguru import logger
from multiprocessing import Pool

BASE_DIR = Path("doc")


def format_markdown(module_name: str, module_doc: str, functions, classes) -> str:
    parts = [f"# Module `{module_name}`\n"]

    if module_doc:
        parts.append("## Module Doc\n")
        parts.append(module_doc + "\n")

    if functions:
        parts.append("## Functions\n")
        for name, doc in functions:
            parts.append(f"### `{name}()`\n")
            parts.append(doc + "\n")

    if classes:
        parts.append("## Classes\n")
        for name, doc in classes:
            parts.append(f"### `{name}`\n")
            parts.append(doc + "\n")

    return "\n".join(parts).strip() + "\n"


def extract_ast_docs(src: str) -> tuple[str, list, list]:
    try:
        tree = ast.parse(src)
    except Exception:
        return "", [], []

    module_doc = dedent(ast.get_docstring(tree) or "").strip()
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node) or ""
            doc = dedent(doc).strip()
            if doc:
                functions.append((node.name, doc))

        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            doc = dedent(doc).strip()
            if doc:
                classes.append((node.name, doc))

    return module_doc, functions, classes


def extract_from_file(py_path: str) -> tuple[str, str, str, list, list]:
    try:
        with open(py_path, encoding="utf-8") as f:
            src = f.read()
    except Exception:
        return None

    module_doc, functions, classes = extract_ast_docs(src)
    if not module_doc and not functions and not classes:
        return None

    return module_doc, functions, classes


def extract_from_importable(name: str):
    try:
        module = importlib.import_module(name)
    except Exception:
        return None

    try:
        src = inspect.getsource(module)
        return extract_ast_docs(src)
    except Exception:
        doc = dedent(inspect.getdoc(module) or "").strip()
        if not doc:
            return None
        return doc, [], []


def module_to_md_paths(name: str):
    parts = name.split(".")
    folder = os.path.join(BASE_DIR, *parts[:-1])
    filename = f"{parts[-1]}.md"
    return folder, os.path.join(folder, filename)


def file_to_md_paths(py_file: str, root: str):
    rel = os.path.relpath(py_file, root)
    parts = rel.split(os.sep)
    parts[-1] = parts[-1].replace(".py", ".md")
    folder = os.path.join(BASE_DIR, *parts[:-1])
    outfile = os.path.join(BASE_DIR, *parts)
    return folder, outfile


def save_markdown(folder: str, path: str, content: str):
    folderpath = Path(folder)
    if not folderpath.exists():
        folderpath.mkdir(exist_ok=True)
    outpath = Path(path)
    if outpath.exists():
        outpath = unique_path(outpath)
    outpath.write_text(content, encoding="utf-8")


def process_importable_task(name: str):
    logger.info(f"processing module {name}")
    result = extract_from_importable(name)
    if not result:
        return

    module_doc, functions, classes = result

    folder, out_path = module_to_md_paths(name)
    md = format_markdown(name, module_doc, functions, classes)
    save_markdown(folder, out_path, md)


def process_file_task(py_file):
    filepath = Path(py_file)
    root = str(filepath.parent)
    logger.info(f"processing file {filepath.name} from {filepath.parent.name}")
    result = extract_from_file(str(py_file))
    if not result:
        return

    module_doc, functions, classes = result
    rel = os.path.relpath(py_file)
    module_name = rel.replace(os.sep, ".").replace(".py", "")

    folder, out_path = file_to_md_paths(py_file, root)
    md = format_markdown(module_name, module_doc, functions, classes)
    save_markdown(folder, out_path, md)


def main():
    if not BASE_DIR.exists():
        BASE_DIR.mkdir(exist_ok=True)
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, extensions=[".py", ".pyi", ".pyx", ".pxd"])

    logger.info(f"processing {len(files)} files")
    with Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file_task, (f,)))
            if len(pending) > 16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


"""

    logger.info(f"processing {len(importable)} importable")
    with Pool(8) as pool:
        pending=deque()
        for x in importables:
            pending.append(pool.apply_async(process_importable_task, (x,)))
            if len(pending)>16:
                pending.popleft().get()
        while pending:
            pending.popleft().get()

"""

if __name__ == "__main__":
    main()
