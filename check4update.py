#!/data/data/com.termux/files/usr/bin/python

import regex as re
import requests
from dh import get_installed_packages
from packaging.version import Version

PIPY_URL = "https://pypi.org"


def get_latest_version(pkg_name):
    wheel_pattern = re.compile(
        rf"{re.escape(pkg_name)}-([0-9][A-Za-z0-9\.\-_]*)(\.whl|\.tar\.gz|\.zip)",
        re.IGNORECASE,
    )
    versions = []
    url = f"{PIPY_URL}/{pkg_name}/json"
    try:
        response = requests.get(url, timeout=50)
        response.raise_for_status()
        for line in response.content.splitlines():
            match = wheel_pattern.search(line)
            if match:
                versions.append(Version(match.group(1)))
        return max(versions) if versions else None
    except:
        return None


def check_for_updates(package_name, ver):
    latest_version = get_latest_version(package_name)
    installed_version = Version(ver)
    if latest_version is None or installed_version is None:
        print(f"Could not determine version for {package_name}")
        return False
    if latest_version > installed_version:
        print(f"Update available for {package_name}: {installed_version} -> {latest_version}")
        return True
    print(f"{package_name} is up to date: {installed_version}")
    return False


if __name__ == "__main__":
    installed = get_installed_packages()
    for pkg, ver in installed.items():
        check_for_updates(pkg, ver)
