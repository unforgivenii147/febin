#!/data/data/com.termux/files/usr/bin/python
import subprocess

import regex as re
import requests
from bs4 import BeautifulSoup
from packaging.version import Version

MIRROR_URL = "https://mirror-pypi.runflare.com"


def extract_latest(pkg_name):
    wheel_pattern = re.compile(rf"{re.escape(pkg_name)}-([0-9][A-Za-z0-9\.\-_]*)(\.whl|\.tar\.gz)", re.IGNORECASE)
    versions = []
    url = f"{MIRROR_URL}/{package_name}/json"
    response = requests.get(url)
    response.raise_for_status()
    for line in response.content.splitlines():
        match = wheel_pattern.search(line)
        if match:
            versions.append(Version(match.group(1)))
    return max(versions) if versions else None


def get_latest_version_from_mirror(package_name):
    url = f"{MIRROR_URL}/{package_name}/json"
    response = requests.get(url)
    response.raise_for_status()
    print(response)
    soup = BeautifulSoup(html_content, "html.parser")
    links = soup.find_all("a")
    latest_version = None
    for link in links:
        href = link.get("href")
        if href and (".whl" in href or ".tar.gz" in href):
            match = re.search(r"wheel-([\d.]+)\.tar\.gz", href) or re.search(
                r"wheel-([\d.]+)-py\d+-none-any\.whl", href
            )
            if match:
                version = match.group(1)
                if latest_version is None or version > latest_version:
                    latest_version = version
    return latest_version


def get_installed_version(package_name):
    try:
        result = subprocess.run(["pip", "show", package_name], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":")[1].strip()
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error getting installed version: {e}")
        return None


def check_for_updates(package_name, mirror_url="https://mirror-pypi.runflare.com"):
    latest_version = get_latest_version_from_mirror(package_name, mirror_url)
    installed_version = get_installed_version(package_name)
    if latest_version is None or installed_version is None:
        print(f"Could not determine version for {package_name}")
        return False
    if latest_version > installed_version:
        print(f"Update available for {package_name}: {installed_version} -> {latest_version}")
        return True
    print(f"{package_name} is up to date: {installed_version}")
    return False


if __name__ == "__main__":
    package_to_check = "wheel"
    check_for_updates(package_to_check)
