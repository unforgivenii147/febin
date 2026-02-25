#!/data/data/com.termux/files/usr/bin/env python3
import os
import shutil
from pathlib import Path


def get_size_str(size_bytes):
    """Convert bytes to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def folderize_by_extension(root_dir):
    root_path = Path(root_dir)
    extension_stats = {}  # Dictionary to store stats for each extension

    # First pass: collect all files and calculate stats
    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            # Get extension
            ext = file_path.suffix.lower()[1:] if file_path.suffix else "no_extension"

            # Get file size
            size = file_path.stat().st_size

            # Update stats
            if ext not in extension_stats:
                extension_stats[ext] = {"count": 0, "total_size": 0, "files": []}

            extension_stats[ext]["count"] += 1
            extension_stats[ext]["total_size"] += size
            extension_stats[ext]["files"].append(file_path)

    # Second pass: move files to their respective folders
    created_dirs = set()

    for ext, stats in extension_stats.items():
        # Create target directory
        target_dir = root_path / ext
        target_dir.mkdir(exist_ok=True)
        created_dirs.add(ext)

        # Move each file
        for file_path in stats["files"]:
            # Skip if file is already in the target directory
            if file_path.parent == target_dir:
                continue

            target_path = target_dir / file_path.name

            # Handle filename conflicts
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1

            # Move the file
            shutil.move(str(file_path), str(target_path))

    # Remove empty directories (bottom-up)
    for dir_path in sorted(root_path.glob("**/*"), key=lambda p: len(p.parts), reverse=True):
        if dir_path.is_dir() and dir_path != root_path:
            try:
                dir_path.rmdir()
                print(f"Removed empty directory: {dir_path.relative_to(root_path)}")
            except OSError:
                pass  # Directory not empty, skip

    # Print summary report
    print("\n" + "=" * 50)
    print("ORGANIZATION SUMMARY")
    print("=" * 50)

    total_files = 0
    total_size = 0

    # Sort extensions alphabetically for nice output
    for ext in sorted(extension_stats.keys()):
        stats = extension_stats[ext]
        total_files += stats["count"]
        total_size += stats["total_size"]

        ext_display = ext if ext else "no_extension"
        size_str = get_size_str(stats["total_size"])
        print(f"{ext_display:<15} : {stats['count']:4} file{'s' if stats['count'] != 1 else ' '}  {size_str:>8}")

    print("-" * 50)
    print(f"{'TOTAL':<15} : {total_files:4} files  {get_size_str(total_size):>8}")
    print("=" * 50)

    return created_dirs, extension_stats


if __name__ == "__main__":
    target_dir = os.getcwd()
    print(f"Organizing files in: {target_dir}")

    created_dirs, stats = folderize_by_extension(target_dir)

    print(f"\nCreated {len(created_dirs)} extension folders.")
    print("Done!")
