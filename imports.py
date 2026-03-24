#!/data/data/com.termux/files/usr/bin/python
import ast
import importlib.metadata
import importlib.util
import numbers
from pathlib import Path
import sys

from dh import STDLIB, get_files, get_installed_pkgs


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for node_name in node.names:
            self.imports.add(node_name.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level == 0 and node.module:
            self.imports.add(node.module.split(".")[0])
        self.generic_visit(node)


def find_imports(start_path):
    all_imports = set()
    std_libs = STDLIB
    files = get_files(start_path, extensions=[".py"])
    for f in files:
        try:
            code = f.read_text(encoding="utf-8")
            tree = ast.parse(code)
            visitor = ImportVisitor()
            visitor.visit(tree)
            all_imports.update(visitor.imports)
        except (SyntaxError, UnicodeDecodeError):
            continue
    local_files = {p.stem for p in start_path.glob("*.py")}
    return sorted(
        [imp for imp in all_imports if imp not in std_libs and imp not in local_files and imp != "__future__"]
    )


def get_version(module_name):
    try:
        return importlib.metadata.version(module_name)
    except importlib.metadata.PackageNotFoundError:
        pass
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return "Not Installed"
        mod = importlib.import_module(module_name)
        for k, v in mod.__dict__.items():
            if ("version" in k.lower() or "ver" in k.lower()) and isinstance(v, (str, numbers.Number)):
                return str(v)
    except Exception:
        return "Not Installed(unknown)"
    return "Not Installed(NA)"


def main():
    root_dir = Path.cwd()
    sys.argv[1:]
    output_file = root_dir / "importz.txt"
    modules = find_imports(root_dir)
    results = []
    print(f"{'Module':<20} | {'Version':<15}")
    print("-" * 40)
    for mod in modules:
        if mod.startswith("_"):
            continue
        ver = get_version(mod)
        line = f"{mod:<20} | {ver:<15}"
        print(line)
        if "Not Installed" in ver:
            results.append(f"{mod}=={ver}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    cleaned = []
    with open(output_file, encoding="utf-8") as fin:
        lines = fin.readlines()
        for line in lines:
            cleaned.append(
                line.rstrip()
                .replace("Not Installed", "")
                .replace("==(NA)", "")
                .replace("==(unknown)", "")
                .replace("==", "")
            )
    pkgz = get_installed_pkgs()
    cleaned = [p for p in cleaned if p not in pkgz and not p.startswith("_")]
    if cleaned:
        with output_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(cleaned))
    elif output_file.exists():
        output_file.unlink()
        print(f"empty {output_file} removed")
    if output_file.stat().st_size < 2:
        output_file.unlink()


if __name__ == "__main__":
    main()
