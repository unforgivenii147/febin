#!/data/data/com.termux/files/usr/bin/python
import ast
import hashlib
import logging
import shutil
from pathlib import Path

from joblib import Parallel, delayed

OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "const.py"
LOG_FILE = OUTPUT_DIR / "error.log"
PYTHON_FILES_TO_PROCESS = "**/*.py"  # پردازش تمام فایل‌های پایتون
OUTPUT_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_constants(filepath: Path) -> list[tuple[str, str, str]]:
    constants = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check if all targets are simple names (not attributes or subscripts)
                is_simple_assign = all(isinstance(t, ast.Name) for t in node.targets)
                # Check if the assignment is at the module level (or immediately within a class)
                # For simplicity, we're focusing on module-level constants primarily.
                # You might want to add more sophisticated checks for class-level constants.
                if is_simple_assign and isinstance(node.value, ast.Constant):
                    for target in node.targets:
                        const_name = target.id
                        # Heuristic: Assume uppercase names are constants
                        if const_name.isupper():
                            const_value = ast.unparse(node.value)  # Use ast.unparse for value representation
                            const_type = type(node.value.value).__name__
                            constants.append((const_name, const_value, const_type))
            elif isinstance(node, ast.AnnAssign):  # Handle annotated assignments like MY_VAR: int = 10
                if isinstance(node.target, ast.Name) and node.value is not None:
                    if node.target.id.isupper():
                        const_name = node.target.id
                        const_value = ast.unparse(node.value)
                        # Type hint is in node.annotation, but this is trickier to get nicely
                        # For simplicity here, we'll still try to infer type from value
                        const_type = (
                            type(node.value.value).__name__ if isinstance(node.value, ast.Constant) else "unknown"
                        )
                        constants.append((const_name, const_value, const_type))
    except SyntaxError as e:
        logging.error(f"Syntax error in {filepath}: {e}")
    except Exception as e:
        logging.error(f"Error processing {filepath}: {e}")
    return constants


def process_file(filepath: Path) -> tuple[str, list[tuple[str, str, str]] | None]:
    """Processes a single file: calculates hash and extracts constants."""
    file_hash = get_file_hash(filepath)
    constants = extract_constants(filepath)
    return file_hash, constants


# --- Main Execution ---
def main():
    # Clear previous output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    # Find all Python files
    current_dir = Path(".")
    python_files = list(current_dir.glob(PYTHON_FILES_TO_PROCESS))
    if not python_files:
        print("No Python files found in the current directory.")
        return
    print(f"Found {len(python_files)} Python files. Processing...")
    # Use joblib for parallel processing
    # n_jobs=-1 uses all available CPU cores
    results = Parallel(n_jobs=-1)(delayed(process_file)(f) for f in python_files)
    # Deduplicate constants by hash and collect unique constants
    unique_constants = {}
    processed_hashes = set()
    # Use a dictionary to store constants, keyed by hash to handle content duplicates
    all_constants_by_hash = {}
    for file_hash, constants in results:
        if constants is None:  # Skip files with errors
            continue
        if file_hash not in processed_hashes:
            processed_hashes.add(file_hash)
            for name, value, ctype in constants:
                if file_hash not in all_constants_by_hash:
                    all_constants_by_hash[file_hash] = []

                constant_repr = f"{name} = {value}"
                found = False
                for idx, (existing_name, existing_value, existing_type) in enumerate(all_constants_by_hash[file_hash]):
                    if existing_name == name and existing_value == value:
                        all_constants_by_hash[file_hash][idx] = (name, value, ctype)
                        found = True
                        break
                if not found:
                    all_constants_by_hash[file_hash].append((name, value, ctype))
    # Flatten the unique constants into a single list for output
    final_constants = []
    for file_hash, const_list in all_constants_by_hash.items():
        final_constants.extend(const_list)
    # Sort constants alphabetically by name for consistent output
    final_constants.sort(key=lambda x: x[0])
    # Write constants to the output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Automatically generated constants file\n")
        f.write("# Based on files in the current directory\n\n")
        written_consts = set()  # To ensure no exact duplicates make it to file if hash collision occurs or logic error
        for name, value, ctype in final_constants:
            # Final check for exact duplicates in the output file
            constant_line = f"{name} = {value}"
            if constant_line not in written_consts:
                f.write(f"# Type: {ctype}\n")
                f.write(f"{constant_line}\n\n")
                written_consts.add(constant_line)
    print(f"Successfully extracted {len(written_consts)} unique constants to {OUTPUT_FILE}")
    if LOG_FILE.exists():
        print(f"Errors logged to {LOG_FILE}")


if __name__ == "__main__":
    main()
