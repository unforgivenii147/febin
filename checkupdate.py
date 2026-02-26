#!/usr/bin/env python3
"""
Enhanced script with colored output for checking package updates.
Saves updatable packages to requirements.txt in current directory.
Install colorama first: pip install colorama
"""

import sys
import json
import requests
from packaging.version import Version, InvalidVersion
from typing import Dict, Optional, List, Tuple
import time
import os
from datetime import datetime

try:
    from colorama import init, Fore, Style

    init()  # Initialize colorama
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False

    # Create dummy color constants
    class Fore:
        GREEN = ""
        YELLOW = ""
        RED = ""
        CYAN = ""
        MAGENTA = ""
        RESET = ""

    class Style:
        BRIGHT = ""
        RESET_ALL = ""


def get_installed_packages() -> Dict[str, str]:
    """Get installed packages and their versions."""
    try:
        import pkg_resources

        installed_packages = {}
        for dist in pkg_resources.working_set:
            installed_packages[dist.project_name.lower()] = dist.version
        return installed_packages
    except Exception as e:
        print(f"Error getting installed packages: {e}")
        sys.exit(1)


def check_package_on_pypi(package_name: str, current_version: str) -> Optional[str]:
    """Check the latest version of a package on PyPI."""
    try:
        time.sleep(0.01)  # Be nice to PyPI

        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
        else:
            return None

    except requests.exceptions.RequestException:
        return None


def save_requirements(updates: List[Tuple[str, str, str]], filename: str = "requirements.txt"):
    """Save updatable packages to requirements.txt with latest versions."""
    try:
        with open(filename, "w") as f:
            f.write(f"# Requirements generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Packages that have updates available\n\n")

            for package, current, latest in sorted(updates):
                f.write(f"{package}=={latest}  # was {current}\n")

        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving requirements file: {e}{Style.RESET_ALL}")
        return False


def load_existing_requirements(filename: str = "requirements.txt") -> Dict[str, str]:
    """Load existing requirements file to compare."""
    requirements = {}
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith("#"):
                        # Handle different formats: package==version, package>=version, etc.
                        if "==" in line:
                            package, version = line.split("==", 1)
                            # Remove any trailing comments
                            if " #" in version:
                                version = version.split(" #", 1)[0]
                            requirements[package.strip().lower()] = version.strip()
                        elif ">=" in line:
                            package, version = line.split(">=", 1)
                            if " #" in version:
                                version = version.split(" #", 1)[0]
                            requirements[package.strip().lower()] = version.strip()
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not read existing {filename}: {e}{Style.RESET_ALL}")
    return requirements


def interactive_save_menu(updates: List[Tuple[str, str, str]]):
    """Interactive menu for saving requirements."""
    if not updates:
        return

    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}SAVE OPTIONS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

    # Check if requirements.txt already exists
    existing_req = load_existing_requirements()

    print("\nWhat would you like to do?")
    print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} Save all updatable packages to requirements.txt (overwrite)")
    print(f"  {Fore.GREEN}[2]{Style.RESET_ALL} Save to a different filename")
    print(f"  {Fore.GREEN}[3]{Style.RESET_ALL} Show packages that would be saved (preview)")
    print(f"  {Fore.GREEN}[4]{Style.RESET_ALL} Skip saving")

    if existing_req:
        print(f"  {Fore.GREEN}[5]{Style.RESET_ALL} Update existing requirements.txt (keep non-updatable packages)")
        print(f"  {Fore.GREEN}[6]{Style.RESET_ALL} Show differences with existing requirements.txt")

    choice = input(f"\n{Fore.CYAN}Enter your choice (1-{6 if existing_req else 4}): {Style.RESET_ALL}").strip()

    if choice == "1":
        if save_requirements(updates):
            print(f"{Fore.GREEN}✅ Saved {len(updates)} packages to requirements.txt{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to save requirements.txt{Style.RESET_ALL}")

    elif choice == "2":
        filename = input("Enter filename (e.g., updates-20240226.txt): ").strip()
        if not filename:
            filename = f"updates-{datetime.now().strftime('%Y%m%d')}.txt"
        if save_requirements(updates, filename):
            print(f"{Fore.GREEN}✅ Saved {len(updates)} packages to {filename}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to save {filename}{Style.RESET_ALL}")

    elif choice == "3":
        print(f"\n{Fore.CYAN}Packages that would be saved:{Style.RESET_ALL}")
        for package, current, latest in sorted(updates):
            print(f"  {package:<30} {current} -> {latest}")
        print(f"\nTotal: {len(updates)} packages")

        # Ask again after preview
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        interactive_save_menu(updates)  # Recursive call

    elif choice == "4":
        print(f"{Fore.YELLOW}Skipping save.{Style.RESET_ALL}")

    elif choice == "5" and existing_req:
        # Update existing requirements
        updated_count = 0
        try:
            # Read existing requirements
            with open("requirements.txt", "r") as f:
                lines = f.readlines()

            # Create a map of updates
            update_map = {pkg: latest for pkg, _, latest in updates}

            # Update lines
            new_lines = []
            for line in lines:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith("#"):
                    # Check each package in the line
                    for pkg in update_map:
                        if pkg in line_stripped.lower() and ("==" in line_stripped or ">=" in line_stripped):
                            # Update version
                            if "==" in line_stripped:
                                package_name = line_stripped.split("==")[0].strip()
                                new_lines.append(f"{package_name}=={update_map[pkg]}  # updated from {line_stripped}\n")
                            elif ">=" in line_stripped:
                                package_name = line_stripped.split(">=")[0].strip()
                                new_lines.append(f"{package_name}>={update_map[pkg]}  # updated from {line_stripped}\n")
                            updated_count += 1
                            break
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            # Write back
            with open("requirements.txt", "w") as f:
                f.writelines(new_lines)

            print(f"{Fore.GREEN}✅ Updated {updated_count} packages in requirements.txt{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error updating requirements.txt: {e}{Style.RESET_ALL}")

    elif choice == "6" and existing_req:
        # Show differences
        print(f"\n{Fore.CYAN}Differences with existing requirements.txt:{Style.RESET_ALL}")

        updates_map = {pkg: (curr, latest) for pkg, curr, latest in updates}

        for pkg, (current, latest) in updates_map.items():
            if pkg in existing_req:
                if existing_req[pkg] != latest:
                    print(f"  {pkg:<30} {existing_req[pkg]} -> {latest} (update available)")
                else:
                    print(f"  {pkg:<30} {existing_req[pkg]} (already at latest)")
            else:
                print(f"  {pkg:<30} (new package) {current} -> {latest}")

        # Ask again after preview
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        interactive_save_menu(updates)

    else:
        print(f"{Fore.YELLOW}Invalid choice. Skipping save.{Style.RESET_ALL}")


