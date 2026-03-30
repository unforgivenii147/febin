#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from collections import deque
from multiprocessing import get_context

from dh import get_files, run_command
from termcolor import cprint


c_files = {".c", ".h", ".inc"}
cpp_files = {".cpp", ".cc", ".cxx", ".hpp", ".hpp11", ".hh", ".hxx"}


def validate_cpp(path: Path) -> tuple[bool, str]:
    cmd = ""
    if path.suffix in c_files:
        cmd = "clang -fsyntax-only str(path)"
    if path.suffix in cpp_files:
        cmd = "clang++ -fsyntax-only str(path)"
    ret, txt, err = run_command(cmd)
    del cmd
    return path, ret, txt, err


if __name__ == "__main__":
    cwd = Path.cwd()
    files = [
        path
        for path in get_files(
            cwd, extensions=[".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inc", "hpp11"]
        )
        if path.is_file() and not path.is_symlink()
    ]
    results = []
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(validate_cpp, (f,)))
            if len(pending) > 16:
                results.append(pending.popleft().get())
        while pending:
            results.append(pending.popleft().get())
    for result in results:
        if int(result[1]) == 2:
            cprint(f"[\u2716] : {result[0].name} has error", "white")
        else:
            cprint(f"[\u2705] : {result[0].name} is ok", "cyan")
