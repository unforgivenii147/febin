import sys
from pathlib import Path

from dh import mpf3, unique_path


def process_file(path):
    new_name = path.name.lower()
    if new_name == path.name:
        return
    new_path = path.with_name(new_name)
    if new_path.exists():
        new_path = unique_path(new_path)
    content = path.read_bytes()
    new_path.write_bytes(content)
    print(f"{path.name} -> {new_path.name}")
    path.unlink()
    print(f"{path.name} removed")


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else list(cwd.rglob("*"))
    mpf3(process_file, files)
