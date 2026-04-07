#!/data/data/com.termux/files/usr/bin/python
import argparse
import os
import shlex
import stat
from pathlib import Path


def collect_tree(root: Path):
    files = set()
    dirs = set()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
            for d in dirnames:
                rel = os.path.normpath(os.path.join(rel_dir, d))
                dirs.add(rel)
                for f in filenames:
                    rel = os.path.normpath(os.path.join(rel_dir, f))
                    files.add(rel)
    return files, dirs


def write_shell_copy(script_path: Path, src_root: Path, dst_root: Path, only_dirs, only_files):
    with script_path.open("w", encoding="utf-8") as sh:
        sh.write("#!/bin/sh\n")
        for d in sorted(only_dirs):
            dst_dir = dst_root / d
            sh.write(f"mkdir -p {shlex.quote(str(dst_dir))}\n")
        for f in sorted(only_files):
            dst_file = dst_root / f
            src_file = src_root / f
            parent = dst_file.parent
            sh.write(
                f"mkdir -p {shlex.quote(str(parent))} && cp -a {shlex.quote(str(src_file))} {shlex.quote(str(dst_file))}\n"
            )
    st = script_path.stat()
    script_path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("first")
    p.add_argument("second")
    p.add_argument("--out-dir", default=".")
    args = p.parse_args()
    first = Path(args.first).resolve()
    second = Path(args.second).resolve()
    outdir = Path(args.out_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    f_files, f_dirs = collect_tree(first)
    s_files, s_dirs = collect_tree(second)
    only_files_first = f_files - s_files
    only_files_second = s_files - f_files
    only_dirs_first = f_dirs - s_dirs
    only_dirs_second = s_dirs - f_dirs
    only_in_first_sh = outdir / "only_in_first.sh"
    only_in_second_sh = outdir / "only_in_second.sh"
    common_txt = outdir / "common.txt"
    write_shell_copy(only_in_first_sh, first, second, only_dirs_first, only_files_first)
    write_shell_copy(only_in_second_sh, second, first, only_dirs_second, only_files_second)
    commons = sorted((f_files & s_files) | (f_dirs & s_dirs))
    with common_txt.open("w", encoding="utf-8") as cf:
        for c in commons:
            cf.write(c + "\n")
    print("Wrote:", only_in_first_sh, only_in_second_sh, common_txt)


if __name__ == "__main__":
    main()
