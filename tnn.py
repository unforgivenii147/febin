#!/data/data/com.termux/files/usr/bin/python
import argparse  # اضافه کردن argparse برای مدیریت بهتر آرگومان‌ها
import sys
from pathlib import Path

import regex as re

TAB_PATTERN = re.compile(r"\t")  # نام متغیر را کمی توصیفی‌تر کردم
SPACE_REPLACEMENT = " " * 4  # تعریف رشته جایگزین (4 اسپیس)


def replace_tabs_in_file(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(
            f"Error: Could not decode {file_path.name} with UTF-8. Skipping.",
            file=sys.stderr,
        )
        return
    except OSError as e:
        print(f"Error reading {file_path.name}: {e}. Skipping.", file=sys.stderr)
        return
    if not TAB_PATTERN.search(content):
        return
    new_content = TAB_PATTERN.sub(SPACE_REPLACEMENT, content)
    try:
        file_path.write_text(new_content, encoding="utf-8")
        print(f"Successfully replaced tabs in {file_path.name}.")
    except OSError as e:
        print(f"Error writing to {file_path.name}: {e}. Skipping.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Replaces tab characters with 4 spaces in Python files or specified text files."
    )
    parser.add_argument(
        "files",
        nargs="*",  # اجازه می‌دهد صفر یا بیشتر فایل به عنوان آرگومان داده شوند
        help="Specific files to process. If none, all *.py files in current directory and subdirectories are processed.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output (e.g., skip messages for files without tabs).",
    )
    args = parser.parse_args()
    if args.files:
        file_paths = [Path(f) for f in args.files]
        for f_path in file_paths:
            if not f_path.exists():
                print(f"Warning: File '{f_path}' not found. Skipping.", file=sys.stderr)
        file_paths = [f for f in file_paths if f.exists()]  # فقط فایل‌های موجود را نگه می‌دارد
    else:
        print("No specific files provided. Searching for all *.py files in current directory and subdirectories...")
        file_paths = list(Path.cwd().rglob("*.py"))  # rglob یک iterator برمی‌گرداند، بهتر است به لیست تبدیل شود
    file_paths.sort()
    if not file_paths:
        print("No Python files found to process.")
        sys.exit(0)
    print(f"Found {len(file_paths)} files to process.")
    for file_path in file_paths:
        replace_tabs_in_file(file_path)  # فراخوانی تابع با نام صحیح


if __name__ == "__main__":
    main()
