#!/data/data/com.termux/files/usr/bin/env python
import sys
from pathlib import Path

from dh import format_size, get_nobinary, get_size

STRTOFIND = ["dist-info", ".so", ".py", ".pth", "__", ".zip"]


def clean_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines()
                     if not any(s in line for s in STRTOFIND))


def clean_file(path: str) -> None:
    try:
        with open(
                path,
                encoding="utf-8",
                errors="ignore",
        ) as f:
            original = f.read()
    except Exception:
        return
    cleaned = clean_text(original)
    if cleaned != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)


def main() -> None:
    root = Path.cwd()
    isz = get_size(root)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(root)
    if len(files) == 1:
        clean_file(files[0])
        sys.exit(0)
    pool = Pool(8)
    for f in files:
        p.apply_async(clean_file, (f, ))
    pool.close()
    pool.join()

    esz = get_size(root)
    diffsize = isz - esz
    print(f"space freed : {format_size(diffsize)}")


# (".zip",".whl",".tar.gz",".tgz",".tar",)

if __name__ == "__main__":
    main()
