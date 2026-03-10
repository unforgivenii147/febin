#!/data/data/com.termux/files/usr/bin/env python
from datetime import datetime
import os
import sys
import time

from dh import get_installed_packages
from packaging.version import InvalidVersion, Version
import requests

try:
    from colorama import Fore, Style, init

    init()
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False

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


r"""
def extract_pkgver(text,pkgname,pkgver):
    lines=response.splitlines()
    lines=lines.reverse()
    target=''
    for i in range(0,len(lines)):
        cleaned=lines[i].strip().lstrip().rstrip()
        if cleaned=='</body>':
            target=lines[i+1]
            break
    if target and('.whl' in target or '.tar.gz' in target):
    text=text.strip()
    text=text.replace('<a href="','')
    indx=text.index('#')
    text=text[:indx]
    print(text)
        if pkg==0 and ver==0:
                     print('latest version')
                     return ver
                 else:
                     print('update available')
                     return ver
    if pkgname in text:
        if pkgver in text:
            return 0,0
    ver=re.match(r'[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}',text)
    if ver and ver > pkgver:
        return 0,ver
"""


def check_package_on_pypi(package_name: str, current_version: str) -> str | None:
    try:
        time.sleep(0.001)
        #        url = f"https://pypi.org/pypi/{package_name}/json"
        url = f"https://mirror-pypi.runflare.com/{package_name}/json"
        response = requests.get(url, timeout=5)
        print(response)
        if response.status_code == 200:
            print(type(response))
            print(type(response.json()))
            data = response.json()
            if data:
                print(data)
            else:
                print("no data")
            return data["info"]["version"]
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def save_requirements(
    updates: list[tuple[str, str, str]],
    filename: str = "requirements.txt",
):
    try:
        with open(filename, "w") as f:
            f.write(f"# Requirements generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Packages that have updates available\n\n")
            for (
                package,
                current,
                latest,
            ) in sorted(updates):
                f.write(f"{package}=={latest}  # was {current}\n")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving requirements file: {e}{Style.RESET_ALL}")
        return False


def load_existing_requirements(
    filename: str = "requirements.txt",
) -> dict[str, str]:
    requirements = {}
    if os.path.exists(filename):
        try:
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "==" in line:
                            package, version = line.split("==", 1)
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


def interactive_save_menu(
    updates: list[tuple[str, str, str]],
):
    if not updates:
        return
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}SAVE OPTIONS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
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
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        interactive_save_menu(updates)
    elif choice == "4":
        print(f"{Fore.YELLOW}Skipping save.{Style.RESET_ALL}")
    elif choice == "5" and existing_req:
        updated_count = 0
        try:
            with open("requirements.txt") as f:
                lines = f.readlines()
            update_map = {pkg: latest for pkg, _, latest in updates}
            new_lines = []
            for line in lines:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith("#"):
                    for pkg in update_map:
                        if pkg in line_stripped.lower() and ("==" in line_stripped or ">=" in line_stripped):
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
            with open("requirements.txt", "w") as f:
                f.writelines(new_lines)
            print(f"{Fore.GREEN}✅ Updated {updated_count} packages in requirements.txt{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error updating requirements.txt: {e}{Style.RESET_ALL}")
    elif choice == "6" and existing_req:
        print(f"\n{Fore.CYAN}Differences with existing requirements.txt:{Style.RESET_ALL}")
        updates_map = {pkg: (curr, latest) for pkg, curr, latest in updates}
        for pkg, (
            current,
            latest,
        ) in updates_map.items():
            if pkg in existing_req:
                if existing_req[pkg] != latest:
                    print(f"  {pkg:<30} {existing_req[pkg]} -> {latest} (update available)")
                else:
                    print(f"  {pkg:<30} {existing_req[pkg]} (already at latest)")
            else:
                print(f"  {pkg:<30} (new package) {current} -> {latest}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        interactive_save_menu(updates)
    else:
        print(f"{Fore.YELLOW}Invalid choice. Skipping save.{Style.RESET_ALL}")


def main():
    print(f"{Fore.CYAN}📦 Checking for package updates on PyPI...{Style.RESET_ALL}")
    print("(Results will appear as each package is checked)\n")
    installed = get_installed_packages()
    total_packages = len(installed)
    print(f"Processing {total_packages} packages:\n")
    updates_found = []
    not_found = []
    for i, (
        package,
        current_version,
    ) in enumerate(sorted(installed.items()), 1):
        progress = f"[{i:3d}/{total_packages:3d}]"
        latest_version = check_package_on_pypi(package, current_version)
        if latest_version is None:
            print(f"{progress} {package:<30} : {Fore.YELLOW}⚠️  not found on PyPI{Style.RESET_ALL}")
            not_found.append(package)
            continue
        try:
            if Version(current_version) < Version(latest_version):
                print(f"{progress} {package:<30} : {Fore.RED}📦 {current_version} -> {latest_version}{Style.RESET_ALL}")
                updates_found.append(
                    (
                        package,
                        current_version,
                        latest_version,
                    )
                )
            else:
                print(f"{progress} {package:<30} : {Fore.GREEN}✅ {current_version}{Style.RESET_ALL}")
        except InvalidVersion:
            if current_version < latest_version:
                print(f"{progress} {package:<30} : {Fore.RED}📦 {current_version} -> {latest_version}{Style.RESET_ALL}")
                updates_found.append(
                    (
                        package,
                        current_version,
                        latest_version,
                    )
                )
            else:
                print(f"{progress} {package:<30} : {Fore.GREEN}✅ {current_version}{Style.RESET_ALL}")
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
        print(f"\n{Fore.CYAN}💡 To upgrade all packages:{Style.RESET_ALL}")
        packages_to_upgrade = [p[0] for p in updates_found]
        print(f"   python -m pip install --upgrade {' '.join(packages_to_upgrade)}")
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
