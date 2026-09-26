#!/data/data/com.termux/files/usr/bin/python
"""Try importing packages and log which ones succeed or fail.

With arguments, each argument is treated as a module name and imported.
Without arguments, every installed distribution is imported in turn.  Results
are logged (with full tracebacks on failure) to ``/sdcard/allimport.log`` via
loguru.

Usage::

    trimpo.py [package ...]
"""

import sys
import traceback
from importlib import import_module
from importlib.metadata import distributions

from loguru import logger

logger.add("/sdcard/allimport.log", diagnose=True)


def tryimport(package: str) -> bool | str:
    """Attempt to import ``package``.

    Args:
        package: Importable module name.

    Returns:
        ``True`` on success, otherwise the formatted traceback string.
    """
    try:
        import_module(package)
        logger.info(f"\u2713 {package}")
        return True
    except Exception:  # noqa: BLE001 - report any import failure, keep going
        logger.debug(f"X {package}")
        return traceback.format_exc()


def tryallimport() -> None:
    """Import every installed distribution, logging success or failure."""
    for pkg in distributions():
        pkn: str = pkg.metadata["name"]
        try:
            import_module(pkn)
            logger.info(f"\u2713 {pkn}")
        except Exception:  # noqa: BLE001 - one bad package must not stop the rest
            logger.debug(f"X {pkn}")


if __name__ == "__main__":
    args: list[str] = sys.argv[1:]
    if args:
        pkgs: list[str] = list(args)
        for pkg in pkgs:
            tryimport(pkg)
    else:
        tryallimport()
    sys.exit(0)
