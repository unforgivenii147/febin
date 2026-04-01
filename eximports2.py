#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from collections import defaultdict

from tree_sitter import Parser, Language
import tree_sitter_python as tsp


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
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        # If file is not under base_path, return the full path
        return file_path


# Dictionary to store imports by folder path
folder_imports = defaultdict(list)
processed_files_count = 0
folders_found = set()
for py in Path().rglob("*.py"):
    # Skip hidden directories and site-packages
    if any(part.startswith(".") for part in py.parts) or "site-packages" in py.parts:
        continue
    # Skip files in the output directory
    if OUT_DIR in py.parents:
        continue
    try:
        src = py.read_bytes()
        tree = parser.parse(src)
        imports = extract_file(src, tree)
        if imports:
            # Get the folder containing the Python file
            folder_path = py.parent
            relative_folder = get_relative_path(folder_path, Path())
            folders_found.add(str(relative_folder))
            # Add imports with file comment
            file_header = f"# === {py.name} ===\n"
            folder_imports[relative_folder].append(file_header + "\n".join(imports))
            processed_files_count += 1
    except Exception as e:
        print(f"⚠️  Error processing {py}: {e}")
# Write collected imports to folder-specific files
for (
    folder,
    imports_list,
) in folder_imports.items():
    if not imports_list:
        continue
    # Create output file path: output/foldername/imports.py
    out_file = OUT_DIR / folder / "imports.py"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    # Combine all imports with proper spacing
    content = "\n\n".join(imports_list)
    # Add a comprehensive header
    header = f"""# Auto-generated imports file for folder: {folder}
# Generated from {len(imports_list)} Python file(s) ({processed_files_count} total files processed)
# Date: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    out_file.write_text(header + content)
    print(f"✅ saved: {out_file} ({len(imports_list)} files)")
print(f"\n✨ Done! Processed {processed_files_count} files in {len(folder_imports)} folder(s)")
print(f"📁 Folders: {', '.join(sorted(folders_found))}")
