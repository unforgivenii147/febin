#!/data/data/com.termux/files/usr/bin/python
import argparse
import shutil
import sys
from pathlib import Path

from dh import unique_path


def safe_move(
    source,
    destination,
    verbose=True,
    no_clobber=True,
):
    source_path = Path(source)
    if not source_path.exists():
        print(
            f"Error: Source '{source}' does not exist",
            file=sys.stderr,
        )
        return False
    dest_path = Path(destination)
    if dest_path.is_dir():
        dest_path /= source_path.name
    if no_clobber and dest_path.exists():
        dest_path = unique_path(dest_path)
        print(f"Target exists, renaming to: {dest_path}")
    try:
        shutil.move(str(source_path), str(dest_path))
        print(f"copied '{source}' -> '{dest_path}'")
        return True
    except Exception as e:
        print(
            f"Error moveing file: {e}",
            file=sys.stderr,
        )
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Safe mv - move files without overwriting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.txt /target/dir/
  %(prog)s -v file.txt file2.txt dir/
  %(prog)s -f file.txt file.txt
        """,
    )
    parser.add_argument(
        "-s",
        "sources",
        nargs="+",
        help="Source files/directories to move",
    )
    parser.add_argument("destination", help="Destination path")
    parser.add_argument(
        "-v",
        "--verbose",
        default=True,
        action="store_true",
        help="Explain what is being done",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite (like regular mv)",
    )
    parser.add_argument(
        "-n",
        "--no-clobber",
        action="store_true",
        default=True,
        help="Do not overwrite existing files (default)",
    )
    args = parser.parse_args()
    if len(args.sources) > 1:
        dest_path = Path(args.destination)
        if not dest_path.is_dir() and not args.destination.endswith("/"):
            print(
                "Error: When moving multiple files, destination must be a directory",
                file=sys.stderr,
            )
            sys.exit(1)
        if not dest_path.exists():
            try:
                dest_path.mkdir(parents=True)
                print(f"Created directory: {dest_path}")
            except Exception as e:
                print(
                    f"Error creating directory: {e}",
                    file=sys.stderr,
                )
                sys.exit(1)
    success_count = 0
    for source in args.sources:
        if safe_move(
            source,
            args.destination,
            args.verbose,
            not args.force,
        ):
            success_count += 1
    if success_count == len(args.sources):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
