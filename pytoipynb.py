#!/data/data/com.termux/files/usr/bin/env python
"""
Simple converter from .py to .ipynb
"""
import json
import sys
from pathlib import Path
import nbformat as nbf
def simple_convert(py_file, ipynb_file=None):
    """Convert Python file to Jupyter notebook (one cell only)"""
    if not ipynb_file:
        ipynb_file = Path(py_file).stem + ".ipynb"
    # Read Python file
    with open(py_file, "r", encoding="utf-8") as f:
        code = f.read()
    # Create notebook
    nb = nbf.v4.new_notebook()
    nb["cells"] = [nbf.v4.new_code_cell(code)]
    # Save notebook
    with open(ipynb_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"Converted {py_file} to {ipynb_file}")
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simple_convert.py input.py [output.ipynb]")
        sys.exit(1)
    py_file = sys.argv[1]
    ipynb_file = sys.argv[2] if len(sys.argv) > 2 else None
    simple_convert(py_file, ipynb_file)
