#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import time
from pathlib import Path
import brotlicffi
from dh import fsz, get_files, gsz
from joblib import Parallel, delayed
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
CHUNK_SIZE = 32768


def compress_chunk(chunk_data, quality=11):
    try:
        return brotlicffi.compress(chunk_data, quality=quality)
    except Exception as e:
        logger.error(f"Error compressing chunk: {e}")
        return None


def process_single_file(path, cwd):
    try:
        relative_path = path.relative_to(cwd)
        compressed_filepath = path.with_suffix(path.suffix + ".br")
        original_size = path.stat().st_size
        chunks = []
        with path.open("rb") as f_in:
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk:
                    break
                chunks.append(chunk)
        if not chunks:
            logger.warning(f"File {path.name} is empty. Skipping compression.")
            return {
                "success": False,
                "filepath": path,
                "original_size": original_size,
                "compressed_size": 0,
                "reason": "empty_file",
            }
        logger.info(f"Compressing {len(chunks)} chunks for {path.name}...")
        compressed_chunks = Parallel(n_jobs=-1, verbose=0)(delayed(compress_chunk)(chunk, quality) for chunk in chunks)
        compressed_chunks = [c for c in compressed_chunks if c is not None]
        if not compressed_chunks:
            logger.error(f"All chunks failed to compress for {path.name}. Original not deleted.")
            return {
                "success": False,
                "filepath": path,
                "original_size": original_size,
                "compressed_size": 0,
                "reason": "chunk_compression_failed",
            }
        with compressed_filepath.open("wb") as f_out:
            f_out.writelines(compressed_chunks)
        compressed_size = gsz(compressed_filepath)
        if compressed_filepath.exists() and compressed_size > 0:
            path.unlink()
            logger.info(f"Successfully compressed and deleted original: {path.name} -> {compressed_filepath.name}")
            return {
                "success": True,
                "filepath": path,
                "original_size": original_size,
                "compressed_size": compressed_size,
            }
        if compressed_filepath.exists():
            compressed_filepath.unlink()
        logger.error(f"Failed to compress {path.name} (empty or invalid output). Original not deleted.")
        return {
            "success": False,
            "filepath": path,
            "original_size": original_size,
            "compressed_size": 0,
            "reason": "invalid_compressed_output",
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing {path.name}: {e}")
        return {
            "success": False,
            "filepath": path,
            "original_size": 0,
            "compressed_size": 0,
            "reason": "unexpected_error",
        }


def main():
    cwd = Path.cwd()
    all_files = get_files(cwd)
    files_to_compress = [f for f in all_files if not f.suffix == ".br"]
    if not files_to_compress:
        logger.info("No files found to compress in the current directory.")
        return
    logger.info(
        f"Found {len(files_to_compress)} files to compress. Starting sequential file processing with parallel chunk compression..."
    )
    total_files_processed = 0
    successful_compressions = 0
    total_original_size = 0
    total_compressed_size = 0
    start_time = time.perf_counter()
    for file_idx, filepath in enumerate(files_to_compress):
        logger.info(f"--- Processing file {file_idx + 1}/{len(files_to_compress)}: {filepath} ---")
        result = process_single_file(filepath, cwd)
        total_files_processed += 1
    if result["success"]:
        successful_compressions += 1
        total_original_size += result["original_size"]
        total_compressed_size += result["compressed_size"]
    logger.info(f"--- Finished file {file_idx + 1}/{len(files_to_compress)} ---")
    end_time = time.perf_counter()
    logger.info("\n" + "=" * 50)
    logger.info("Compression Summary:")
    logger.info(f"Total files scanned: {len(files_to_compress)}")
    logger.info(f"Files successfully compressed and originals deleted: {successful_compressions}")
    logger.info(f"Files with failed compression: {total_files_processed - successful_compressions}")
    if total_original_size > 0:
        reduction_percent = ((total_original_size - total_compressed_size) / total_original_size) * 100
        logger.info(f"Total original size: {total_original_size / (1024 * 1024):.2f} MB")
        logger.info(f"Total compressed size: {total_compressed_size / (1024 * 1024):.2f} MB")
        logger.info(f"Total size reduction: {reduction_percent:.2f}%")
    else:
        logger.info("No data was successfully compressed to calculate reduction.")
    logger.info(f"Compressed files are saved in the '{output_base_dir}' directory.")
    logger.info(f"Total time taken: {end_time - start_time:.2f} seconds")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
