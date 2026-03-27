#!/data/data/com.termux/files/usr/bin/python
"""Simple converter from .py to .ipynb."""

import sys
import json
from pathlib import Path

import nbformat as nbf


def simple_convert(py_file, ipynb_file=None):
    """Convert Python file to Jupyter notebook (one cell only)."""
    if not ipynb_file:
        ipynb_file = Path(py_file).stem + ".ipynb"
    # Read Python file
    code = Path(py_file).read_text(encoding="utf-8")
    # Create notebook
    nb = nbf.v4.new_notebook()
    nb["cells"] = [nbf.v4.new_code_cell(code)]
    # Save notebook
    with Path(ipynb_file).open("w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"Converted {py_file} to {ipynb_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simple_convert.py input.py [output.ipynb]")
        sys.exit(1)
    py_file = sys.argv[1]
    ipynb_file = sys.argv[2] if len(sys.argv) > 2 else None
    simple_convert(py_file, ipynb_file)
