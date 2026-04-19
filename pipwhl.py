#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
import os
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup  # Using BeautifulSoup for robust HTML parsing

# --- Configuration ---
# Set your local mirror URL here
LOCAL_MIRROR_URL = "https://mirror-pypi.runflare.com"
# --- End Configuration ---


def download_file(url, dest_folder="."):
    """Downloads a file from a URL to a specified directory."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        filepath = os.path.join(dest_folder, filename)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename}")
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None


def get_package_info_from_mirror(package_name):
    """
    Fetches package info from the local mirror and parses HTML to find wheel URLs.
    Returns the URL of the latest available wheel, or None if not found.
    """
    mirror_package_url = f"{LOCAL_MIRROR_URL}/{package_name}"
    print(f"Fetching package info from mirror: {mirror_package_url}")

    try:
        response = requests.get(mirror_package_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        wheel_urls = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # We are looking for links that point to .whl files
            if href.endswith(".whl"):
                # Construct the full URL if it's a relative path, though typically absolute
                if href.startswith("/"):
                    full_url = f"{LOCAL_MIRROR_URL}{href}"
                else:
                    full_url = href
                wheel_urls.append(full_url)

        if not wheel_urls:
            print(f"No .whl files found for {package_name} on the mirror.")
            return None

        # For simplicity, let's just take the first wheel URL found.
        # A more sophisticated approach would parse version numbers and pick the latest.
        # Example: We could use packaging.version.parse for version comparison.
        # For now, let's assume the order might be somewhat sensible or we just need any wheel.
        print(f"Found wheel URLs for {package_name}: {wheel_urls}")
        return wheel_urls[0]  # Return the first wheel URL found

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from mirror {mirror_package_url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while parsing mirror response: {e}")
        return None


def install_or_download(package_name):
    """Installs package if wheel is available from mirror, otherwise downloads source."""
    print(f"Checking for package: {package_name}")

    # First, try to get a wheel URL from the local mirror
    wheel_url = get_package_info_from_mirror(package_name)

    if wheel_url:
        print(f"Wheel found for {package_name} at {wheel_url}. Installing...")
        try:
            # Use pip to install directly from the wheel URL
            # We should also tell pip to use our mirror if possible, but direct URL install is more explicit.
            install_command = [sys.executable, "-m", "pip", "install", wheel_url]
            subprocess.run(install_command, check=True)
            print(f"Successfully installed {package_name} from wheel.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package_name} from {wheel_url}: {e}")
            # If installation fails, we don't have a fallback source URL from the mirror parsing,
            # so we can't easily download the source.
            print(f"Installation failed for {package_name}. Could not find a source archive fallback from mirror.")
    else:
        print(f"No wheel found for {package_name} on the mirror.")
        # Fallback: Try to find a source archive (tar.gz or zip) from the mirror
        # This part requires more sophisticated parsing of the mirror's HTML.
        # For now, let's assume if no wheel, we can't directly install or download source via this script's logic.
        # A more complete solution would fetch the HTML, parse for .tar.gz/.zip, and download.

        # --- Placeholder for downloading source archives ---
        # If you want to add source download:
        # 1. Modify get_package_info_from_mirror to also return source URLs if no wheel is found.
        # 2. Then call download_file(source_url) here.
        print(f"This script currently only handles wheel installations from the mirror.")
        print(
            f"If a source archive (.tar.gz or .zip) were available and desired, additional parsing logic would be needed."
        )
        # Example of how you might find source URLs if you modified the parser:
        # source_url = get_source_url_from_mirror(package_name) # hypothetical function
        # if source_url:
        #     print(f"Source archive found for {package_name}. Downloading...")
        #     download_file(source_url)
        # else:
        #     print(f"Could not find any installable or downloadable artifacts for {package_name} on the mirror.")
        # --- End Placeholder ---


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pip_wrapper.py <package_name1> [package_name2 ...]")
        sys.exit(1)

    packages_to_process = sys.argv[1:]

    # Ensure BeautifulSoup is installed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("The 'beautifulsoup4' library is required. Please install it: pip install beautifulsoup4")
        sys.exit(1)

    for pkg in packages_to_process:
        install_or_download(pkg)
