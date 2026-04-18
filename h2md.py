#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path

from markdownify import markdownify


def convert_html_to_markdown(cwd):
    for root, _, files in os.walk(cwd):
        for file in files:
            if file.endswith(".html"):
                html_file_path = os.path.join(root, file)
                md_file_path = os.path.join(
                    root,
                    f"{os.path.splitext(file)[0]}.md",
                )
                with Path(html_file_path).open(encoding="utf-8") as html_file:
                    html_content = html_file.read()
                    md_content = markdownify(html_content)
                Path(md_file_path).write_text(md_content, encoding="utf-8")
                print(f"[\u2714] {Path(md_file_path).name}")


if __name__ == "__main__":
    current_dir = Path.cwd()
    convert_html_to_markdown(current_dir)
