#!/data/data/com.termux/files/usr/bin/env python
import os


def find_md_files(directory="."):
    md_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md") and file != "SUMMARY.md":
                rel_path = os.path.relpath(
                    os.path.join(root, file),
                    start=directory,
                )
                md_files.append(rel_path)
    return md_files


def update_summary():
    md_files = find_md_files()
    md_files.sort()
    with open("SUMMARY.md") as f:
        lines = f.readlines()
    header = []
    for line in lines:
        if line.strip() and not line.strip().startswith("- ["):
            header.append(line)
        else:
            break
    new_entries = []
    for md_file in md_files:
        title = os.path.splitext(md_file)[0].replace("_", " ").replace(os.sep, " ").title()
        entry = f"- [{title}](.{os.sep}{md_file})\n"
        new_entries.append(entry)
    with open("SUMMARY.md", "w") as f:
        f.writelines(header)
        f.write("\n")
        f.writelines(new_entries)
    print(f"Updated SUMMARY.md with {len(new_entries)} chapters.")


if __name__ == "__main__":
    update_summary()
