#!/data/data/com.termux/files/usr/bin/python
import os
import json
from pathlib import Path
import argparse
from datetime import UTC, datetime
from collections import defaultdict

import xxhash


BACKUP_FILE = ".symlink_backup.json"
MIN_FILE_SIZE = 8


def calculate_file_hash(filepath, chunk_size=8192):
    hasher = xxhash.xxh64()
    try:
        with Path(filepath).open("rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        print(f"[ERROR] Reading {filepath}: {e}")
        return None


def find_duplicates(directory="."):
    print(f"[INFO] Scanning directory: {Path(directory).resolve()}")
    size_map = defaultdict(list)
    file_count = 0
    skipped_count = 0
    for root, dirs, files in os.walk(directory):
        if ".git" in dirs:
            dirs.remove(".git")
        for filename in files:
            if filename.startswith("."):
                continue
            filepath = os.path.join(root, filename)
            if Path(filepath).is_symlink():
                print(f"[DEBUG] Skipping symlink: {filepath}")
                continue
            try:
                size = Path(filepath).stat().st_size
                if size < MIN_FILE_SIZE:
                    print(f"[DEBUG] Skipping file under {MIN_FILE_SIZE} bytes: {filepath}")
                    skipped_count += 1
                    continue
                size_map[size].append(filepath)
                file_count += 1
            except OSError as e:
                print(f"[ERROR] Accessing {filepath}: {e}")
    print(f"[INFO] Scanned {file_count + skipped_count} files ({skipped_count} skipped due to size)")
    print(f"[INFO] Found {file_count} files that qualify for duplicate analysis")
    hash_map = defaultdict(list)
    potential_duplicates = [files for files in size_map.values() if len(files) > 1]
    print(f"[INFO] Checking {sum(len(files) for files in potential_duplicates)} potential duplicates...")
    for files in potential_duplicates:
        for filepath in files:
            file_hash = calculate_file_hash(filepath)
            if file_hash:
                hash_map[file_hash].append(filepath)
    return {h: files for h, files in hash_map.items() if len(files) > 1}


def choose_keeper(files):
    return min(files, key=lambda f: (len(f), f))


def create_symlinks(duplicates, dry_run=False):
    backup_data = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "operations": [],
    }
    total_saved = 0
    symlink_count = 0
    for file_hash, files in duplicates.items():
        keeper = choose_keeper(files)
        keeper_abs = Path(keeper).resolve()
        print(f"\n[INFO] Duplicate group (hash: {file_hash[:16]}...):")
        print(f"  Keeping: {keeper}")
        for duplicate in files:
            if duplicate == keeper:
                continue
            duplicate_abs = Path(duplicate).resolve()
            get_size = Path(duplicate).stat().st_size
            print(f"  Symlinking: {duplicate} -> {keeper_abs}")
            if not dry_run:
                backup_data["operations"].append({
                    "symlink": duplicate_abs,
                    "target": keeper_abs,
                    "original_existed": True,
                    "size": get_size,
                })
                try:
                    Path(duplicate).unlink()
                    Path(duplicate_abs).symlink_to(keeper_abs)
                    symlink_count += 1
                    total_saved += get_size
                except OSError as e:
                    print(f"  [ERROR] {e}")
            else:
                print(f"  [DRY RUN] Would replace {duplicate} with symlink to {keeper}")
                symlink_count += 1
                total_saved += get_size
    if not dry_run and symlink_count > 0:
        with Path(BACKUP_FILE).open("w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2)
        print(f"\n[INFO] Backup data saved to {BACKUP_FILE}")
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Symlinks created: {symlink_count}")
    print(f"  Space saved: {total_saved / (1024 * 1024):.2f} MB")
    if dry_run:
        print("[DRY RUN] No changes were made")
    return symlink_count


def reverse_symlinks(backup_file=BACKUP_FILE):
    if not Path(backup_file).exists():
        print(f"[ERROR] Backup file {backup_file} not found!")
        return False
    with Path(backup_file).open(encoding="utf-8") as f:
        backup_data = json.load(f)
    print(f"[INFO] Restoring from backup created at: {backup_data['timestamp']}")
    print(f"[INFO] Operations to reverse: {len(backup_data['operations'])}")
    restored_count = 0
    for op in backup_data["operations"]:
        symlink_path = op["symlink"]
        target_path = op["target"]
        if not Path(symlink_path).is_symlink():
            print(f"[WARNING] {symlink_path} is not a symlink, skipping")
            continue
        if not Path(target_path).exists():
            print(f"[ERROR] Target file {target_path} no longer exists!")
            continue
        try:
            Path(symlink_path).unlink()
            import shutil

            shutil.copy2(target_path, symlink_path)
            restored_count += 1
            print(f"[INFO] Restored: {symlink_path}")
        except OSError as e:
            print(f"[ERROR] Restoring {symlink_path}: {e}")
    print(f"\n[INFO] Restored {restored_count} files")
    backup_renamed = f"{backup_file}.restored.{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}"
    Path(backup_file).rename(backup_renamed)
    print(f"[INFO] Backup file renamed to: {backup_renamed}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Find duplicate files and replace with symlinks (reversible)")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse previous symlinking operation",
    )
    parser.add_argument(
        "--backup-file",
        default=BACKUP_FILE,
        help=f"Backup file path (default: {BACKUP_FILE})",
    )
    args = parser.parse_args()
    if args.reverse:
        reverse_symlinks(args.backup_file)
    else:
        duplicates = find_duplicates(args.directory)
        if not duplicates:
            print("\n[INFO] No duplicates found!")
            return
        print(f"\n[INFO] Found {len(duplicates)} groups of duplicates")
        print(f"[INFO] Total duplicate files: {sum(len(files) - 1 for files in duplicates.values())}")
        if args.dry_run:
            print("\n[INFO] [DRY RUN MODE - No changes will be made]")
        create_symlinks(duplicates, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
