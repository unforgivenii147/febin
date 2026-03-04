#!/data/data/com.termux/files/usr/bin/env python
import os
import sqlite3
import sys


def get_current_folder_name():
    return os.path.basename(os.getcwd())


def get_user_folder_name(default_name):
    while True:
        user_input = input(f"Enter folder name (default: {default_name}): ").strip()
        if not user_input:
            return default_name
        return user_input


def folder_exists_in_db(cursor, folder_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (folder_name,),
    )
    return cursor.fetchone() is not None


def create_folder_table(cursor, folder_name):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{folder_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_contents TEXT
        )
    """)


def read_file_contents(filepath):
    try:
        encodings = [
            "utf-8",
            "latin-1",
            "cp1252",
            "iso-8859-1",
        ]
        for encoding in encodings:
            try:
                with open(filepath, encoding=encoding) as f:
                    return f.read(1024 * 1024)
            except (
                UnicodeDecodeError,
                UnicodeError,
            ):
                continue
        return "[Binary file content not stored]"
    except PermissionError:
        return "[Permission denied - cannot read file]"
    except Exception as e:
        return f"[Error reading file: {e!s}]"


def get_files_in_current_dir():
    current_dir = os.getcwd()
    files = []
    try:
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if os.path.isfile(item_path):
                print(f"  Reading: {item}")
                contents = read_file_contents(item_path)
                files.append(
                    {
                        "filename": item,
                        "contents": contents,
                    }
                )
    except PermissionError:
        print("Warning: Permission denied accessing some files")
    return files


def insert_files(cursor, folder_name, files):
    for file_info in files:
        cursor.execute(
            f"""
            INSERT INTO "{folder_name}" (filename,  file_contents)
            VALUES (?, ?)
        """,
            (
                file_info["filename"],
                file_info["contents"],
            ),
        )


def main():
    if not os.access("/sdcard/", os.W_OK):
        print("Error: Cannot write to /sdcard/. Make sure you have proper permissions.")
        print("On Android, you might need to:")
        print("1. Grant storage permissions to Termux/terminal app")
        print("2. Or run the script with appropriate permissions")
        sys.exit(1)
    default_name = get_current_folder_name()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    while folder_exists_in_db(cursor, folder_name):
        print(f"Folder name '{folder_name}' already exists in database!")
        folder_name = input("Please enter a different name: ").strip()
        if not folder_name:
            folder_name = default_name + "_new"
            print(f"Using '{folder_name}' as default")
    create_folder_table(cursor, folder_name)
    print(f"\nScanning current directory: {os.getcwd()}")
    print("Reading file contents (limited to 1MB per file)...")
    files = get_files_in_current_dir()
    if not files:
        print("No files found in current directory!")
    else:
        print(f"\nFound {len(files)} files:")
        insert_files(cursor, folder_name, files)
        conn.commit()
        print(f"\n✅ Successfully added {len(files)} files to table '{folder_name}'")


if __name__ == "__main__":
    main()
