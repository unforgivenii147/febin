#!/data/data/com.termux/files/usr/bin/python
"""
Convert a Python script to a Jupyter notebook.
Usage: python py2ipynb.py input.py [output.ipynb]
"""

import argparse
import json
from pathlib import Path

import nbformat as nbf


def py_to_ipynb(input_file, output_file=None):
    """
    Convert a Python file to a Jupyter notebook.
    Args:
        input_file (str): Path to input .py file
        output_file (str, optional): Path to output .ipynb file
    """
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found.")
        return False
    # Read the Python file
    with open(input_file, encoding="utf-8") as f:
        code = f.read()
    # Create a new notebook
    nb = nbf.v4.new_notebook()
    # Split code into cells (separate by double newlines or function/class definitions)
    cells = []
    current_cell = []
    lines = code.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check for potential cell breaks
        if i > 0 and (
                # Function or class definition
                line.startswith("def ") or line.startswith("class ") or
                # Import statements (group them)
            ((line.startswith("import ") or line.startswith("from "))
             and not current_cell[-1].startswith(("import ", "from "))) or
                # Empty line after some code
            (line.strip() == "" and current_cell and i + 1 < len(lines)
             and lines[i + 1].strip() and not lines[i + 1].startswith(
                 (" ", "\t")))):
            # Create a cell from accumulated lines
            if current_cell:
                cell_code = "\n".join(current_cell).strip()
                if cell_code:
                    cells.append(nbf.v4.new_code_cell(cell_code))
                current_cell = []
        current_cell.append(line.rstrip())
        i += 1
    # Add the last cell
    if current_cell:
        cell_code = "\n".join(current_cell).strip()
        if cell_code:
            cells.append(nbf.v4.new_code_cell(cell_code))
    # Add cells to notebook
    nb["cells"] = cells
    # Set default output filename if not provided
    if output_file is None:
        output_file = Path(input_file).stem + ".ipynb"
    # Write the notebook
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Successfully converted '{input_file}' to '{output_file}'")
    print(f"Created {len(cells)} cell(s)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Python script to a Jupyter notebook")
    parser.add_argument("input", help="Input Python file (.py)")
    parser.add_argument(
        "output",
        nargs="?",
        help="Output notebook file (.ipynb) (optional)",
    )
    parser.add_argument(
        "--no-split",
        action="store_true",
        help="Don't split code into multiple cells (one cell only)",
    )
    args = parser.parse_args()
    # Override splitting behavior if requested
    if args.no_split:
        # Simple conversion - everything in one cell
        with open(args.input, encoding="utf-8") as f:
            code = f.read()
        nb = nbf.v4.new_notebook()
        nb["cells"] = [nbf.v4.new_code_cell(code)]
        output_file = args.output or Path(args.input).stem + ".ipynb"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                nb,
                f,
                indent=1,
                ensure_ascii=False,
            )
        print(
            f"Successfully converted '{args.input}' to '{output_file}' (single cell)"
        )
    else:
        # Use the smart splitting conversion
        py_to_ipynb(args.input, args.output)


if __name__ == "__main__":
    main()
