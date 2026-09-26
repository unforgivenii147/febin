#!/data/data/com.termux/files/usr/bin/python
"""Print the number of characters in a UTF-8 text file.

Usage::

    count_chars.py <input_file>

Unlike :mod:`charcount`, this variant has no external dependencies and reports
a friendly error (exit status ``1``) when the file cannot be found.
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    # Exactly one positional argument (the file to inspect) is required.
    if len(sys.argv) != 2:
        print("Usage: python count_chars_of_input_file.py <input_file>")
        sys.exit(1)

    input_file: str = sys.argv[1]
    try:
        with Path(input_file).open(encoding="utf-8") as file:
            content: str = file.read()
            char_count: int = len(content)
            print(f"Number of characters in '{input_file}': {char_count}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
