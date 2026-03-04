#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
def format_size(sb: float) -> str:
    if sb < 1024:
        return f"{sb:.2f} B"
    elif sb < 1024**2:
        return f"{sb / 1024:.2f} KB"
    elif sb < 1024**3:
        return f"{sb / 1024**2:.2f} MB"
    else:
        return f"{sb / 1024**3:.2f} GB"
def remove_pyc_files(directory):
    path = Path(directory)
    pyc_count = 0
    space_freed = 0
    pycache_count = 0
    for pyc_file in path.rglob("*.pyc"):
        get_size = pyc_file.stat().st_size
        pyc_file.unlink()
        pyc_count += 1
        space_freed += get_size
    for pycache_dir in path.rglob("__pycache__"):
        if not list(pycache_dir.iterdir()):
            pycache_dir.rmdir()
            pycache_count += 1
    freed_size_str = format_size(space_freed)
    print("\n--- Report ---")
    print(f".pyc removed: {pyc_count}")
    print(f"Space freed: {freed_size_str}")
    print(f"dir removed: {pycache_count}")
if __name__ == "__main__":
    current_dir = Path.cwd()
    remove_pyc_files(current_dir)
    print("Finished.")
