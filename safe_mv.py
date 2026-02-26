#!/usr/bin/env python3
"""
Safe mv wrapper - Moves files without overwriting, adds _(number) suffix if file exists
"""

import os
import shutil
import argparse
import sys
from pathlib import Path

def get_unique_filename(destination):
    """
    Generate a unique filename by adding _(number) suffix if file exists
    """
    dest_path = Path(destination)
    
    if not dest_path.exists():
        return destination
    
    # Split into stem and suffix
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1

def safe_move(source, destination, verbose=False, no_clobber=True):
    """
    Move source to destination without overwriting
    If no_clobber is True, rename destination with number suffix if it exists
    If no_clobber is False, behave like regular mv (overwrite)
    """
    source_path = Path(source)
    
    # Check if source exists
    if not source_path.exists():
        print(f"Error: Source '{source}' does not exist", file=sys.stderr)
        return False
    
    # Determine destination
    dest_path = Path(destination)
    
    # If destination is a directory, move inside it
    if dest_path.is_dir():
        dest_path = dest_path / source_path.name
    
    # Generate unique filename if needed
    if no_clobber and dest_path.exists():
        original_dest = str(dest_path)
        dest_path = Path(get_unique_filename(str(dest_path)))
        if verbose:
            print(f"Target exists, renaming to: {dest_path}")
    
    # Perform the move
    try:
        shutil.move(str(source_path), str(dest_path))
        if verbose:
            print(f"Moved '{source}' -> '{dest_path}'")
        return True
    except Exception as e:
        print(f"Error moving file: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Safe mv - Move files without overwriting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.txt /target/dir/     # Moves file, adds number if exists
  %(prog)s -v file.txt file2.txt dir/ # Move multiple files with verbose
  %(prog)s -f file.txt file.txt       # Force overwrite (like regular mv)
        """
    )
    
    parser.add_argument('sources', nargs='+', help='Source files/directories to move')
    parser.add_argument('destination', help='Destination path')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Explain what is being done')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Force overwrite (like regular mv)')
    parser.add_argument('-n', '--no-clobber', action='store_true', default=True,
                       help='Do not overwrite existing files (default)')
    
    args = parser.parse_args()
    
    # Handle multiple sources
    if len(args.sources) > 1:
        # Destination must be a directory for multiple sources
        dest_path = Path(args.destination)
        if not dest_path.is_dir() and not args.destination.endswith('/'):
            print(f"Error: When moving multiple files, destination must be a directory",
                  file=sys.stderr)
            sys.exit(1)
        
        # Create destination directory if it doesn't exist
        if not dest_path.exists():
            try:
                dest_path.mkdir(parents=True)
                if args.verbose:
                    print(f"Created directory: {dest_path}")
            except Exception as e:
                print(f"Error creating directory: {e}", file=sys.stderr)
                sys.exit(1)
    
    # Process each source
    success_count = 0
    for source in args.sources:
        if safe_move(source, args.destination, args.verbose, not args.force):
            success_count += 1
    
    # Exit with appropriate code
    if success_count == len(args.sources):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()