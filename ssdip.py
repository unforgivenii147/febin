#!/data/data/com.termux/files/usr/bin/python
from collections import defaultdict
from pathlib import Path
import sys

import ssdeep


def find_fuzzy_duplicates(start_dir: Path = Path.cwd(), threshold: int = 70):
    """
    Finds files with similar content using ssdeep fuzzy hashing.
    Threshold is a value between 0 and 100, higher means more similar.
    """
    file_hashes = {}  # Stores {filepath: fuzzy_hash}
    duplicates = defaultdict(list)

    print(f"Scanning for fuzzy duplicates in: {start_dir}")

    for filepath in start_dir.rglob("*"):
        if filepath.is_file() and not filepath.is_symlink():
            try:
                # Read a portion of the file for ssdeep, larger files benefit from more data
                # ssdeep works best with files > 1KB. Adjust read_size as needed.
                read_size = 1024 * 1024  # Read up to 1MB initially
                with open(filepath, "rb") as f:
                    data = f.read(read_size)
                    if len(data) > 50:  # ssdeep requires some minimum data
                        fuzzy_hash = ssdeep.hash(data)
                        file_hashes[filepath] = fuzzy_hash
            except OSError as e:
                print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Unexpected error processing {filepath}: {e}", file=sys.stderr)

    print(f"Calculated fuzzy hashes for {len(file_hashes)} files.")

    # Compare hashes:
    # Iterate through each file and compare its hash against all subsequent files
    # to avoid redundant comparisons (A vs B and B vs A).
    processed_files = list(file_hashes.keys())
    for i, f1_path in enumerate(processed_files):
        if not file_hashes.get(f1_path):
            continue  # Skip if hash failed earlier

        for j in range(i + 1, len(processed_files)):
            f2_path = processed_files[j]
            if not file_hashes.get(f2_path):
                continue

            # Compare hashes
            comparison_score = ssdeep.compare(file_hashes[f1_path], file_hashes[f2_path])

            if comparison_score >= threshold:
                print(
                    f"Potential match: {f1_path.relative_to(start_dir)} and {f2_path.relative_to(start_dir)} (Score: {comparison_score})"
                )
                # You can add these to a list to process further (e.g., to delete older ones)
                duplicates[f1_path].append((f2_path, comparison_score))

    if not duplicates:
        print("No significantly similar files found.")
    else:
        print("\n--- Fuzzy Duplicate Sets ---")
        # You would typically then implement logic to decide which file to keep
        # and which to delete from these sets.
        for file, similar_files in duplicates.items():
            print(f"\nFile: {file.relative_to(start_dir)}")
            for dup_file, score in similar_files:
                print(f"  - Similar: {dup_file.relative_to(start_dir)} (Score: {score})")


if __name__ == "__main__":
    cwd = Path.cwd()

    find_fuzzy_duplicates(cwd, threshold=90)
