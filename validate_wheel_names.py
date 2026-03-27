#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib
import shutil

import regex as re

WHEEL_PATTERN = re.compile(
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])"
    r"-"
    r"([^-]+)"
    r"-"
    r"(\d[^-]*)"
    r"-"
    r"([^-]+)"
    r"-"
    r"([^-]+)"
    r"-"
    r"([^-]+)"
    r"\.whl$",
    re.IGNORECASE,
)


def is_valid_wheel_name(filename):
    return WHEEL_PATTERN.match(filename) is not None


def main():
    invalid_dir = "invalid_wheels"
    pathlib.Path(invalid_dir).mkdir(exist_ok=True, parents=True)
    for filename in os.listdir("."):
        if filename.endswith(".whl"):
            if not is_valid_wheel_name(filename):
                print(f"Invalid wheel name: {filename}")
                shutil.move(
                    filename,
                    os.path.join(invalid_dir, filename),
                )
            else:
                print(f"Valid wheel name: {filename}")


if __name__ == "__main__":
    main()
