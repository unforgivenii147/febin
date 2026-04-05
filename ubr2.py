#!/data/data/com.termux/files/usr/bin/python
import os
import time
from joblib import Parallel, delayed
import brotlicffi
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
CHUNK_SIZE = 1 * 1024 * 1024


def compress_chunk(chunk_data, quality=11):
    try:
        return brotlicffi.compress(chunk_data, quality=quality)
    except Exception as e:
        logger.error(f"Error compressing chunk: {e}")
        return None


def process_single_file(filepath, current_dir, output_base_dir, quality=11):
    try:
        relative_path = os.path.relpath(filepath, current_dir)
        output_sub_dir = os.path.join(output_base_dir, os.path.dirname(relative_path))
        os.makedirs(output_sub_dir, exist_ok=True)
        compressed_filepath = os.path.join(output_sub_dir, os.path.basename(filepath) + ".br")
        original_size = os.path.getsize(filepath)
        logger.info(f"Processing file: {filepath} (Size: {original_size / (1024 * 1024):.2f} MB)")
        chunks = []
        with open(filepath, "rb") as f_in:
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk:
                    break
                chunks.append(chunk)
        if not chunks:
            logger.warning(f"File {filepath} is empty. Skipping compression.")
            return {
                "success": False,
                "filepath": filepath,
                "original_size": original_size,
                "compressed_size": 0,
                "reason": "empty_file",
            }
        logger.info(f"Compressing {len(chunks)} chunks for {filepath}...")
        compressed_chunks = Parallel(n_jobs=-1, verbose=0)(delayed(compress_chunk)(chunk, quality) for chunk in chunks)
        compressed_chunks = [c for c in compressed_chunks if c is not None]
        if not compressed_chunks:
            logger.error(f"All chunks failed to compress for {filepath}. Original not deleted.")
            return {
                "success": False,
                "filepath": filepath,
                "original_size": original_size,
                "compressed_size": 0,
                "reason": "chunk_compression_failed",
            }
        with open(compressed_filepath, "wb") as f_out:
            f_out.writelines(compressed_chunks)
            compressed_size = os.path.getsize(compressed_filepath)
        if os.path.exists(compressed_filepath) and compressed_size > 0:
            os.remove(filepath)
            logger.info(f"Successfully compressed and deleted original: {filepath} -> {compressed_filepath}")
            return {
                "success": True,
                "filepath": filepath,
                "original_size": original_size,
                "compressed_size": compressed_size,
            }
        if os.path.exists(compressed_filepath):
            os.remove(compressed_filepath)
        logger.error(f"Failed to compress {filepath} (empty or invalid output). Original not deleted.")
        return {
            "success": False,
            "filepath": filepath,
            "original_size": original_size,
            "compressed_size": 0,
            "reason": "invalid_compressed_output",
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing {filepath}: {e}")
        return {
            "success": False,
            "filepath": filepath,
            "original_size": 0,
            "compressed_size": 0,
            "reason": "unexpected_error",
        }


def get_all_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        file_list.extend(os.path.join(root, filename) for filename in files)
    return file_list


def main():
    current_dir = os.getcwd()
    output_base_dir = os.path.join(current_dir, "compressed_files")
    all_files = get_all_files(current_dir)
    files_to_compress = [f for f in all_files if not f.endswith(".br") and not f.startswith(output_base_dir)]
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
    start_time = time.time()
    for file_idx, filepath in enumerate(files_to_compress):
        logger.info(f"--- Processing file {file_idx + 1}/{len(files_to_compress)}: {filepath} ---")
        result = process_single_file(filepath, current_dir, output_base_dir)
        total_files_processed += 1
        if result["success"]:
            successful_compressions += 1
            total_original_size += result["original_size"]
            total_compressed_size += result["compressed_size"]
    logger.info(f"--- Finished file {file_idx + 1}/{len(files_to_compress)} ---")
    end_time = time.time()
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
