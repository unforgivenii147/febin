#!/data/data/com.termux/files/usr/bin/python
"""
Fast script to clean requirements.txt using multiprocessing
Minimal output - only reports removed packages.
"""

import csv
import os
import site


def get_all_dist_info_dirs():
    """Quickly find all dist-info directories."""
    dist_info_dirs = []
    for site_dir in [
        *site.getsitepackages(),
        site.getusersitepackages(),
    ]:
        if os.path.exists(site_dir):
            dist_info_dirs.extend(
                os.path.join(site_dir, item) for item in os.listdir(site_dir) if item.endswith(".dist-info")
            )
    return dist_info_dirs


def check_pure(dist_info_path):
    record_file = os.path.join(dist_info_path, "RECORD")
    pkg_name = os.path.basename(dist_info_path).replace(".dist-info", "").split("-")[0].lower()
    sum = 0
    if os.path.exists(record_file):
        with open(record_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[-1] and isinstance(int(row[-1]), int):
                    sum += int(row[-1])
    if sum < 1024 * 1024:
        #        print(f"{pkg_name} : {sum}")
        return pkg_name
    else:
        return None


def get_pure():
    dist_info_dirs = get_all_dist_info_dirs()
    purz = []
    for ddir in dist_info_dirs:
        ispure = check_pure(ddir)
        if ispure:
            print(ispure)
            purz.append(ispure)
    with open("/sdcard/okpure", "w", encoding="utf-8") as f:
        f.writelines(f"{k}\n" for k in purz)
    print(len(purz))


if __name__ == "__main__":
    get_pure()
