#!/data/data/com.termux/files/usr/bin/env python
"""
Script to extract tar.zst, tar.xz, and standalone .zst archives.
If a filename is provided, process only that file.
If no argument, recursively search current directory.
Deletes original archives after successful extraction and reports size change.
"""

import argparse
from pathlib import Path
import sys
import tarfile
import tempfile
import time

import zstandard as zstd


def get_dir_size(path):
    """Calculate total size of directory in bytes."""
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def get_size(path):
    """Get size of a single file."""
    return path.stat().st_size if path.exists() else 0


def extract_zst_file(archive_path, extract_path):
    """Extract a standalone .zst file."""
    output_path = extract_path / archive_path.stem  # Remove .zst extension
    with open(archive_path, "rb") as compressed_file:
        dctx = zstd.ZstdDecompressor()
        with open(output_path, "wb") as output_file:
            dctx.copy_stream(compressed_file, output_file)
    return output_path


def extract_tar_zst(archive_path, extract_path):
    """Extract tar.zst archive using zstandard library."""
    # Decompress zst to temporary tar file
    with open(archive_path, "rb") as compressed_file:
        dctx = zstd.ZstdDecompressor()
        with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as temp_tar:
            dctx.copy_stream(compressed_file, temp_tar)
            temp_tar_path = temp_tar.name
    # Extract the tar file
    try:
        with tarfile.open(temp_tar_path, "r") as tar:
            tar.extractall(path=extract_path)
    finally:
        # Clean up temporary tar file
        Path(temp_tar_path).unlink()


def extract_tar_xz(archive_path, extract_path):
    """Extract tar.xz archive."""
    with tarfile.open(archive_path, "r:xz") as tar:
        tar.extractall(path=extract_path)


def process_archive(
    archive_path,
    dry_run=False,
    keep_original=False,
    quiet=False,
):
    """
    Process a single archive: extract it and delete original if successful.
    Returns tuple (success, archive_size, extracted_size)
    """
    if not archive_path.exists():
        if not quiet:
            print(f"Error: File {archive_path} does not exist")
        return False, 0, 0
    archive_size = archive_path.stat().st_size
    extract_path = archive_path.parent
    archive_name = archive_path.name
    extracted_files = []
    # Determine archive type
    is_tar_zst = archive_name.endswith(".tar.zst")
    is_tar_xz = archive_name.endswith(".tar.xz")
    is_standalone_zst = archive_name.endswith(".zst") and not is_tar_zst
    if not (is_tar_zst or is_tar_xz or is_standalone_zst):
        if not quiet:
            print(f"Skipping unsupported file: {archive_path} (not .zst, .tar.zst, or .tar.xz)")
        return False, 0, 0
    try:
        if dry_run:
            if not quiet:
                print(f"[DRY RUN] Would extract: {archive_path}")
            return True, archive_size, 0
        if not quiet:
            print(f"Extracting: {archive_path}")
        # Extract based on file type
        if is_standalone_zst:
            output_file = extract_zst_file(archive_path, extract_path)
            extracted_files = [output_file]
        elif is_tar_zst:
            extract_tar_zst(archive_path, extract_path)
            extracted_files = ["multiple files (tar contents)"]
        elif is_tar_xz:
            extract_tar_xz(archive_path, extract_path)
            extracted_files = ["multiple files (tar contents)"]
        # Calculate size of extracted files
        extracted_size = 0
        if extracted_files and extracted_files[0] != "multiple files (tar contents)":
            # For single file extraction
            for file_path in extracted_files:
                if file_path.exists():
                    extracted_size += file_path.stat().st_size
        else:
            # For tar archives, approximate by finding files created in the last minute
            current_time = time.time()
            for item in extract_path.rglob("*"):
                if item.is_file() and item != archive_path:
                    # Check if file was created within the last minute
                    if current_time - item.stat().st_ctime < 60:
                        extracted_size += item.stat().st_size
        # Delete original archive if extraction was successful and not in dry-run mode
        if not keep_original:
            archive_path.unlink()
            if not quiet:
                print(f"  ✓ Extracted and removed original: {archive_name}")
        elif not quiet:
            print(f"  ✓ Extracted (kept original): {archive_name}")
        return True, archive_size, extracted_size
    except Exception as e:
        if not quiet:
            print(f"  ✗ Error processing {archive_path}: {e}")
        return False, 0, 0


