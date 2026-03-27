#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import subprocess


if __name__ == "__main__":
    target_dir = Path(Path.cwd())
    os.chdir(target_dir.parent)
    subprocess.run(
        [
            "wheel",
            "pack",
            str(target_dir),
            "-d",
            "/sdcard/whl",
        ],
        check=False,
    )
