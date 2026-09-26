#!/data/data/com.termux/files/usr/bin/python
"""Convert every AVIF image in ``avif_images/`` to JPEG in ``jpg_images/``.

Each ``*.avif`` / ``*.aviff`` file is opened with Pillow, converted to RGB and
saved as a high-quality (95) JPEG in the output directory, which is created if
necessary.
"""

import os
from pathlib import Path

from PIL import Image

input_dir: str = "avif_images"
output_dir: str = "jpg_images"
Path(output_dir).mkdir(exist_ok=True, parents=True)

for filename in os.listdir(input_dir):
    if filename.lower().endswith((".avif", ".aviff")):
        input_path: str = os.path.join(input_dir, filename)
        output_path: str = os.path.join(
            output_dir,
            os.path.splitext(filename)[0] + ".jpg",
        )
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=95)
