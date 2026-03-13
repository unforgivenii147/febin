#!/usr/bin/env python3
"""
Script to scan site-packages directories and update RECORD files with new hashes.
Removes references to .pyc files and direct_url.json, and logs missing files.
"""

import base64
import hashlib
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("record_updater.log"),
        logging.StreamHandler(sys.stdout)
    ],
)
logger = logging.getLogger(__name__)


def find_site_packages() -> Path | None:
    """Find the system site-packages directory."""
    import site

    # Get all site-packages directories
    site_packages_dirs = site.getsitepackages()
    if not site_packages_dirs:
        logger.error("No site-packages directories found")
        return None
    # Use the first one (usually the main site-packages)
    site_packages = Path(site_packages_dirs[0])
    logger.info(f"Found site-packages directory: {site_packages}")
    return site_packages


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of a file and return it in the format used in RECORD files."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read the file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        # Get the hash and encode in base64 (without padding)
        hash_bytes = sha256_hash.digest()
        hash_b64 = base64.urlsafe_b64encode(hash_bytes).decode("ascii").rstrip(
            "=")
        return f"sha256={hash_b64}"
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return ""


def get_size(filepath: Path) -> int:
    """Get the size of a file."""
    try:
        return filepath.stat().st_size
    except Exception as e:
        logger.error(f"Error getting size for {filepath}: {e}")
        return 0


def parse_record_line(line: str) -> tuple[str, str, str]:
    """Parse a line from a RECORD file into path, hash, and size."""
    parts = line.strip().split(",")
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        return parts[0], parts[1], ""
    else:
        return parts[0], "", ""


def should_include_file(filepath: Path, relative_path: str) -> bool:
    """Determine if a file should be included in the RECORD file."""
    # Exclude .pyc files
    if filepath.suffix == ".pyc" or filepath.name.endswith(".pyc"):
        return False
    # Exclude direct_url.json
    if filepath.name == "direct_url.json":
        return False
    if filepath.name == "INSTALLER":
        return False
    # Exclude the RECORD file itself
    if filepath.name == "RECORD":
        return False
    # Include all other files
    return True


def update_record_file(record_path: Path, dist_info_dir: Path) -> bool:
    """Update a single RECORD file with new hashes."""
    logger.info(f"Processing {record_path}")
    if not record_path.exists():
        logger.error(f"RECORD file not found: {record_path}")
        return False
    # Read the current RECORD file
    try:
        with open(record_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Error reading {record_path}: {e}")
        return False
    # Process each line and generate new entries
    new_lines = []
    missing_files = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        relative_path, _old_hash, _old_size = parse_record_line(line)
        # Skip the RECORD file itself
        if relative_path == "RECORD":
            continue
        # Construct the full path
        full_path = dist_info_dir.parent / relative_path
        # Check if the file should be included
        if not should_include_file(full_path, relative_path):
            logger.debug(f"Skipping {relative_path} (excluded file type)")
            continue
        # Check if the file exists
        if not full_path.exists():
            missing_files.append(relative_path)
            logger.warning(f"Missing file: {relative_path}")
            continue
        # Calculate new hash and size
        new_hash = calculate_file_hash(full_path)
        new_size = get_size(full_path)
        if new_hash:
            new_lines.append(f"{relative_path},{new_hash},{new_size}")
        else:
            # If hash calculation failed, keep the original line
            logger.warning(
                f"Failed to calculate hash for {relative_path}, keeping original"
            )
            new_lines.append(line)
    # Add the RECORD file entry (will be updated with its own hash after writing)
    record_relative = str(record_path.relative_to(dist_info_dir.parent))
    new_lines.append(f"{record_relative},,")
    # Log missing files summary
    if missing_files:
        logger.info(
            f"Found {len(missing_files)} missing files in {dist_info_dir.name}:"
        )
        for missing in missing_files:
            logger.info(f"  - {missing}")
    # Write the updated RECORD file
    try:
        with open(record_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        logger.info(f"Successfully updated {record_path}")
        # Now update the RECORD file's own entry with its new hash
        update_record_self_hash(record_path, dist_info_dir)
        return True
    except Exception as e:
        logger.error(f"Error writing {record_path}: {e}")
        return False


def update_record_self_hash(record_path: Path, dist_info_dir: Path):
    """Update the RECORD file's own hash entry."""
    try:
        # Read the current RECORD file
        with open(record_path, encoding="utf-8") as f:
            lines = f.readlines()
        # Calculate the new hash for the RECORD file itself
        record_hash = calculate_file_hash(record_path)
        record_size = get_size(record_path)
        # Update the last line (which should be the RECORD entry)
        if lines:
            last_line = lines[-1].strip()
            parts = last_line.split(",")
            if len(parts) >= 1:
                record_relative = parts[0]
                lines[-1] = f"{record_relative},{record_hash},{record_size}\n"
        # Write back the updated RECORD file
        with open(record_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        logger.debug(f"Updated self-hash for {record_path}")
    except Exception as e:
        logger.error(f"Error updating self-hash for {record_path}: {e}")


def scan_and_update():
    """Main function to scan site-packages and update all RECORD files."""
    site_packages = find_site_packages()
    if not site_packages:
        return
    # Find all .dist-info directories
    dist_info_dirs = list(site_packages.glob("*.dist-info"))
    if not dist_info_dirs:
        logger.warning(f"No .dist-info directories found in {site_packages}")
        return
    logger.info(f"Found {len(dist_info_dirs)} distribution info directories")
    updated_count = 0
    failed_count = 0
    for dist_info_dir in dist_info_dirs:
        record_path = dist_info_dir / "RECORD"
        if update_record_file(record_path, dist_info_dir):
            updated_count += 1
        else:
            failed_count += 1
    logger.info(
        f"Summary: {updated_count} RECORD files updated, {failed_count} failed"
    )


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Starting site-packages RECORD file updater")
    logger.info("=" * 60)
    try:
        scan_and_update()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    logger.info("Script completed successfully")


if __name__ == "__main__":
    main()
