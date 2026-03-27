#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import time
import shutil
import typing
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


DEST_DIR = Path("/data/data/com.termux/files/home/tmp/tgz")
if not DEST_DIR.exists():
    DEST_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".tar.gz", ".whl", ".tar.xz", ".zip", ".tar.zst"}


def copy_if_match(src_path) -> None:
    if ".tar" in src_path.suffixes:
        full_suffix = "".join(src_path.suffixes)
    if full_suffix in ALLOWED_EXTENSIONS:
        try:
            dest = DEST_DIR / src_path.name
            shutil.copy2(str(src_path), str(dest))
            print(f"{src_path.name} -> {dest.parent.name / dest.name}")
        except Exception as e:
            print(f"Failed to copy {src_path.name}: {e}")


def startup_scan(path) -> None:

    patterns = ["*.tar.gz", "*.zip", "*.tar.xz", ".tar.zst", ".tar.bz2"]

    matching_files = [f for pattern in patterns for f in path.rglob(pattern)]

    matching_files = list(set(matching_files))
    for file_path in matching_files:
        copy_if_match(file_path)


class CopyEventHandler(FileSystemEventHandler):
    @typing.override
    def on_created(self, event) -> None:
        if not event.is_directory:
            copy_if_match(event.src_path)

    @typing.override
    def on_modified(self, event) -> None:
        if not event.is_directory:
            copy_if_match(event.src_path)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/data/data/com.termux/files/usr/tmp"
    startup_scan(path)
    event_handler = CopyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
