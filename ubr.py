#!/data/data/com.termux/files/usr/bin/python
import sys
import mmap
from pathlib import Path

from dh import get_size, get_files, format_size
from termcolor import cprint
import brotlicffi


CHUNK_SIZE = 32768
N_JOBS = -1


def decompress_chunk(data):
    return brotlicffi.decompress(data)


def parallel_decompress(in_path, out_path):
    try:
        file_size = in_path.stat().st_size
        if not file_size:
            return False
        with out_path.open("wb") as fout, in_path.open("rb") as fin:
            mm = mmap.mmap(fin.fileno(), length=0, access=mmap.ACCESS_READ)
            offset = 0
            while offset < file_size:
                block_size_bytes = mm[offset : offset + 4]
                if len(block_size_bytes) != 4:
                    break  # Handle potential EOF
                block_size = int.from_bytes(block_size_bytes, "big")
                offset += 4

                block_data_start = offset
                block_data_end = offset + block_size
                block_data = mm[block_data_start:block_data_end]

                decompressed_data = decompress_chunk(block_data)
                fout.write(decompressed_data)

                offset += block_size
            mm.close()
            return True
    except OSError:
        return False


def process_file(fp):
    fp = Path(fp)
    if not fp.exists() or fp.suffix != ".br":
        return
    before = get_size(fp)
    outfile = Path(str(fp).replace(".br", ""))
    if parallel_decompress(fp, outfile):
        fp.unlink()
    elif outfile.exists():
        outfile.unlink()
        return
    after = get_size(outfile)
    ratio = round(((after - before) / after) * 100, 3)
    cprint(f"{outfile.name}", "green", end=" | ")
    cprint(f"{ratio}", "cyan")
    del before, after, ratio
    return


def main():
    root_dir = Path.cwd()
    before = get_size(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, recursive=True)
    for f in files:
        process_file(f)
    diff_size = before - get_size(root_dir)
    print(f"{format_size(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
