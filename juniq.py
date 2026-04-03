#!/data/data/com.termux/files/usr/bin/python
import json
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python dedup_json.py <json_file>")
    sys.exit(1)
fname = sys.argv[1]
with Path(fname).open(encoding="utf-8") as f:
    data = json.load(f)
if not isinstance(data, dict):
    msg = "JSON must be an object (key-value pairs)"
    raise ValueError(msg)
unique = dict(data.items())
with Path(fname).open("w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"updated: {fname}")
