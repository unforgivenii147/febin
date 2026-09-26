#!/data/data/com.termux/files/usr/bin/python
"""Pack the current directory into a wheel and drop it in ``/sdcard/whl``.

The current working directory is assumed to be an unpacked wheel tree.  The
script changes into its parent, then invokes ``wheel pack`` on it, writing the
resulting ``.whl`` to ``/sdcard/whl``.
"""

import os
import subprocess
from pathlib import Path

if __name__ == "__main__":
    target_dir: Path = Path(Path.cwd())
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
