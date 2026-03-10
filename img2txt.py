#!/data/data/com.termux/files/usr/bin/env python
from multiprocessing import Pool
from pathlib import Path
import sys

from dh import format_size, get_nobinary, get_size
from termcolor import cprint
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
from pytesseract import image_to_string


def preprocess_image(img):
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    threshold = 150
    return img.point(lambda x: 255 if x > threshold else 0)


def extract_text(image_path):
    img = Image.open(image_path)
    processed_img = preprocess_image(img)
    return image_to_string(
        processed_img,
        lang="eng",
        config="--oem 1 --psm 6",
    )


def process_file(file_path):
    print(f"Processing {file_path.name}")
    text = extract_text(file_path)
    if text:
        txtfile = file_path.with_suffix(".txt")
        with open(txtfile, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{txtfile} created.")
    else:
        print("No text found.")


def main() -> None:
    dir = Path.cwd()
    before = get_size(dir)
    args = sys.argv[1:]
    if args:
        files = [Path(arg) for arg in args]
    else:
        files = [Path(f) for f in dir.rglob("*") if f.suffix in {".jpg", ".png"}]

    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    else:
        p = Pool(8)
        for _ in p.imap_unordered(process_file, files):
            pass
        p.close()
        p.join()
        after = get_size(dir)
        cprint(
            f"{format_size(before - after)}",
            "cyan",
        )


if __name__ == "__main__":
    main()
