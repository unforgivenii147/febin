#!/data/data/com.termux/files/usr/bin/python
import sys


def clean_requirements(fname):
    with open(fname) as f:
        lines = f.readlines()
    packages = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pkg = line.split(">")[0].split("<")[0].split("=")[0].split("~")[0].strip()
        if pkg:
            packages.add(pkg)
    with open(fname, "w") as f:
        f.write("\n".join(sorted(packages)))
    print(f"Updated  {fname} with {len(packages)} unique packages.")


if __name__ == "__main__":
    fn = sys.argv[1]
    clean_requirements(fn)
