#!/data/data/com.termux/files/usr/bin/python
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from pathlib import Path
import sys

from dh import (
    STDLIB,
    get_files,
    get_installed_pkgs,
)
from tree_sitter import Language, Parser
import tree_sitter_python as tsp

parser = Parser()
parser.language = Language(tsp.language())
VALID = {
    "import_statement",
    "import_from_statement",
}


def extract_file(src: bytes, tree):
    root = tree.root_node
    chunks = []
    for node in root.children:
        if node.type in VALID:
            chunks.append(src[node.start_byte : node.end_byte].decode())
    return chunks


def process_file(fp):
    src = fp.read_bytes()
    tree = parser.parse(src)
    return extract_file(src, tree)


def main():
    outfile = Path("importz.txt")
    all_imports = []
    root_dir = Path.cwd()
    files = get_files(root_dir, extensions=[".py"])
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(process_file, f) for f in files]
        for future in as_completed(futures):
            results.append(future.result())
    for imports in results:
        if imports:
            for k in imports:
                if k not in all_imports:
                    all_imports.append(k)
    all_imports = sorted(set(all_imports))
    outfile.write_text("\n".join(all_imports))
    content = outfile.read_text(encoding="utf-8")
    impoz = []
    for line in content.splitlines():
        line = line.lower()
        if line.startswith("import "):
            line = line.replace("import ", "")
            if " as " in line:
                indx = line.index(" as ")
                line = line[:indx]
            if "." in line:
                indx = line.index(".")
                line = line[:indx]
            if line not in impoz and not line.startswith("_"):
                impoz.append(line + "\n")
        elif line.startswith("from "):
            line = line.replace("from ", "")
            if line.startswith("."):
                continue
            if " as " in line:
                indx = line.index(" as ")
                line = line[:indx]
            if "." in line:
                indx = line.index(".")
                line = line[:indx]
            if " import" in line:
                indx = line.index(" import")
                line = line[:indx]
            if line not in impoz and not line.startswith("_"):
                impoz.append(line + "\n")
    impoz = sorted(set(impoz))
    stdlib_plus_installed = list(STDLIB)
    inpkg = [p.replace("-", "_").lower() for p in get_installed_pkgs()]
    stdlib_plus_installed.extend(inpkg)
    filterd = []
    for rq in impoz:
        if rq.strip() not in stdlib_plus_installed:
            print(rq.strip())
            filterd.append(rq)
    outfile.write_text("\n".join(filterd))


if __name__ == "__main__":
    sys.exit(main())
