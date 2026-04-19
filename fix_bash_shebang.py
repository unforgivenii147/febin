import os
from pathlib import Path

TARGET_SHEBANG = "#!/data/data/com.termux/files/usr/bin/bash"


def process_file(filepath):
    print(f"processing {filepath}")
    with Path(filepath).open("r+", encoding="utf-8") as f:
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
        Path(filepath).chmod(0o755)


if __name__ == "__main__":
    cwd = Path.cwd()
    for path in cwd.rglob("*.sh"):
        process_file(path)
