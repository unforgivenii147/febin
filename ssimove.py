#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil

import ssdeep

# --- Configuration ---
# Directory to search for files (current directory by default)
SEARCH_DIR = Path.cwd()
# Directory to move similar file groups into
OUTPUT_DIR = SEARCH_DIR / "output"
# Threshold for ssdeep similarity. Higher means more similar.
# A score of 0 means completely different. A score of 100 means identical.
# Common values to start with are 40-60. Adjust based on your needs.
SIMILARITY_THRESHOLD = 60
# Minimum number of files in a group to be considered for moving
MIN_GROUP_SIZE = 2
# --- End Configuration ---


def calculate_fuzzy_hash(filepath: Path) -> str:
    """Calculates the ssdeep fuzzy hash for a given file."""
    try:
        # ssdeep.hash_from_file() reads the entire file, which can be memory intensive for large files.
        # For very large files, a chunked approach might be needed, but ssdeep's library might not directly support it easily.
        # We'll assume files are manageable for now.
        return ssdeep.hash_from_file(str(filepath))
    except ssdeep.Error as e:
        print(f"Error calculating ssdeep hash for {filepath}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error for {filepath}: {e}")
        return ""


def find_similar_files(
    search_dir: Path,
    output_dir: Path,
    similarity_threshold: int,
    min_group_size: int,
) -> None:
    """Finds similar files recursively, calculates their hashes, and moves similar groups."""
    output_dir.mkdir(parents=True, exist_ok=True)

    file_hashes: dict[Path, str] = {}
    # Collect all files and their hashes first
    for filepath in search_dir.rglob("*"):
        if filepath.is_file() and not filepath.is_symlink():
            hash_value = calculate_fuzzy_hash(filepath)
            if hash_value:
                file_hashes[filepath] = hash_value

    if not file_hashes:
        print("No files found or no hashes could be generated.")
        return

    # Store potential groups of similar files.
    # Key: A representative file from a group, Value: List of similar files in that group
    similar_groups: dict[Path, list[Path]] = {}
    processed_files = set()  # Keep track of files already assigned to a group

    # Compare each file's hash with every other file's hash
    file_paths = list(file_hashes.keys())
    num_files = len(file_paths)

    for i in range(num_files):
        current_file = file_paths[i]
        if current_file in processed_files:
            continue

        current_hash = file_hashes[current_file]
        current_group = [current_file]  # Start a new group with the current file

        for j in range(i + 1, num_files):
            other_file = file_paths[j]
            if other_file in processed_files:
                continue

            other_hash = file_hashes[other_file]

            # Calculate similarity score
            # ssdeep.compare(hash1, hash2) returns a similarity score (0-100)
            try:
                similarity = ssdeep.compare(current_hash, other_hash)
                if similarity >= similarity_threshold:
                    print(f"  - Found similarity ({similarity}/{current_hash} vs {other_hash} -> {other_file})")
                    current_group.append(other_file)
            except ssdeep.Error as e:
                print(f"Error comparing hashes for {current_file} and {other_file}: {e}")
            except Exception as e:
                print(f"Unexpected error comparing hashes for {current_file} and {other_file}: {e}")

        # If the current group has enough files to meet the minimum size requirement
        if len(current_group) >= min_group_size:
            # Add all files from this group to processed_files to avoid re-processing them
            processed_files.update(current_group)

            # Use the first file of the group as the key for this group
            # Ensure this group isn't a subset of an already found larger group
            # (This simple approach might group files multiple times if not careful.
            # A more robust way would be to use connected components, but this is simpler for now.)
            # For simplicity, we'll just add it and clean up later if needed.
            # A better approach: check if any file in current_group is already part of another identified group.
            # For now, let's assume distinct groups based on the first element.

            # We need a way to ensure that if file A is similar to B, and B is similar to C,
            # they all end up in the same group, even if A is not directly similar to C.
            # This implies a graph problem (finding connected components).
            # The current pairwise comparison is a start but might miss transitive similarities.

            # For this script, let's make a simplifying assumption:
            # If a file is part of a group, we mark it as processed.
            # The `current_group` will be the definitive list of similar files for this iteration.
            # We'll use the first file as a "representative" for this iteration's finding.
            representative_file = current_group[0]
            similar_groups[representative_file] = current_group
            print(f"  -> Added group (starting with {representative_file.name}) with {len(current_group)} files.")

    # --- Move files into groups ---
    print("\n--- Moving Similar Files ---")
    moved_files_count = 0
    group_counter = 0

    # Now, process the identified groups and move them
    # We need to be careful not to move a file multiple times if it was part of multiple initial groups.
    # The `processed_files` set helps here.
    files_to_move = set()
    final_groups_to_move = []

    for rep_file, group in similar_groups.items():
        # Only consider files that haven't been part of another processed group
        valid_group = [f for f in group if f not in processed_files or f == rep_file]
        if len(valid_group) >= min_group_size:
            final_groups_to_move.append(valid_group)
            files_to_move.update(valid_group)  # Add to a set of all files that will be moved

    # Update processed_files with all files that are confirmed to be moved
    processed_files.update(files_to_move)

    for group in final_groups_to_move:
        group_counter += 1
        # Create a unique subdirectory for each group
        # Use a counter to ensure unique names, as file names might clash
        group_output_subdir = output_dir / f"group_{group_counter:03d}"
        group_output_subdir.mkdir(parents=True, exist_ok=True)
        print(f"Creating group directory: {group_output_subdir}")

        for file_to_move in group:
            try:
                # Construct the destination path
                dest_path = group_output_subdir / file_to_move.name
                # Ensure we don't overwrite if a file with the same name already exists
                # (though unlikely if original files are unique)
                if dest_path.exists():
                    print(f"  - Warning: Destination file already exists, skipping: {dest_path}")
                    continue

                shutil.move(str(file_to_move), str(dest_path))
                print(f"  - Moved: {file_to_move.name} to {group_output_subdir.name}/")
                moved_files_count += 1
            except FileNotFoundError:
                print(
                    f"  - Error: File not found during move (might have been moved already or deleted): {file_to_move}"
                )
            except Exception as e:
                print(f"  - Error moving {file_to_move.name}: {e}")

    print("\n--- Summary ---")
    if group_counter == 0:
        print("No groups of similar files found that met the criteria.")
    else:
        print(f"Moved {moved_files_count} files into {group_counter} groups.")
        print(f"Similar files have been moved to: {output_dir}")


if __name__ == "__main__":
    # Ensure the script is run from the directory you want to process or modify SEARCH_DIR
    if Path.cwd() == SEARCH_DIR:
        print("INFO: Processing files in the current directory.")
    else:
        print(f"INFO: Processing files in: {SEARCH_DIR}")

    # Add a small check to prevent accidental deletion if output dir is same as search dir
    if SEARCH_DIR.resolve() == OUTPUT_DIR.resolve():
        print("ERROR: SEARCH_DIR and OUTPUT_DIR cannot be the same. Please configure them differently.")
    else:
        find_similar_files(
            search_dir=SEARCH_DIR,
            output_dir=OUTPUT_DIR,
            similarity_threshold=SIMILARITY_THRESHOLD,
            min_group_size=MIN_GROUP_SIZE,
        )
