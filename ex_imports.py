#!/data/data/com.termux/files/usr/bin/python
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import tree_sitter_python as tsp
from dh import get_files
from tree_sitter import Language, Parser

OUTPUT_DIR = Path("output")
parser = Parser()
parser.language = Language(tsp.language())
VALID = {
    "import_statement",
    "import_from_statement",
}


def process_file(fp):
    src = fp.read_bytes()
    tree = parser.parse(src)
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir()
    cwd = Path.cwd()
    outfile = Path(f"output/{cwd.name}_importz.py")
    all_imports = []
    files = get_files(cwd, extensions=[".py"])
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(process_file, f) for f in files]
        results.extend(future.result() for future in as_completed(futures))
    for imports in results:
        if imports:
            for k in imports:
                if not k.startswith("from .") and k not in all_imports:
                    all_imports.append(k)
    all_imports = sorted(set(all_imports))
    outfile.write_text("\n".join(all_imports), encoding="utf-8")
    print("done.")


if __name__ == "__main__":
    sys.exit(main())
