#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import subprocess
import tempfile

SVGCPATH = "/data/data/com.termux/files/home/.cargo/bin/svgcleaner"


def clean_single_svg(in_file, svgcleaner_path=SVGCPATH):
    """Clean a single SVG file and return size change."""
    if not os.path.exists(in_file):
        msg = f"Input file not found: {in_file}"
        raise FileNotFoundError(msg)
    before_size = os.path.getsize(in_file)
    tmp_out_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name
        subprocess.run(
            [
                svgcleaner_path,
                "--copy-on-error",
                "--remove-comments=yes",
                in_file,
                tmp_out_path,
            ],
            check=True,
            capture_output=True,
        )
        after_size = os.path.getsize(tmp_out_path)
        if after_size != 0:
            os.replace(tmp_out_path, in_file)
            size_change = before_size - after_size
            return (
                True,
                in_file,
                before_size,
                after_size,
                size_change,
            )
        else:
            return (
                False,
                in_file,
                before_size,
                after_size,
                size_change,
            )
    except subprocess.CalledProcessError as e:
        return (
            False,
            in_file,
            0,
            0,
            f"Error: {e.stderr.decode('utf-8')}",
        )
    except Exception as e:
        return (
            False,
            in_file,
            0,
            0,
            f"Unexpected error: {e}",
        )
    finally:
        if tmp_out_path and os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)


def find_svg_files(root_dir):
    """Find all SVG files in a directory recursively."""
    return [str(f) for f in Path(root_dir).rglob("*.svg")]


def clean_svg_dir(root_dir, svgcleaner_path="svgcleaner"):
    """Clean all SVG files in a directory and show size changes."""
    svg_files = find_svg_files(root_dir)
    if not svg_files:
        print("No SVG files found.")
        return
    total_before = 0
    total_after = 0
    total_saved = 0
    for in_file in svg_files:
        success, f, before, after, size_change = clean_single_svg(in_file, svgcleaner_path)
        if success:
            print(f"Cleaned: {f}")
            print(f"  Before: {before} bytes, After: {after} bytes, Saved: {size_change} bytes")
            total_before += before
            total_after += after
            total_saved += size_change
        else:
            print(f"Failed to clean {f}: {size_change}")
    print("\n--- Summary ---")
    print(f"Total files processed: {len(svg_files)}")
    print(f"Total size before: {total_before} bytes")
    print(f"Total size after: {total_after} bytes")
    print(f"Total size saved: {total_saved} bytes")


if __name__ == "__main__":
    input_dir = Path.cwd()
    clean_svg_dir(input_dir)
