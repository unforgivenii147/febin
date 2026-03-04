#!/usr/bin/env python3
"""
Compress files in current directory recursively using xz (lzma) compression.
Single-threaded version for maximum reliability.
"""

import argparse
import contextlib
import logging
import lzma
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.FileHandler("compression_errors.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def atomic_write(data, final_path):
    """
    Write data atomically using a temporary file.
    """
    # Create temporary file in same directory
    temp_dir = os.path.dirname(final_path)
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=temp_dir, prefix=".tmp_", suffix=".xz", delete=False
        ) as temp_file:
            temp_path = temp_file.name
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        # Rename temporary file to final destination
        shutil.move(temp_path, final_path)
        return True
    except Exception as e:
        logger.error(f"Atomic write failed: {e}")
        if temp_path and os.path.exists(temp_path):
            with contextlib.suppress(BaseException):
                os.remove(temp_path)
        return False


def safe_delete(file_path, max_retries=3, delay=0.5):
    """
    Safely delete a file with retries.
    """
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                time.sleep(delay)  # Delay before deletion
                os.remove(file_path)
                logger.debug(f"Deleted: {file_path}")
                return True
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # Increasing delay
                continue
            logger.error(f"Cannot delete {file_path} after {max_retries} attempts")
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")
            return False
    return False


def should_compress(file_path):
    """
    Determine if a file should be compressed.
    """
    try:
        # Skip if it's a symlink
        if os.path.islink(file_path):
            return False
        # Skip if it's not a regular file
        if not os.path.isfile(file_path):
            return False
        # Skip already compressed files
        compressed_extensions = (".xz", ".lzma", ".gz", ".bz2", ".zip", ".7z", ".rar")
        if str(file_path).lower().endswith(compressed_extensions):
            return False
        # Skip empty files
        return os.path.getsize(file_path) != 0
    except (OSError, PermissionError):
        return False


def compress_file(file_path, delete_delay=0.5):
    """
    Compress a single file using lzma compression.
    """
    original_path = str(file_path)
    compressed_path = original_path + ".xz"
    # Skip if compressed file already exists
    if os.path.exists(compressed_path):
        logger.warning(f"Compressed file exists, skipping: {compressed_path}")
        return False
    try:
        original_size = os.path.getsize(original_path)
        logger.info(f"Compressing: {original_path} ({original_size} bytes)")
        # Read original file
        with open(original_path, "rb") as f_in:
            data = f_in.read()
        # Compress using lzma (preset 6 for balance, 9 for max compression)
        try:
            compressed_data = lzma.compress(data, preset=9)  # Max compression
        except MemoryError:
            # Fall back to lower compression if memory error
            logger.warning(f"Memory error with preset 9, trying preset 6 for {original_path}")
            compressed_data = lzma.compress(data, preset=6)
        # Write compressed data atomically
        if not atomic_write(compressed_data, compressed_path):
            logger.error(f"Failed to write compressed file: {compressed_path}")
            return False
        # Verify compressed file
        if not os.path.exists(compressed_path):
            logger.error(f"Compressed file not created: {compressed_path}")
            return False
        compressed_size = os.path.getsize(compressed_path)
        if compressed_size == 0:
            logger.error(f"Compressed file is empty: {compressed_path}")
            os.remove(compressed_path)
            return False
        # Delete original file with delay
        if safe_delete(original_path, delay=delete_delay):
            reduction = (1 - compressed_size / original_size) * 100
            logger.info(f"✓ Compressed: {os.path.basename(original_path)}")
            logger.info(f"  {original_size} → {compressed_size} bytes ({reduction:.1f}% reduction)")
            return True
        else:
            logger.warning(f"Compressed but couldn't delete original: {original_path}")
            return True  # Compression succeeded even if deletion failed
    except lzma.LZMAError as e:
        logger.error(f"LZMA error compressing {original_path}: {e}")
        # Clean up partial compressed file
        if os.path.exists(compressed_path):
            os.remove(compressed_path)
        return False
    except PermissionError as e:
        logger.error(f"Permission denied for {original_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error compressing {original_path}: {e}")
        # Clean up partial compressed file
        if os.path.exists(compressed_path):
            os.remove(compressed_path)
        return False


