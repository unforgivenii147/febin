#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import sys
from pathlib import Path

from dh import MIME2EXT


def get_file_mime(file_path):
    try:
        result = subprocess.run(
            [
                "file",
                "--brief",
                "--mime-type",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(
            f"Error detecting file type for {file_path}: {e}",
            file=sys.stderr,
        )
        return None


def check_files(directory):
    mismatched_files = []

    for root, _, files in os.walk(directory):
        for name in files:
            file_path = Path(root) / name
            ext = file_path.suffix.lower()
            if ext == ".css":
                continue
            mime = get_file_mime(file_path)
            print(f"{name} --> {mime}")
            if mime:
                expected_exts = MIME2EXT.get(mime, [])
                if expected_exts and ext not in expected_exts:
                    new_path = None
                    new_ext = expected_exts[0]
                    if new_ext == ".txt" and ext == ".css":
                        continue
                    #                        new_ext = filetype.guess(file_path)
                    new_path = file_path.with_suffix(new_ext)
                    if new_path.exists():
                        new_path = unique_path(new_path)
                        content = file_path.read_text(encoding="utf-8")
                        new_path.write_text(content, encoding="utf-8")
                        file_path.unlink()
                    mismatched_files.append((
                        file_path,
                        ext,
                        mime,
                        new_path,
                    ))
    return mismatched_files


def main():
    cwd = Path.cwd()

    mismatches = check_files(cwd)
    if mismatches:
        print("Files with mismatched extensions:")
        for (
            file_path,
            _ext,
            mime,
            new_path,
        ) in mismatches:
            if new_path:
                print(
                    f"\033[5;93m{file_path.relative_to(cwd)} | {mime} | \033[5;96m{new_path.relative_to(cwd)}]\033[0m"
                )

            else:
                print(f"{file_path.relative_to(cwd)} -> \033[5m;94mdetected: {mime}\033[0m")
    else:
        print("All file extensions match their detected types.")


if __name__ == "__main__":
    main()
