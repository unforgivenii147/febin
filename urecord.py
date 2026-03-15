#!/usr/bin/env python3
"""
Script to scan site-packages directories and update RECORD files by removing
references to .pyc files and direct_url.json
"""

import argparse
import csv
import os
import sys


def find_site_packages():
    import site

    site_packages = site.getsitepackages()
    valid_paths = [p for p in site_packages if p is not None]
    if not valid_paths:
        user_site = site.getusersitepackages()
        if user_site and os.path.exists(user_site):
            valid_paths = [user_site]
    return valid_paths


def update_record_file(record_path):
    try:
        with open(record_path, encoding="utf-8") as f:
            lines = list(csv.reader(f))
        original_count = len(lines)
        filtered_lines = []
        for row in lines:
            if not row:
                continue
            file_path = row[0] if row else ""
            if (
                file_path.endswith(".pyc")
                or file_path
                in {
                    "direct_url.json",
                    "INSTALLER",
                }
                or file_path.startswith("LICENSE")
            ):
                continue
            filtered_lines.append(row)
        if len(filtered_lines) == original_count:
            return False
        with open(
            record_path,
            "w",
            encoding="utf-8",
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerows(filtered_lines)
        print(f"  Updated: {record_path} (removed {original_count - len(filtered_lines)} entries)")
        return True
    except Exception as e:
        print(
            f"  Error processing {record_path}: {e}",
            file=sys.stderr,
        )
        return False


def scan_and_update(site_packages_dirs, dry_run=False):
    total_updated = 0
    total_files = 0
    for site_dir in site_packages_dirs:
        if not os.path.exists(site_dir):
            print(f"Directory does not exist: {site_dir}")
            continue
        print(f"\nScanning: {site_dir}")
        for root, _dirs, files in os.walk(site_dir):
            if not root.endswith(".dist-info"):
                continue
            if "RECORD" in files:
                record_path = os.path.join(root, "RECORD")
                total_files += 1
                if dry_run:
                    try:
                        with open(
                            record_path,
                            encoding="utf-8",
                        ) as f:
                            lines = list(csv.reader(f))
                        pyc_count = sum(1 for row in lines if row and row[0].endswith(".pyc"))
                        direct_url_count = sum(1 for row in lines if row and row[0] == "direct_url.json")
                        if pyc_count > 0 or direct_url_count > 0:
                            total_updated += 1
                    except Exception as e:
                        print(
                            f"  Error reading {record_path}: {e}",
                            file=sys.stderr,
                        )
                elif update_record_file(record_path):
                    total_updated += 1
    return total_files, total_updated


def main():
    parser = argparse.ArgumentParser(
        description="Remove .pyc and direct_url.json references from RECORD files in site-packages"
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be changed without actually modifying files",
    )
    parser.add_argument(
        "--site-dir",
        "-s",
        action="append",
        help="Specific site-packages directory to scan (can be used multiple times)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print more detailed information",
    )
    args = parser.parse_args()
    site_dirs = args.site_dir or find_site_packages()
    if not site_dirs:
        print(
            "Error: Could not find site-packages directory",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"Python version: {sys.version}")
    print(f"Site packages directories: {', '.join(site_dirs)}")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'ACTUAL UPDATE'}")
    total_files, total_updated = scan_and_update(site_dirs, args.dry_run)
    print(f"\n{'=' * 50}")
    print("Summary:")
    print(f"  Total RECORD files found: {total_files}")
    print(f"  Files that would be/are updated: {total_updated}")
    if args.dry_run and total_updated > 0:
        print("\nRun without --dry-run to apply these changes")


if __name__ == "__main__":
    main()
