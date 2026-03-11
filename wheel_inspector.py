#!/data/data/com.termux/files/usr/bin/env python
"""
Inspect and validate generated .whl files.
"""

import zipfile
from pathlib import Path
from typing import Dict, List, Tuple
import sys


class WheelInspector:
    """Inspect .whl files."""

    def __init__(self, verbose: bool = False):
        """
        Initialize WheelInspector.

        Args:
            verbose: Verbose output
        """
        self.verbose = verbose

    def log(self, message: str):
        """Log message."""
        if self.verbose:
            print(f"[INSPECT] {message}")

    def inspect_wheel(self, wheel_path: Path) -> Dict:
        """
        Inspect a .whl file.

        Args:
            wheel_path: Path to .whl file

        Returns:
            Dictionary with wheel information
        """
        if not wheel_path.exists():
            return {"error": f"File not found: {wheel_path}"}

        try:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                info = {
                    "filename": wheel_path.name,
                    "size_mb": wheel_path.stat().st_size / (1024 * 1024),
                    "file_count": len(zf.namelist()),
                    "files": zf.namelist(),
                    "metadata": {},
                }

                # Read METADATA
                metadata_files = [f for f in zf.namelist() if f.endswith("/METADATA")]
                if metadata_files:
                    metadata_content = zf.read(metadata_files[0]).decode("utf-8")
                    for line in metadata_content.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            info["metadata"][key.strip()] = value.strip()

                # Read WHEEL
                wheel_files = [f for f in zf.namelist() if f.endswith("/WHEEL")]
                if wheel_files:
                    wheel_content = zf.read(wheel_files[0]).decode("utf-8")
                    info["wheel_metadata"] = wheel_content

                # Count file types
                info["file_types"] = {
                    ".py": len([f for f in zf.namelist() if f.endswith(".py")]),
                    ".so": len([f for f in zf.namelist() if f.endswith(".so")]),
                    ".pyd": len([f for f in zf.namelist() if f.endswith(".pyd")]),
                    ".c": len([f for f in zf.namelist() if f.endswith(".c")]),
                }

                return info

        except Exception as e:
            return {"error": str(e)}

    def validate_wheel(self, wheel_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a .whl file.

        Args:
            wheel_path: Path to .whl file

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        try:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                files = zf.namelist()

                # Check for METADATA
                has_metadata = any(f.endswith("/METADATA") for f in files)
                if not has_metadata:
                    issues.append("Missing METADATA file")

                # Check for WHEEL
                has_wheel = any(f.endswith("/WHEEL") for f in files)
                if not has_wheel:
                    issues.append("Missing WHEEL file")

                # Check for RECORD
                has_record = any(f.endswith("/RECORD") for f in files)
                if not has_record:
                    issues.append("Missing RECORD file")

                # Check dist-info directory
                dist_info = [f for f in files if ".dist-info/" in f]
                if not dist_info:
                    issues.append("No dist-info directory found")

        except Exception as e:
            issues.append(f"Error reading wheel: {str(e)}")

        return len(issues) == 0, issues

    def inspect_directory(self, directory: Path) -> List[Dict]:
        """
        Inspect all .whl files in a directory.

        Args:
            directory: Directory to inspect

        Returns:
            List of inspection results
        """
        wheels = list(directory.glob("*.whl"))
        results = []

        for wheel in wheels:
            info = self.inspect_wheel(wheel)
            is_valid, issues = self.validate_wheel(wheel)

            info["is_valid"] = is_valid
            info["issues"] = issues
            results.append(info)

        return results

    def print_inspection(self, wheel_path: Path):
        """Print detailed inspection of a wheel."""
        info = self.inspect_wheel(wheel_path)

        if "error" in info:
            print(f"Error: {info['error']}")
            return

        print(f"\n{'=' * 60}")
        print(f"Wheel: {info['filename']}")
        print(f"{'=' * 60}")

        print("\nBasic Info:")
        print(f"  Size: {info['size_mb']:.2f} MB")
        print(f"  Files: {info['file_count']}")

        if info["file_types"]:
            print("\nFile Types:")
            for ext, count in info["file_types"].items():
                if count > 0:
                    print(f"  {ext}: {count}")

        if info["metadata"]:
            print("\nMetadata:")
            for key, value in info["metadata"].items():
                if key in ["Name", "Version", "Summary", "Author"]:
                    print(f"  {key}: {value}")

        is_valid, issues = self.validate_wheel(wheel_path)
        print(f"\nValidation: {'✓ VALID' if is_valid else '✗ INVALID'}")

        if issues:
            print("Issues:")
            for issue in issues:
                print(f"  - {issue}")

        print(f"{'=' * 60}\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Inspect and validate .whl files")

    parser.add_argument("wheel", nargs="?", help="Path to .whl file or directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not args.wheel:
        args.wheel = str(Path.home() / "tmp" / "whl")

    path = Path(args.wheel)
    inspector = WheelInspector(verbose=args.verbose)

    if path.is_file() and path.suffix == ".whl":
        inspector.print_inspection(path)

    elif path.is_dir():
        wheels = list(path.glob("*.whl"))

        if not wheels:
            print(f"No .whl files found in {path}")
            return

        print(f"\nInspecting {len(wheels)} .whl files...\n")

        results = inspector.inspect_directory(path)

        valid_count = sum(1 for r in results if r.get("is_valid", True))
        invalid_count = len(results) - valid_count

        for result in results:
            status = "✓" if result.get("is_valid", True) else "✗"
            size = result.get("size_mb", 0)
            files = result.get("file_count", 0)

            print(f"{status} {result['filename']:<50} {size:>8.2f} MB ({files} files)")

        print(f"\nValid: {valid_count}/{len(results)}")
        print(f"Invalid: {invalid_count}/{len(results)}")

    else:
        print(f"Invalid path: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
