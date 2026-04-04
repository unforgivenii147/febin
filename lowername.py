#!/data/data/com.termux/files/usr/bin/python
import sys
from functools import partial
from pathlib import Path
from dh import unique_path, mpf


def rename_item_to_lowercase(path: Path, dry_run: bool = False, verbose: bool = False) -> tuple[Path, Path] | None:
    """
    Renames a file or directory to its lowercase equivalent.
    Handles existing lowercase names by generating unique names.
    Args:
        path: The Path object of the file or directory to rename.
        dry_run: If True, only print what would happen, don't actually rename.
        verbose: If True, print detailed messages.
    Returns:
        A tuple (path, new_path) if renamed, None otherwise.
        Returns None if no rename is needed or an error occurs (and not dry_run).
    """
    if not path.exists():
        if verbose:
            print(f"Warning: {path} does not exist. Skipping.", file=sys.stderr)
        return None
    # Get the new name in lowercase
    new_name_lower = path.name.lower()
    # If the name is already lowercase, no rename is needed
    if new_name_lower == path.name:
        if verbose:
            print(f"Skipping {path.name}: already lowercase.")
        return None
    # Construct the potential new path
    new_path_candidate = path.parent / new_name_lower
    # If the target lowercase name already exists AND it's not the current item itself
    # (which can happen if the case difference is the only change),
    # then we need to find a unique name.
    if new_path_candidate.exists() and new_path_candidate != path:
        new_path = unique_path(new_path_candidate)
        if verbose:
            print(f"Note: Target {new_path_candidate.name} already exists. Using unique path: {new_path.name}")
    else:
        new_path = new_path_candidate
    if dry_run:
        print(f"DRY RUN: Would rename '{path}' to '{new_path}'")
        return (path, new_path)
    try:
        Path(path).rename(new_path)  # os.rename works for both files and directories
        if verbose:
            print(f"Renamed '{path.name}' to '{new_path.name}'")
        return (path, new_path)
    except OSError as e:
        print(f"Error renaming '{path.name}' to '{new_path.name}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred for '{path.name}': {e}", file=sys.stderr)
        return None


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    if dry_run:
        args.remove("--dry-run")
        print("--- DRY RUN MODE: No changes will be made ---")
    verbose = "--verbose" in args
    if verbose:
        args.remove("--verbose")
    # Determine paths to process
    if args:
        # Process specific paths provided as arguments
        paths_to_process = [Path(p) for p in args]
    else:
        # If no arguments, process all files and directories recursively from CWD
        # IMPORTANT: When renaming directories, you must process deeper items first.
        # If you rename a parent directory first, its children's path will become invalid.
        all_items = list(cwd.rglob("*"))
        # Sort items by depth in descending order so children are processed before parents
        # This ensures that when we rename /a/B/c, we rename 'c' then 'B', then 'a'.
        paths_to_process = sorted(all_items, key=lambda p: len(p.parts), reverse=True)
        # Also include the current directory itself if it's explicitly passed,
        # but for rglob, it already gets its sub-items.
        # The cwd itself would be handled last if it were part of the list.
        # For simplicity, if no args, we assume we want to process everything *inside* cwd.
        # If you wanted to rename cwd itself, you'd need to explicitly pass it.
    if not paths_to_process:
        print("No files or directories found to process.")
        return
    print(f"Found {len(paths_to_process)} items to potentially rename.")
    # Use partial to pass dry_run and verbose flags to the processing function
    process_func_with_flags = partial(rename_item_to_lowercase, dry_run=dry_run, verbose=verbose)
    # Execute the renaming in parallel
    # mpf3 should be a robust multiprocessing function.
    # The return value (list of (original, new) tuples or None) can be collected if needed.
    results = mpf(process_func_with_flags, paths_to_process)
    if dry_run:
        print("--- DRY RUN COMPLETE ---")
    else:
        # Optional: Print a summary of changes made
        renamed_count = sum(1 for r in results if r is not None)
        print(f"\nSummary: Renamed {renamed_count} items.")


if __name__ == "__main__":
    main()
