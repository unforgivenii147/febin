#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys
from time import perf_counter


def main():
    start = perf_counter()
    fn = sys.argv[1]
    lines = []
    with open(fn, encoding="utf-8") as f:
        lines = f.readlines()
    new_fn = Path(fn).stem + "_list.txt"
    with open(new_fn, "w", encoding="utf-8") as fo:
        fo.write("{")
        for line in lines:
            str1 = '"' + str(line.strip()) + '", ' if '"' not in line else "'" + str(line.strip()) + "', "
            fo.write(str1)
        fo.write("}")
    print(f"{perf_counter() - start} seconds")


if __name__ == "__main__":
    sys.exit(main())
