#!/data/data/com.termux/files/usr/bin/python

from typing import Any
from pathlib import Path

from dh import gsz
from termcolor import cprint


def main() -> None:
    root = Path.cwd()
    kp: dict[Any, Any] = {}
    files = [p for p in root.rglob("*") if p.is_file() and p.exists() and not p.is_symlink() and ".git" not in p.parts]
    for f in files:
        path = Path(root / f)
        psz = gsz(path)
        kp.setdefault(psz, []).append(path.name)
    orig = kp
    kz = sorted(kp.keys())
    pk: dict[Any, list[str]] = {}
    for x in kz:
        pk[x] = orig.get(x, [])
    for k, v in pk.items():
        if len(v) > 1:
            cprint(f"{k}:", "cyan")
            for i in v:
                print(f"    - {i}")


if __name__ == "__main__":
    main()
