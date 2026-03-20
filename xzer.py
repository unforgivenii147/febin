#!/data/data/com.termux/files/usr/bin/python
import contextlib
import lzma
from pathlib import Path
import sys
import tempfile
import time

from dh import format_size
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
        return False
    try:
        original_size = file_path.stat().st_size
        with file_path.open("rb") as f_in:
            data = f_in.read()
        compressed_data: bytes
        compressed_data = lzma.compress(data, preset=9)
        if not atomic_write(compressed_data, compressed_path):
            return False
        if not compressed_path.exists() or compressed_path.stat().st_size==0:
            return False
        if safe_delete(file_path, delay=delete_delay):
            compressed_size = compressed_path.stat().st_size
            reduction = (1 - compressed_size / original_size) * 100
            logger.info(f"{file_path.name}|{original_size} → {compressed_size} bytes ({reduction:.1f}% reduction)")
            return True
    except Exception:
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
        if file_path.is_file() and not file_path.is_symlink() and should_compress(file_path):
            files_to_compress.append(file_path)
    return files_to_compress


def should_compress(file_path):
    path = Path(file_path)
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
            ".br",
        )
        if path.suffix in compressed_extensions:
            return False
        return path.stat().st_size != 0
    except (OSError, PermissionError):
        return False


def main() -> None:
    args = sys.argv[1:]
    start_dir = Path.cwd()
    files_to_compress = scan_files(start_dir)
    if not files_to_compress:
        logger.info("No files to compress")
        return
    total_original = 0
    total_compressed = 0
    successful = 0
    for i, file_path in enumerate(files_to_compress, 1):
        logger.info(f"\n[{i}/{len(files_to_compress)}] Processing...")
        orig_size = file_path.stat().st_size
        total_original += orig_size
        if compress_file(file_path, args.delay):
            successful += 1
            compressed_path = file_path.with_suffix(file_path.suffix + ".xz")
            if compressed_path.exists():
                total_compressed += compressed_path.stat().st_size
    if successful > 0:
        savings = total_original - total_compressed
        savings_percent = (savings / total_original) * 100
        logger.info(f"Space saved: {format_size(savings)} ({savings_percent:.1f}%)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nCompression interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
