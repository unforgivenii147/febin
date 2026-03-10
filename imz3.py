#!/data/data/com.termux/files/usr/bin/env python
import ast
import os
from dh import get_pyfiles,STDLIB,get_installed_pkgs
from pathlib import Path
from typing import Set

def extract_imports_from_py(code: str, base_path: Path = None) -> Set[str]:
    results = set()
    try:
        tree = ast.parse(code)
    except Exception:
        return results
    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for a in node.names:
                mod = a.name.split(".", 1)[0]
                if not mod in STDLIB:
                    results.add(mod)

        elif isinstance(node, ast.ImportFrom):

            if node.level > 0:
                if base_path is not None:

                    module_str = "." * node.level
                    if node.module:
                        module_str += node.module

                    if is_local_module(base_path, module_str):
                        continue


                if node.module:
                    continue
                else:
                    continue

            if node.module:
                mod = node.module.split(".", 1)[0]
                if not mod in STDLIB:
                    results.add(mod)
    return results

def is_local_module(base_path: Path, module: str) -> bool:

    dots = len(module) - len(module.lstrip("."))
    mod = module.lstrip(".")

    parent = base_path.parent
    for _ in range(dots - 1):
        parent = parent.parent


    pkg_dir = parent / mod.replace(".", "/")
    if (pkg_dir / "__init__.py").exists():
        return True

    py_file = pkg_dir.with_suffix(".py")
    if py_file.exists():
        return True
    return False

def main():
    dir=Path.cwd()
    importz = []
    for file in get_pyfiles(dir):
        with open(file, "r") as f:
            contents = f.read()
            importz.append(extract_imports_from_py(contents))
    with open("importz.txt", "w") as fo:
        for im in importz:
            for k in im:
                fo.write(str(k)+'\n')

if __name__ == "__main__":
    main()
