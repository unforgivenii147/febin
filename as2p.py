#!/data/data/com.termux/files/usr/bin/python

import os
import pathlib

import regex as re


def refactor_file(file_path):
    try:
        content = pathlib.Path(file_path).read_text(encoding="utf-8")
        original_content = content
        content = re.sub(
            r"os\.path\.join\(([^,]+),\s*([^)]+)\)",
            r"(pathlib.Path(\g<1>) / \g<2>)",
            content,
        )
        content = re.sub(
            r"os\.listdir\(([^)]+)\)",
            r"[f.name for f in pathlib.Path(\g<1>).iterdir()]",
            content,
        )
        content = re.sub(r"os\.remove\(([^)]+)\)", r"pathlib.Path(\g<1>).unlink()", content)
        content = re.sub(r"os\.path\.splitext\(([^)]+)\)", r"(\1.stem, \1.suffix)", content)
        if "import os" in content and "import pathlib" not in content:
            lines = content.splitlines()
            import_path = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_path = i
            if import_path != -1:
                lines.insert(import_path + 1, "import pathlib")
            else:
                lines.insert(0, "import pathlib")
            content = "\n".join(lines)
        if content != original_content:
            pathlib.Path(file_path).write_text(content, encoding="utf-8")
            print(f"Successfully refactored: {file_path}")
        else:
            print(f"No changes needed for: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


for root, _dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            print(f"Processing: {full_path}")
            refactor_file(full_path)
print("\nMigration process finished.")
