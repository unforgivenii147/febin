#!/data/data/com.termux/files/usr/bin/python
import json
import pathlib
import sys

if len(sys.argv) != 2:
    print("Usage: python dedup_json.py <json_file>")
    sys.exit(1)
fname = sys.argv[1]
with pathlib.Path(fname).open(encoding="utf-8") as f:
    data = json.load(f)
if not isinstance(data, dict):
    msg = "JSON must be an object (key-value pairs)"
    raise ValueError(msg)
unique = dict(data.items())
with pathlib.Path(fname).open("w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"updated: {fname}")
