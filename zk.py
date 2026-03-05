#!/data/data/com.termux/files/usr/bin/env python

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from sysconfig import get_path

CYAN = "\033[0;96m"
GREEN = "\033[0;92m"
YELLOW = "\033[1;93m"
RED = "\033[0;91m"
NC = "\033[0m"


def print_info(msg):
    print(f"{CYAN}{msg}{NC}")


def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")


def print_warning(msg):
    print(f"{YELLOW}{msg}{NC}")


def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")


def get_package_path(pkg_name):

    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {pkg_name}; print({pkg_name}.__file__)"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            path = result.stdout.strip()

            if path.endswith("__init__.py"):
                return str(Path(path).parent)

            if path.endswith(".py"):
                return path
            return path
    except Exception as e:
        print_error(f"Error importing {pkg_name}: {e}")
    return None


def is_single_file_module(pkg_path):

    return pkg_path.endswith(".py")


def is_package_directory(pkg_path):

    if not os.path.isdir(pkg_path):
        return False

    py_files = []
    for root, dirs, files in os.walk(pkg_path):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        py_files.extend([f for f in files if f.endswith(".py")])
    return len(py_files) > 1


def compile_to_bytecode(directory):

    try:
        subprocess.run([sys.executable, "-m", "compileall", "-b", "-q", directory], check=True, timeout=60)

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    os.remove(os.path.join(root, file))

        for root, dirs, files in os.walk(directory):
            if "__pycache__" in dirs:
                shutil.rmtree(os.path.join(root, "__pycache__"))
        return True
    except Exception as e:
        print_error(f"Compilation failed: {e}")
        return False


def find_so_files(directory):

    so_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".so"):
                so_files.append(os.path.join(root, file))
    return so_files


def create_zip(src_path, zip_path, pkg_name):

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isfile(src_path):
                arcname = os.path.basename(src_path)
                zf.write(src_path, arcname)
            else:
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(src_path))
                        zf.write(file_path, arcname)
        return True
    except Exception as e:
        print_error(f"Failed to create zip: {e}")
        return False


def get_site_packages():

    site_packages = get_path("purelib")
    if not site_packages:
        site_packages = os.path.join(
            os.path.dirname(sys.executable),
            f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages",
        )
    return site_packages


def main():
    parser = argparse.ArgumentParser(description="Convert Python packages to zipped format for efficient storage")
    parser.add_argument("package", help="Package name to zip")
    parser.add_argument(
        "-p", "--pyc", action="store_true", help="Store as compiled bytecode (.pyc) instead of source (.py)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    pkg_name = args.package
    use_pyc = args.pyc
    print_info(f"Processing package: {pkg_name}...")

    pkg_path = get_package_path(pkg_name)
    if not pkg_path:
        print_error(f"Package '{pkg_name}' not found!")
        sys.exit(1)
    if args.verbose:
        print_info(f"Package path: {pkg_path}")

    if is_single_file_module(pkg_path):
        print_warning(f"Skipping '{pkg_name}' - single file modules are not supported")
        sys.exit(0)

    if not is_package_directory(pkg_path):
        print_warning(f"Skipping '{pkg_name}' - not a multi-file package")
        sys.exit(0)
    site_packages = get_site_packages()
    zip_dir = site_packages
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, f"{pkg_name}.zip")

    if os.path.exists(zip_path):
        print_warning(f"{pkg_name}.zip already exists. Overwriting...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        print_warning("Step 1: Preparing package...")

        tmp_pkg_path = os.path.join(tmp_dir, os.path.basename(pkg_path))
        shutil.copytree(pkg_path, tmp_pkg_path)

        if use_pyc:
            print_warning("Compiling to bytecode...")
            if not compile_to_bytecode(tmp_pkg_path):
                sys.exit(1)

        so_files = find_so_files(tmp_pkg_path)
        if so_files:
            print_warning("C extensions detected. Keeping in site-packages...")

            for so_file in so_files:
                rel_path = os.path.relpath(so_file, tmp_pkg_path)
                if args.verbose:
                    print_info(f"Excluding: {rel_path}")
                os.remove(so_file)

        print_warning("Step 2: Creating zip archive...")
        if not create_zip(tmp_pkg_path, zip_path, pkg_name):
            sys.exit(1)

        original_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(pkg_path)
            for filename in filenames
        )

        compressed_size = os.path.getsize(zip_path)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        print_warning("Step 3: Creating loader stub...")
        loader_path = os.path.join(site_packages, f"{pkg_name}.py")
        loader_code = f"""import sys, os
ZIP_PATH = os.path.join(r'{zip_dir}', r'{pkg_name}.zip')
if ZIP_PATH not in sys.path: sys.path.insert(0, ZIP_PATH)
module = __import__(r'{pkg_name}')
sys.modules[r'{pkg_name}'] = module
"""
        try:
            with open(loader_path, "w") as f:
                f.write(loader_code)
        except Exception as e:
            print_error(f"Failed to create loader stub: {e}")
            sys.exit(1)

        try:
            shutil.rmtree(pkg_path)
        except Exception as e:
            print_error(f"Failed to remove original package: {e}")
            sys.exit(1)

    mode = ".pyc" if use_pyc else ".py"
    size_mb = compressed_size / (1024 * 1024)
    original_mb = original_size / (1024 * 1024)
    print_success(f"{pkg_name} zipped successfully")
    print_info(f"Mode: {mode}")
    print_info(f"Original size: {original_mb:.2f} MB")
    print_info(f"Compressed size: {size_mb:.2f} MB")
    print_info(f"Compression ratio: {compression_ratio:.1f}%")
    print_info(f"Saved to: {zip_path}")


if __name__ == "__main__":
    main()
