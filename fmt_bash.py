#!/data/data/com.termux/files/usr/bin/python
import argparse
import os
import subprocess
import sys


def has_no_extension(name):
    return os.path.splitext(name)[1] == ""


def has_shell_shebang(path):
    try:
        with open(path, "rb") as f:
            first = f.readline(256).decode("utf-8", errors="ignore").strip()
    except Exception:
        return False
    if not first.startswith("#!"):
        return False
    # treat both bash and sh shebangs as shell scripts
    return ("bash" in first) or ("sh" in first)


def find_candidates(root=".", recursive=False):
    if recursive:
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                fullpath = os.path.join(dirpath, name)
                if not os.path.islink(fullpath):
                    yield fullpath
    else:
        for name in os.listdir(root):
            fullpath = os.path.join(root, name)
            if not os.path.islink(fullpath):
                yield fullpath


def main():
    p = argparse.ArgumentParser(description="Format bash/sh scripts without extension using shfmt")
    p.add_argument("-r", "--recursive", action="store_true", help="search directories recursively")
    p.add_argument("-n", "--dry-run", action="store_true", help="print files that would be formatted, do not run shfmt")
    p.add_argument("--shfmt", default="shfmt", help="path to shfmt (default: shfmt)")
    args = p.parse_args()
    # check shfmt availability unless dry-run
    if not args.dry_run:
        try:
            subprocess.run([args.shfmt, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(
                f'Error: shfmt not found at "{args.shfmt}". Install shfmt or pass correct path with --shfmt.',
                file=sys.stderr,
            )
            sys.exit(2)
    candidates = []
    for path in find_candidates(".", recursive=args.recursive):
        if not os.path.isfile(path):
            continue
        name = os.path.basename(path)
        if name.startswith("."):
            # skip hidden files by default
            continue
        if not has_no_extension(name):
            continue
        if has_shell_shebang(path):
            candidates.append(path)
    if not candidates:
        print("No matching no-extension shell scripts found.")
        return
    if args.dry_run:
        print("Files that would be formatted:")
        for f in candidates:
            print(" ", f)
        return
    failed = []
    for f in candidates:
        print("Formatting:", f)
        try:
            res = subprocess.run([args.shfmt, "-w", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print("  shfmt failed:", res.stderr.strip(), file=sys.stderr)
                failed.append(f)
        except Exception as e:
            print("  error running shfmt:", e, file=sys.stderr)
            failed.append(f)
    if failed:
        print(f"Finished with {len(failed)} failures.", file=sys.stderr)
        sys.exit(1)
    else:
        print("All done.")


if __name__ == "__main__":
    main()
