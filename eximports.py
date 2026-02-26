#!/usr/bin/env python
from collections import defaultdict
from pathlib import Path

import tree_sitter_python as tsp
from tree_sitter import Language, Parser

parser = Parser()
parser.language = Language(tsp.language())

OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

VALID = {
    "import_statement",
    "import_from_statement",
}


def extract_file(src: bytes, tree):
    root = tree.root_node

    chunks = []
    for node in root.children:
        if node.type in VALID:
            chunks.append(src[node.start_byte : node.end_byte].decode())

    return chunks


# Dictionary to store imports by folder path
folder_imports = defaultdict(list)

for py in Path(".").rglob("*.py"):
    # Skip hidden directories and site-packages
    if any(part.startswith(".") for part in py.parts) or "site-packages" in py.parts:
        continue

    # Skip files in the output directory
    if OUT_DIR in py.parents:
        continue

    src = py.read_bytes()
    tree = parser.parse(src)

    imports = extract_file(src, tree)

    if imports:
        # Get the folder containing the Python file
        folder_path = py.parent
        relative_folder = folder_path.relative_to(".")

        # Add imports with file comment
        folder_imports[relative_folder].append(f"\n".join(imports))

# Write collected imports to folder-specific files
for folder, imports_list in folder_imports.items():
    if not imports_list:
        continue

    # Create output file path: output/foldername/imports.py
    out_file = OUT_DIR / folder / "imports.py"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Combine all imports with proper spacing
    content = "\n\n".join(imports_list)

    out_file.write_text(content)


print(f"\n✨ Done! Processed {len(folder_imports)} folder(s)")
