#!/data/data/com.termux/files/usr/bin/python
import regex 
from pathlib import Path
def fix_invalid_escapes(filepath: Path):
    fixed_lines = []
    made_change = False
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True) 
        for i, line in enumerate(lines):
            modified_line = regex.sub(r'\\(?!([nrt b\\\'\"]))', r'\\\\\\1', line) 
            if modified_line != line:
                made_change = True
                fixed_lines.append(modified_line)
            else:
                fixed_lines.append(line)
        if made_change:
            backup_file=filepath.with_name(filepath.name+".bak")
            backup_file.write_text(content,encoding="utf-8")
            filepath.write_text("".join(fixed_lines), encoding='utf-8')
            print(f"Fixed invalid escapes in: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
def process_directory(directory: Path = Path('.')):
    for filepath in directory.rglob("*.py"):
        if filepath.is_file(): 
            fix_invalid_escapes(filepath)
if __name__ == "__main__":
    print("Starting to fix invalid escape sequences in Python files...")
    current_directory = Path('.')
    process_directory(current_directory)
    print("Finished processing all Python files.")
