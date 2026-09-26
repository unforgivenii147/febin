#!/data/data/com.termux/files/usr/bin/python
"""Quarantine Python files that fail to parse.

Every target file is parsed with :func:`ast.parse`; any file that raises a
:class:`SyntaxError` (or any other parse error) is copied into an ``ERROR``
sub-directory of the current working directory.  Files given on the command
line are checked, otherwise every ``*.py`` file in the current directory is.

Usage::

    asteval.py [file ...]
"""

import ast
import sys
from pathlib import Path

from dh import cpf, mpf3a

cwd: Path = Path.cwd()
err_dir: Path = Path(f"{cwd}/ERROR")
err_dir.mkdir(exist_ok=True)


def process_file(fp: Path) -> None:
    """Copy ``fp`` into the ERROR directory when it does not parse.

    Args:
        fp: Path to the candidate Python source file.
    """
    content: str = fp.read_text(encoding="utf-8")
    try:
        ast.parse(content)
    except Exception:  # noqa: BLE001 - any parse failure means "quarantine it"
        newpath: Path = err_dir / fp.name
        cpf(fp, newpath)


def main() -> int:
    """Parse each target file in parallel via :func:`dh.mpf3a`.

    Returns:
        Process exit code (always ``0``).
    """
    args: list[str] = sys.argv[1:]
    files: list[Path] = (
        [Path(f) for f in args] if args else [Path(p) for p in cwd.glob("*.py")]
    )
    mpf3a(process_file, files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
