import sys
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

from termcolor import cprint

CHUNK_SIZE = 32768
MAX_WORKERS: int = 8
MAX_IN_FLIGHT = 8
SKIP_DIRS = {".git"}


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


def safe_delete(fp: Path, max_retries: int = 3, delay: float = 0.5) -> bool:
    for attempt in range(max_retries):
        try:
            fp.unlink()
            return True
        except FileNotFoundError:
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                _sleep(delay * (attempt + 1))
                continue
            print(f"PermissionError: Could not delete {fp} after {max_retries} retries.")
            return False
        except OSError as e:
            print(f"OSError deleting {fp}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error deleting {fp}: {e}")
            return False
    return False


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


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


def mpf3(
    func: Callable[[Any], Any],
    items: Iterable[Any],
    max_in_flight: int = 8,
    num_processes: int = 8,
    context_method: str = "spawn",
) -> None:
    with get_context(context_method).Pool(num_processes) as p:
        pending = deque()
        for item in items:
            pending.append(p.apply_async(func, (item,)))
            if len(pending) >= max_in_flight:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


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


def process_file(fp):
    before = gsz(fp)
    cmd = f"prettier -w {fp!s}"
    code, _out, _err = run_command(cmd)
    if code == 0:
        diffsize = before - gsz(fp)
        if not diffsize:
            cprint("[NO CHANGE] ", "green", end="")
            cprint(f"{fp.name}", "white")
        elif diffsize < 0:
            cprint(
                f"[OK] {fp.name} ",
                "white",
                end="",
            )
            cprint(
                f" + {fsz(diffsize)}",
                "green",
            )
        elif diffsize > 0:
            cprint(
                f"[OK] {fp.name} ",
                "white",
                end="",
            )
            cprint(
                f" - {fsz(diffsize)}",
                "cyan",
            )
        return True
    cprint(f"[ERROR] {fp.name}", "red")
    return False


def main() -> None:
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(arg) for arg in args]
        if args
        else get_files(
            cwd,
            extensions=[
                ".md",
                ".js",
                ".css",
                ".ts",
                ".tsx",
                ".jsx",
                ".json",
                ".html",
                ".cjs",
                ".cts",
                ".mts",
                ".mjs",
                ".coffee",
                ".yaml",
                ".yml",
            ],
        )
    )
    before = gsz(cwd)
    if not files:
        print("no file found.")
        sys.exit(0)
    mpf3(process_file, files)
    diffsize = before - gsz(cwd)
    cprint(f"space change:{fsz(diffsize)}", "cyan")


if __name__ == "__main__":
    main()
