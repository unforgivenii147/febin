#!/data/data/com.termux/files/usr/bin/python
import argparse
import mmap
from pathlib import Path
import random
import secrets


def enhanced_shuffle(
    input_file,
    output_file_prefix=None,
    methods=None,
    repeats=3,
):
    if methods is None:
        methods = ["basic", "crypto", "shuffle3"]
    input_file_path = Path(input_file)
    file_size = input_file_path.stat().st_size
    print(f"Read {file_size} bytes from {input_file}")

    lines = []
    if file_size > 5 * 1024 * 1024:  # 5MB threshold
        print("File size > 5MB, attempting to use mmap.")
        try:
            with open(input_file, "r+b") as f:  # Open in binary mode for mmap
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                # Decode mmap'd bytes to string and split into lines
                # This part can be tricky with encoding and line endings
                # For simplicity, assuming utf-8 and standard line endings
                decoded_content = mm.decode("utf-8", errors="ignore")
                lines = decoded_content.splitlines(
                    keepends=True
                )  # keepends=True to preserve original line endings for writing back
                mm.close()
        except Exception as e:
            print(f"Error using mmap: {e}. Falling back to standard file reading.")
            # Fallback to standard reading if mmap fails
            with open(input_file, encoding="utf-8") as f:
                lines = f.readlines()
    else:
        with open(input_file, encoding="utf-8") as f:
            lines = f.readlines()

    original_count = len(lines)
    print(f"Read {original_count} lines from {input_file}")

    for method in methods:
        print(f"\n--- Shuffling with method: {method} ---")
        shuffled_lines = lines.copy()
        for _ in range(repeats):
            if method == "basic":
                random.shuffle(shuffled_lines)
            elif method == "crypto":
                crypto_shuffle(shuffled_lines)
            elif method == "shuffle3":
                shuffle3(shuffled_lines)
            # weighted method is removed as per instructions

        output_path = output_file_prefix if output_file_prefix else input_file
        # Append method name to output file to distinguish them
        if output_file_prefix:
            output_path = f"{output_file_prefix}_{method}.txt"
        else:
            # If overwriting, create new files with method suffix
            base, ext = os.path.splitext(input_file)
            output_path = f"{base}_{method}{ext}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(shuffled_lines)
        print(f"Shuffled {original_count} lines using method '{method}' with {repeats} passes")
        print(f"Output written to: {output_path}")


def crypto_shuffle(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        lst[i], lst[j] = lst[j], lst[i]


def shuffle3(lst):
    sys_random = random.SystemRandom()
    for i in range(len(lst) - 1, 0, -1):
        j = sys_random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]


def test_randomness(input_file):
    # For testing, we'll still use a specific method, e.g., crypto
    # As running all methods for testing might be too verbose.
    # If you want to test each method, this function would need adjustment.
    method_to_test = "crypto"  # Defaulting to crypto for test
    print(f"Testing randomness with method: {method_to_test}")

    lines_to_test = []
    try:
        with open(input_file, encoding="utf-8") as f:
            lines_to_test = [line.strip() for line in f.readlines()[:100]]
    except Exception as e:
        print(f"Error reading file for testing: {e}")
        return

    if not lines_to_test:
        print("No lines found to test.")
        return

    original_order = lines_to_test.copy()
    for i in range(5):
        current_lines = original_order.copy()  # Reset for each shuffle iteration
        if method_to_test == "basic":
            random.shuffle(current_lines)
        elif method_to_test == "crypto":
            crypto_shuffle(current_lines)
        elif method_to_test == "shuffle3":
            shuffle3(current_lines)

        changes = sum(
            1
            for a, b in zip(
                original_order,
                current_lines,
                strict=False,
            )
            if a != b
        )
        print(f"Shuffle {i + 1}: {changes} out of {len(current_lines)} positions changed")


def main():
    parser = argparse.ArgumentParser(description="Randomize lines in a file")
    parser.add_argument("input_file", help="Input file to shuffle")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file prefix (default: will append method name to input file name)",
    )
    # Method argument is removed
    parser.add_argument(
        "-r",
        "--repeats",
        type=int,
        default=3,
        help="Number of shuffle passes per method (default: 3)",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test randomness of the 'crypto' method",
    )
    args = parser.parse_args()

    # Ensure output file naming is handled correctly when not overwriting
    output_prefix = args.output
    if output_prefix and not output_prefix.endswith((".txt", ".TXT")):
        # If user provides a prefix without extension, add .txt for clarity
        # This might need adjustment based on desired behavior for custom extensions
        output_prefix += ".txt"

    if args.test:
        test_randomness(args.input_file)
    else:
        # Run all three methods
        enhanced_shuffle(
            args.input_file,
            output_prefix,
            methods=["basic", "crypto", "shuffle3"],  # Explicitly list methods
            repeats=args.repeats,
        )


if __name__ == "__main__":
    main()
