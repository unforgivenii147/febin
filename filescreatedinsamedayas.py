#!/usr/bin/env python3
"""
Simpler version - finds files in the same directory created on the same day as input file.
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def get_file_creation_time(filepath):
    """Get creation/modification time of a file."""
    try:
        stat = os.stat(filepath)
        # On Windows, use creation time; on Unix, use modification time
        if sys.platform == "win32":
            return datetime.fromtimestamp(stat.st_ctime)
        else:
            return datetime.fromtimestamp(stat.st_mtime)
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        sys.exit(1)

    # Get the directory of the input file
    directory = os.path.dirname(filename) or "."

    # Get creation time of input file
    target_time = get_file_creation_time(filename)
    if not target_time:
        sys.exit(1)

    target_date = target_time.date()

    print(f"Input file: {filename}")
    print(f"Created on: {target_date}")
    print("-" * 50)

    # Find files in the same directory created on the same day
    found_files = []

    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)

        # Skip directories and the input file itself
        if not os.path.isfile(filepath) or os.path.samefile(filepath, filename):
            continue

        file_time = get_file_creation_time(filepath)
        if file_time and file_time.date() == target_date:
            found_files.append((file_time, file))

    # Sort by creation time
    found_files.sort()

    if not found_files:
        print("No other files found created on the same day.")
    else:
        print(f"Found {len(found_files)} other file(s) created on the same day:")
        for file_time, file in found_files:
            print(f"{file_time.strftime('%H:%M:%S')} - {file}")


if __name__ == "__main__":
    main()
