#!/data/data/com.termux/files/usr/bin/python
from collections import defaultdict
import os


def find_path_duplicates():
    # Get the PATH environment variable
    path_env = os.environ.get("PATH", "")
    # Split by colon and filter out empty strings
    directories = [d for d in path_env.split(":") if d]
    # Dictionary to store: executable_name -> [list_of_directories]
    app_map = defaultdict(list)
    print(f"--- Scanning {len(directories)} directories in PATH ---\n")
    for directory in directories:
        # Check if the directory actually exists
        if not os.path.isdir(directory):
            continue
        try:
            # List all files in the directory
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                # Ensure it's a file and it's executable
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    app_map[item].append(directory)
        except PermissionError:
            print(f"Permission denied: {directory}")
            continue
    # Filter and display duplicates
    duplicates_found = False
    for app, locations in app_map.items():
        if len(locations) > 1:
            duplicates_found = True
            print(f"Duplicate found: [ {app} ]")
            for i, loc in enumerate(locations):
                # Highlight which one is actually being used (the first one)
                status = " (ACTIVE)" if i == 0 else " (SHADOWED)"
                print(f"  - {loc}{status}")
            print("-" * 30)
    if not duplicates_found:
        print("Clean as a whistle! No duplicate executables found.")


if __name__ == "__main__":
    find_path_duplicates()
