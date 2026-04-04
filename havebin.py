#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
from dh import get_ipkgs


def find_packages_with_bin_scripts(output_file="have_scripts.txt"):
    """
    Finds Python packages that install executable scripts into a 'bin' directory
    (e.g., ~/.local/bin or a virtual environment's bin).
    This script works by:
    1. Listing all installed Python packages.
    2. For each package, attempting to find its installed files using `pip show -f <package_name>`.
    3. Checking if any of these files reside in a 'bin' directory (common for executables).
    4. Saving the names of such packages to a specified output file.
    """
    print("Starting search for packages with 'bin' scripts...")
    try:
        # Get a list of all installed packages
        # pip list --format=freeze lists packages in requirements.txt format (e.g., package==version)
        # We only need the package name, so we split by '==' or take the first word.
        #        result = subprocess.run(["pip", "list", "--format=freeze"], capture_output=True, text=True, check=True)
        installed_packages = get_ipkgs()
        #        installed_packages.append(pkg_name)
        if not installed_packages:
            print("No Python packages found via 'pip list'. Please ensure pip is installed and accessible.")
            return
        print(f"Found {len(installed_packages)} installed packages. Checking each for 'bin' scripts...")
        packages_with_scripts = []
        total_packages = len(installed_packages)
        for i, package_name in enumerate(installed_packages):
            print(f"[{i + 1}/{total_packages}] Checking '{package_name}'...", end="\r")
            try:
                # Use pip show -f to list all installed files for the package
                # -f or --files: Show list of files installed by the package.
                result = subprocess.run(
                    ["pip", "show", "-f", package_name],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",  # Ensure correct encoding
                    errors="ignore",  # Ignore decoding errors for filenames
                )
                lines = result.stdout.split("\n")
                # These are typical locations where pip/setuptools install scripts
                bin_indicators = [
                    os.path.join(os.sep, "bin", ""),  # /bin/ (absolute)
                    os.path.join("bin", ""),  # bin/ (relative to install root)
                    os.path.join("scripts", ""),  # scripts/ (common on Windows)
                ]
                found_script_in_bin = False
                for line in lines:
                    line = line.strip()
                    if line.startswith("Location:"):  # Skip the Location line itself
                        continue
                    if line.startswith("Files:"):  # Files section starts after this
                        continue
                    # This is a heuristic. A more robust check might involve checking file permissions
                    # or shebangs, but this is a good starting point.
                    for indicator in bin_indicators:
                        if indicator in line.lower() and (
                            line.endswith(".py")  # Python scripts
                            or os.path.splitext(line)[1] == ""  # Executables often have no extension
                            or os.path.splitext(line)[1] == ".exe"  # Windows executables
                        ):
                            # Exclude __pycache__ and .dist-info/ etc.
                            if not any(
                                exclude_part in line
                                for exclude_part in ["__pycache__", ".dist-info", ".egg-info", ".pth"]
                            ):
                                found_script_in_bin = True
                                break
                    if found_script_in_bin:
                        break
                if found_script_in_bin:
                    packages_with_scripts.append(package_name)
            except subprocess.CalledProcessError as e:
                # pip show -f will return an error if the package is not found
                # or if there's an issue. For example, if 'pip list' returns a package
                # that's somehow not found by 'pip show'.
                # print(f"\nWarning: Could not get files for '{package_name}'. Error: {e.stderr.strip()}")
                pass  # Suppress verbose errors for individual packages
            except Exception as e:
                print(f"\nAn unexpected error occurred while checking '{package_name}': {e}")
        with open(output_file, "w") as f:
            for pkg in packages_with_scripts:
                f.write(pkg + "\n")
        print(f"\nSearch complete. Found {len(packages_with_scripts)} packages with 'bin' scripts.")
        print(f"List saved to '{output_file}'.")
    except FileNotFoundError:
        print("Error: 'pip' command not found. Please ensure Python and pip are installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error running pip command: {e.cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    find_packages_with_bin_scripts()
