#!/data/data/com.termux/files/usr/bin/python
import base64
import io
import os
import sqlite3
import sys

import py7zr


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
            file_contents BLOB,
            compressed BOOLEAN DEFAULT 0,
            original_size INTEGER DEFAULT 0,
            compressed_size INTEGER DEFAULT 0
        )
    """)


def compress_data(data_bytes):
    """Compress data using 7z and return as base64 string"""
    if not data_bytes:
        return None
    try:
        # Create in-memory buffer for the archive
        buffer = io.BytesIO()
        # Create 7z archive with the data
        with py7zr.SevenZipFile(buffer, "w") as archive:
            archive.writestr("content", data_bytes)
        # Get compressed data
        compressed_data = buffer.getvalue()
        # Encode as base64 for safe storage in SQLite
        return base64.b64encode(compressed_data).decode("ascii")
    except Exception as e:
        print(f"    Compression error: {e!s}")
        return None


def read_file_contents(filepath):
    try:
        encodings = [
            "utf-8",
            "latin-1",
            "cp1252",
            "iso-8859-1",
        ]
        get_size = os.path.getsize(filepath)
        # For very large files, warn but still try to read
        if get_size > 10 * 1024 * 1024:  # 10MB
            print(f"    Warning: Large file ({get_size / 1024 / 1024:.1f}MB), may take time to compress")
        # First try to read as text
        for encoding in encodings:
            try:
                with open(filepath, encoding=encoding) as f:
                    content = f.read()
                    return {
                        "content": content,
                        "is_binary": False,
                        "original_size": len(
                            content.encode(
                                "utf-8",
                                errors="replace",
                            )
                        ),
                    }
            except (
                UnicodeDecodeError,
                UnicodeError,
            ):
                continue
        # If text reading fails, read as binary
        with open(filepath, "rb") as f:
            content = f.read()
            return {
                "content": content,
                "is_binary": True,
                "original_size": len(content),
            }
    except PermissionError:
        error_msg = "[Permission denied - cannot read file]"
        return {
            "content": error_msg,
            "is_binary": False,
            "original_size": len(error_msg),
        }
    except Exception as e:
        error_msg = f"[Error reading file: {e!s}]"
        return {
            "content": error_msg,
            "is_binary": False,
            "original_size": len(error_msg),
        }


def get_files_in_current_dir():
    current_dir = os.getcwd()
    files = []
    try:
        for item in sorted(os.listdir(current_dir)):
            item_path = os.path.join(current_dir, item)
            if os.path.isfile(item_path):
                get_size = os.path.getsize(item_path)
                size_str = f"{get_size / 1024:.1f}KB" if get_size < 1024 * 1024 else f"{get_size / 1024 / 1024:.1f}MB"
                print(f"  Processing: {item} ({size_str})")
                file_data = read_file_contents(item_path)
                # Store text content directly, compress binary content
                if file_data["is_binary"]:
                    # Compress binary content
                    compressed = compress_data(file_data["content"])
                    if compressed:
                        files.append(
                            {
                                "filename": item,
                                "contents": compressed,
                                "compressed": 1,
                                "original_size": file_data["original_size"],
                                "compressed_size": len(compressed),
                            }
                        )
                        print(
                            f"    ✓ Compressed {file_data['original_size'] / 1024:.1f}KB to {len(compressed) / 1024:.1f}KB"
                        )
                    else:
                        # Fallback to storing as text representation if compression fails
                        files.append(
                            {
                                "filename": item,
                                "contents": "[Binary file - compression failed]",
                                "compressed": 0,
                                "original_size": file_data["original_size"],
                                "compressed_size": 0,
                            }
                        )
                else:
                    # Store text files uncompressed (they're already efficient)
                    files.append(
                        {
                            "filename": item,
                            "contents": file_data["content"],
                            "compressed": 0,
                            "original_size": file_data["original_size"],
                            "compressed_size": 0,
                        }
                    )
                    print(f"    ✓ Stored as text ({file_data['original_size'] / 1024:.1f}KB)")
    except PermissionError:
        print("Warning: Permission denied accessing some files")
    return files


def insert_files(cursor, folder_name, files):
    for file_info in files:
        cursor.execute(
            f"""
            INSERT INTO "{folder_name}" (filename, file_contents, compressed, original_size, compressed_size)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                file_info["filename"],
                file_info["contents"],
                file_info.get("compressed", 0),
                file_info.get("original_size", 0),
                file_info.get("compressed_size", 0),
            ),
        )


def main():
    # Check if py7zr is installed
    try:
        pass
    except ImportError:
        print("Error: py7zr library is not installed.")
        print("Install it with: pip install py7zr")
        sys.exit(1)
    db_path = "/sdcard/pkgs.db"
    # Check permissions
    if not os.access("/sdcard/", os.W_OK):
        print("Error: Cannot write to /sdcard/. Make sure you have proper permissions.")
        print("On Android, you might need to:")
        print("1. Grant storage permissions to Termux/terminal app")
        print("2. Or run the script with appropriate permissions")
        sys.exit(1)
    default_name = get_current_folder_name()
    folder_name = get_user_folder_name(default_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check if folder already exists
    while folder_exists_in_db(cursor, folder_name):
        print(f"Folder name '{folder_name}' already exists in database!")
        folder_name = input("Please enter a different name: ").strip()
        if not folder_name:
            folder_name = default_name + "_new"
            print(f"Using '{folder_name}' as default")
    # Create table with compression support
    create_folder_table(cursor, folder_name)
    print(f"\nScanning current directory: {os.getcwd()}")
    print("Reading and compressing file contents...")
    files = get_files_in_current_dir()
    if not files:
        print("No files found in current directory!")
    else:
        # Insert files into database
        insert_files(cursor, folder_name, files)
        conn.commit()
        # Calculate statistics
        total_original = sum(f.get("original_size", 0) for f in files)
        total_compressed = sum(f.get("compressed_size", 0) for f in files)
        print(f"\n✅ Successfully added {len(files)} files to table '{folder_name}'")
        if total_compressed > 0:
            ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
            print("📊 Storage stats:")
            print(f"   Original size: {total_original / 1024 / 1024:.2f}MB")
            print(f"   Compressed size: {total_compressed / 1024 / 1024:.2f}MB")
            print(f"   Compression ratio: {ratio:.1f}% saved")
        else:
            print(f"   Total size: {total_original / 1024 / 1024:.2f}MB")
    conn.close()


if __name__ == "__main__":
    main()
