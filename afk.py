#!/data/data/com.termux/files/usr/bin/python
"""Auto-fix every Python file in the current directory.

Each ``*.py`` file found by :func:`dh.get_pyfiles` is passed through
:func:`dh.fix_code`.  When the fix shrinks the file the reduction (in
characters) is printed in cyan and the file is rewritten in place; otherwise a
``no change`` note is emitted.
"""

from pathlib import Path

from dh import fix_code, get_pyfiles
from termcolor import cprint


def process_file(fp: Path) -> None:
    """Run :func:`dh.fix_code` on ``fp`` and rewrite it if anything changed.

    Args:
        fp: Path to the Python source file to fix.
    """
    code: str = fp.read_text(encoding="utf-8")
    result: str = fix_code(code)
    diff_size: int = len(code) - len(result)
    if diff_size:
        print(f"{fp.name} ", end="")
        cprint(f"{diff_size}", "cyan")
        fp.write_text(result, encoding="utf-8")
    else:
        print(f"{fp.name} no change")


if __name__ == "__main__":
    cwd: Path = Path.cwd()
    files: list[Path] = get_pyfiles(cwd)
    for f in files:
        process_file(f)
