#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path

from dh import format_size, get_size, get_nobinary
from multiprocessing import Pool
import regex as re
from termcolor import cprint

LIC_FILE = Path("/sdcard/lic")
MIN_BLANK_LINES = 3
NUM_WORKERS = 8


def load_patterns(lic_path: Path) -> list[str]:
    try:
        with open(
            lic_path,
            encoding="utf-8",
            errors="ignore",
        ) as f:
            content = f.read()
        pattern_separator = r"\n(?:\s*\n){" + str(MIN_BLANK_LINES) + r",}"
        patterns = re.split(pattern_separator, content)
        patterns = [p.strip() for p in patterns if p.strip()]
        #        print(f"Loaded {len(patterns)} pattern(s) from {lic_path}")
        for _idx, pattern in enumerate(patterns, 1):
            pattern[:50].replace("\n", "\\n")
        return patterns
    except Exception as e:
        print(f"Error loading patterns from {lic_path}: {e}")
        return []


def escape_for_regex(text: str) -> str:
    escaped = re.escape(text)
    return escaped.replace(r"\n", r"\s*\n\s*")


def remove_patterns_from_content(content: str, patterns: list[str]) -> str:
    cleaned = content
    for pattern in patterns:
        regex_pattern = escape_for_regex(pattern)
        cleaned = re.sub(regex_pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)

    return cleaned


def process_file(file_path, patterns) -> tuple:
    path = Path(file_path)
    before = get_size(path)

    original_content = path.read_text(encoding="utf-8")
    cleaned_content = remove_patterns_from_content(original_content, patterns)

    if len(cleaned_content) != len(original_content):
        path.write_text(cleaned_content)
        cprint(f"{path.name} updated", "green", end=" | ")
        ds = before - get_size(path)
        cprint(f"{format_size(ds)}")


def main():

    if not LIC_FILE.exists():
        print(f"Error: License file not found: {LIC_FILE}")
        return
    patterns = load_patterns(LIC_FILE)
    if not patterns:
        print("No patterns found. Exiting.")
        return
    print()
    root_dir = Path.cwd()
    all_files = get_nobinary(root_dir)
    if not all_files:
        print("No files to process.")
        return

    for f in all_files:
        process_file(f, patterns)


if __name__ == "__main__":
    main()
