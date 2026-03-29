#!/data/data/com.termux/files/usr/bin/python
from shutil import copy2
from pathlib import Path

from dh import is_binary, unique_path


DEST = Path(str(Path.home()) + "/tmp/scripts")
if not DEST.exists():
    DEST.mkdir(exist_ok=True)


def find_scripts_without_extension(directory):
    scripts_without_extension = []
    for item in directory.rglob("*"):
        if item.is_symlink():
            continue
        if ".git" in item.parts:
            continue
        if item.is_file() and not item.suffix:
            # Check if the file is likely a Python script by trying to read the first line
            # This is a heuristic and might not catch all cases perfectly
            if is_binary(item):
                continue
            try:
                with Path(item).open("r", encoding="utf-8") as f:
                    first_line = f.readline()
                    if first_line.strip().startswith("#!") and "python" in first_line:
                        scripts_without_extension.append(item)
            except Exception as e:
                # Handle potential errors like permission issues or non-text files
                print(f"Could not read {item}: {e}")
    return scripts_without_extension


if __name__ == "__main__":
    cwd = Path.cwd()

    found_scripts = find_scripts_without_extension(cwd)

    if found_scripts:
        print("Found Python scripts without extension (relative paths):")
        for script_path in found_scripts:
            print(script_path.relative_to(cwd))
            dest = DEST / script_path.name
            if dest.exists():
                dest = unique_path(dest)
            copy2(str(script_path), str(dest))
            print(f"{script_path.name} -> {dest:}")
    else:
        print("No Python scripts without extension found in the current directory or its subdirectories.")
