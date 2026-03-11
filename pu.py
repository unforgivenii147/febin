#!/data/data/com.termux/files/usr/bin/env python
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from typing import Dict
from pip._internal.cli.main import main as pip_main


def display_packages(packages: Dict[str, str], title: str = "Packages"):
    if not packages:
        return
    print(f"\n{title}:")
    for pkg, version in sorted(packages.items()):
        print(f"  - {pkg} (version: {version})")
    print(f"\nTotal: {len(packages)} package(s)")


def find_matching_packages(pattern: str, packages: Dict[str, str]) -> Dict[str, str]:
    matches = {}
    pattern_lower = pattern.lower()
    for package_name, version in packages.items():
        if pattern_lower in package_name.lower():
            matches[package_name] = version
    return matches


def get_pkgs():
    pkgfile = Path("/sdcard/pip.freeze")
    pkgfile_content = pkgfile.read_text()
    packages = {}
    for line in pkgfile_content.splitlines():
        if "==" in line:
            name, version = line.split("==", 1)
            packages[name] = version
    return packages


def uninstall(packages: list[str]):
    args = ["uninstall", "-y", *packages]
    return pip_main(args)


def main():
    pat = sys.argv[1]
    pkgs = get_pkgs()
    matc = find_matching_packages(pat, pkgs)
    if not matc:
        print(f"No installed packages found containing '{pattern}' in their name.")
        sys.exit(0)
    display_packages(matc, "Packages to uninstall")
    uninstall(list(matc.keys()))


if __name__ == "__main__":
    main()
