#!/data/data/com.termux/files/usr/bin/python

import csv
import os
import zipfile
from pathlib import Path


def is_empty_wheel(wheel_path: str | Path) -> bool:
    """Return True when the wheel only contains ``.dist-info`` entries."""
    with zipfile.ZipFile(wheel_path, "r") as z:
        dist_info_dirs = [name for name in z.namelist() if name.endswith((".dist-info/", ".dist-info"))]
        if not dist_info_dirs:
            return False
        dist_info = dist_info_dirs[0].rstrip("/")
        record_path = dist_info + "/RECORD"
        if record_path not in z.namelist():
            return False
        with z.open(record_path) as f:
            reader = csv.reader(line.decode("utf-8") for line in f)
            for row in reader:
                if not row:
                    continue
                file_path = row[0]
                if not file_path.startswith(dist_info + "/"):
                    return False
    return True


def main() -> None:
    wheels = [f for f in os.listdir(".") if f.endswith(".whl")]
    if not wheels:
        return
    empty = [wheel for wheel in wheels if is_empty_wheel(wheel)]
    if not empty:
        return
    for _w in empty:
        pass


if __name__ == "__main__":
    main()
