#!/data/data/com.termux/files/usr/bin/env python
"""count characters of input file"""
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python count_chars_of_input_file.py <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    try:
        with open(input_file) as file:
            content = file.read()
            char_count = len(content)
            print(f"Number of characters in '{input_file}': {char_count}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
