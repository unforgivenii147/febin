#!/data/data/com.termux/files/usr/bin/env python
import argparse
import os
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
def main():
    parser = argparse.ArgumentParser(description="Extract text from images.")
    parser.add_argument(
        "file",
        nargs="?",
        help="Image file to process",
    )
    args = parser.parse_args()
    if args.file:
        file_path = Path(args.file)
        if file_path.exists() and file_path.suffix in {".jpg", ".png"}:
            process_file(file_path)
        else:
            print(
                "Error: File does not exist or is not a supported image format."
            )
    else:
        dir = Path().cwd()
        for root, _, files in os.walk(dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in {
                        ".jpg",
                        ".png",
                }:
                    process_file(file_path)
if __name__ == "__main__":
    main()
