import sys

from pathlib import Path

from pip._internal.cli.main import main as pip_main


def display_packages(
    packages: dict[str, str],
    title: str = "Packages",
):
    if not packages:
        return
    print(f"\n{title}:")
    for pkg, version in sorted(packages.items()):
        print(f"  - {pkg} (version: {version})")

    print(f"\nTotal: {len(packages)} package(s)")


def find_matching_packages(pattern: str, packages: dict[str, str]) -> dict[str, str]:
    pattern_lower = pattern.lower()
    return {
        package_name: version for package_name, version in packages.items() if pattern_lower in package_name.lower()
    }


def get_pkgs():
    pkgfile = Path("/sdcard/pip.freeze")

    pkgfile_content = pkgfile.read_text(encoding="utf-8")
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
        print(f"No installed packages found containing '{pat}' in their name.")
        sys.exit(0)
    display_packages(matc, "Packages to uninstall")
    uninstall(list(matc.keys()))


if __name__ == "__main__":
    main()
