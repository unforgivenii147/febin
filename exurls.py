import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def extract_links(url: str):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag.get("href").strip()
        if href:
            abs_url = urljoin(url, href)
            parsed = urlparse(abs_url)
            if parsed.scheme in {"http", "https"}:
                links.add(abs_url)
    return sorted(links)


def split_internal_external(base_url, links):
    base_domain = urlparse(base_url).netloc
    internal = []
    external = []
    for link in links:
        if urlparse(link).netloc == base_domain:
            internal.append(link)
        else:
            external.append(link)
    return internal, external


def save_links(name, links):
    path = Path(name)
    content = "\n".join(links)
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Extract and save all URLs from a webpage")
    parser.add_argument("url", nargs="?", help="Target URL")
    args = parser.parse_args()
    url = args.url or input("Enter URL: ").strip()
    if not url.startswith(("http://", "https://")):
        print(
            "Error: URL must start with http:// or https://",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        links = extract_links(url)
    except Exception as e:
        print(
            f"Failed to fetch or parse URL: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    internal, external = split_internal_external(url, links)
    if internal and external:
        save_links("internal.txt", internal)
        save_links("external.txt", external)
        save_links("all_links.txt", links)
        return
    save_links("all_links.txt", links)
    print(f"Total links     : {len(links)}: {internal} + {external}")


if __name__ == "__main__":
    main()
