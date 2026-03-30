#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

import regex as re


whl_directory = Path()  # Use Path object for the directory
whl_pattern = re.compile(
    r"(?P<name>[\w\-]+)-(?P<version>[\d\.]+(?:-\d{8})?)-(?P<python>py3-none-any|cp37-abi3-linux_armv8l|cp312-cp312-linux_armv8l|cp312-cp312-linux_arm|py3-none-linux_armv8l)\.whl"
)


def cleanup_wheels(whl_dir: Path):
    deleted_files = 0
    latest_versions = {}

    # Iterate through all .whl files in the directory
    for file_path in whl_dir.glob("*.whl"):
        file_name = file_path.name  # Get the filename from the Path object
        match = whl_pattern.match(file_name)
        if match:
            package_name = match.group("name")
            version = match.group("version")
            python_variant = match.group("python")

            if "-" in version:
                date_part = version.split("-")[-1]
                # Store the latest version based on date_part
                if package_name not in latest_versions or date_part > latest_versions[package_name][0]:
                    latest_versions[package_name] = (date_part, version, file_path)
            else:
                # Handle versions without a date part if necessary, though the pattern suggests they might have it.
                # For simplicity, we'll assume versions with date part are the ones to track for "latest".
                pass

    # Second pass to delete files
    for file_path in whl_dir.glob("*.whl"):
        file_name = file_path.name
        match = whl_pattern.match(file_name)
        if match:
            package_name = match.group("name")
            version = match.group("version")
            python_variant = match.group("python")

            # Specific exceptions for deletion
            if (package_name == "pycryptodome" and python_variant == "py3-none-any") or (
                package_name == "matplotlib" and python_variant == "py3-none-any"
            ):
                file_path.unlink()  # Use unlink() directly on the Path object
                print(f"Deleted: {file_name}")
                deleted_files += 1
            # Delete older versions based on the date_part
            elif "-" in version:
                date_part = version.split("-")[-1]
                if (package_name in latest_versions and latest_versions[package_name][0] != date_part) or (
                    package_name in latest_versions and latest_versions[package_name][2] != file_path
                ):
                    file_path.unlink()
                    print(f"Deleted: {file_name}")
                    deleted_files += 1

    return deleted_files


# Get all .whl files using pathlib's glob
whl_files_paths = list(whl_directory.glob("*.whl"))
deleted_files = cleanup_wheels(whl_directory)
print(f"Number of files deleted: {deleted_files}")
