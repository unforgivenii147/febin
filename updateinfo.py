#!/data/data/com.termux/files/usr/bin/python
"""
Script to update author name, email, and GitHub URL in Python package configuration files.
"""

import re
import sys
from pathlib import Path

# Your information
NEW_INFO = {
    "name": "Isaac Onagh",
    "email": "mkalafsaz@gmail.com",
    "github_username": "unforgivenii147",
}


def update_setup_py(file_path: Path) -> bool:
    """Update setup.py file with new author info and GitHub URL."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        # Update author and author_email
        content = re.sub(
            r'author\s*=\s*["\'][^"\']*["\']',
            f'author="{NEW_INFO["name"]}"',
            content,
        )
        content = re.sub(
            r'author_email\s*=\s*["\'][^"\']*["\']',
            f'author_email="{NEW_INFO["email"]}"',
            content,
        )
        # Update GitHub URLs
        # Pattern for github.com/username/projectname
        content = re.sub(
            r'(https?://github\.com/)[^/]+(/[^"\']*)',
            rf"\g<1>{NEW_INFO['github_username']}\g<2>",
            content,
        )
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def update_pyproject_toml(
    file_path: Path,
) -> bool:
    """Update pyproject.toml file with new author info and GitHub URL."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        # Update author information in [project] section
        if "[project]" in content:
            # Handle different formats of author specification
            # Format: authors = [{name = "...", email = "..."}]
            author_pattern = (
                r'(authors\s*=\s*\[\s*\{[^}]*name\s*=\s*["\'][^"\']*["\'][^}]*email\s*=\s*["\'][^"\']*["\'][^}]*\})'
            )

            def replace_author(match):
                author_block = match.group(1)
                # Replace name
                author_block = re.sub(
                    r'name\s*=\s*["\'][^"\']*["\']',
                    f'name = "{NEW_INFO["name"]}"',
                    author_block,
                )
                # Replace email
                return re.sub(
                    r'email\s*=\s*["\'][^"\']*["\']',
                    f'email = "{NEW_INFO["email"]}"',
                    author_block,
                )

            content = re.sub(
                author_pattern,
                replace_author,
                content,
                flags=re.DOTALL,
            )
        # Update GitHub URLs in [project.urls] or other sections
        # Pattern for github.com/username/projectname
        content = re.sub(
            r"(https?://github\.com/)[^/]+(/)",
            rf"\g<1>{NEW_INFO['github_username']}\g<2>",
            content,
        )
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def update_setup_cfg(file_path: Path) -> bool:
    """Update setup.cfg file with new author info and GitHub URL."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        # Update author and author_email in metadata section
        if "[metadata]" in content:
            # Update author
            content = re.sub(
                r"^author\s*=\s*.*$",
                f"author = {NEW_INFO['name']}",
                content,
                flags=re.MULTILINE,
            )
            # Update author_email
            content = re.sub(
                r"^author_email\s*=\s*.*$",
                f"author_email = {NEW_INFO['email']}",
                content,
                flags=re.MULTILINE,
            )
        # Update GitHub URLs
        content = re.sub(
            r"(https?://github\.com/)[^/]+(/)",
            rf"\g<1>{NEW_INFO['github_username']}\g<2>",
            content,
        )
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Main function to update all configuration files."""
    print("🔍 Scanning for configuration files...")
    print("📝 New information:")
    print(f"   Name: {NEW_INFO['name']}")
    print(f"   Email: {NEW_INFO['email']}")
    print(f"   GitHub Username: {NEW_INFO['github_username']}")
    print("-" * 50)
    # Define files to update
    files_to_update = [
        (Path("setup.py"), update_setup_py),
        (
            Path("pyproject.toml"),
            update_pyproject_toml,
        ),
        (Path("setup.cfg"), update_setup_cfg),
    ]
    updated_count = 0
    for file_path, update_func in files_to_update:
        if file_path.exists():
            if update_func(file_path):
                updated_count += 1
        else:
            print(f"ℹ️  {file_path} not found, skipping...")
    print("-" * 50)
    if updated_count > 0:
        print(f"✅ Successfully updated {updated_count} file(s)")
    else:
        print("ℹ️  No files were updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
