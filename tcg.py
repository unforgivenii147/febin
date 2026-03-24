#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import subprocess
import sys

# Define shebangs for Termux
TERMUX_PYTHON_SH = "#!/data/data/com.termux/files/usr/bin/python\n"
TERMUX_BASH_SH = "#!/data/data/com.termux/files/usr/bin/bash\n"


def get_clipboard_content() -> str:
    """Fetches content from the Termux clipboard."""
    try:
        # Use 'text=True' to get output as string
        return subprocess.check_output(["termux-clipboard-get"], text=True, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: 'termux-clipboard-get' command not found. Is Termux:API installed?", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get clipboard content. STDERR: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def determine_script_type(content: str) -> str | None:
    """
    Analyzes the script content to determine if it's Python or Bash.
    Returns 'python', 'bash', or None if undetermined.
    """
    stripped_content = content.lstrip()

    # Check for explicit Python shebangs
    if stripped_content.startswith("#!/data/data/com.termux/files/usr/bin/python"):
        return "python"
    # Heuristic for Python: contains common Python keywords/structures
    if (
        "import " in content
        or "def " in content
        or "class " in content
        or stripped_content.startswith("print(")
        or stripped_content.startswith("sys.exit(")
    ):
        return "python"
    # Heuristic for Python (alternative shebangs)
    if stripped_content.startswith("#!python") or stripped_content.startswith("#!/usr/bin/env python"):
        return "python"

    # Check for explicit Bash shebangs
    if stripped_content.startswith("#!/bin/sh") or stripped_content.startswith("#!/bin/bash"):
        return "bash"
    # Heuristic for Bash: common shell commands
    if stripped_content.startswith(
        (
            "echo ",
            "cd ",
            "export ",
            "if ",
            "for ",
            "while ",
            "case ",
            "grep ",
            "ls ",
            "mkdir ",
            "rm ",
            "mv ",
            "cp ",
            "chmod ",
            "sudo ",
        )
    ):
        return "bash"
    # Heuristic for Bash (alternative shebangs)
    if stripped_content.startswith("#!/bin/sh") or stripped_content.startswith("#!/bin/bash"):
        return "bash"

    return None


def create_script_file(output_path: Path, content: str, script_type: str):
    """Writes content to the output file, sets permissions, and creates symlink if applicable."""
    final_content = content

    # Ensure the correct Termux shebang is present
    if script_type == "python":
        if not final_content.startswith(TERMUX_PYTHON_SH):
            # Try to replace existing shebang or prepend if none exists
            lines = final_content.splitlines()
            if lines and lines[0].startswith("#!"):
                lines[0] = TERMUX_PYTHON_SH
            else:
                lines.insert(0, TERMUX_PYTHON_SH)
            final_content = "\n".join(lines)
    elif script_type == "bash" and not final_content.startswith(TERMUX_BASH_SH):
        lines = final_content.splitlines()
        if lines and lines[0].startswith("#!"):
            lines[0] = TERMUX_BASH_SH
        else:
            lines.insert(0, TERMUX_BASH_SH)
        final_content = "\n".join(lines)

    # Write the content to the file
    try:
        output_path.write_text(final_content, encoding="utf-8")
        print(f"Script saved to: {output_path}")
    except OSError as e:
        print(f"Error writing to file {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Make the script executable
    try:
        os.chmod(output_path, 0o755)
        print(f"Made {output_path.name} executable.")
    except OSError as e:
        print(f"Error setting execute permission for {output_path}: {e}", file=sys.stderr)

    # Create symlink if in ~/bin or ~/bashbin
    user_home = Path.home()
    if output_path.parent == user_home / "bin" or output_path.parent == user_home / "bashbin":
        symlink_name = output_path.stem
        symlink_path = output_path.parent / symlink_name
        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                print(f"Symlink '{symlink_path.name}' already exists. Skipping creation.")
            else:
                symlink_path.symlink_to(output_path.resolve())  # Use resolve() for absolute path
                print(f"Created symlink: {symlink_path.name} -> {output_path.name}")
        except OSError as e:
            print(f"Error creating symlink {symlink_path.name}: {e}", file=sys.stderr)
        except Exception as e:  # Catch other potential errors during symlink creation
            print(f"An unexpected error occurred during symlink creation: {e}", file=sys.stderr)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output-file>", file=sys.stderr)
        sys.exit(1)

    output_file_arg = sys.argv[1]
    output_path = Path(output_file_arg)

    # Ensure the output directory exists
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create directory {output_path.parent}: {e}", file=sys.stderr)
        sys.exit(1)

    clipboard_content = get_clipboard_content()
    if not clipboard_content:
        print("Clipboard is empty. Nothing to process.", file=sys.stderr)
        sys.exit(0)

    script_type = determine_script_type(clipboard_content)

    if not script_type:
        print(
            "Warning: Could not reliably determine script type (Python/Bash). Attempting to save as-is.",
            file=sys.stderr,
        )
        # Default to saving without forcing a shebang if type is undetermined
        create_script_file(output_path, clipboard_content, None)
    else:
        create_script_file(output_path, clipboard_content, script_type)


if __name__ == "__main__":
    main()
