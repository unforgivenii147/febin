#!/data/data/com.termux/files/usr/bin/python
import os
import pathlib

TARGET_SHEBANG = "#!/data/data/com.termux/files/usr/bin/bash"
BASH_KEYWORDS = {
    "set ",
    "unset ",
    "then",
    "done",
    "cd",
    "chdir",
    "bash",
    "copy",
    "not",
    "del",
    "do",
    "echo",
    "else",
    "errorlevel",
    "exist",
    "exit",
    "fi",
    "for",
    "goto",
    "if",
    "in",
    "md",
    "mkdir",
    "move",
    "pause",
    "ren",
    "set",
    "shift",
    "export",
}


def is_bash_file(filepath):
    return bool(filepath.endswith(".sh"))


def process_file(filepath):
    print(f"processing {filepath}")
    with pathlib.Path(filepath).open("r+", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return
        if lines and lines[0].startswith("#!"):
            lines[0] = TARGET_SHEBANG + "\n"
            if len(lines) > 1 and lines[1].strip() != "":
                lines.insert(1, "\n")
        f.seek(0)
        f.writelines(lines)
        f.truncate()
        print(f"{os.path.relpath(filepath)} updated.")
    if "bin" in filepath.split(os.sep):
        pathlib.Path(filepath).chmod(0o755)


def traverse_directory(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if pathlib.Path(filepath).is_symlink():
                continue
            if is_bash_file(filepath):
                process_file(filepath)


if __name__ == "__main__":
    traverse_directory(pathlib.Path.cwd())
