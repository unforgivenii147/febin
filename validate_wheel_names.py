#!/data/data/com.termux/files/usr/bin/env python
import os
import regex as re
import shutil

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
    os.makedirs(invalid_dir, exist_ok=True)
    for filename in os.listdir("."):
        if filename.endswith(".whl"):
            if not is_valid_wheel_name(filename):
                print(f"Invalid wheel name: {filename}")
                shutil.move(filename, os.path.join(invalid_dir, filename))
            else:
                print(f"Valid wheel name: {filename}")


if __name__ == "__main__":
    main()
