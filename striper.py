#!/data/data/com.termux/files/usr/bin/python
from sys import argv


def remove_spaces_from_file(fname) -> None:
    try:
        with open(fname) as file:
            lines = file.readlines()
            cleaned_lines = [line.lstrip().strip().rstrip() for line in lines]
        with open(fname, "w") as file:
            for k in cleaned_lines:
                file.writelines(k + "\n")
        print(f"{fname} cleaned.")
    except FileNotFoundError:
        print(f"Error: File '{fname}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    remove_spaces_from_file(argv[1])
