#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib
import re


def refactor_file(file_path):
    try:
        content = pathlib.Path(file_path).read_text(encoding="utf-8")
        original_content = content  # Keep a copy to check if changes were made

        # --- Refactoring rules ---
        # os.path.join
        content = re.sub(r"os\.path\.join\(([^,]+),\s*([^)]+)\)", r"(pathlib.Path(\g<1>) / \g<2>)", content)
        # os.listdir
        content = re.sub(r"os\.listdir\(([^)]+)\)", r"[f.name for f in pathlib.Path(\g<1>).iterdir()]", content)
        # os.remove
        content = re.sub(r"os\.remove\(([^)]+)\)", r"pathlib.Path(\g<1>).unlink()", content)
        # os.walk - This is a more complex one and might need a dedicated function if os.walk is used heavily.
        # For simplicity, we'll leave it as is for now and note it as a potential area for further improvement.
        # os.relpath - Similar to os.walk, requires careful handling.
        # os.path.splitext - Can be replaced by `pathlib.Path(file_path).stem` and `pathlib.Path(file_path).suffix`
        content = re.sub(
            r"os\.path\.splitext\(([^)]+)\)", r"(\1.stem, \1.suffix)", content
        )  # This is a simplified replacement and assumes \1 is a pathlib.Path object or a string that can be directly converted. May need adjustment.
        # os.lstat - Can be replaced by `pathlib.Path(file_path).lstat()`

        # --- Add pathlib import if os is imported ---
        if "import os" in content and "import pathlib" not in content:
            # Add import pathlib after the last import statement or at the beginning if no other imports
            lines = content.splitlines()
            import_path = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_path = i
            if import_path != -1:
                lines.insert(import_path + 1, "import pathlib")
            else:
                lines.insert(0, "import pathlib")  # If no import found, add at the top
            content = "\n".join(lines)

        # --- Replace os.walk, os.relpath, os.lstat (more advanced, added as comments for now) ---
        # Note: os.walk replacement is complex. A full rewrite might be needed for robust migration.
        # Example for os.lstat:
        # content = re.sub(r"os\.lstat\(([^)]+)\)", r"pathlib.Path(\g<1>).lstat()", content)

        if content != original_content:
            pathlib.Path(file_path).write_text(content, encoding="utf-8")
            print(f"Successfully refactored: {file_path}")
        else:
            print(f"No changes needed for: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")


# Using os.walk to find all .py files
for root, _dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            print(f"Processing: {full_path}")
            refactor_file(full_path)

print("\nMigration process finished.")
