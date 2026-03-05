#!/data/data/com.termux/files/usr/bin/env python
import sys
import importlib
import traceback
from loguru import logger
from importlib import import_module
from importlib.metadata import distributions

logger.add("/sdcard/allimport.log", diagnose=True)


# @logger.catch
def tryimport(package):

    try:
        import_module(package)
        logger.info(f"\u2713 {package}")
        return True
    except Exception:
        logger.debug(f"X {package}")
        return traceback.format_exc()


# @logger.catch
def tryallimport():
    for pkg in distributions():
        pkn = pkg.metadata["name"]
        try:
            import_module(pkn)
            logger.info(f"\u2713 {pkn}")
        except Exception:
            logger.debug(f"X {pkn}")


if __name__ == "__main__":
    modn = sys.argv[1]
    tryimport(modn)
#    tryallimport()
#    sys.exit(0)
