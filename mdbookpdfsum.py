#!/data/data/com.termux/files/usr/bin/env python
import os
import pypdf
import lxml.html
import urllib
import argparse
import re


class Section:
    def __init__(self, title: str, source_file: str, depth: int, index: int):
        self.title = title
        self.source_file = source_file
        self.depth = depth
        self.index = index
        self.parent = None
        self.children = []
        self.outline_item = None

    def set_parent(self, parent):
        self.parent = parent

    def add_children(self, child):
        self.children.append(child)

    def path_to_root(self):
        path = []
        node = self
        while not node.is_root():
            path.append(str(node.index + 1))
            node = node.parent
        path = path[::-1]
        return path

    def is_root(self):
        return self.parent is None

    def __str__(self):
        path = self.path_to_root()
        return "{}. {}".format(".".join(path), self.title)


def check_title(prefix_path: str, node: Section, overwrite: bool) -> bool:
    all_matched = True
    for child in node.children:
        child_result = check_title(prefix_path, child, overwrite)
        if not child_result:
            return False
    if node.is_root():
        return True
    source_file = os.path.join(prefix_path, node.source_file)
    if not os.path.exists(source_file):
        print(f"File {source_file} does not exist")
        return False
    with open(source_file, "r") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:]
            if not title.startswith(node.title):
                all_matched = False
                print(
                    "[ERROR] Title not matched: source_file:{}, line num:{}, title:{}, title in `SUMMARY.md`:{}".format(
                        source_file, idx, title, node.title
                    )
                )
                break
    if not all_matched and overwrite:
        lines.insert(0, f"# {node.title}\n")
        print(f"[Info] Overwrite title as {node.title} in {node.source_file}")
        with open(source_file, "w") as f:
            f.writelines(lines)
        all_matched = True
    return all_matched


def get_dom_id(node: Section):
    source_path = node.source_file
    if source_path.startswith("./"):
        source_path = source_path[2:]
    source_path = source_path.split(".")[0]
    result = source_path
    result = result.lower()
    result = result.replace("/", "-")
    result = result.replace(" ", "-")
    return result


def add_outline(html_root, reader: pypdf.PdfReader, writer: pypdf.PdfWriter, node: Section):
    if not node.is_root():
        id = get_dom_id(node)
        try:
            results = html_root.get_element_by_id(id)
        except KeyError:
            print("[ERROR] Element not found: [{}]".format(id))
            return
        if results is None:
            print("[ERROR] Element is None, id: [{}]".format(id))
            return
        dest = reader.named_destinations["/{}".format(urllib.parse.quote(id))]
        page = None
        fit = None
        if dest.get("/Type") != "/Fit":
            page = reader.get_destination_page_number(dest)
            fit = pypdf.generic.Fit(
                dest.get("/Type"),
                (dest.get("/Left"), dest.get("/Top"), dest.get("/Zoom")),
            )
        node.outline_item = writer.add_outline_item(str(node), page, node.parent.outline_item, fit=fit)
    for child in node.children:
        add_outline(html_root, reader, writer, child)


def main():
    parser = argparse.ArgumentParser(prog="mdbook_pdf_summary", description="Add outline to the PDF file.")
    parser.add_argument(
        "--html_path",
        type=str,
        help="path of the `print.html` generated `mdbook-pdf`",
        default="print.html",
    )
    parser.add_argument(
        "--pdf_path",
        type=str,
        help="path of the `output.pdf` generated `mdbook-pdf`",
        default="output.pdf",
    )
    parser.add_argument(
        "--summary_path",
        type=str,
        help="path of the `SUMMARY.md`",
        default="src/SUMMARY.md",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        help="path of the output PDF file",
        default="output_with_outline.pdf",
    )
    args = parser.parse_args()
    print("============ args =============")
    print("args.html_path: ", args.html_path)
    print("args.pdf_path: ", args.pdf_path)
    print("args.summary_path: ", args.summary_path)
    print("args.output_path: ", args.output_path)
    if not os.path.exists(args.html_path):
        raise FileNotFoundError(f"{args.html_path} does not exist")
    if not os.path.exists(args.pdf_path):
        raise FileNotFoundError(f"{args.pdf_path} does not exist")
    if not os.path.exists(args.summary_path):
        raise FileNotFoundError(f"{args.summary_path} does not exist")
    reader = pypdf.PdfReader(args.pdf_path)
    writer = pypdf.PdfWriter()
    writer.append(reader)
    with open(args.summary_path) as f:
        md_text = f.read()
    section_root = parse_section_tree(md_text)
    html_root = None
    with open(args.html_path, "r", encoding="utf8") as f:
        data = f.read()
        html_root = lxml.html.fromstring(data)
    if html_root is None:
        raise ("[ERROR] html_root is None")
    add_outline(html_root, reader, writer, section_root)
    with open(args.output_path, "wb") as f:
        writer.write(f)
        print("[INFO] Write to {}".format(args.output_path))


def print_section_tree(root: Section):
    print(root)
    for child in root.children:
        print_section_tree(child)


def parse_section_tree(md_text: str):
    root = Section("root", "", 0, 0)
    bfs_map = {0: [root]}
    pattern = re.compile(r"( *)- ([^:\n]+)(?:: ([^\n]*))?\n?")
    tmp = None
    min_indent_num = 4
    for indent, name, value in pattern.findall(md_text):
        title = name.split("](")[0].split("[")[1]
        source_file = name.split("](")[1].split(")")[0]
        indent_num = len(indent)
        if indent_num > 0 and indent_num < min_indent_num:
            min_indent_num = indent_num
        depth = indent_num // min_indent_num
        if depth + 1 not in bfs_map:
            bfs_map[depth + 1] = []
        tmp = Section(title, source_file, depth + 1, 0)
        bfs_map[depth + 1].append(tmp)
        parent = bfs_map[depth][-1]
        tmp.set_parent(parent)
        tmp.index = len(parent.children)
        parent.add_children(tmp)
    return root


if __name__ == "__main__":
    main()
