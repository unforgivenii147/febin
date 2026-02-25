#!/usr/bin/env python3
"""
Script to extract .zst, .tar.zst, and .tar.xz archives.
If a filename is provided, process only that file.
If no argument, recursively search current directory.
Deletes original archives after successful extraction and reports size change.
"""

import argparse
import tarfile
import tempfile
from pathlib import Path
import zstandard as zstd
import time


def get_dir_size(path):
    """Calculate total size of directory in bytes."""
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


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
            tar.extractall(path=extract_path, filter="fully_trusted")

    #            tar.extractall(path=extract_path)
    finally:
        # Clean up temporary tar file
        Path(temp_tar_path).unlink()


def extract_tar_xz(archive_path, extract_path):
    """Extract tar.xz archive."""
    with tarfile.open(archive_path, "r:xz") as tar:
        tar.extractall(path=extract_path, filter="data")


def process_archive(archive_path, dry_run=False, quiet=False):
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

    # Determine archive type
    is_tar_zst = archive_name.endswith(".tar.zst")
    is_tar_xz = archive_name.endswith(".tar.xz")
    is_standalone_zst = archive_name.endswith(".zst") and not is_tar_zst

    if not (is_tar_zst or is_tar_xz or is_standalone_zst):
        if not quiet:
            print(f"Skipping unsupported file: {archive_path}")
        return False, 0, 0

    try:
        if dry_run:
            if not quiet:
                print(f"[DRY RUN] Would extract: {archive_name}")
            return True, archive_size, 0

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

        # Delete original archive after successful extraction
        archive_path.unlink()

        if not quiet:
            print(f"Extracted: {archive_name} -> original removed")

        return True, archive_size, extracted_size

    except Exception as e:
        if not quiet:
            print(f"Error processing {archive_name}: {e}")
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
        "If no argument, recursively search current directory.\n"
        "Original archives are automatically removed after successful extraction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target", nargs="?", default=None, help="File to extract or directory to search (default: current directory)"
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Show what would be done without actually extracting"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress all output except errors and final summary"
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
            print(f"Processing: {target_path.name}")

        # Calculate initial directory size (for the parent directory)
        parent_dir = target_path.parent
        initial_size = get_dir_size(parent_dir)

        # Process the file
        success, arch_size, ext_size = process_archive(target_path, args.dry_run, args.quiet)

        if success and not args.dry_run:
            final_size = get_dir_size(parent_dir)
            size_change = final_size - initial_size
            size_change_mb = size_change / (1024 * 1024)

            print(f"\nSummary:")
            print(f"  Archive size: {arch_size / (1024 * 1024):.2f} MB")
            print(f"  Extracted size: {ext_size / (1024 * 1024):.2f} MB")
            if arch_size > 0:
                print(f"  Compression ratio: {ext_size / arch_size:.2f}:1")
            print(f"  Directory size change: {size_change_mb:+.2f} MB")

        return 0 if success else 1

    # Directory mode (recursive search)
    else:
        if not args.quiet:
            print(f"Scanning {target_path} for archives...")

        archives = find_archives(target_path)

        if not archives:
            print("No supported archives found.")
            return 0

        if not args.quiet:
            print(f"Found {len(archives)} archives")

        # Calculate initial size
        initial_size = get_dir_size(target_path)
        processed_count = 0
        failed_count = 0
        total_archive_size = 0
        total_extracted_size = 0

        # Process each archive
        for archive in archives:
            success, arch_size, ext_size = process_archive(archive, args.dry_run, args.quiet)
            if success:
                processed_count += 1
                total_archive_size += arch_size
                total_extracted_size += ext_size
            else:
                failed_count += 1

        # Calculate final size and show summary
        if not args.dry_run:
            final_size = get_dir_size(target_path)
            size_change = final_size - initial_size
            size_change_mb = size_change / (1024 * 1024)

            print(f"\n{'=' * 50}")
            print(f"Summary:")
            print(f"  Processed: {processed_count} archives")
            if failed_count > 0:
                print(f"  Failed: {failed_count} archives")
            print(f"  Initial size: {initial_size / (1024 * 1024):.2f} MB")
            print(f"  Final size:   {final_size / (1024 * 1024):.2f} MB")
            print(f"  Size change:  {size_change_mb:+.2f} MB")
            if total_archive_size > 0:
                compression_ratio = total_extracted_size / total_archive_size
                print(f"  Compression ratio: {compression_ratio:.2f}:1")
        else:
            print(f"\n{'=' * 50}")
            print(f"DRY RUN: Would process {len(archives)} archives")

        return 0


if __name__ == "__main__":
    exit(main())
