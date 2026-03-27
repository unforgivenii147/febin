#!/data/data/com.termux/files/usr/bin/python
import argparse
import logging
import lzma
import os
import shutil
import sys
from datetime import datetime
from multiprocessing import cpu_count
from pathlib import Path


def setup_logging(verbose=True):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


def extract_with_lzma(xz_path, remove_original=True):
    try:
        xz_path = Path(xz_path)
        if not xz_path.exists():
            return (
                False,
                xz_path,
                None,
                "File does not exist",
            )
        if xz_path.suffix != ".xz":
            return (
                False,
                xz_path,
                None,
                "Not an .xz file",
            )
        output_path = xz_path.with_suffix("")
        if output_path.exists():
            return (
                False,
                xz_path,
                output_path,
                "Output file already exists",
            )
        with (
            lzma.open(xz_path, "rb") as compressed_file,
            Path(output_path).open("wb") as output_file,
        ):
            shutil.copyfileobj(compressed_file, output_file)
        if remove_original:
            xz_path.unlink()
            logging.debug("Removed original: %s", xz_path)
        return True, xz_path, output_path, None
    except lzma.LZMAError as e:
        return (
            False,
            xz_path,
            None,
            f"LZMA error: {e}",
        )
    except PermissionError as e:
        return (
            False,
            xz_path,
            None,
            f"Permission denied: {e}",
        )
    except Exception as e:
        return (
            False,
            xz_path,
            None,
            f"Unexpected error: {e}",
        )


def extract_with_system_xz(xz_path, remove_original=False):
    try:
        xz_path = Path(xz_path)
        if not xz_path.exists():
            return (
                False,
                xz_path,
                None,
                "File does not exist",
            )
        output_path = xz_path.with_suffix("")
        if output_path.exists():
            return (
                False,
                xz_path,
                output_path,
                "Output file already exists",
            )
        cmd = f"xz -d {xz_path} {'--keep' if not remove_original else ''}"
        result = os.system(cmd)
        if result == 0:
            return (
                True,
                xz_path,
                output_path,
                None,
            )
        else:
            return (
                False,
                xz_path,
                None,
                f"System xz command failed with code {result}",
            )
    except Exception as e:
        return (
            False,
            xz_path,
            None,
            f"Unexpected error: {e}",
        )


def find_xz_files(directory):
    directory = Path(directory)
    if not directory.exists():
        logging.error("Directory does not exist: %s", directory)
        return []
    return [path for path in directory.rglob("*.xz") if path.is_file()]


def process_file(args):
    file_path, use_system, remove_original = args
    if use_system:
        return extract_with_system_xz(file_path, remove_original)
    else:
        return extract_with_lzma(file_path, remove_original)


def main():
    parser = argparse.ArgumentParser(
        description="Recursively extract all .xz files in a directory tree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Extract all .xz files in current directory
  %(prog)s /path/to/dir         # Extract all .xz files in specific directory
  %(prog)s --remove             # Remove original .xz files after extraction
  %(prog)s --system --workers 4 # Use system xz with 4 worker processes
        """,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to search for .xz files (default: current directory)",
    )
    parser.add_argument(
        "-r",
        "--remove",
        default=True,
        action="store_true",
        help="Remove original .xz files after successful extraction",
    )
    parser.add_argument(
        "-s",
        "--system",
        action="store_true",
        help="Use system xz command instead of Python lzma (faster for large files)",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=8,
        help=f"Number of worker processes (default: {cpu_count()})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list files that would be extracted, without extracting",
    )
    args = parser.parse_args()
    setup_logging(args.verbose)
    logging.info(f"Searching for .xz files in: {args.directory}")
    xz_files = find_xz_files(args.directory)
    if not xz_files:
        logging.warning("No .xz files found")
        return 0
    logging.info(f"Found {len(xz_files)} .xz files")
    if args.dry_run:
        logging.info("Dry run - files that would be extracted:")
        for i, xz_file in enumerate(xz_files, 1):
            output = xz_file.with_suffix("")
            print(f"{i:3d}. {xz_file} -> {output}")
        return 0
    process_args = [(f, args.system, args.remove) for f in xz_files]
    logging.info(f"Starting extraction with {args.workers} workers...")
    start_time = datetime.now()
    success_count = 0
    error_count = 0
    try:
        with Pool(processes=args.workers) as pool:
            for i, result in enumerate(
                pool.imap_unordered(process_file, process_args),
                1,
            ):
                (
                    success,
                    xz_path,
                    output_path,
                    error,
                ) = result
                if success:
                    success_count += 1
                    status = f"[{i}/{len(xz_files)}] ✓ {xz_path.name} -> {output_path.name}"
                    if args.remove:
                        status += " (original removed)"
                    logging.info(status)
                else:
                    error_count += 1
                    logging.error(f"[{i}/{len(xz_files)}] ✗ {xz_path.name}: {error}")
    except KeyboardInterrupt:
        logging.warning("\nExtraction interrupted by user")
        return 1
    elapsed_time = datetime.now() - start_time
    logging.info("=" * 50)
    logging.info(f"Extraction complete in {elapsed_time.total_seconds():.2f} seconds")
    logging.info("Successfully extracted: %s files", success_count)
    if error_count > 0:
        logging.warning("Failed to extract: %s files", error_count)
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
