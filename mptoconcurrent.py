#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib
import shutil
from concurrent.futures import ThreadPoolExecutor

import regex as re


def find_py_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        py_files.extend(os.path.join(root, file) for file in files if file.endswith(".py"))
    return py_files


def backup_file(file_path):
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)
    return backup_path


def replace_multiprocessing(file_path):
    try:
        content = pathlib.Path(file_path).read_text(encoding="utf-8")
        if "import multiprocessing" not in content and "from multiprocessing" not in content:
            return False, file_path, "No mp"
        backup_file(file_path)
        content = re.sub(
            r"^\s*import\s+multiprocessing\s*$",
            "from concurrent.futures import ProcessPoolExecutor as PoolExecutor",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^\s*from\s+multiprocessing\s+import\s+.*$",
            "from concurrent.futures import ProcessPoolExecutor as PoolExecutor",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"\bmultiprocessing\.Pool\b",
            "ProcessPoolExecutor",
            content,
        )
        content = re.sub(
            r"\bPool\b(?=\()",
            "ProcessPoolExecutor",
            content,
        )
        content = re.sub(
            r"\bmultiprocessing\.Process\b",
            "ProcessPoolExecutor",
            content,
        )
        pathlib.Path(file_path).write_text(content, encoding="utf-8")
        return (
            True,
            file_path,
            "Successfully replaced multiprocessing with concurrent.futures.",
        )
    except Exception as e:
        return (
            False,
            file_path,
            f"Error: {e!s}",
        )


def main():
    current_dir = pathlib.Path.cwd()
    py_files = find_py_files(current_dir)
    if not py_files:
        print("No Python files found in the current directory.")
        return
    print(f"Found {len(py_files)} Python files to process.")
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(replace_multiprocessing, py_files))
    success = sum(1 for r in results if r[0])
    print(f"\nProcessing complete. Success: {success}/{len(py_files)} files.")
    for result in results:
        print(f"{'✓' if result[0] else '✗'} {result[1]}: {result[2]}")


if __name__ == "__main__":
    main()
