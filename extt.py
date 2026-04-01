#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from tree_sitter import Parser, Language
import tree_sitter_python as tsp


parser = Parser()
parser.language = Language(tsp.language())
OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)
VALID = {
    "function_definition",
    "class_definition",
}


def get_node_text(src: bytes, node):
    return src[node.start_byte : node.end_byte].decode()


def get_node_name(node):
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode() if hasattr(child, "text") else None
    return None


def extract_functions_and_classes(src: bytes, tree):
    root = tree.root_node
    definitions = []

    def traverse(node):
        if node.type in VALID:
            name = get_node_name(node)
            node_text = get_node_text(src, node)
            # Add decorators if present
            decorators = []
            prev_node = node.prev_sibling
            while prev_node and prev_node.type == "decorator":
                decorators.append(get_node_text(src, prev_node))
                prev_node = prev_node.prev_sibling
            if decorators:
                node_text = "\n".join(reversed(decorators)) + "\n" + node_text
            definitions.append({
                "type": node.type.replace("_definition", ""),
                "name": name,
                "text": node_text,
                "line": node.start_point.row + 1,
            })
        for child in node.children:
            traverse(child)

    traverse(root)
    return definitions


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        return file_path


# Dictionary to store definitions by folder path
folder_definitions = defaultdict(lambda: defaultdict(list))
processed_files_count = 0
folders_found = set()
total_definitions = 0
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
        definitions = extract_functions_and_classes(src, tree)
        if definitions:
            # Get the folder containing the Python file
            folder_path = py.parent
            relative_folder = get_relative_path(folder_path, Path())
            folders_found.add(str(relative_folder))
            # Store definitions by file
            folder_definitions[relative_folder][py.name] = {
                "definitions": definitions,
                "path": py,
            }
            processed_files_count += 1
            total_definitions += len(definitions)
    except Exception as e:
        print(f"⚠️  Error processing {py}: {e}")
# Write collected definitions to folder-specific files
for (
    folder,
    files_dict,
) in folder_definitions.items():
    if not files_dict:
        continue
    # Create output file path: output/foldername/definitions.py
    out_file = OUT_DIR / folder / "definitions.py"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    # Build content with better organization
    content_parts = []
    # Add table of contents
    content_parts.extend(("#" + "=" * 78, "# TABLE OF CONTENTS", "#" + "=" * 78, ""))
    for file_name, file_data in sorted(files_dict.items()):
        content_parts.append(f"# File: {file_name}")
        def_counts = {"function": 0, "class": 0}
        for d in file_data["definitions"]:
            def_counts[d["type"]] += 1
        if def_counts["function"] > 0:
            content_parts.append(f"#   Functions: {def_counts['function']}")
        if def_counts["class"] > 0:
            content_parts.append(f"#   Classes: {def_counts['class']}")
        content_parts.append("")
    content_parts.extend(("#" + "=" * 78, "# DEFINITIONS", "#" + "=" * 78, ""))
    # Add actual definitions
    for file_name, file_data in sorted(files_dict.items()):
        content_parts.extend((
            f"\n# {'=' * 76}",
            f"# File: {file_name}",
            f"# Path: {file_data['path']}",
            f"# {'=' * 76}\n",
        ))
        # Group by type (classes first, then functions)
        classes = [d for d in file_data["definitions"] if d["type"] == "class"]
        functions = [d for d in file_data["definitions"] if d["type"] == "function"]
        if classes:
            content_parts.extend(("#" + "-" * 40, "# CLASSES", "#" + "-" * 40, ""))
            for i, cls in enumerate(classes):
                if i > 0:
                    content_parts.append("\n" + "#" + "-" * 38 + "\n")
                content_parts.append(f"# Line: {cls['line']}")
                if cls["name"]:
                    content_parts.append(f"# Class: {cls['name']}")
                content_parts.append(cls["text"])
        if functions:
            if classes:
                content_parts.append("\n" + "#" + "-" * 40)
            else:
                content_parts.append("#" + "-" * 40)
            content_parts.extend(("# FUNCTIONS", "#" + "-" * 40, ""))
            for i, func in enumerate(functions):
                if i > 0:
                    content_parts.append("\n" + "#" + "-" * 38 + "\n")
                content_parts.append(f"# Line: {func['line']}")
                if func["name"]:
                    content_parts.append(f"# Function: {func['name']}")
                content_parts.append(func["text"])
        content_parts.append("\n" + "#" + "=" * 78 + "\n")
    # Combine all content
    content = "\n".join(content_parts)
    # Add header
    header = f"""#!/usr/bin/env python
# Auto-generated definitions file
# Folder: {folder}
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Files processed: {len(files_dict)}
# Total definitions: {sum(len(f["definitions"]) for f in files_dict.values())}
"""
    out_file.write_text(header + content)
    # Statistics
    total_defs_in_folder = sum(len(f["definitions"]) for f in files_dict.values())
    print(f"✅ saved: {out_file}")
    print(f"   📊 {len(files_dict)} files, {total_defs_in_folder} definitions")
    print(f"   📁 {folder}")
print(
    f"\n✨ Done! Processed {processed_files_count} files with {total_definitions} total definitions in {len(folder_definitions)} folder(s)"
)
if folders_found:
    print("📁 Folders:")
    for folder in sorted(folders_found):
        def_count = sum(len(f["definitions"]) for f in folder_definitions[Path(folder)].values())
        file_count = len(folder_definitions[Path(folder)])
        print(f"   • {folder}: {file_count} files, {def_count} definitions")
