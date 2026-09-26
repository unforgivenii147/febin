#!/data/data/com.termux/files/usr/bin/python
"""Archive the current directory to ``<name>.tar.gz`` then delete the originals.

The current directory is compressed into a gzip tarball placed next to it, and
its original contents are removed in parallel (the freshly created archive is
never deleted).
"""

import shutil
import tarfile
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def remove_items_fast(items: Iterable[Path]) -> None:
    """Delete files and directories concurrently.

    Args:
        items: Paths to remove; directories are removed recursively.
    """
    with ThreadPoolExecutor(max_workers=32) as ex:
        ex.map(lambda p: shutil.rmtree(p) if p.is_dir() else p.unlink(), items)


def compress_and_cleanup(root: Path = Path()) -> None:
    """Tar-gzip ``root`` into its parent and delete the original contents.

    Args:
        root: Directory to archive; defaults to the current directory.
    """
    root = root.resolve()
    archive_name: str = f"{root.name}.tar.gz"
    archive_path: Path = root.parent / archive_name
    print(f"Creating archive: {archive_path}")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(root, arcname=root.name)
    print("Archive created. Removing original files...")
    items: list[Path] = []
    for item in root.iterdir():
        if item.resolve() == archive_path:
            continue
        items.append(item)
    remove_items_fast(items)
    print("Cleanup complete.")


if __name__ == "__main__":
    compress_and_cleanup()
