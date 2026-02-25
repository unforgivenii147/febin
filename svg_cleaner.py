#!/data/data/com.termux/files/usr/bin/env python3
import os
import subprocess
import sys
import tempfile


def clean_svg_inplace(in_file, svgcleaner_path="svgcleaner"):
    """
    Clean an SVG file in-place using the svgcleaner Rust executable.

    Args:
        in_file (str): Path to the input SVG file.
        svgcleaner_path (str): Path to the svgcleaner executable (default: "svgcleaner").
    """
    if not os.path.exists(in_file):
        raise FileNotFoundError(f"Input file not found: {in_file}")

    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_out:
        tmp_out_path = tmp_out.name

    try:
        # Run svgcleaner
        subprocess.run(
            [svgcleaner_path, in_file, tmp_out_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Replace the original file with the cleaned version
        os.replace(tmp_out_path, in_file)
        print(f"Successfully cleaned and updated: {in_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error running svgcleaner: {e.stderr.decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        # Clean up the temporary file if it still exists
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python svgcleaner_wrapper.py <input-svg-file>")
        sys.exit(1)

    input_file = sys.argv[1]
    clean_svg_inplace(input_file)
