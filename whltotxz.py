#!/data/data/com.termux/files/usr/bin/env python3
import io
from pathlib import Path
import tarfile
import zipfile


def whl_to_tarxz(source_dir: str):
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"Directory {source_dir} does not exist.")
        return
    zip_files = list(source_path.glob("*.whl"))
    if not zip_files:
        print("No zip files found.")
        return
    for zip_file in zip_files:
        tar_xz_file = zip_file.with_suffix(".tar.xz")
        print(f"Converting {zip_file} -> {tar_xz_file}")
        with (
            zipfile.ZipFile(zip_file, "r") as zf,
            tarfile.open(tar_xz_file, "w:xz") as tf,
        ):
            for member in zf.infolist():
                if member.is_dir():
                    continue
                file_data = zf.read(member.filename)
                tar_info = tarfile.TarInfo(name=member.filename)
                tar_info.size = len(file_data)
                tf.addfile(tar_info, fileobj=io.BytesIO(file_data))
        print(f"Created {tar_xz_file}")


if __name__ == "__main__":
    whl_to_tarxz(".")
