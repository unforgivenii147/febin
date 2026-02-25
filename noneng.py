#!/data/data/com.termux/files/usr/bin/env python3
import os
from pathlib import Path

from dh import BIN_EXT, TXT_EXT, is_binary
from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0

MAX_CHARS = 5000


def is_text_file(pth):
    path = Path(pth)
    if path.suffix.lower() in TXT_EXT:
        return True
    if path.suffix.lower() in BIN_EXT:
        return False
    if not is_binary(path):
        return True
    else:
        return False


def contains_non_english(path):
    try:
        with open(
            path,
            encoding="utf-8",
            errors="ignore",
        ) as f:
            text = f.read(MAX_CHARS).strip()
            if len(text) < 20:
                return False
            return detect(text) != "en"
    except (LangDetectException, OSError):
        return False


def main():
    for root, _, files in os.walk("."):
        for file in files:
            path = os.path.join(root, file)
            if is_text_file(path) and contains_non_english(path):
                print(os.path.relpath(path))


if __name__ == "__main__":
    main()
