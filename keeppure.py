#!/data/data/com.termux/files/usr/bin/env python
"""
Fast script to clean requirements.txt using multiprocessing
Minimal output - only reports removed packages
"""

import csv
from multiprocess import Pool, cpu_count
import os
import site


def get_all_dist_info_dirs():
    """Quickly find all dist-info directories"""
    dist_info_dirs = []
    for site_dir in [
        *site.getsitepackages(),
        site.getusersitepackages(),
    ]:
        if os.path.exists(site_dir):
            for item in os.listdir(site_dir):
                if item.endswith(".dist-info"):
                    dist_info_dirs.append(os.path.join(site_dir, item))
    return dist_info_dirs


def check_package_binary(dist_info_path):
    """Check a single package for binary files (for multiprocessing)"""
    record_file = os.path.join(dist_info_path, "RECORD")
    pkg_name = os.path.basename(dist_info_path).replace(".dist-info", "").split("-")[0].lower()
    if os.path.exists(record_file):
        try:
            with open(record_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and any(
                        row[0].endswith(ext)
                        for ext in [
                            ".so",
                            ".pyd",
                        ]
                    ):
                        return pkg_name
        except:
            pass
    return None


def get_binary_packages_parallel():
    """Get all binary packages using multiprocessing"""
    dist_info_dirs = get_all_dist_info_dirs()
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(check_package_binary, dist_info_dirs)
    return {pkg for pkg in results if pkg}


def clean_requirements_txt(
    requirements_file="requirements.txt",
):
    """Fast cleanup of requirements.txt - minimal output"""
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found")
        return
    binary_packages = get_binary_packages_parallel()
    with open("/sdcard/binary_pkgs", "w") as fbin:
        fbin.write("\n".join(binary_packages))
        print("binary_pkgs created.")
    with open(requirements_file) as f:
        lines = [line.rstrip() for line in f]
    comments = [line for line in lines if line.startswith("#")]
    requirements = [line for line in lines if line and not line.startswith("#")]
    pure_python = []
    removed = []
    for req in requirements:
        pkg_name = req.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
        if pkg_name in binary_packages:
            removed.append(req)
        else:
            pure_python.append(req)
    with open(requirements_file, "w") as f:
        for comment in comments:
            f.write(f"{comment}\n")
        for pkg in sorted(pure_python):
            f.write(f"{pkg}\n")
    if removed:
        print(f"\n🗑️  Removed binary packages ({len(removed)}):")
        for pkg in sorted(removed):
            print(f"   - {pkg}")
    else:
        print("✅ No binary packages found in requirements.txt")


if __name__ == "__main__":
    import sys

    req_file = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    clean_requirements_txt(req_file)
