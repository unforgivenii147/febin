#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
from pathlib import Path

from dh import get_filez


def has_shell_shebang(path):
    try:
        with Path(path).open("rb") as f:
            first = f.readline(256).decode("utf-8", errors="ignore").strip()
    except Exception:
        return False
    if not first.startswith("#!"):
        return False
    return ("bash" in first) or ("sh" in first)


def process_file(fp):
    print("Formatting: ", fp.name)
    try:
        res = subprocess.run(["shfmt", "-w", str(fp)], capture_output=True, text=True)
        if res.returncode != 0:
            print("  shfmt failed:", res.stderr.strip(), file=sys.stderr)
            return False
    except Exception as e:
        print("  error running shfmt:", e, file=sys.stderr)
        return False
    return True


def main():
    cwd = Path.cwd()
    failed = [
        path
        for path in get_filez(cwd)
        if ((not path.suffix and has_shell_shebang(path)) or path.suffix == ".sh") and not process_file(path)
    ]
    if failed:
        print(f"Finished with {len(failed)} failures: ", file=sys.stderr)
        for f in failed:
            print("  - ", f.relative_to(cwd))
    else:
        print("All done.")


if __name__ == "__main__":
    main()
