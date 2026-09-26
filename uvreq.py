#!/data/data/com.termux/files/usr/bin/python
"""Extract package names from a ``uv.lock`` file into ``requirements.txt``.

Every ``name = "..."`` line in ``uv.lock`` is parsed and the package name is
printed and appended to ``requirements.txt`` in the current directory.
"""

from pathlib import Path


def process_file(fp: str) -> None:
    """Append each ``name = "..."`` entry found in ``fp`` to requirements.txt.

    Args:
        fp: Path to the lock file to read.
    """
    path: Path = Path(fp)
    content: str = path.read_text(encoding="utf-8")
    lines: list[str] = content.splitlines()
    for line in lines:
        if 'name = "' in line:
            pkg_name: str = line.split('name = "')[1].split('"')[0]
            print(pkg_name)
            with Path("requirements.txt").open("a", encoding="utf-8") as f:
                f.write(pkg_name + "\n")


def main() -> None:
    """Process the default ``uv.lock`` file in the current directory."""
    filename: str = "uv.lock"
    process_file(filename)


if __name__ == "__main__":
    main()
