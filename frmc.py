#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path

from dh import SOURCE_CODE_EXT, clean_blank_lines, format_size, get_nobinary, get_size, is_binary, mpf
from termcolor import cprint


def process_file(fp):
    if fp.suffix == ".md":
        return
    removed: int = 0
    inline: int = 0
    if is_binary(fp) or fp.suffix in SOURCE_CODE_EXT:
        print(f"[skip] {fp.name} is binary or source code")
        return
    before: int = get_size(fp)
    lines = fp.read_text(encoding="utf-8").splitlines(keepends=True)
    print(f"[Ok] {fp.name} ", end="")
    if not lines:
        return
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#!") or "#!" in stripped:
            cleaned.append(line)
            continue
        if "#" in line and not line.startswith("#"):
            indx = line.index("#")
            cleaned.append(line[:indx])
            inline += 1
            continue
        if not line.startswith("#"):
            cleaned.append(line)
        else:
            removed += 1
    code = "\n".join(cleaned)
    code = clean_blank_lines(code)
    if fp.suffix != ".py":
        fp.write_text(code, encoding="utf-8")
        after = get_size(fp)
        diffsize = after - before
        cprint(
            f"{format_size(diffsize)} | removed : {removed} | inline : {inline}",
            "yellow",
        )
    else:
        try:
            _ = ast.parse(code)
            fp.write_text(code, encoding="utf-8")
            after = get_size(fp)
            diffsize = after - before
            cprint(
                f"{format_size(diffsize)} | removed : {removed} | inline : {inline}",
                "yellow",
            )
        except:
            cprint("result code invalid.", "magenta")


def main() -> None:
    cwd = Path.cwd()
    before = get_size(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_nobinary(cwd)
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    _ = mpf(process_file, files)
    diffsize = before - get_size(cwd)
    cprint(
        f"{format_size(diffsize)}",
        "cyan",
    )


if __name__ == "__main__":
    main()
