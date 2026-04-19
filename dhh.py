from collections import deque
from collections.abc import Callable, Iterable
from contextlib import suppress as _suppress
from multiprocessing import get_context
from os import scandir as _scandir
from pathlib import Path
from subprocess import run as _run
from tempfile import NamedTemporaryFile as _tmpfile
from time import sleep as _sleep
from typing import Any

from joblib import Parallel, delayed

SKIP_DIRS = {"__pycache__", ".git"}
CHUNK_SIZE = 32768
MAX_WORKERS: int = 8


def run_command(cmd, shell: bool = True) -> tuple[(int, str, str)]:
    try:
        result = _run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
        )
        return (
            result.returncode,
            result.stdout,
            result.stderr,
        )
    except Exception as e:
        return (-1, "", str(e))


def atomic_write(data: bytes, final_path: Path) -> bool:
    temp_dir = final_path.parent
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with _tmpfile(
            mode="wb",
            dir=temp_dir,
            prefix=".tmp_",
            suffix=final_path.suffix,
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(data)
        temp_path.rename(final_path)
        return True
    except OSError as e:
        print(f"Error during atomic write: {e}")  # Log or handle appropriately
        if temp_path and temp_path.exists():
            with _suppress(OSError):  # Suppress errors during cleanup
                temp_path.unlink()
        return False
    except Exception as e:
        print(f"Unexpected error during atomic write: {e}")
        if temp_path and temp_path.exists():
            with _suppress(OSError):
                temp_path.unlink()
        return False


def safe_delete(file_path: Path, max_retries: int = 3, delay: float = 0.5) -> bool:
    for attempt in range(max_retries):
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                _sleep(delay * (attempt + 1))  # Exponential backoff can be better, but linear is fine
                continue
            print(f"PermissionError: Could not delete {file_path} after {max_retries} retries.")
            return False
        except OSError as e:
            print(f"OSError deleting {file_path}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error deleting {file_path}: {e}")
            return False
    return False


def mpf3(
    func: Callable[[Any], Any],
    items: Iterable[Any],
    max_in_flight: int = 8,
    num_processes: int = 8,
    context_method: str = "spawn",
) -> None:
    results = []
    with get_context(context_method).Pool(num_processes) as p:
        pending = deque()
        for item in items:
            pending.append(p.apply_async(func, (item,)))
            if len(pending) >= 8:
                results.append(pending.popleft().get())
        while pending:
            results.append(pending.popleft().get())
    return results


def mpf(process_function: Callable, files: list[Path], **kwargs):
    return Parallel(n_jobs=-1)(delayed(process_function)(file, **kwargs) for file in files)


def get_filez(root: str | Path, exts=None) -> Iterable[Path]:
    root = Path(root)
    if exts is not None:
        exts = set(exts)
        for path in root.rglob("*"):
            if path.is_file() and not path.is_symlink() and path.suffix.lower() in exts:
                yield path
    else:
        for path in root.rglob("*"):
            if path.is_file() and not path.is_symlink():
                yield path


def unique_path(path: Path | str) -> Path:
    path = Path(path)
    if not path.exists():
        return path
    parent = path.parent
    suffixes = path.suffixes
    if suffixes:
        first_suffix_index = path.name.find(suffixes[0])
        stem = path.name[:first_suffix_index]
        full_suffix = "".join(suffixes)  # Reconstruct .tar.gz or .min.js
    else:
        stem = path.name
        full_suffix = ""
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{full_suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def get_files(
    path: str | Path,
    include_hidden: bool = True,
    recursive: bool = True,
    extensions: list[str] | None = None,
) -> list[Path]:
    path = Path(path)
    out = []
    if recursive:
        stack = [path]
        while stack:
            current = stack.pop()
            try:
                with _scandir(current) as it:
                    for entry in it:
                        name = entry.name
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            if name not in SKIP_DIRS:
                                stack.append(Path(entry.path))
                            continue
                        if extensions is not None and not any(entry.name.endswith(ext) for ext in extensions):
                            continue
                        out.append(Path(entry.path))
            except (PermissionError, FileNotFoundError):
                continue
    return out


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{sz:.2f} {units[i]}B"


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def get_pyfiles(path: str | Path) -> list[Path]:
    path = Path(path)
    pyfiles: list[Path] = []
    if path.is_file() and (path.suffix == ".py"):
        return [path]
    if path.is_dir():
        pyfiles = get_files(path, extensions=[".py"])
        no_ext = [p for p in path.rglob("*") if (not p.suffix)]
        if no_ext:
            for f in no_ext:
                if is_python_file(f):
                    pyfiles.append(f)
    return pyfiles
