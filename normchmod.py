#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import stat

import fastwalk


def get_mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def normalize_permissions(homedir: str) -> None:
    DIR_PERM = 0o775
    FILE_PERM = 0o664
    for pth in fastwalk.walk(homedir):
        path = Path(pth)
        try:
            current_perm = get_mode(path)
            if path.is_dir():
                if current_perm != DIR_PERM:
                    os.chmod(path, DIR_PERM)
                    print(f"Set permissions for directory: {path} from {oct(current_perm)} to {oct(DIR_PERM)}")
            elif path.is_file():
                if current_perm != FILE_PERM:
                    os.chmod(path, FILE_PERM)
                    print(f"Set permissions for file: {path} from {oct(current_perm)} to {oct(FILE_PERM)}")
                try:
                    for encod in [
                        "utf-8",
                        "windows-1251",
                    ]:
                        with open(
                            path,
                            errors="ignore",
                            encoding=encod,
                        ) as f:
                            f.read()
                except:
                    print(f"error reading {path.name}")
        except PermissionError as e:
            print(f"Permission denied: {path.name} ({e})")
        except FileNotFoundError:
            continue
        except OSError as e:
            print(f"OS error on {path.name}: {e}")


if __name__ == "__main__":
    normalize_permissions(".")
