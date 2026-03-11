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
    for _root, dirs, files in os.walk(pkg_path):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        py_files.extend([f for f in files if f.endswith(".py")])
    return len(py_files) > 1


def compile_to_bytecode(directory, opt_level=2):
    try:
        opt_flag = []
        if opt_level == 1:
            opt_flag = ["-O"]
        elif opt_level == 2:
            opt_flag = ["-OO"]
        subprocess.run([sys.executable, *opt_flag, "-m", "compileall", "-b", "-q", directory], check=True, timeout=60)
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


def have_so_files(directory) -> bool:

    for _root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".so"):
                return True
    return False


def create_zip(src_path, zip_path, pkg_name):

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isfile(src_path):
                arcname = os.path.basename(src_path)
                zf.write(src_path, arcname)
            else:
                for root, _dirs, files in os.walk(src_path):
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


def check_import(pkg_name, backup_path=None):
    print_info("Checking import...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {pkg_name}; print('OK')"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and "OK" in result.stdout:
            print_success(f"Import check passed for {pkg_name}")
            return True
        else:
            print_error(f"Import check failed for {pkg_name}")
            print_error(f"Error: {result.stderr}")

            if backup_path and os.path.exists(backup_path):
                print_warning("Rolling back to original package...")
                site_packages = get_site_packages()
                pkg_path = os.path.join(site_packages, os.path.basename(backup_path))
                try:
                    shutil.rmtree(pkg_path, ignore_errors=True)
                    shutil.copytree(backup_path, pkg_path)
                    print_success("Rollback completed successfully")
                except Exception as e:
                    print_error(f"Rollback failed: {e}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"Import check timed out for {pkg_name}")
        return False
    except Exception as e:
        print_error(f"Import check error: {e}")
        return False


def zip_package(pkg_name, use_pyc=False, opt_level=2, verbose=True):

    print_info(f"Processing package: {pkg_name}...")
    pkg_path = get_package_path(pkg_name)
    if not pkg_path:
        print_error(f"Package '{pkg_name}' not found!")
        return False
    if verbose:
        print_info(f"Package path: {pkg_path}")
    if have_so_file(pkg_path):
        return None
    if is_single_file_module(pkg_path):
        print_warning(f"Skipping '{pkg_name}' - single file modules are not supported")
        return False
    if not is_package_directory(pkg_path):
        print_warning(f"Skipping '{pkg_name}' - not a multi-file package")
        return False
    site_packages = get_site_packages()
    zip_dir = site_packages
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, f"{pkg_name}.zip")
    if os.path.exists(zip_path):
        print_warning(f"{pkg_name}.zip already exists. Overwriting...")

    backup_path = None
    with tempfile.TemporaryDirectory() as backup_tmp:
        try:
            backup_path = os.path.join(backup_tmp, pkg_name)
            shutil.copytree(pkg_path, backup_path)
            original_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(pkg_path)
                for filename in filenames
            )
            with tempfile.TemporaryDirectory() as tmp_dir:
                print_warning("Step 1: Preparing package...")
                tmp_pkg_path = os.path.join(tmp_dir, os.path.basename(pkg_path))
                shutil.copytree(pkg_path, tmp_pkg_path)
                if use_pyc:
                    print_warning(f"Compiling to bytecode (optimization level: {opt_level})...")
                    if not compile_to_bytecode(tmp_pkg_path, opt_level):
                        print_error("Compilation failed!")
                        return False
                #                so_files = find_so_files(tmp_pkg_path)
                #                if so_files:
                #                    print_warning("C extensions detected. Keeping in site-packages...")
                #                    return
                #                    for so_file in so_files:
                #                        rel_path = os.path.relpath(so_file, tmp_pkg_path)
                #                        if verbose:
                #                            print_info(f"Excluding: {rel_path}")
                #                        os.remove(so_file)
                #                print_warning("Step 2: Creating zip archive...")
                #                if not create_zip(tmp_pkg_path, zip_path, pkg_name):
                #                    return Faize(zip_path)
                #                compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                #                print_warning("Step 3: Creating loader stub...")
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
                    return False

                try:
                    shutil.rmtree(pkg_path)
                except Exception as e:
                    print_error(f"Failed to remove original package: {e}")
                    return False

                print_warning("Step 4: Verifying import...")
                if not check_import(pkg_name, backup_path):
                    print_error("Import verification failed! Rolling back...")
                    try:
                        os.remove(loader_path)
                        os.remove(zip_path)
                        shutil.copytree(backup_path, pkg_path)
                        print_success("Rollback completed successfully")
                    except Exception as e:
                        print_error(f"Rollback failed: {e}")
                    return False

                mode = ".pyc" if use_pyc else ".py"
                size_mb = compressed_size / (1024 * 1024)
                original_mb = original_size / (1024 * 1024)
                print_success(f"{pkg_name} zipped successfully")
                print_info(f"Mode: {mode}")
                print_info(f"Original size: {original_mb:.2f} MB")
                print_info(f"Compressed size: {size_mb:.2f} MB")
                #                print_info(f"Compression ratio: {compression_ratio:.1f}%")
                print_info(f"Saved to: {zip_path}")
                return True
        except Exception as e:
            print_error(f"Error: {e}")
            return False


def unzip_package(pkg_name, verbose=False):

    print_info(f"Unzipping package: {pkg_name}...")
    site_packages = get_site_packages()
    zip_path = os.path.join(site_packages, f"{pkg_name}.zip")
    loader_path = os.path.join(site_packages, f"{pkg_name}.py")
    if not os.path.exists(zip_path):
        print_error(f"Zip file not found: {zip_path}")
        return False
    pkg_path = os.path.join(site_packages, pkg_name)
    try:
        print_warning("Step 1: Extracting zip archive...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(site_packages)
        if verbose:
            print_info(f"Extracted to: {pkg_path}")
        print_warning("Step 2: Cleaning up...")
        if os.path.exists(loader_path):
            os.remove(loader_path)
            if verbose:
                print_info(f"Removed loader: {loader_path}")
        os.remove(zip_path)
        if verbose:
            print_info(f"Removed zip: {zip_path}")
        print_warning("Step 3: Verifying import...")
        if not check_import(pkg_name):
            print_warning("Import verification passed")
        print_success(f"{pkg_name} unzipped successfully")
        print_info(f"Package restored to: {pkg_path}")
        return True
    except Exception as e:
        print_error(f"Unzip failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Zip/Unzip Python packages for efficient storage")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    zip_parser = subparsers.add_parser("zip", default=True, help="Zip a package")
    zip_parser.add_argument("package", help="Package name to zip")
    zip_parser.add_argument(
        "-p", "--pyc", action="store_true", help="Store as compiled bytecode (.pyc) instead of source (.py)"
    )
    zip_parser.add_argument(
        "-O",
        "--optimize",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="""Optimization level for .pyc mode (default: 2):
        0 = No optimization (keeps __doc__, __assert__)
        1 = Basic (-O flag, removes assert statements)
        2 = Advanced (-OO flag, removes docstrings + asserts)""",
    )
    zip_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    unzip_parser = subparsers.add_parser("unzip", help="Unzip a package")
    unzip_parser.add_argument("package", help="Package name to unzip")
    unzip_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    if args.command == "zip":
        success = zip_package(args.package, use_pyc=args.pyc, opt_level=args.optimize, verbose=args.verbose)
        sys.exit(0 if success else 1)
    elif args.command == "unzip":
        success = unzip_package(args.package, verbose=args.verbose)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
