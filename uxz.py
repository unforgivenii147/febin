#!/data/data/com.termux/files/usr/bin/python
import contextlib
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import lzma_mt
from loguru import logger

from dhh import get_files


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


def safe_delete(file_path: Path, max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
        try:
            if file_path.exists():
                time.sleep(0.0005)
                file_path.unlink()
                logger.debug(f"Deleted: {file_path}")
                return True
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(0.0005 * (attempt + 1))
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


def decompress_file(archive_path):
    fname = archive_path.name
    if fname.endswith(".tar.xz"):
        extract_path = archive_path.parent / f"{fname.replace('.tar.xz', '')}"
        with tarfile.open(archive_path, "r:xz") as tar:
            tar.extractall(path=extract_path, filter="data")
        if safe_delete(archive_path):
            return True
    elif fname.endswith(".xz"):
        compressed_data = archive_path.read_bytes()
        out_path = archive_path.parent / f"{fname.replace('.xz', '')}"
        decompressed_data = lzma_mt.decompress(compressed_data, threads=4)
        if atomic_write(decompressed_data, out_path) and safe_delete(archive_path):
            return True
    return False


def main() -> None:
    sys.argv[1:]
    successful = 0
    errors = 0
    start_dir = Path.cwd()
    files_to_decompress = get_files(start_dir, extensions=[".xz", ".tar.xz"])
    if not files_to_decompress:
        logger.info("No files to decompress")
        return
    for i, file_path in enumerate(files_to_decompress, 1):
        logger.info(f"\n[{i}/{len(files_to_decompress)}] Processing...")
        if decompress_file(file_path):
            successful += 1
        else:
            errors += 1
    print(f"successfull: {successful}\nerrors: {errors}")


if __name__ == "__main__":
    main()
