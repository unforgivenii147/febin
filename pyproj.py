#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys


def create_python_project(pkg_name):

    current_dir = Path.cwd()

    src_dir = current_dir / "src"
    pkg_dir = src_dir / pkg_name

    pkg_dir.mkdir(parents=True, exist_ok=True)

    init_file = pkg_dir / "__init__.py"
    init_file.touch()

    readme_file = current_dir / "README.md"
    readme_content = f"""# {pkg_name}
## Description
A Python package named {pkg_name}.
## Installation
```bash
pip install -e .
```
Usage
```python
import {pkg_name}
```
"""
    readme_file.write_text(readme_content)

    pyproject_file = current_dir / "pyproject.toml"
    pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
[project]
name = "{pkg_name}"
version = "1.4.7"
description = "A Python package named {pkg_name}"
readme = "README.md"
authors = [
{{name = "Isaac Onagh", email = "mkalafsaz@gmail.com"}},
]
classifiers = [
"Programming Language :: Python :: 3",
"Operating System :: OS Independent",
]
requires-python = ">=3.9"
[tool.setuptools.packages.find]
where = ["src"]
"""
    pyproject_file.write_text(pyproject_content)
    setuppy_file = current_dir / "setup.py"
    setuppy_content = """from setuptools import setup
setup()
"""
    setuppy_file.write_text(setuppy_content, encoding="utf-8")
    setupcfg_file = current_dir / "setup.cfg"
    setupcfg_content = f"""[metadata]
name = {pkg_name}
version = 1.4.7
author = unforgivenii147
author_email = adnanonagh@gmail.com
platforms = any
classifiers =
    Development Status :: 4 - Beta
    Programming Language :: Python
[options]
zip_safe = False
packages = find_namespace:
include_package_data = True
package_dir =
    =src
[options.packages.find]
where = src
exclude =
    tests
[options.entry_points]
[flake8]
max_line_length = 120
extend_ignore = E203, W503
exclude =
    .tox
    build
    dist
    .eggs
    docs/conf.py
"""
    setupcfg_file.write_text(setupcfg_content, encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        sys.exit * (1)
    pkg = sys.argv[1]
    create_python_project(pkg)


if __name__ == "__main__":
    main()
