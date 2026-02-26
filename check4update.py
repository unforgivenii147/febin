#!/usr/bin/env python3
"""
Script to show available updates for Python packages in current virtual environment.
"""

import subprocess
import sys
import json
from packaging.version import Version, InvalidVersion
from typing import Dict, List, Tuple


def get_installed_packages() -> Dict[str, str]:
    """Get installed packages and their versions."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True, check=True
        )
        packages = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in packages}
    except subprocess.CalledProcessError as e:
        print(f"Error getting installed packages: {e}")
        sys.exit(1)


def check_outdated_packages() -> List[Tuple[str, str, str]]:
    """Check for outdated packages using pip."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )
        outdated = json.loads(result.stdout)
        return [(pkg["name"], pkg["version"], pkg["latest_version"]) for pkg in outdated]
    except subprocess.CalledProcessError as e:
        print(f"Error checking outdated packages: {e}")
        sys.exit(1)


def format_table(data: List[Tuple], headers: List[str]) -> str:
    """Format data as a table."""
    if not data:
        return "No data to display."

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Create separator line
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    # Format headers
    header_row = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"

    # Format data rows
    rows = []
    for row in data:
        row_str = "| " + " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + " |"
        rows.append(row_str)

    # Combine everything
    table = [separator, header_row, separator] + rows + [separator]
    return "\n".join(table)


def is_venv() -> bool:
    """Check if running in a virtual environment."""
    return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)


def main():
    """Main function to display package updates."""

    # Check if running in virtual environment
    if not is_venv():
        print("⚠️  Warning: Not running in a virtual environment!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            print("Exiting.")
            return

    print("📦 Checking for package updates...")

    # Get installed packages
    installed = get_installed_packages()
    total_packages = len(installed)
    print(f"Total installed packages: {total_packages}")

    # Check for outdated packages
    outdated = check_outdated_packages()

    if not outdated:
        print("\n✅ All packages are up to date!")
        return

    # Display outdated packages
    print(f"\n📋 Found {len(outdated)} outdated package(s):\n")

    # Prepare data for table
    table_data = [(name, current, latest) for name, current, latest in outdated]
    headers = ["Package", "Current", "Latest"]

    print(format_table(table_data, headers))

    # Optional: Show upgrade command
    print("\n💡 To upgrade all packages, run:")
    print(f"   {sys.executable} -m pip install --upgrade " + " ".join([pkg[0] for pkg in outdated]))

    print("\n💡 To upgrade a specific package, run:")
    print(f"   {sys.executable} -m pip install --upgrade <package-name>")


if __name__ == "__main__":
    main()
