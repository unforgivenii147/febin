#!/data/data/com.termux/files/usr/bin/env python
import argparse

from packaging import tags
import requests


def is_pure_python(requires_python):
    """Check if the package is pure Python based on its metadata."""
    return requires_python is None or all(
        tag.interpreter == "py" and tag.abi == "none" and tag.platform == "any" for tag in tags.sys_tags()
    )


def get_package_urls(pkg_name):
    """Fetch the download URLs for the package from PyPI."""
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch package info for {pkg_name}")
    data = response.json()
    releases = data.get("releases", {})
    latest_version = sorted(releases.keys(), reverse=True)[0]

    print(f"latest version : {latest_version}")

    release_files = releases[latest_version]
    return release_files, latest_version


def download_package(pkg_name):
    """Download the appropriate package file."""
    release_files, _version = get_package_urls(pkg_name)
    wheel_files = [f for f in release_files if f["packagetype"] == "bdist_wheel"]
    sdist_files = [f for f in release_files if f["packagetype"] == "sdist"]
    pure_python_wheel = None
    for wheel in wheel_files:
        if wheel["python_version"] == "py3" and "any" in wheel["filename"]:
            pure_python_wheel = wheel
            break
    if pure_python_wheel:
        download_url = pure_python_wheel["url"]
        filename = pure_python_wheel["filename"]
    else:
        download_url = sdist_files[0]["url"]
        filename = sdist_files[0]["filename"]
    print(f"Downloading {filename}...")
    response = requests.get(download_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to download {filename}")
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Downloaded {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a Python package from PyPI.")
    parser.add_argument(
        "pkg_name",
        help="Name of the package to download",
    )
    args = parser.parse_args()
    download_package(args.pkg_name)
