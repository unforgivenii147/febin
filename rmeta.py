#!/data/data/com.termux/files/usr/bin/python
import re
from pathlib import Path

# Regex to find meta tags: <meta ... >
# It's designed to be fairly robust, capturing various attribute styles and self-closing tags.
meta_tag_pattern = re.compile(r"<meta[^>]*>", re.IGNORECASE)


def remove_meta_tags(filepath: Path):
    try:
        # Read the HTML file content
        html_content = filepath.read_text(encoding="utf-8", errors="ignore")
        # Use regex to find and remove all meta tags
        new_html_content = meta_tag_pattern.sub("", html_content)
        # Only write back if changes were made
        if new_html_content != html_content:
            # Write the modified content back to the file
            filepath.write_text(new_html_content, encoding="utf-8")
            print(f"Removed meta tags from: {filepath}")
        else:
            print(f"No meta tags found or removed in: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def process_directory(directory: Path):
    for item in directory.rglob("*.html"):
        if item.is_file():
            remove_meta_tags(item)


# --- Main execution ---
if __name__ == "__main__":
    current_dir = Path()
    print(f"Starting to remove meta tags from HTML files in '{current_dir.resolve()}' and its subdirectories...\n")
    process_directory(current_dir)
    print("\nFinished processing. Meta tags have been removed from applicable HTML files.")