def main():
    """Main function with colored output and save functionality."""

    print(f"{Fore.CYAN}📦 Checking for package updates on PyPI...{Style.RESET_ALL}")
    print("(Results will appear as each package is checked)\n")

    # Get installed packages
    installed = get_installed_packages()
    total_packages = len(installed)

    print(f"Processing {total_packages} packages:\n")

    updates_found = []
    not_found = []

    for i, (package, current_version) in enumerate(sorted(installed.items()), 1):
        # Show progress
        progress = f"[{i:3d}/{total_packages:3d}]"

        # Check PyPI
        latest_version = check_package_on_pypi(package, current_version)

        if latest_version is None:
            print(f"{progress} {package:<30} : {Fore.YELLOW}⚠️  not found on PyPI{Style.RESET_ALL}")
            not_found.append(package)
            continue

        # Compare versions
        try:
            if Version(current_version) < Version(latest_version):
                print(f"{progress} {package:<30} : {Fore.RED}📦 {current_version} -> {latest_version}{Style.RESET_ALL}")
                updates_found.append((package, current_version, latest_version))
            else:
                print(f"{progress} {package:<30} : {Fore.GREEN}✅ {current_version}{Style.RESET_ALL}")
        except InvalidVersion:
            # Fall back to string comparison
            if current_version < latest_version:
                print(f"{progress} {package:<30} : {Fore.RED}📦 {current_version} -> {latest_version}{Style.RESET_ALL}")
                updates_found.append((package, current_version, latest_version))
            else:
                print(f"{progress} {package:<30} : {Fore.GREEN}✅ {current_version}{Style.RESET_ALL}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_updates = len(updates_found)
    total_up_to_date = total_packages - total_updates - len(not_found)

    print(f"Total packages checked: {total_packages}")
    print(f"{Fore.GREEN}✅ Up to date: {total_up_to_date}{Style.RESET_ALL}")
    print(f"{Fore.RED}📦 Updates available: {total_updates}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  Not found on PyPI: {len(not_found)}{Style.RESET_ALL}")

    if updates_found:
        print(f"\n{Fore.RED}Packages to upgrade:{Style.RESET_ALL}")
        for package, current, latest in sorted(updates_found):
            print(f"  {package:<30} {current} -> {latest}")

        # Show upgrade command
        print(f"\n{Fore.CYAN}💡 To upgrade all packages:{Style.RESET_ALL}")
        packages_to_upgrade = [p[0] for p in updates_found]
        print(f"   python -m pip install --upgrade {' '.join(packages_to_upgrade)}")

        # Interactive save menu
        interactive_save_menu(updates_found)

    else:
        print(f"\n{Fore.GREEN}✅ All packages are up to date!{Style.RESET_ALL}")

    if not_found:
        print(f"\n{Fore.YELLOW}⚠️  Packages not found on PyPI:{Style.RESET_ALL}")
        for package in sorted(not_found):
            print(f"  {package}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}❌ Check interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)
