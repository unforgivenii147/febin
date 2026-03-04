#!/data/data/com.termux/files/usr/bin/env python
import os
from pathlib import Path

from markdownify import markdownify


def convert_html_to_markdown(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                html_file_path = os.path.join(root, file)
                md_file_path = os.path.join(
                    root,
                    f"{os.path.splitext(file)[0]}.md",
                )
                with open(
                        html_file_path,
                        encoding="utf-8",
                ) as html_file:
                    html_content = html_file.read()
                    md_content = markdownify(html_content)
                with open(
                        md_file_path,
                        "w",
                        encoding="utf-8",
                ) as md_file:
                    md_file.write(md_content)
                print(f"[\u2714] {Path(md_file_path).name}")


if __name__ == "__main__":
    current_dir = os.getcwd()
    convert_html_to_markdown(current_dir)
