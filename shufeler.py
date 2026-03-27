#!/data/data/com.termux/files/usr/bin/python
import argparse
import pathlib
import random
import secrets


def enhanced_shuffle(
    input_file,
    output_file=None,
    method="crypto",
    repeats=3,
):
    with pathlib.Path(input_file).open(encoding="utf-8") as f:
        lines = f.readlines()
    original_count = len(lines)
    print(f"Read {original_count} lines from {input_file}")
    shuffled_lines = lines.copy()
    for _i in range(repeats):
        if method == "basic":
            random.shuffle(shuffled_lines)
        elif method == "crypto":
            crypto_shuffle(shuffled_lines)
        elif method == "shuffle3":
            shuffle3(shuffled_lines)
        elif method == "weighted":
            weighted_shuffle(shuffled_lines)
    output_path = output_file or input_file
    with pathlib.Path(output_path).open("w", encoding="utf-8") as f:
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


def weighted_shuffle(lst):
    n = len(lst)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]
    if n > 1:
        for i in range(n - 1):
            swap_pos = random.randint(i + 1, n - 1)
            lst[i], lst[swap_pos] = (
                lst[swap_pos],
                lst[i],
            )


def test_randomness(input_file):
    with pathlib.Path(input_file).open(encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()[:100]]
    original_order = lines.copy()
    for i in range(5):
        crypto_shuffle(lines)
        changes = sum(
            1
            for a, b in zip(
                original_order,
                lines,
                strict=False,
            )
            if a != b
        )
        print(f"Shuffle {i + 1}: {changes} out of {len(lines)} positions changed")


def main():
    parser = argparse.ArgumentParser(description="Randomize lines in a file")
    parser.add_argument("input_file", help="Input file to shuffle")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file (default: overwrite input)",
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=[
            "basic",
            "crypto",
            "shuffle3",
            "weighted",
        ],
        default="crypto",
        help="Shuffling method (default: crypto)",
    )
    parser.add_argument(
        "-r",
        "--repeats",
        type=int,
        default=3,
        help="Number of shuffle passes (default: 1)",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test randomness",
    )
    args = parser.parse_args()
    if args.test:
        test_randomness(args.input_file)
    else:
        enhanced_shuffle(
            args.input_file,
            args.output,
            args.method,
            args.repeats,
        )


if __name__ == "__main__":
    main()
