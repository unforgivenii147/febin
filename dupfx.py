#!/data/data/com.termux/files/usr/bin/env python

import concurrent.futures as cf
import os
from collections import defaultdict
from pathlib import Path

import xxhash
from dh import format_size, get_size

SKIPPED_PATHS = []
EXCLUDED_DIRS = {".git", ".venv", "venv"}
EXCLUDED_FILENAMES = {"__init__.py"}


def hash_file(path: str, chunk_size: int = 8192 * 10):
    path = Path(path)
    hasher = xxhash.xxh64()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
    except (PermissionError, OSError):
        return path, None
    return path, hasher.hexdigest()


def collect_all_files(directory: Path):
    files = []
    for root, dirs, fs in os.walk(directory, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in fs:
            if f in EXCLUDED_FILENAMES:
                continue
            file_path = Path(root) / f
            if not file_path.is_symlink():
                files.append(file_path)
    return files


def group_by_size(files):
    groups = defaultdict(list)
    for f in files:
        try:
            size = f.stat().st_size
            #            if size > 0: # exclude zero size files
            groups[size].append(f)
        except (PermissionError, OSError):
            SKIPPED_PATHS.append(str(f))
    return groups


def hash_groups_in_parallel(groups):
    candidates = []
    for _size, paths in groups.items():
        if len(paths) > 1:
            candidates.extend(paths)
    if not candidates:
        return {}
    hash_groups = defaultdict(list)
    with cf.ProcessPoolExecutor() as executor:
        futures = {executor.submit(hash_file, str(p)): p for p in candidates}
        for future in cf.as_completed(futures):
            path, h = future.result()
            if h is None:
                SKIPPED_PATHS.append(str(path))
                continue
            hash_groups[h].append(str(path))
    return {h: ps for h, ps in hash_groups.items() if len(ps) > 1}


def display_duplicate_groups(dups) -> None:
    print("\n📋 Duplicate Groups Found:")
    print("=" * 60)

    for i, (h, files) in enumerate(dups.items(), 1):
        rel_files = [os.path.relpath(f, start=os.getcwd()) for f in files]
        size = Path(files[0]).stat().st_size

        print(f"\nGroup {i} (Hash: {h[:8]}..., Size: {size:,} bytes):")
        for j, rel_path in enumerate(rel_files, 1):
            marker = "📄" if j == 1 else "🗑️"
            print(f"  {marker} {rel_path}")

        if len(files) > 1:
            print(f"  → Would keep: {rel_files[0]}")
            print(f"  → Would delete: {', '.join(rel_files[1:])}")

    print("\n" + "=" * 60)


def auto_delete_duplicates(dups) -> None:
    print("\n🔥 AUTO-DELETE MODE: Removing duplicates...\n")
    deleted_count = 0
    deleted_size = 0
    for _h, files in dups.items():
        duplicates = files[1:]
        for f in duplicates:
            try:
                size = Path(f).stat().st_size
                os.remove(f)
                rel_path = os.path.relpath(f, start=os.getcwd())
                print(f"🗑️ {rel_path} removed ({size:,} bytes)")
                deleted_count += 1
                deleted_size += size
            except Exception as e:
                print(f"⚠️ Could not delete {f}: {e}")
    print(
        f"\n✅ Deleted {deleted_count} duplicate files (total: {deleted_size:,} bytes)."
    )


def report_duplicates(dups):
    dup_count = sum(len(files) - 1 for files in dups.values())
    dup_size = sum(
        Path(f).stat().st_size for files in dups.values() for f in files[1:])
    print("\n📊 Summary Report:")
    print(f"   • Duplicate groups: {len(dups)}")
    print(f"   • Total duplicate files: {dup_count}")
    print(f"   • Total duplicate size: {dup_size / 1024 / 1024:.2f} MB")

    if SKIPPED_PATHS:
        print(
            f"\n⚠️ Skipped {len(SKIPPED_PATHS)} files due to permissions/errors"
        )


def main() -> None:
    global SKIPPED_PATHS
    SKIPPED_PATHS = []

    target = Path.cwd()

    before = get_size(target)
    all_files = collect_all_files(target)

    size_groups = group_by_size(all_files)
    duplicates = hash_groups_in_parallel(size_groups)

    if duplicates:
        display_duplicate_groups(duplicates)
        report_duplicates(duplicates)
        auto_delete_duplicates(duplicates)
    else:
        print("\n✅ No duplicates found.")

    after = get_size(target)
    if before - after != 0:
        saved = abs(before - after)
        print(f"\n💾 Space saved: {format_size(saved)}")

    if SKIPPED_PATHS:
        print(
            f"\n⚠️ Skipped {len(SKIPPED_PATHS)} files (see SKIPPED_PATHS list for details)"
        )


if __name__ == "__main__":
    main()
