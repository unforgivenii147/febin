#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import pathlib
import tempfile
import subprocess


def fold_content_pure(fname, width=45):
    content = ""
    content = pathlib.Path(fname).read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    folded_lines = []
    for line in lines:
        while len(line) > width:
            folded_lines.append(line[:width])
            line = line[width:]
        if line:
            folded_lines.append(line)
    with pathlib.Path(fname).open("w", encoding="utf-8") as fo:
        for line in folded_lines:
            fo.write(line + "\n")
    print(f"{fname} updated.")


def fold_file_inplace(filename):
    if not pathlib.Path(filename).exists():
        print(
            f"Error: File '{filename}' not found.",
            file=sys.stderr,
        )
        sys.exit(1)
    original_content = pathlib.Path(filename).read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile(
        mode="w+",
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as temp_f:
        temp_filename = temp_f.name
        temp_f.write(original_content)
        temp_f.flush()
        result = subprocess.run(
            [
                "fold",
                "-w",
                "30",
                "-s",
                temp_filename,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            print(
                f"Error running fold: {result.stderr}",
                file=sys.stderr,
            )
            pathlib.Path(temp_filename).unlink()
            sys.exit(1)
        pathlib.Path(filename).write_text(result.stdout, encoding="utf-8")
    pathlib.Path(temp_filename).unlink()
    print(f"Successfully folded '{filename}' in place.")


if __name__ == "__main__":
    fold_file_inplace(sys.argv[1])
