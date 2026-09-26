#!/data/data/com.termux/files/usr/bin/python
"""Convert ``\\xHH`` hex escapes in a file into their real characters.

The file is read as bytes, decoded as UTF-8 (falling back to Latin-1), and any
``\\xHH`` escape sequence is replaced by the character with that code point.
The readable result is written back in place.

Usage::

    to_unicode.py <filename>
"""

import re as _stdre  # standard library; used only for precise type annotations
import sys
from pathlib import Path

import regex as re  # drop-in regex engine used at runtime


def convert_to_readable(filename: str) -> None:
    """Replace ``\\xHH`` escapes in ``filename`` with real characters.

    Args:
        filename: Path to the file to convert in place.
    """
    outfile: Path = Path(filename)
    try:
        with open(filename, "rb") as f:
            content: bytes = f.read()
        try:
            decoded_content: str = content.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            decoded_content = content.decode("latin-1", errors="ignore")

        def replace_hex(m: "_stdre.Match[str]") -> str:
            """Turn a single ``\\xHH`` match into its character."""
            try:
                return chr(int(m.group(1), 16))
            except ValueError:
                return m.group(0)

        readable_content: str = re.sub(
            r"\\x([0-9a-fA-F]{2})", replace_hex, decoded_content
        )

        outfile.write_text(readable_content, encoding="utf-8")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:  # noqa: BLE001 - report unexpected failures, do not crash
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_script.py <filename>")
    else:
        fname: str = sys.argv[1]
        convert_to_readable(fname)
