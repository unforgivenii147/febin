#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from sys import exit as _exit


def process_file(fp):
    path = Path(fp)
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    for line in lines:
        if 'name = "' in line:
            pkg_name = line.split('name = "')[1].split('"')[0]
            print(pkg_name)
            with Path("requirements.txt").open("a", encoding="utf-8") as f:
                f.write(pkg_name + "\n")


def main():
    filename = "uv.lock"
    process_file(filename)


if __name__ == "__main__":
    _exit(main())
