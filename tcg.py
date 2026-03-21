#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
from pathlib import Path

TERMUX_PYTHON = "#!/data/data/com.termux/files/usr/bin/python\n"
TERMUX_BASH = "#!/data/data/com.termux/files/usr/bin/bash\n"
cwd = Path.cwd()
homebin = Path.home() / "bin"
homebin2 = Path.home() / "bashbin"


def dcheck(fname) -> None:
    lines = fname.read_text(encoding="utf-8").splitlines()
    nl = []
    if lines[0].startswith("#!") and lines[1].startswith("#!"):
        nl.append(lines[0])
        nl.extend(lines[2:])
        print(f"{fname} had 2 shebang")
        fname.write_text("\n".join(nl))
    else:
        return


def get_clipboard():
    try:
        return subprocess.check_output(["termux-clipboard-get"], text=True)
    except subprocess.CalledProcessError:
        print(
            "Error: failed to get clipboard content",
            file=sys.stderr,
        )
        sys.exit(1)


def detect_shebang(content: str) -> str | None:
    stripped = content.lstrip()
    if stripped.startswith("#!") and "python" in stripped:
        return TERMUX_PYTHON
    if "import " in content or "def " in content or "class " in content or stripped.startswith(
            "!python"):
        return TERMUX_PYTHON
    if stripped.startswith((
            "echo ",
            "cd ",
            "export ",
            "set ",
            "if ",
            "for ",
            "#!/bin/sh",
    )):
        return TERMUX_BASH
    return None


def create_symlink(out_file):
    ext = out_file.suffix
    if ext and (cwd in (homebin, homebin2)):
        symlink_path = out_file.parent / out_file.stem
        try:
            out_file.symlink_to(symlink_path)
            print(f"{symlink_path.name} -> {out_file.name}")
        except FileExistsError:
            print(f"{symlink_path.name} exists.")
        except Exception as e:
            print(
                f"Error creating symlink: {e}",
                file=sys.stderr,
            )


def main():
    if len(sys.argv) != 2:
        print(
            f"Usage: {sys.argv[0]} <output-file>",
            file=sys.stderr,
        )
        sys.exit(1)
    out_file = Path(sys.argv[1])
    content = get_clipboard()
    if cwd in (homebin, homebin2):
        shebang = detect_shebang(content)
        if shebang:
            content = shebang + content

    out_file.write_text(content, encoding="utf-8")

    dcheck(out_file)
    if cwd in (homebin, homebin2):
        out_file.chmod(0o755)
        create_symlink(out_file)


if __name__ == "__main__":
    main()
