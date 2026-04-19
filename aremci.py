#!/data/data/com.termux/files/usr/bin/python

import re
import os
import ast
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

COMMENT_AND_DOCSTRING_REGEX = re.compile(
    r"(?:^(\s*)#.*$)|(?:^(\s*)(''').*?(\3)|^(\s*)(\"{3}).*?(\5))|(?:\b(def|class)\s+\w+[^():]*\([^)]*\)\s*:\s*)(\s*)((''').*?(\7)|(\"{3}).*?(\9))",
    re.MULTILINE | re.DOTALL,
)
DOCSTRING_START_REGEX = re.compile(r"^\s*('''|\"{3}).*?(\1)\s*", re.MULTILINE | re.DOTALL)
MAX_WORKERS = os.cpu_count() - 1 or 1


def strip_comments_and_docstrings(file_path_str):
    file_path = Path(file_path_str)
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    original_content = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False
    cleaned_content = DOCSTRING_START_REGEX.sub(r"\1", original_content, count=3)

    def replace_comments(match):
        indent1, comment1, quote1, indent2, quote2, fn_type, indent3, quote3, quote4 = match.groups()
        if comment1:
            return ""
        elif quote1:
            return match.group(0)
        elif quote3:
            return f"{fn_type}{indent3}"
        elif quote4:
            return f"{fn_type}{indent3}"
        return match.group(0)

    no_single_line_comments = re.sub(r"^\s*#.*$", "", original_content, flags=re.MULTILINE)
    try:
        tree = ast.parse(no_single_line_comments)
        cleaned_content_heuristic = DOCSTRING_START_REGEX.sub(r"\1", no_single_line_comments, count=3)
        try:
            ast.parse(cleaned_content_heuristic)
            final_code = cleaned_content_heuristic
        except SyntaxError:
            print(f"Syntax error after stripping comments/docstrings from {file_path}. Reverting.")
            return False
    except SyntaxError as e:
        print(f"Original code has syntax error: {file_path} - {e}. Skipping.")
        return False
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Error creating backup for {file_path}: {e}")
        return False
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_code)
        print(f"Successfully stripped comments/docstrings from {file_path}")
        return True
    except Exception as e:
        print(f"Error writing cleaned file {file_path}: {e}")
        try:
            shutil.move(backup_path, file_path)
            print(f"Restored original content from backup for {file_path}")
        except Exception as restore_e:
            print(f"CRITICAL ERROR: Failed to write cleaned file and restore backup for {file_path}: {restore_e}")
        return False


def find_python_files_recursively(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)


def process_directory(directory):
    python_files = list(find_python_files_recursively(directory))
    print(f"Found {len(python_files)} Python files to process.")
    processed_count = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(strip_comments_and_docstrings, file_path): file_path for file_path in python_files}
        for future in futures:
            file_path = futures[future]
            try:
                success = future.result()
                if success:
                    processed_count += 1
            except Exception as e:
                print(f"Error processing future for {file_path}: {e}")
    print(
        f"\nFinished processing. Successfully stripped comments/docstrings from {processed_count}/{len(python_files)} files."
    )


if __name__ == "__main__":
    target_directory = "."
    print(f"Starting comment and docstring stripping in directory: {Path(target_directory).resolve()}")
    process_directory(target_directory)