def calculate_directory_size(path="."):
    """Calculate total size of all files in directory recursively."""
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.isfile(file_path) and not os.path.islink(file_path):
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
            except (OSError, PermissionError):
                continue
    return total_size, file_count


def format_size(size_bytes):
    """Format bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def scan_files(directory):
    """Scan directory for files to compress."""
    files_to_compress = []
    logger.info(f"Scanning directory: {directory}")
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            file_path = Path(root) / file
            if should_compress(file_path):
                files_to_compress.append(file_path)
    return files_to_compress


def main():
    parser = argparse.ArgumentParser(description="Compress files using xz compression")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to process (default: current directory)")
    parser.add_argument(
        "--delay", "-d", type=float, default=0.5, help="Delay in seconds before deleting original files (default: 0.5)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--preset",
        "-p",
        type=int,
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        default=9,
        help="Compression preset (0-9, default: 9 for max)",
    )
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    start_dir = os.path.abspath(args.directory)
    if not os.path.isdir(start_dir):
        logger.error(f"Directory does not exist: {start_dir}")
        sys.exit(1)
    logger.infgger.info(f"Compression preset: {args.preset}")
    logger.info(f"Delete delay: {args.delay} seconds")
    # Calculate initial directory size
    initial_size, initial_files = calculate_directory_size(start_dir)
    logger.info(f"Initial directory: {format_size(initial_size)} across {initial_files} files")
    # Find files to compress
    files_to_compress = scan_files(start_dir)
    if not files_to_compress:
        logger.info("No files to compress")
        return
    logger.info(f"Found {len(files_to_compress)} files to compress")
    # Show sample of files
    if len(files_to_compress) > 0:
        logger.info("First few files:")
        for f in files_to_compress[:5]:
            logger.info(f"  - {f}")
        if len(files_to_compress) > 5:
            logger.info(f"  ... and {len(files_to_compress) - 5} more")
    # Compress files one by one
    total_original = 0
    total_compressed = 0
    successful = 0
    failed = 0
    start_time = time.time()
    for i, file_path in enumerate(files_to_compress, 1):
        logger.info(f"\n[{i}/{len(files_to_compress)}] Processing...")
        # Get original size before compression
        try:
            orig_size = os.path.getsize(file_path)
            total_original += orig_size
        except:
            pass
        if compress_file(file_path, args.delay):
            successful += 1
            # Get compressed size after successful compression
            compressed_path = str(file_path) + ".xz"
            if os.path.exists(compressed_path):
                total_compressed += os.path.getsize(compressed_path)
        else:
            failed += 1
    elapsed_time = time.time() - start_time
    # Calculate final directory size
    final_size, final_files = calculate_directory_size(start_dir)
    # Report results
    logger.info("\n" + "=" * 60)
    logger.info("COMPRESSION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Successfully compressed: {successful} files")
    logger.info(f"Failed: {failed} files")
    logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")
    if successful > 0:
        logger.info("-" * 40)
        logger.info(f"Total original size: {format_size(total_original)}")
        logger.info(f"Total compressed size: {format_size(total_compressed)}")
        savings = total_original - total_compressed
        if total_original > 0:
            savings_percent = (savings / total_original) * 100
            logger.info(f"Space saved: {format_size(savings)} ({savings_percent:.1f}%)")
    logger.info("-" * 40)
    logger.info(f"Initial: {format_size(initial_size)} across {initial_files} files")
    logger.info(f"Final:   {format_size(final_size)} across {final_files} files")
    logger.info(
        f"Overall reduction: {format_size(initial_size - final_size)} ({(1 - final_size / initial_size) * 100:.1f}%)"
    )
    logger.info("=" * 60)
    logger.info("Check compression_errors.log for any errors")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nCompression interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
