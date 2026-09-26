#!/data/data/com.termux/files/usr/bin/python
"""Create extension-less symlinks for the scripts in ``~/bashbin`` and ``~/bin``.

For every ``*.sh`` file in ``~/bashbin`` and every ``*.py`` file in ``~/bin``
this creates a sibling symlink whose name is the file's stem (no extension),
so the scripts can be invoked without typing the extension.  Existing targets
are left untouched.
"""

from pathlib import Path

BASHBIN: Path = Path.home() / "bashbin"
BIN: Path = Path.home() / "bin"


def process_dir(root_dir: Path, ext: str) -> None:
    """Create stem-named symlinks for ``*.<ext>`` files inside ``root_dir``.

    Args:
        root_dir: Directory to scan for source files.
        ext: File extension to match, without a leading dot (e.g. ``"py"``).
    """
    for path in root_dir.glob(f"*.{ext}"):
        symlink_path: Path = path.with_name(path.stem)
        if not symlink_path.exists():
            symlink_path.symlink_to(path)
            # NOTE: original code referenced the undefined names ``link_name``
            # and ``src_file`` here, which raised NameError at runtime; fixed to
            # report the actual symlink and its target.
            print(f"Created symlink: {symlink_path} -> {path}")
        else:
            continue


if __name__ == "__main__":
    # ``glob`` matches on the literal extension, so pass it without a dot.
    process_dir(BASHBIN, "sh")
    process_dir(BIN, "py")
