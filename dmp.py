#!/data/data/com.termux/files/usr/bin/python
"""
This script finds and removes empty directories under the current working directory,
excluding specified directories and handling specific cases like 'mc' directories in 'tmp'.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Set of directory names to always exclude from deletion checks
EXCLUDED_NAMES: Set[str] = {
    "tmp",
    "cache",
    "bin",
    "Android",
    ".git",
    "etc",
    "config",
    "var",
    "venv",  # Commonly excluded virtual environment directory
    "node_modules",  # Commonly excluded Node.js dependency directory
}
# Directories that, if they contain any of EXCLUDED_NAMES in their path, are also excluded
# This is for preventing deletion of subdirectories within, for example, a .git directory.
EXCLUDED_PATH_COMPONENTS: Set[str] = {
    ".git",
    "tmp",
    "etc",
    "var",
    "config",
}


def is_excluded(path: Path, root_path: Path) -> bool:
    """
    Checks if a given path should be excluded from empty directory checks.
    Exclusion rules:
    1. If its own name is in EXCLUDED_NAMES.
    2. If any component of its *relative* path (from the root_path) is in EXCLUDED_PATH_COMPONENTS.
    3. Special case: if path.name starts with "mc" and its parent is "tmp".
    """
    if path.name in EXCLUDED_NAMES:
        return True
    try:
        relative_parts = path.relative_to(root_path).parts
        if any(part in EXCLUDED_PATH_COMPONENTS for part in relative_parts):
            return True
    except ValueError:
        # path is not relative to root_path, should not happen if called correctly
        pass
    if path.name.startswith("mc") and path.parent.name == "tmp":
        return True
    return False


def delete_empty_dirs_iterative(root: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[int, List[Path]]:
    """
    Finds and deletes empty directories iteratively from the bottom up.
        root: The starting directory to scan.
        dry_run: If True, only print what would be deleted, don't actually delete.
        verbose: If True, print detailed messages about processed directories.
        A tuple containing:
        - The count of directories removed.
        - A list of Path objects that were removed.
    """
    removed_count: int = 0
    removed_dirs_list: List[Path] = []
    # Start with all subdirectories of the root (and root itself if it becomes empty)
    dirs_to_visit: List[Path] = [d for d in root.rglob("*") if d.is_dir()]
    # Sort in reverse order to process deeper directories first (bottom-up)
    dirs_to_visit.sort(key=lambda p: len(p.parts), reverse=True)
    if root.is_dir():
        dirs_to_visit.append(root)
    for path in dirs_to_visit:
        if not path.is_dir():  # Might have been deleted by a previous iteration
            continue
        if is_excluded(path, root):
            if verbose:
                print(f"Skipping excluded directory: {path.relative_to(root)}")
            continue
        try:
            # Check if directory is empty after filtering out other directories
            # and non-directory files
            if not any(entry for entry in path.iterdir() if entry.is_dir() or entry.is_file()):
                if verbose:
                    print(f"Empty directory found: {path.relative_to(root)}")
                if not dry_run:
                    path.rmdir()
                    removed_count += 1
                    removed_dirs_list.append(path)
                    if verbose:
                        print(f"  --> Removed: {path.relative_to(root)}")
                else:
                    print(f"  (Dry Run) Would remove: {path.relative_to(root)}")
        except PermissionError:
            print(f"[ERROR] Permission denied for: {path.relative_to(root)}", file=sys.stderr)
        except OSError as e:
            print(f"[ERROR] Could not process {path.relative_to(root)}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred with {path.relative_to(root)}: {e}", file=sys.stderr)
    return removed_count, removed_dirs_list


def main():
    parser = argparse.ArgumentParser(description="Find and remove empty directories, excluding specified ones.")
    parser.add_argument(
        "path",
        nargs="?",  # Optional argument
        type=Path,
        default=Path.cwd(),
        help="The root directory to start scanning from (default: current working directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run: show what would be deleted without actually deleting.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output, showing skipped and found directories.",
    )
    args = parser.parse_args()
    root_path = args.path.resolve()  # Resolve to absolute path
    if not root_path.is_dir():
        print(f"Error: The provided path '{root_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print("--- DRY RUN MODE (no changes will be made) ---")
    removed_count, removed_dirs_list = delete_empty_dirs_iterative(
        root_path, dry_run=args.dry_run, verbose=args.verbose
    )
    if removed_count > 0:
        if args.dry_run:
            print(f"Would have removed {removed_count} empty directories:")
        else:
            print(f"removed {removed_count}")
        for d_path in sorted(removed_dirs_list):  # Sort for consistent output
            print(f"- {d_path.relative_to(root_path)}")
    else:
        print("No empty dir.")


if __name__ == "__main__":
    main()
