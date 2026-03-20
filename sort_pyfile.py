#!/data/data/com.termux/files/usr/bin/python
import ast
from pathlib import Path
import sys


def sort_python_script(file_path: Path):
    """
    Sorts functions, classes, and constants alphabetically within a Python script.
    Constants and classes are sorted before functions.
    Saves the sorted code back to the original file.
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Error parsing Python code in {file_path}: {e}")
        return

    # Separate top-level items
    constants = []
    classes = []
    functions = []
    other_nodes = []  # To preserve imports, comments, etc. at the beginning

    # Collect top-level nodes
    for node in tree.body:
        if isinstance(node, ast.Assign):
            # Basic check for constants: assignment at module level, uppercase name
            # This is a simplification; real constant detection can be complex.
            # We'll assume assignments directly in the module body are candidates.
            # More robust would be to check if all targets are Name nodes with uppercase IDs.
            is_constant = True
            for target in node.targets:
                if not isinstance(target, ast.Name) or not target.id.isupper():
                    is_constant = False
                    break
            if is_constant:
                constants.append(node)
            else:
                other_nodes.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node)
        else:
            other_nodes.append(node)

    # Sort the collected items
    # Sort constants by name
    constants.sort(key=lambda node: node.targets[0].id if node.targets else "")
    # Sort classes by name
    classes.sort(key=lambda node: node.name)
    # Sort functions by name
    functions.sort(key=lambda node: node.name)

    # Reconstruct the body: imports/other, then constants, then classes, then functions
    # The 'other_nodes' will contain imports and potentially other elements that
    # should remain in their original relative positions *before* the sorted blocks.
    # For simplicity, we'll place all imports and non-sorted elements first,
    # followed by the sorted constants, classes, and functions.
    # A more sophisticated approach would preserve the original order of non-sorted elements.

    # Separate imports from other non-sorted nodes for better preservation
    imports = []
    misc_nodes = []
    for node in other_nodes:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
        else:
            misc_nodes.append(node)

    # Ensure imports are kept at the very top
    new_body = imports + misc_nodes + constants + classes + functions

    # Create a new AST with the sorted body
    new_tree = ast.Module(body=new_body, type_ignores=[])

    # Use astunparse or similar to convert back to source code.
    # Since ast.unparse is built-in from Python 3.9, we'll use that.
    # If you are on an older Python, you might need to install 'astunparse'.
    try:
        import astunparse

        sorted_code = astunparse.unparse(new_tree)
    except ImportError:
        print("Warning: 'astunparse' library not found. Trying built-in 'ast.unparse' (Python 3.9+).")
        try:
            sorted_code = ast.unparse(new_tree)
        except AttributeError:
            print("Error: Your Python version is too old to have 'ast.unparse'.")
            print("Please install the 'astunparse' library: pip install astunparse")
            return
    except Exception as e:
        print(f"Error converting AST back to code: {e}")
        return

    # Write the sorted code back to the file
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(sorted_code)
        print(f"Successfully sorted and saved: {file_path}")
    except Exception as e:
        print(f"Error writing sorted code back to {file_path}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sort_script.py <path_to_python_script>")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    sort_python_script(script_path)
