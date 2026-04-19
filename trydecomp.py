#!/data/data/com.termux/files/usr/bin/python

import sys
import zlib
import bz2
import gzip
import zipfile
import tarfile
import pickle
import lzma

# Attempting to import third-party libraries, but will handle ImportError gracefully
try:
    import brotli
except ImportError:
    brotli = None
try:
    import zstandard

    zstd_available = True
except ImportError:
    zstd_available = False
try:
    import py7zr
except ImportError:
    py7zr = None


def try_decompress(filename):
    """
    Tries to decompress a file using various built-in and third-party libraries.
    Reports success or failure for each method.
    """
    print(f"Attempting to decompress: {filename}\n")

    # Built-in libraries
    compression_methods = {
        "zlib": zlib.decompress,
        "bz2": bz2.decompress,
        "gzip": gzip.decompress,
        "lzma": lzma.decompress,
        "pickle": lambda data: pickle.loads(data),  # Pickle is for deserialization, not just decompression
    }

    # Third-party libraries (conditionally available)
    if brotli:
        compression_methods["brotli"] = brotli.decompress
    if zstd_available:
        # zstandard library typically uses a ZstdDecompressor object for streaming
        # For simplicity, we will try to decompress the whole data at once if possible
        # This might not work for very large files or specific zstd stream formats
        def zstd_decompress_all(data):
            try:
                dctx = zstandard.ZstdDecompressor()
                return dctx.decompress(data)
            except zstandard.ZstdError as e:
                raise ValueError(f"Zstandard decompression error: {e}") from e

        compression_methods["zstandard"] = zstd_decompress_all

    if py7zr:
        # py7zr is for archives, not direct data decompression, needs special handling
        pass

    try:
        with open(filename, "rb") as f:
            file_data = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {filename}\n")
        return
    except Exception as e:
        print(f"Error reading file {filename}: {e}\n")
        return

    success = False

    # Test built-in decompression methods
    for name, func in compression_methods.items():
        try:
            print(f"Trying {name}...")
            decompressed_data = func(file_data)
            # Check if decompression resulted in some data and if it seems valid (e.g., not excessively large/small)
            # This is a heuristic, a more robust check might involve trying to parse the decompressed data
            if decompressed_data and len(decompressed_data) < len(file_data) * 10:  # Basic sanity check
                print(f"  SUCCESS: Decompressed using {name}. Size: {len(decompressed_data)} bytes.\n")
                # Optionally save the decompressed data
                # with open(f"{filename}.decompressed_by_{name}.bin", "wb") as outfile:
                #     outfile.write(decompressed_data)
                success = True
                # break # Stop after first success if desired, or continue to test others
            else:
                print(f"  FAILED: {name} did not yield valid decompressed data (size: {len(decompressed_data)}).\n")
        except Exception as e:
            print(f"  FAILED: {name} raised an exception: {type(e).__name__}: {e}\n")

    # Test archive formats (requires special handling)
    # Tarfile
    if tarfile.is_tarfile(filename):
        try:
            print("Trying tarfile...")
            with tarfile.open(filename, "r") as tar:
                members = tar.getmembers()
                if members:
                    print(
                        f"  SUCCESS: Opened as tar archive with {len(members)} members. First member: {members[0].name}\n"
                    )
                    # Optionally extract first file
                    # if members[0].isfile():
                    #     extracted_file = tar.extractfile(members[0])
                    #     if extracted_file:
                    #         decompressed_data = extracted_file.read()
                    #         print(f"  Extracted first member ({members[0].name}) successfully. Size: {len(decompressed_data)} bytes.\n")
                    success = True
                else:
                    print("  FAILED: tarfile is empty.\n")
        except Exception as e:
            print(f"  FAILED: tarfile opened with exception: {type(e).__name__}: {e}\n")

    # Zipfile
    if zipfile.is_zipfile(filename):
        try:
            print("Trying zipfile...")
            with zipfile.ZipFile(filename, "r") as zip_ref:
                file_list = zip_ref.namelist()
                if file_list:
                    print(f"  SUCCESS: Opened as zip archive with {len(file_list)} files. First file: {file_list[0]}\n")
                    # Optionally extract first file
                    # first_file_info = zip_ref.getinfo(file_list[0])
                    # with zip_ref.open(file_list[0]) as extracted_file:
                    #     decompressed_data = extracted_file.read()
                    #     print(f"  Extracted first file ({file_list[0]}) successfully. Size: {len(decompressed_data)} bytes.\n")
                    success = True
                else:
                    print("  FAILED: zipfile is empty.\n")
        except Exception as e:
            print(f"  FAILED: zipfile opened with exception: {type(e).__name__}: {e}\n")

    # py7zr (7z archive)
    if py7zr:
        try:
            print("Trying py7zr (7z archive)...")
            with py7zr.SevenZipFile(filename, mode="r") as z:
                file_list = z.getnames()
                if file_list:
                    print(f"  SUCCESS: Opened as 7z archive with {len(file_list)} files. First file: {file_list[0]}\n")
                    # Optionally extract first file
                    # first_file_info = z.getinfo(file_list[0])
                    # with z.open(file_list[0]) as extracted_file:
                    #     decompressed_data = extracted_file.read()
                    #     print(f"  Extracted first file ({file_list[0]}) successfully. Size: {len(decompressed_data)} bytes.\n")
                    success = True
                else:
                    print("  FAILED: py7zr archive is empty.\n")
        except Exception as e:
            print(f"  FAILED: py7zr opened with exception: {type(e).__name__}: {e}\n")

    if not success:
        print("No compression or archive format was successfully identified and decompressed.\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script_name.py <filename>\n")
        sys.exit(1)

    input_filename = sys.argv[1]
    try_decompress(input_filename)
