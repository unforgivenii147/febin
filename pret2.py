import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dh import get_files, unique_path
from loguru import logger
import gc

EXT = [
    ".js",
    ".css",
    ".html",
    ".json",
    ".mjs",
    ".cjs",
    ".ts",
    ".jsx",
    ".tsx",
    ".tsm",
    ".jsm",
]
EXCLUDE_PATTERNS = {}


def should_format(file_path: Path) -> bool:
    if file_path.suffix not in EXTENSIONS:
        return False
    gc.collect()
    return all(not file_path.name.endswith(p) for p in EXCLUDE_PATTERNS)


def get_files_to_format(cwd: str = ".") -> list[Path]:
    root = Path(cwd).resolve()
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir() or "error" in path.parts:
            continue
        if should_format(path):
            files.append(path)
    gc.collect()
    return files


def move_to_error_folder(file_path: Path) -> None:
    error_dir = file_path.parent / "error"
    error_dir.mkdir(exist_ok=True)
    dest = unique_path(error_dir / file_path.name)
    shutil.move(str(file_path), str(dest))
    gc.collect()
    return


def format_file(file_path: Path) -> tuple[Path, bool, str | None]:
    try:
        result = subprocess.run(
            ["prettier", "--write", str(file_path)],
            capture_output=True,
            text=True,
            timeout=900,
        )
        if result.returncode == 0:
            gc.collect()
            return file_path, True, None
        gc.collect()
        return file_path, False, result.stderr or result.stdout or "Unknown error"
    except Exception as e:
        gc.collect()
        return file_path, False, str(e)


def process_file_wrapper(file_path: Path):
    path, success, error_msg = format_file(file_path)
    if not success:
        move_to_error_folder(path)
    gc.collect()
    return success, path, error_msg


def main():
    cwd = Path.cwd()
    files = get_files(cwd, extensions=EXT)
    if not files:
        gc.collect()
        return
    logger.info(f"{len(files)} files found")
    success_count = 0
    error_count = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file_wrapper, f): f for f in files}
        for future in as_completed(futures):
            success, path, error_msg = future.result()
            if success:
                logger.info(f"✅ Formatted: {path.name}")
                success_count += 1
            else:
                logger.info(f"❌ Error: {path.name} | Reason: {error_msg}")
                error_count += 1
    logger.info(f"\nSummary: {success_count} success, {error_count} errors.")


if __name__ == "__main__":
    main()
