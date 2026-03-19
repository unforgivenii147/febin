#!/data/data/com.termux/files/usr/bin/python
import sys


def dict_val(line: str) -> str:
    if ":" in line:
        out = line.split(":", 1)[1].strip()
        print(out)
        return out
    elif "=" in line:
        out = line.split("=", 1)[1].strip()
        print(out)
        return out
    else:
        return line


def main():
    fname = sys.argv[1]
    with open(fname, encoding="utf8", errors="replace") as f:
        lines = f.readlines()
    all_lines = [line for line in lines if ":" in line or "=" in line]
    all_lines.sort(key=dict_val)
    with open(fname, "w") as fo:
        fo.writelines(all_lines)


if __name__ == "__main__":
    main()
