import contextlib
import lzma
import tempfile
import time
from pathlib import Path

from loguru import logger


def atomic_write(data: bytes, final_path: Path) -> bool:
    """
    Atomically writes data to a file using a temporary file.
    Ensures that the file is either fully written or not at all.
    """
    temp_dir = final_path.parent
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        # Use delete=False so we can manually move it
        with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=temp_dir,
                prefix=".tmp_",
                suffix=".xz",
                delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(data)
            temp_file.flush()
            # os.fsync is still useful for ensuring data is written to disk
            # but it works on file descriptors. Pathlib doesn't directly expose this easily.
            # On POSIX systems, temp_file.fileno() can be used.
            # For cross-platform compatibility or simpler approach, we can omit fsync or use platform specific calls.
            # Here, we'll rely on Python's file handling and the final move for atomicity.

        # Use Path.rename for atomic move on most systems
        temp_path.rename(final_path)
        logger.debug(f"Atomically written to: {final_path}")
        return True
    except Exception as e:
        logger.error(f"Atomic write failed for {final_path}: {e}")
        if temp_path and temp_path.exists():
            with contextlib.suppress(BaseException):
                temp_path.unlink(
                )  # Use unlink() to remove a file with pathlib
        return False


def safe_delete(file_path: Path,
                max_retries: int = 3,
                delay: float = 0.5) -> bool:
    """
    Safely deletes a file with retries.
    """
    for attempt in range(max_retries):
        try:
            if file_path.exists():
                time.sleep(delay)
                file_path.unlink(
                )  # Use unlink() to remove a file with pathlib
                logger.debug(f"Deleted: {file_path}")
                return True
            return True  # File doesn't exist, so deletion is "successful"
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            logger.error(
                f"Cannot delete {file_path} after {max_retries} attempts due to PermissionError"
            )
            return False
        except FileNotFoundError:
            logger.debug(
                f"File not found during deletion attempt: {file_path}")
            return True  # Already deleted or never existed
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")
            return False
    return False


def compress_file(file_path: Path, delete_delay: float = 0.5) -> bool:
    """
    Compresses a single file using LZMA.
    Deletes the original file upon successful compression.
    """
    compressed_path = file_path.with_suffix(file_path.suffix + ".xz")

    if compressed_path.exists():
        logger.warning(f"Compressed file exists, skipping: {compressed_path}")
        return False

    try:
        original_size = file_path.stat().st_size
        logger.info(f"Compressing: {file_path} ({original_size} bytes)")

        with file_path.open("rb") as f_in:
            data = f_in.read()

        compressed_data: bytes
        try:
            # preset=9 is the highest compression, might consume more memory
            compressed_data = lzma.compress(data, preset=9)
        except MemoryError:
            logger.warning(
                f"Memory error with preset 9, trying preset 6 for {file_path}")
            compressed_data = lzma.compress(data, preset=6)

        if not atomic_write(compressed_data, compressed_path):
            logger.error(f"Failed to write compressed file: {compressed_path}")
            return False

        if not compressed_path.exists():
            logger.error(f"Compressed file not created: {compressed_path}")
            return False

        compressed_size = compressed_path.stat().st_size
        if compressed_size == 0:
            logger.error(f"Compressed file is empty: {compressed_path}")
            compressed_path.unlink()
            return False

        if safe_delete(file_path, delay=delete_delay):
            reduction = (1 - compressed_size / original_size) * 100
            logger.info(f"✓ Compressed: {file_path.name}")
            logger.info(
                f"  {original_size} → {compressed_size} bytes ({reduction:.1f}% reduction)"
            )
            return True
        else:
            logger.warning(
                f"Compressed but couldn't delete original: {file_path}")
            # Return True because compression was successful, even if deletion failed.
            # The user might want to handle the leftover original file.
            return True
    except lzma.LZMAError as e:
        logger.error(f"LZMA error compressing {file_path}: {e}")
        if compressed_path.exists():
            compressed_path.unlink()
        return False
    except PermissionError as e:
        logger.error(f"Permission denied for {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error compressing {file_path}: {e}")
        if compressed_path.exists():
            compressed_path.unlink()
        return False


def calculate_directory_size(path: Path = Path()) -> tuple[int, int]:
    """
    Calculates the total size and file count of a directory, excluding hidden files/dirs.
    """
    total_size = 0
    file_count = 0
    # Use rglob to recursively find all files, then filter
    # Exclude hidden files/directories (those starting with '.')
    for file_path in path.rglob("*"):
        if file_path.is_file() and not file_path.is_symlink():
            # Check if any part of the path is a hidden directory
            if any(part.startswith(".") for part in file_path.parts):
                continue
            try:
                size = file_path.stat().st_size
                total_size += size
                file_count += 1
            except (OSError, PermissionError, FileNotFoundError):
                # Silently skip files that cannot be accessed or don't exist
                continue
    return total_size, file_count


def scan_files(directory: Path) -> list[Path]:
    """
    Scans a directory for files that should be compressed.
    Returns a list of Path objects.
    """
    files_to_compress = []
    logger.info(f"Scanning directory: {directory}")
    # Use rglob to find all files, then filter based on should_compress
    for file_path in directory.rglob("*"):
        if file_path.is_file() and not file_path.is_symlink():
            # Exclude hidden files/directories (those starting with '.')
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if should_compress(
                    file_path
            ):  # Assuming should_compress exists and takes a Path object
                files_to_compress.append(file_path)
    return files_to_compress


def should_compress(file_path):
    try:
        if path.is_symlink():
            return False
        if not path.is_file():
            return False
        compressed_extensions = (
            ".xz",
            ".lzma",
            ".gz",
            ".bz2",
            ".zip",
            ".7z",
            ".rar",
        )
        if file_path.suffix in compressed_extensions:
            return False
        return get_size(file_path) != 0
    except (OSError, PermissionError):
        return False
