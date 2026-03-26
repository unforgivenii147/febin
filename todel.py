#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib


def delete_multiline_string_from_files(search_string, directory=".") -> None:
    EXT = [
        ".txt",
        ".py",
        ".md",
        ".pyx",
        ".pyi",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
    ]
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path) and os.path.splitext(file_path)[1] in EXT:
                try:
                    content = pathlib.Path(file_path).read_text(encoding="utf-8")
                    if search_string in content:
                        new_content = content.replace(search_string, "")
                        pathlib.Path(file_path).write_text(new_content, encoding="utf-8")
                        print(f"Deleted string from {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")


def read_string_to_delete(
    filename="/sdcard/todel.txt",
):
    try:
        with open(filename, encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading the file {filename}: {e}")
        return None


if __name__ == "__main__":
    string_to_delete = read_string_to_delete()
    if string_to_delete:
        delete_multiline_string_from_files(string_to_delete)
