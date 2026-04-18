#!/data/data/com.termux/files/usr/bin/python
import mmap
import sys
from pathlib import Path

import brotlicffi
from joblib import Parallel, delayed
from termcolor import cprint

from dhh import fsz, get_files, gsz

CHUNK_SIZE = 32768
QUALITY = 11
N_JOBS = -1


def compress_chunk(data, quality=QUALITY):
    return brotlicffi.compress(data, quality=quality)


def parallel_compress(in_path, out_path):
    try:
        file_size = in_path.stat().st_size
        if not file_size:
            return False
        chunk_count = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        with out_path.open("wb", buffering=1024 * 1024) as fout, in_path.open("rb") as fin:
            mm = mmap.mmap(fin.fileno(), length=0, access=mmap.ACCESS_READ)
            chunks = [mm[i * CHUNK_SIZE : min((i + 1) * CHUNK_SIZE, file_size)] for i in range(chunk_count)]
            compressed_chunks = Parallel(n_jobs=N_JOBS, backend="loky")(
                delayed(compress_chunk)(chunk) for chunk in chunks
            )
            for block in compressed_chunks:
                fout.write(len(block).to_bytes(4, "big"))
                fout.write(block)
            mm.close()
            return True
    except OSError:
        return False


def process_file(fp):
    fp = Path(fp)
    if not fp.exists() or fp.suffix == ".br":
        return
    before = gsz(fp)
    outfile = Path(str(fp) + ".br")
    if parallel_compress(fp, outfile):
        fp.unlink()
    elif outfile.exists():
        outfile.unlink()
    after = gsz(outfile)
    ratio = (after / before) * 100
    cprint(f"{outfile.name}", "green", end=" | ")
    cprint(f"{ratio:.3f}", "cyan")
    del before, after, ratio
    return


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd, recursive=True)
    for f in files:
        process_file(f)
    diff_size = before - gsz(cwd)
    print(f"{fsz(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
