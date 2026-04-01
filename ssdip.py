#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from collections import defaultdict

import ssdeep


def find_fuzzy_duplicates(start_dir: Path = Path.cwd(), threshold: int = 70):
    file_hashes = {}
    duplicates = defaultdict(list)
    print(f"Scanning for fuzzy duplicates in: {start_dir}")
    for filepath in start_dir.rglob("*"):
        if filepath.is_file() and not filepath.is_symlink():
            try:
                read_size = 1024 * 1024
                with Path(filepath).open("rb") as f:
                    data = f.read(read_size)
                    if len(data) > 50:
                        fuzzy_hash = ssdeep.hash(data)
                        file_hashes[filepath] = fuzzy_hash
            except OSError as e:
                print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Unexpected error processing {filepath}: {e}", file=sys.stderr)
    print(f"Calculated fuzzy hashes for {len(file_hashes)} files.")

    processed_files = list(file_hashes.keys())
    for i, f1_path in enumerate(processed_files):
        if not file_hashes.get(f1_path):
            continue
        for j in range(i + 1, len(processed_files)):
            f2_path = processed_files[j]
            if not file_hashes.get(f2_path):
                continue

            comparison_score = ssdeep.compare(file_hashes[f1_path], file_hashes[f2_path])
            if comparison_score >= threshold:
                print(
                    f"Potential match: {f1_path.relative_to(start_dir)} and {f2_path.relative_to(start_dir)} (Score: {comparison_score})"
                )

                duplicates[f1_path].append((f2_path, comparison_score))
    if not duplicates:
        print("No significantly similar files found.")
    else:
        print("\n--- Fuzzy Duplicate Sets ---")

        for file, similar_files in duplicates.items():
            print(f"\nFile: {file.relative_to(start_dir)}")
            for dup_file, score in similar_files:
                print(f"  - Similar: {dup_file.relative_to(start_dir)} (Score: {score})")


if __name__ == "__main__":
    cwd = Path.cwd()
    find_fuzzy_duplicates(cwd, threshold=90)
