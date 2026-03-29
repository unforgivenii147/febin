#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import xxhash

def file_hash(path, block_size=1024 * 1024):
    h = xxhash.xxh64()
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        print(f"Error hashing {path}: {e}")
        return None

def find_duplicates_parallel(files_to_hash, max_workers=None):
    hash_map = defaultdict(list)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit hashing tasks
        future_to_file = {executor.submit(file_hash, f): f for f in files_to_hash}
        
        # Process results as they complete
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                h = future.result()
                if h: # Only process if hashing was successful
                    hash_map[h].append(file)
            except Exception as e:
                print(f"Error processing {file}: {e}")
    return hash_map

def find_and_delete_dups(root=Path("."), max_workers=None):
    # Step 1: group by file size (cheap)
    size_groups = defaultdict(list)
    for f in root.rglob("*"):
        if f.is_file():
            try:
                size = f.stat().st_size
                size_groups[size].append(f)
            except OSError as e:
                print(f"Error accessing {f}: {e}")

    # Step 2: Identify files that *might* be duplicates (same size)
    files_to_hash = []
    for size, files in size_groups.items():
        if len(files) > 1:
            files_to_hash.extend(files)

    # Step 3: Hash potential duplicates in parallel
    print(f"Hashing {len(files_to_hash)} potential duplicate files...")
    hash_map = find_duplicates_parallel(files_to_hash, max_workers=max_workers)

    # Step 4: Identify actual duplicates and decide which to keep (newest)
    duplicates_to_delete = []
    for h, files in hash_map.items():
        if len(files) > 1:
            # Sort files by modification time (newest first)
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            # Keep the first one (newest), mark others for deletion
            duplicates_to_delete.extend(files[1:])
            print(f"Found duplicate set for hash {h[:8]}...: {[str(f) for f in files]}")

    # Step 5: Auto-delete duplicates
    if duplicates_to_delete:
        print(f"\nDeleting {len(duplicates_to_delete)} duplicate files (keeping the newest of each set)...")
        deleted_count = 0
        for dup in duplicates_to_delete:
            try:
                dup.unlink()
                print(f"Deleted: {dup}")
                deleted_count += 1
            except OSError as e:
                print(f"Failed to delete {dup}: {e}")
        print(f"\nFinished. {deleted_count} duplicates removed.")
    else:
        print("\nNo duplicate files found.")

if __name__ == "__main__":
    find_and_delete_dups(max_workers=8)
