#!/data/data/com.termux/files/usr/bin/python
import importlib.metadata
import typing
from pathlib import Path
from typing import Union
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor, as_completed

CHUNK_SIZE = 524288


class QuickXorHash:
    def __init__(self):
        self._hash = [0] * 20
        self._length = 0

    def update(self, data: bytes):
        for b in data:
            shift = self._length % 160
            byte_index = shift // 8
            bit_index = shift % 8

            self._hash[byte_index] ^= (b << bit_index) & 0xFF

            if bit_index > 0 and byte_index < 19:
                self._hash[byte_index + 1] ^= (b >> (8 - bit_index)) & 0xFF

            self._length += 1

    def digest(self):
        length_bytes = self._length.to_bytes(8, "little")
        for i in range(8):
            self._hash[20 - 8 + i] ^= length_bytes[i]
        return bytes(self._hash)

    def hexdigest(self):
        # Using hexdigest() from hashlib is more standard and often faster if allowed.
        # If QuickXorHash's output format is critical, stick to b64encode.
        return b64encode(self.digest()).decode("ascii")


def calculate_xorhash(path: Path) -> tuple[str, Path]:
    """Calculates the XOR hash for a single file."""
    q = QuickXorHash()
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                q.update(chunk)
        return q.hexdigest(), path
    except Exception as e:
        # Handle potential errors during file reading or hashing
        print(f"Error hashing file {path}: {e}")
        return None, path # Return None for hash to indicate failure


def find_dups_optimized(root: Path, max_workers: int = None):
    """
    Finds duplicate files in a directory using parallel processing.

    Args:
        root: The root directory to search.
        max_workers: The maximum number of worker threads to use.
                     Defaults to the number of CPUs.
    """
    file_hashes = {}
    paths_to_process = []


    # Inside find_dups_optimized
    # ... then use ThreadPoolExecutor on paths_to_hash



    # First, collect all relevant files
    for path in root.rglob("*"):
        try:
            if not path.is_symlink() and path.is_file():
                paths_to_process.append(path)
        except OSError as e:
            print(f"Error accessing path {path}: {e}")
            continue # Skip this path if there's an OS error

    if not paths_to_process:
        return {}

    files_by_size = {}
    for path in paths_to_process:
        try:
            size = path.stat().st_size
            files_by_size.setdefault(size, []).append(path)
        except OSError as e:
            print(f"Error getting size for {path}: {e}")
            continue

    # Now, only hash files where len(paths) > 1 in files_by_size
    paths_to_hash = []
    for size, paths in files_by_size.items():
        if len(paths) > 1:
            paths_to_hash.extend(paths)

    # Use ThreadPoolExecutor for I/O-bound operations (reading files)
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all file hashing tasks
        future_to_path = {executor.submit(calculate_xorhash, path): path for path in paths_to_hash}

        for future in as_completed(future_to_path):
            hash_result, path = future.result()
            if hash_result is not None: # Only process if hashing was successful
                file_hashes.setdefault(hash_result, []).append(path)

    # Filter for duplicates
    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


if __name__ == "__main__":
    root_dir = Path.cwd()
    print(f"Scanning directory: {root_dir}")
    # You can adjust max_workers based on your system's cores.
    # None typically defaults to a reasonable number of threads.
    dupes = find_dups_optimized(root_dir)

    if not dupes:
        print("No duplicate files found.")
    else:
        print(f"Found {len(dupes)} group(s) of duplicate files:")
        for h, paths in dupes.items():
            print(f"Duplicate group ({h}):")
            for p in paths:
                print("  ", p)
