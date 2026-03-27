#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import pathlib
import subprocess


if len(sys.argv) != 2:
    print("Usage: python extract_subtitles.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_dir = "subtitles"

if not pathlib.Path(output_dir).exists():
    pathlib.Path(output_dir).mkdir(parents=True)
command = f"ffmpeg -i {input_file} -map_metadata:s:0 {output_dir}/subtitles.srt"
subprocess.run(command, check=False, shell=True)
print("Subtitles extracted")
