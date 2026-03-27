#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib


search_string = 'b64 = """'
current_dir = pathlib.Path.cwd()
for root, _dirs, files in os.walk(current_dir):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            with pathlib.Path(file_path).open(encoding="utf-8") as f:
                content = f.read()
                if search_string in content:
                    print(f"Found in file: {file_path}")
        except (
            UnicodeDecodeError,
            PermissionError,
        ):
            continue
