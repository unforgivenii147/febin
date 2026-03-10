#!/data/data/com.termux/files/usr/bin/env python
from multiprocessing import Pool, cpu_count
import os
import subprocess

from rich.progress import Progress


def optimize_png(file_path):
    try:
        original_size = os.path.getsize(file_path)
        subprocess.run(
            ["oxipng", "-o", "max", "--quiet", "--strip", "safe", file_path, "--force"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        optimized_size = os.path.getsize(file_path)
        return original_size - optimized_size
    except subprocess.CalledProcessError:
        return 0


def find_png_files(directory):
    png_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".png"):
                png_files.append(os.path.join(root, file))
    return png_files


def main():
    current_dir = os.getcwd()
    png_files = find_png_files(current_dir)
    if not png_files:
        print("No PNG files found in the current directory or subdirectories.")
        return
    with Progress() as progress:
        task = progress.add_task("[cyan]Optimizing PNGs...", total=len(png_files))
        num_processes = min(cpu_count(), 8)
        with Pool(num_processes) as pool:
            for _ in pool.imap_unordered(optimize_png, png_files):
                progress.update(task, advance=1)
    total_space_freed = sum(optimize_png(fp) for fp in png_files) / (1024 * 1024)
    print(f"\n[bold green]Total space freed: {total_space_freed:.2f} MB[/bold green]")


if __name__ == "__main__":
    main()