def find_archives(directory):
    """Find all supported archives in directory recursively."""
    directory = Path(directory).resolve()
    archives = []
    # Find standalone .zst files (not ending with .tar.zst)
    for zst_file in directory.rglob("*.zst"):
        if not zst_file.name.endswith(".tar.zst"):
            archives.append(zst_file)
    # Find tar.zst files
    archives.extend(directory.rglob("*.tar.zst"))
    # Find tar.xz files
    archives.extend(directory.rglob("*.tar.xz"))
    # Remove duplicates and sort
    return sorted(set(archives))


def main():
    parser = argparse.ArgumentParser(
        description="Extract .zst, .tar.zst, and .tar.xz archives.\n"
        "If a filename is provided, process only that file.\n"
        "If no argument, recursively search current directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="File to extract or directory to search (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without actually extracting",
    )
    parser.add_argument(
        "--keep-original",
        "-k",
        action="store_true",
        help="Keep original archive files after extraction",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output",
    )
    args = parser.parse_args()
    # Determine if target is a file or directory
    if args.target:
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"Error: {target_path} does not exist")
            return 1
        is_single_file = target_path.is_file()
    else:
        # No argument provided - use current directory
        target_path = Path.cwd().resolve()
        is_single_file = False
    # Process single file mode
    if is_single_file:
        if not args.quiet:
            print(f"Processing single file: {target_path}")
        # Calculate initial directory size (for the parent directory)
        parent_dir = target_path.parent
        before = get_dir_size(parent_dir)
        # Process the file
        success, arch_size, ext_size = process_archive(
            target_path,
            args.dry_run,
            args.keep_original,
            args.quiet,
        )
        if not args.dry_run and success:
            after = get_dir_size(parent_dir)
            size_change = after - before
            size_change_mb = size_change / (1024 * 1024)
            print(f"\n{'=' * 50}")
            print(f"Summary for {target_path.name}:")
            print(f"  Archive size: {arch_size / (1024 * 1024):.2f} MB")
            print(f"  Extracted size: {ext_size / (1024 * 1024):.2f} MB")
            if arch_size > 0:
                print(f"  Compression ratio: {ext_size / arch_size:.2f}:1")
            print(f"  Directory size change: {size_change_mb:+.2f} MB")
        elif args.dry_run:
            print(f"\n{'=' * 50}")
            print(f"DRY RUN: Would extract {target_path.name}")
        return 0 if success else 1
    # Directory mode (recursive search)
    else:
        if not args.quiet:
            print(f"Recursively scanning {target_path} for archives...")
        archives = find_archives(target_path)
        if not archives:
            print("No supported archives found.")
            return 0
        if not args.quiet:
            print(f"Found {len(archives)} archives to process")
            # Show breakdown by type
            zst_count = sum(1 for a in archives if a.suffix == ".zst" and not a.name.endswith(".tar.zst"))
            tar_zst_count = sum(1 for a in archives if a.name.endswith(".tar.zst"))
            tar_xz_count = sum(1 for a in archives if a.name.endswith(".tar.xz"))
            if zst_count:
                print(f"  - Standalone .zst: {zst_count}")
            if tar_zst_count:
                print(f"  - .tar.zst: {tar_zst_count}")
            if tar_xz_count:
                print(f"  - .tar.xz: {tar_xz_count}")
        # Calculate initial size
        before = get_dir_size(target_path)
        processed_count = 0
        failed_count = 0
        total_archive_size = 0
        total_extracted_size = 0
        # Process each archive
        for archive in archives:
            success, arch_size, ext_size = process_archive(
                archive,
                args.dry_run,
                args.keep_original,
                args.quiet,
            )
            if success:
                processed_count += 1
                total_archive_size += arch_size
                total_extracted_size += ext_size
            else:
                failed_count += 1
        # Calculate final size and show summary
        if not args.dry_run:
            after = get_dir_size(target_path)
            size_change = after - before
            size_change_mb = size_change / (1024 * 1024)
            print(f"\n{'=' * 50}")
            print("Summary:")
            print(f"  Processed: {processed_count} archives")
            if failed_count > 0:
                print(f"  Failed: {failed_count} archives")
            print(f"  Initial directory size: {before / (1024 * 1024):.2f} MB")
            print(f"  Final directory size:   {after / (1024 * 1024):.2f} MB")
            print(f"  Size change:            {size_change_mb:+.2f} MB")
            if total_archive_size > 0:
                compression_ratio = total_extracted_size / total_archive_size
                print(f"  Average compression ratio: {compression_ratio:.2f}:1")
                print(f"  Space saved by compression: {total_archive_size / (1024 * 1024):.2f} MB")
        else:
            print(f"\n{'=' * 50}")
            print("DRY RUN SUMMARY:")
            print(f"  Would process: {len(archives)} archives")
        return 0


if __name__ == "__main__":
    sys.exit(main())
