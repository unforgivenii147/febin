#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
import subprocess


def copy_lines_to_clipboard(filename: str, start_line: int | None = None, end_line: int | None = None):
    """
    Reads specified lines from a file and copies them to the Termux clipboard.
    If start_line and end_line are None, copies the entire file content.

    Args:
        filename: The path to the input file.
        start_line: The starting line number (1-based index). If None, copies entire file.
        end_line: The ending line number (1-based index). If None and start_line is given, reads to the end of the file.
    """
    input_file = Path(filename)

    if not input_file.is_file():
        print(f"Error: File not found at '{filename}'", file=sys.stderr)
        sys.exit(1)

    try:
        with input_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}", file=sys.stderr)
        sys.exit(1)

    total_lines = len(lines)
    content_to_copy = ""

    if start_line is None:
        # If no start_line is given, copy the entire file
        content_to_copy = "".join(lines)
    else:
        # Adjust start_line to be 0-based index
        start_index = start_line - 1

        # Determine the end_index
        if end_line is None:
            end_index = total_lines  # Reads to the end of the file
        else:
            end_index = end_line

        # Validate line numbers
        if not (0 <= start_index < total_lines):
            print(f"Error: Start line ({start_line}) is out of bounds. File has {total_lines} lines.", file=sys.stderr)
            sys.exit(1)
        if not (0 <= end_index <= total_lines):
            print(
                f"Error: End line ({end_line if end_line is not None else 'end of file'}) is out of bounds. File has {total_lines} lines.",
                file=sys.stderr,
            )
            sys.exit(1)
        if start_index >= end_index:
            start_index, end_index
        # Extract the lines
        selected_lines = lines[start_index:end_index]
        content_to_copy = "".join(selected_lines)

    if not content_to_copy:
        print("No content selected to copy.", file=sys.stderr)
        sys.exit(0)

    # Copy to clipboard using termux-clipboard-set
    try:
        process = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
        _stdout, stderr = process.communicate(input=content_to_copy)
        if process.returncode != 0:
            print(f"Error: Failed to copy to clipboard. STDERR: {stderr}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("Error: 'termux-clipboard-set' command not found. Is Termux:API installed?", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while copying to clipboard: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print(f"Usage: {sys.argv[0]} <filename> [start_line] [end_line]", file=sys.stderr)
        print("  <filename>: Path to the input file.", file=sys.stderr)
        print(
            "  [start_line]: The first line number to copy (1-based index). If omitted, copies the entire file.",
            file=sys.stderr,
        )
        print(
            "  [end_line]: The last line number to copy (1-based index). If omitted and start_line is given, copies to the end of the file.",
            file=sys.stderr,
        )
        sys.exit(1)

    path = Path(sys.argv[1])

    start_line = None
    end_line = None

    if len(sys.argv) >= 3:
        try:
            start_line = int(sys.argv[2])
        except ValueError:
            print("Error: <start_line> must be an integer.", file=sys.stderr)
            sys.exit(1)

    if len(sys.argv) == 4:
        try:
            end_line = int(sys.argv[3])
        except ValueError:
            print("Error: <end_line> must be an integer.", file=sys.stderr)
            sys.exit(1)

    # If start_line was provided but end_line was not, and it's not the 'entire file' case
    # then we should validate start_line against total lines before proceeding to copy.
    # If start_line is None, the 'entire file' case handles it.
    if start_line is not None and end_line is None and len(sys.argv) == 3:
        # We need to read the file once to check total_lines for validation before copying
        # This is a slight inefficiency, but necessary for robust validation.
        # Alternatively, we could try to copy and catch errors, but explicit validation is cleaner.
        if not path.is_file():
            print(f"Error: File not found at '{filename}'", file=sys.stderr)
            sys.exit(1)
        try:
            with path.open("r", encoding="utf-8") as f:
                total_lines = len(f.readlines())
            if not (1 <= start_line <= total_lines):
                print(
                    f"Error: Start line ({start_line}) is out of bounds. File has {total_lines} lines.", file=sys.stderr
                )
                sys.exit(1)
        except OSError as e:
            print(f"Error reading file '{filename}' for validation: {e}", file=sys.stderr)
            sys.exit(1)

    copy_lines_to_clipboard(path, start_line, end_line)


if __name__ == "__main__":
    main()
