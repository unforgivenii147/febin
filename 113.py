import contextlib
import lzma
import tempfile
import time
from pathlib import Path

from loguru import logger


def atomic_write(data: bytes, final_path: Path) -> bool:
    temp_dir = final_path.parent
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
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

        temp_path.rename(final_path)
        logger.debug(f"Atomically written to: {final_path}")
        return True
    except Exception as e:
        logger.error(f"Atomic write failed for {final_path}: {e}")
        if temp_path and temp_path.exists():
            with contextlib.suppress(BaseException):
                temp_path.unlink()
        return False


def safe_delete(file_path: Path, max_retries: int = 3, delay: float = 0.5) -> bool:
    for attempt in range(max_retries):
        try:
            if file_path.exists():
                time.sleep(delay)
                file_path.unlink()
                logger.debug(f"Deleted: {file_path}")
                return True
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            logger.error(f"Cannot delete {file_path} after {max_retries} attempts due to PermissionError")
            return False
        except FileNotFoundError:
            logger.debug(f"File not found during deletion attempt: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")
            return False
    return False


def compress_file(file_path: Path, delete_delay: float = 0.5) -> bool:
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
            compressed_data = lzma.compress(data, preset=9)
        except MemoryError:
            logger.warning(f"Memory error with preset 9, trying preset 6 for {file_path}")
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
            logger.info(f"  {original_size} → {compressed_size} bytes ({reduction:.1f}% reduction)")
            return True
        logger.warning(f"Compressed but couldn't delete original: {file_path}")

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
    total_size = 0
    file_count = 0

    for file_path in path.rglob("*"):
        if file_path.is_file() and not file_path.is_symlink():
            if any(part.startswith(".") for part in file_path.parts):
                continue
            try:
                size = file_path.stat().st_size
                total_size += size
                file_count += 1
            except (OSError, PermissionError, FileNotFoundError):
                continue
    return total_size, file_count


def scan_files(directory: Path) -> list[Path]:
    files_to_compress = []
    logger.info(f"Scanning directory: {directory}")

    for file_path in directory.rglob("*"):
        if file_path.is_file() and not file_path.is_symlink():
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if should_compress(file_path):
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
