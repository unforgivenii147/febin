import sys
from pathlib import Path

from termcolor import cprint

from dhh import fsz, get_files, gsz, mpf, run_command


def process_file(fp):
    before = gsz(fp)
    if not fp.exists():
        return False
    print(f"{fp.name}", end=" ")
    cmd = f"terser {fp}"
    code, output, err = run_command(cmd)
    if code == 0:
        fp.write_text(output)
        diffsize = before - gsz(fp)
        if diffsize == 0:
            cprint("[NO CHANGE]", "white")
        elif diffsize < 0:
            cprint(
                f"[OK] + {fsz(diffsize)}",
                "yellow",
            )
        elif diffsize > 0:
            cprint(
                f"[OK] - {fsz(diffsize)}",
                "cyan",
            )
        return True
    cprint(f"[ERROR] {err}", "magenta")
    return False


def main():
    args = sys.argv[1:]
    cwd = Path.cwd()
    before = gsz(cwd)
    files = (
        [Path(p) for p in args] if args else get_files(cwd, extensions=[".js", ".ts", ".cjs", ".mjs", ".jsx", ".tsx"])
    )
    _ = mpf(process_file, files)
    diff_size = before - gsz(cwd)
    cprint(f"space freed : {fsz(diff_size)}", "green")


if __name__ == "__main__":
    sys.exit(main())
