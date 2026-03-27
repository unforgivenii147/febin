#!/data/data/com.termux/files/usr/bin/python

import contextlib
import re

import requests
from dh import get_installed_packages
from packaging.version import Version
from termcolor import cprint


def get_latest_pkg_version(pkg_name):
    url = f"https://mirror-pypi.runflare.com/{pkg_name}/json"
    html = requests.get(url, timeout=10).text

    # Match file names in href links
    # Examples matched:
    #   wheel-0.46.3-py3-none-any.whl
    #   wheel-0.3.tar.gz
    #   wheel-0.2.zip
    #
    # Groups:
    # 1 = version (0.46.3, 0.3, etc.)
    wheel_pattern = re.compile(rf"{re.escape(pkg_name)}-([0-9][A-Za-z0-9\.\-_]*)\.(?:whl|tar\.gz|zip)", re.IGNORECASE)

    versions = []

    for match in wheel_pattern.finditer(html):
        version_str = match.group(1)
        with contextlib.suppress(BaseException):
            versions.append(Version(version_str))

    return max(versions) if versions else None


if __name__ == "__main__":
    installed = get_installed_packages()
    updatable: list = []
    for pkg, version in installed.items():
        latest_version = get_latest_pkg_version(pkg)
        if str(version).strip() != str(latest_version).strip():
            cprint(f"{pkg} : {version}", "green", end=" | ")
            cprint(f"{latest_version}", "cyan")
        else:
            cprint(f"{pkg} : {version} | {latest_version}", "white")
