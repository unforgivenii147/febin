#!/data/data/com.termux/files/usr/bin/python
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CHUNK_SIZE = 524288
MAX_BYTE_INDEX = 19


class QuickXorHash:
    def __init__(self) -> None:
        self._hash = [0] * 20
        self._length = 0

    def update(self, data: bytes):
        for b in data:
            shift = self._length % 160
            byte_index = shift // 8
            bit_index = shift % 8
            self._hash[byte_index] ^= (b << bit_index) & 0xFF
            if bit_index > 0 and byte_index < MAX_BYTE_INDEX:
                self._hash[byte_index + 1] ^= (b >> (8 - bit_index)) & 0xFF
            self._length += 1

    def digest(self):
        length_bytes = self._length.to_bytes(8, "little")
        for i in range(8):
            self._hash[20 - 8 + i] ^= length_bytes[i]
        return bytes(self._hash)

    def hexdigest(self):
        return b64encode(self.digest()).decode("ascii")


def calculate_xorhash(path: Path) -> tuple[str, Path]:
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
        print(f"Error hashing file {path}: {e}")
        return None, path


def find_dups_optimized(root: Path):
    file_hashes = {}
    paths_to_process = []
    for path in root.rglob("*"):
        try:
            if not path.is_symlink() and path.is_file():
                paths_to_process.append(path)
        except OSError as e:
            print(f"Error accessing path {path}: {e}")
            continue
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
    paths_to_hash = []
    for paths in files_by_size.values():
        if len(paths) > 1:
            paths_to_hash.extend(paths)
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_path = {executor.submit(calculate_xorhash, path): path for path in paths_to_hash}
        for future in as_completed(future_to_path):
            hash_result, path = future.result()
            if hash_result is not None:
                file_hashes.setdefault(hash_result, []).append(path)
    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


if __name__ == "__main__":
    cwd = Path.cwd()
    print(f"Scanning directory: {cwd}")
    dupes = find_dups_optimized(cwd)
    if not dupes:
        print("No duplicate files found.")
    else:
        print(f"Found {len(dupes)} group(s) of duplicate files:")
        for h, paths in dupes.items():
            print(f"Duplicate group ({h}):")
            for p in paths:
                print("  ", p)
