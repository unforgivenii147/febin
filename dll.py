#!/usr/bin/env python3
"""
Script to delete a range of lines from a file.
Gets filename and line numbers (x, y) from user input.
Deletes lines from x to y (inclusive) and updates file in place.
"""

import sys


def delete_lines_from_file():
    filename, fromline, toline = sys.argv[1:]
    fromline = int(fromline)
    toline = int(toline)
    try:
        with open(filename) as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    len(lines)
    if fromline > toline:
        temp = fromline
        fromline = toline
        toline = temp
        del temp
    new_lines = lines[:fromline - 1] + lines[toline:]
    try:
        with open(filename, "w") as file:
            file.writelines(new_lines)
        print(f"emaining lines: {len(new_lines)}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        return


if __name__ == "__main__":
    delete_lines_from_file()
