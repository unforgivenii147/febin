#!/data/data/com.termux/files/usr/bin/python
import operator
import os
from pathlib import Path
import regex as re
from packaging.version import Version

wheel_pattern = re.compile(r"^(?P<name>.+)-(?P<version>\d+(\.\d+)+).*\.metadata$")
files = [f for f in os.listdir(".") if (f.endswith((".metadata", ".whl")))]
print(f"{len(files)} files found.")
packages = {}
for f in files:
    matchz = wheel_pattern.match(f)
    if not matchz:
        continue
    name = matchz.group("name")
    version = Version(matchz.group("version"))
    if name not in packages:
        packages[name] = []
    packages[name].append((version, f))
for name, versions in packages.items():
    versions.sort(reverse=True, key=operator.itemgetter(0))
    latest = versions[0]
    old = versions[1:]
    for _v, filename in old:
        Path(filename).unlink()
        print(f"{filename} removed")
