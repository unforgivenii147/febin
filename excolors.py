#!/data/data/com.termux/files/usr/bin/python
import os
import regex as re


def extract_colors_from_file(file_path):
    """Extract hex color codes from a single file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # Regex pattern for hex color codes (3 or 6 digits)
    pattern = r"#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})\b"
    return re.findall(pattern, content)


def process_directory(directory):
    """Process all text files in directory and subdirectories."""
    colors = set()  # Using set to avoid duplicates
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".txt", ".html", ".css", ".js", ".json", ".md", ".py")):
                file_path = os.path.join(root, file)
                try:
                    found_colors = extract_colors_from_file(file_path)
                    for color in found_colors:
                        # Normalize to 6-digit format if it's 3-digit
                        if len(color) == 3:
                            color = "".join([c * 2 for c in color])
                        colors.add(f"#{color.lower()}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return sorted(colors)


def save_colors_to_file(colors, output_file):
    """Save colors to output file, one per line."""
    with open(output_file, "w") as f:
        f.write("\n".join(colors))


def main():
    current_dir = os.getcwd()
    output_file = os.path.join(current_dir, "colors.txt")
    print(f"Searching for color codes in {current_dir}...")
    colors = process_directory(current_dir)
    save_colors_to_file(colors, output_file)
    print(f"Found {len(colors)} unique colors saved to {output_file}")


if __name__ == "__main__":
    main()
