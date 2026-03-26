#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

from fastwalk import walk_files
import regex as re


def extract_requirements(metadata_path):
    with open(metadata_path, encoding="utf-8") as f:
        lines = f.readlines()
    requirements = []
    for line in lines:
        if line.startswith("Requires-Dist:"):
            match = re.match(
                r"Requires-Dist:\s*([^\s;]+)",
                line,
            )
            if match:
                requirements.append(match.group(1))
    if not requirements:
        print("No dependencies found in METADATA.")
        return
    print(f"{len(requirements)} reqs found")
    with open("/sdcard/requirements.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(requirements))


if __name__ == "__main__":
    root_dir = Path.cwd()
    for pth in walk_files(root_dir):
        path = Path(pth)
        if path.is_file() and path.name == "METADATA":
            extract_requirements(path)
