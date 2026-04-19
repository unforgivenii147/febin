#!/data/data/com.termux/files/usr/bin/python
"""
Refactor Python files: replace `os` module usage with `pathlib`.
USAGE:
  python refactor_os_to_pathlib.py [--dry] [--in-place] [files...]
--dry        Show diffs only (default)
  --in-place   Apply changes directly
  files...     Files/dirs to process (default: current dir, .py only)
EXAMPLES:
  python refactor_os_to_pathlib.py --dry
  python refactor_os_to_pathlib.py --in-place src/ tests/
  python refactor_os_to_pathlib.py myscript.py
"""

import ast
import difflib
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# -----------------------------
# Safe import & pattern mapping
# -----------------------------
# Mapping: (module, attr) → (replacement_module, replacement_import, new_call)
# If replacement_module is None → inline replacement (no import change)
REPLACEMENTS: Dict[Tuple[str, str], Tuple[Optional[str], str, str]] = {
    # os.path
    ("os", "path.join"): (
        "pathlib",
        "Path",
        "lambda *args: Path(*args[:-1]).joinpath(args[-1]) if len(args) > 1 else Path(*args)",
    ),
    ("os", "path.exists"): ("pathlib", "Path", "lambda p: Path(p).exists()"),
    ("os", "path.isdir"): ("pathlib", "Path", "lambda p: Path(p).is_dir()"),
    ("os", "path.isfile"): ("pathlib", "Path", "lambda p: Path(p).is_file()"),
    ("os", "path.abspath"): ("pathlib", "Path", "lambda p: Path(p).resolve()"),
    ("os", "path.realpath"): ("pathlib", "Path", "lambda p: Path(p).resolve()"),
    ("os", "path.basename"): ("pathlib", "Path", "lambda p: Path(p).name"),
    ("os", "path.dirname"): ("pathlib", "Path", "lambda p: Path(p).parent"),
    ("os", "path.splitext"): (
        "pathlib",
        "Path",
        "lambda p: (Path(p).stem, Path(p).suffix)",
    ),
    ("os", "path.splitext")[::-1]: None,  # skip duplicate key
    ("os", "path.split"): (
        "pathlib",
        "Path",
        "lambda p: (str(Path(p).parent), Path(p).name)",
    ),
    ("os", "path.getmtime"): ("pathlib", "Path", "lambda p: Path(p).stat().st_mtime"),
    ("os", "path.getsize"): ("pathlib", "Path", "lambda p: Path(p).stat().st_size"),
    ("os", "path.relpath"): (
        "pathlib",
        "Path",
        "lambda p, start='.': Path(p).resolve().relative_to(Path(start).resolve())",
    ),
    ("os", "path.commonpath"): (
        "pathlib",
        "Path",
        "lambda paths: Path(os.path.commonpath(paths))",
    ),  # keep os for now (hard to replace)
    ("os", "path.samefile"): (
        "pathlib",
        "Path",
        "lambda p1, p2: Path(p1).samefile(Path(p2))",
    ),
    ("os", "path.expanduser"): ("pathlib", "Path", "lambda p: Path(p).expanduser()"),
    ("os", "path.expandvars"): ("pathlib", "Path", "lambda p: Path(p).expandvars()"),
    ("os", "path.normpath"): ("pathlib", "Path", "lambda p: Path(p).resolve()"),  # ≈
    ("os", "path.normcase"): (
        "pathlib",
        "Path",
        "lambda p: Path(p).resolve().as_posix()",
    ),  # not exact
    # os (non-pathlib)
    ("os", "makedirs"): ("shutil", "Path", "lambda p, *a, **k: Path(p).mkdir(*a, **k)"),
    ("os", "mkdir"): (
        "pathlib",
        "Path",
        "lambda p: Path(p).mkdir(parents=False, exist_ok=False)",
    ),
    ("os", "rmdir"): ("pathlib", "Path", "lambda p: Path(p).rmdir()"),
    ("os", "remove"): ("pathlib", "Path", "lambda p: Path(p).unlink()"),
    ("os", "rename"): ("pathlib", "Path", "lambda src, dst: Path(src).rename(dst)"),
    ("os", "replace"): ("pathlib", "Path", "lambda src, dst: Path(src).replace(dst)"),
    ("os", "listdir"): ("pathlib", "Path", "lambda p='.': list(Path(p).iterdir())"),
    ("os", "walk"): (
        "pathlib",
        "Path",
        "lambda top: ((str(p), [d.name for d in p.iterdir() if d.is_dir()], [f.name for f in p.iterdir() if f.is_file()]) for p in Path(top).rglob('*') if p.is_dir())",
    ),  # simplified
    ("os", "stat"): ("pathlib", "Path", "lambda p: Path(p).stat()"),
    ("os", "chdir"): (
        "pathlib",
        "Path",
        "lambda p: os.chdir(p)",
    ),  # os.chdir still needed
    ("os", "getcwd"): ("pathlib", None, "lambda: Path.cwd()"),  # Path.cwd() is enough
    ("os", "environ"): ("os", None, "os.environ"),  # keep os for env
    ("os", "chmod"): ("pathlib", "Path", "lambda p, mode: Path(p).chmod(mode)"),
    ("os", "chown"): ("pathlib", "Path", "lambda p, uid, gid: Path(p).chown(uid, gid)"),
    ("os", "symlink"): (
        "pathlib",
        "Path",
        "lambda src, dst: Path(dst).symlink_to(src)",
    ),
    ("os", "readlink"): ("pathlib", "Path", "lambda p: str(Path(p).readlink())"),
    ("os", "unlink"): ("pathlib", "Path", "lambda p: Path(p).unlink()"),
    ("os", "rename"): ("pathlib", "Path", "lambda src, dst: Path(src).rename(dst)"),
    ("os", "scandir"): ("pathlib", "Path", "lambda p='.': Path(p).iterdir()"),
}


# Special-case: `os.path.join(a, b, c)` → `Path(a) / b / c`
# We handle this via a post-pass regex (below)
# -----------------------------
# AST visitor to detect `os` usage
# -----------------------------
class OsUsageFinder(ast.NodeVisitor):
    def __init__(self):
        self.uses_os = False
        self.os_import_name: Optional[str] = None  # e.g., alias 'import os as o'
        self.os_path_import_name: Optional[str] = None
        self.os_used_attrs: Set[str] = set()
        self.os_path_used_attrs: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name == "os":
                self.uses_os = True
                self.os_import_name = alias.asname or "os"
            elif alias.name == "os.path":
                self.uses_os = True
                self.os_path_import_name = alias.asname or "os.path"
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "os":
            self.uses_os = True
            for alias in node.names:
                self.os_used_attrs.add(alias.name)
        elif node.module == "os.path":
            self.uses_os = True
            for alias in node.names:
                self.os_path_used_attrs.add(alias.name)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # os.something
        if isinstance(node.value, ast.Name) and node.value.id == self.os_import_name:
            self.uses_os = True
            self.os_used_attrs.add(node.attr)
        # os.path.something
        if isinstance(node.value, ast.Attribute):
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == self.os_import_name
                and node.value.attr == "path"
            ):
                self.uses_os = True
                self.os_path_used_attrs.add(node.attr)
        self.generic_visit(node)


def rewrite_os_to_pathlib(source: str, tree: ast.AST) -> str:
    # Step 1: Replace `os.path.join(...)` with `Path(...) / ...`
    #   os.path.join(a, b, c) → Path(a) / b / c
    source = re.sub(
        r"\bos\.path\.join\s*\(\s*([^)]*)\s*\)",
        lambda m: _join_replacer(m.group(1)),
        source,
    )
    # Step 2: Replace function calls like os.getcwd() → Path.cwd()
    #   os.getcwd() → Path.cwd()
    source = re.sub(r"\bos\.getcwd\s*\(\s*\)", "Path.cwd()", source)
    # Step 3: Replace os.listdir() → list(Path().iterdir()) or Path().iterdir()
    #   os.listdir() → list(Path().iterdir())
    source = re.sub(r"\bos\.listdir\s*\(\s*\)", "list(Path().iterdir())", source)
    source = re.sub(r'\bos\.listdir\s*\(\s*"([^"]+)"\s*\)', r'list(Path("\1").iterdir())', source)
    source = re.sub(r"\bos\.listdir\s*\(\s*\'([^\']+)\'\s*\)", r'list(Path("\1").iterdir())', source)
    # Step 4: Replace os.path.exists, .isdir, etc.
    #   os.path.exists(p) → Path(p).exists()
    for attr in [
        "exists",
        "isdir",
        "isfile",
        "abspath",
        "realpath",
        "basename",
        "dirname",
        "splitext",
        "split",
        "getmtime",
        "getsize",
        "relpath",
        "samefile",
        "expanduser",
        "expandvars",
        "normpath",
        "normcase",
    ]:
        pattern = rf"\bos\.path\.{attr}\s*\(\s*([^)]*)\s*\)"
        repl = _make_pathlib_call(attr)
        source = re.sub(pattern, repl, source)
    # Step 5: Replace os.makedirs, os.mkdir, etc.
    for os_attr, (mod, imp, repl) in REPLACEMENTS.items():
        if mod is None and imp == "Path" and "lambda" in repl:
            # Already handled above; skip
            continue
        if os_attr[0] == "os" and os_attr[1] not in ["path"]:
            pattern = rf"\bos\.{os_attr[1]}\s*\(\s*([^)]*)\s*\)"
            # Simple heuristic: use lambda if not simple
            if os_attr[1] in [
                "makedirs",
                "mkdir",
                "rmdir",
                "remove",
                "rename",
                "replace",
                "stat",
                "chmod",
                "chown",
                "symlink",
                "readlink",
                "unlink",
                "scandir",
            ]:
                # For now, just rewrite to Path(...).method()
                if os_attr[1] == "makedirs":
                    source = re.sub(
                        r"\bos\.makedirs\s*\(\s*([^,]+)\s*(?:,\s*([^)]+))?\s*\)",
                        lambda m: (
                            f"Path({m.group(1)}).mkdir(parents=True, exist_ok=True)"
                            if m.group(2) is None
                            else f"Path({m.group(1)}).mkdir({m.group(2)})"
                        ),
                        source,
                    )
                elif os_attr[1] == "mkdir":
                    source = re.sub(
                        r"\bos\.mkdir\s*\(\s*([^)]+)\s*\)",
                        r"Path(\1).mkdir(parents=False, exist_ok=False)",
                        source,
                    )
                elif os_attr[1] == "rmdir":
                    source = re.sub(r"\bos\.rmdir\s*\(\s*([^)]+)\s*\)", r"Path(\1).rmdir()", source)
                elif os_attr[1] == "remove":
                    source = re.sub(
                        r"\bos\.remove\s*\(\s*([^)]+)\s*\)",
                        r"Path(\1).unlink()",
                        source,
                    )
                elif os_attr[1] == "rename":
                    source = re.sub(
                        r"\bos\.rename\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)",
                        r"Path(\1).rename(\2)",
                        source,
                    )
                elif os_attr[1] == "replace":
                    source = re.sub(
                        r"\bos\.replace\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)",
                        r"Path(\1).replace(\2)",
                        source,
                    )
                elif os_attr[1] == "stat":
                    source = re.sub(r"\bos\.stat\s*\(\s*([^)]+)\s*\)", r"Path(\1).stat()", source)
                elif os_attr[1] == "chmod":
                    source = re.sub(
                        r"\bos\.chmod\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)",
                        r"Path(\1).chmod(\2)",
                        source,
                    )
                elif os_attr[1] == "chown":
                    source = re.sub(
                        r"\bos\.chown\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)",
                        r"Path(\1).chown(\2, \3)",
                        source,
                    )
                elif os_attr[1] == "symlink":
                    source = re.sub(
                        r"\bos\.symlink\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)",
                        r"Path(\2).symlink_to(\1)",
                        source,
                    )
                elif os_attr[1] == "readlink":
                    source = re.sub(
                        r"\bos\.readlink\s*\(\s*([^)]+)\s*\)",
                        r"str(Path(\1).readlink())",
                        source,
                    )
                elif os_attr[1] == "unlink":
                    source = re.sub(
                        r"\bos\.unlink\s*\(\s*([^)]+)\s*\)",
                        r"Path(\1).unlink()",
                        source,
                    )
                elif os_attr[1] == "scandir":
                    source = re.sub(
                        r"\bos\.scandir\s*\(\s*([^)]*)\s*\)",
                        r"Path(\1).iterdir()",
                        source,
                    )
    # Step 6: Add `from pathlib import Path` if needed (simple heuristic)
    #   We'll just try to add it if os.path.* or Path(...) used
    if "Path(" in source and "from pathlib import Path" not in source:
        # Insert after first import or at top
        lines = source.splitlines(keepends=True)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                insert_idx = i + 1
            elif line.strip() and not line.strip().startswith("#"):
                break
        if insert_idx == 0:
            insert_idx = 1  # after shebang/comments
        lines.insert(insert_idx, "from pathlib import Path\n")
        source = "".join(lines)
    return source


def _join_replacer(args: str) -> str:
    """Convert `os.path.join(a, b, c)` → `Path(a) / b / c`"""
    parts = [p.strip() for p in args.split(",") if p.strip()]
    if not parts:
        return "Path()"
    if len(parts) == 1:
        return f"Path({parts[0]})"
    # Join with /
    return " / ".join([f"Path({parts[0]})"] + parts[1:])


def _make_pathlib_call(attr: str) -> str:
    """Return replacement lambda for os.path.attr"""
    # Map common cases to simple Path() calls
    mapping = {
        "exists": lambda p: f"Path({p}).exists()",
        "isdir": lambda p: f"Path({p}).is_dir()",
        "isfile": lambda p: f"Path({p}).is_file()",
        "abspath": lambda p: f"Path({p}).resolve()",
        "realpath": lambda p: f"Path({p}).resolve()",
        "basename": lambda p: f"Path({p}).name",
        "dirname": lambda p: f"Path({p}).parent",
        "splitext": lambda p: f"(Path({p}).stem, Path({p}).suffix)",
        "split": lambda p: f"(str(Path({p}).parent), Path({p}).name)",
        "getmtime": lambda p: f"Path({p}).stat().st_mtime",
        "getsize": lambda p: f"Path({p}).stat().st_size",
        "relpath": lambda p: f"Path({p}).resolve().relative_to(Path('.').resolve())",
        "samefile": lambda p: f"Path({p}).exists() and Path({p}).samefile(Path({p}))",  # simplified
        "expanduser": lambda p: f"Path({p}).expanduser()",
        "expandvars": lambda p: f"Path({p}).expandvars()",
        "normpath": lambda p: f"str(Path({p}).resolve())",  # approximate
        "normcase": lambda p: f"Path({p}).as_posix().lower()",  # approximate
    }
    return mapping.get(attr, lambda p: f"Path({p}).{attr}()")


# -----------------------------
# Main refactoring logic
# -----------------------------
def process_file(path: Path, dry_run: bool = True) -> bool:
    try:
        with path.open("r", encoding="utf-8") as f:
            original = f.read()
    except UnicodeDecodeError:
        print(f"⚠️  Skipping non-UTF-8 file: {path}")
        return False
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return False
    try:
        tree = ast.parse(original)
    except SyntaxError as e:
        print(f"⚠️  Skipping unparseable file: {path} ({e})")
        return False
    finder = OsUsageFinder()
    finder.visit(tree)
    if not finder.uses_os:
        return False  # No `os` usage — skip
    new_source = rewrite_os_to_pathlib(original, tree)
    if new_source.strip() == original.strip():
        return False
    if dry_run:
        diff = list(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                new_source.splitlines(keepends=True),
                fromfile=f"{path} (original)",
                tofile=f"{path} (refactored)",
                lineterm="",
            )
        )
        print(f"\n✅ {path} — would change (diff preview):")
        print("".join(diff[:20]))  # Show first 20 lines
        if len(diff) > 20:
            print(f"… ({len(diff) - 20} more lines)")
        return True
    else:
        try:
            with path.open("w", encoding="utf-8") as f:
                f.write(new_source)
            print(f"✅ {path} — refactored")
            return True
        except Exception as e:
            print(f"❌ Error writing {path}: {e}")
            return False


def collect_files(targets: List[str]) -> List[Path]:
    py_files: List[Path] = []
    excluded_dirs = {
        "__pycache__",
        ".git",
        ".ruff_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        "node_modules",
        ".tox",
        ".mypy_cache",
    }
    for target in targets:
        p = Path(target)
        if not p.exists():
            print(f"⚠️  Path not found: {target}")
            continue
        if p.is_file() and p.suffix == ".py":
            py_files.append(p.resolve())
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                # Filter excluded dirs *in-place* to avoid descending
                dirs[:] = [d for d in dirs if d not in excluded_dirs]
                for f in files:
                    if f.endswith(".py"):
                        py_files.append(Path(root) / f)
    return sorted(set(py_files))


def main():
    args = sys.argv[1:]
    if not args or {"-h", "--help"} & set(args):
        print(__doc__)
        sys.exit(0)
    dry_run = "--dry" in args
    in_place = "--in-place" in args
    if dry_run and in_place:
        print("❌ Cannot use both --dry and --in-place")
        sys.exit(1)
    if in_place:
        print("⚠️  🔥 IN-PLACE MODE: changes will be written to files.")
        confirm = input("Continue? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)
    files_to_process = args
    if not files_to_process:
        files_to_process = ["."]
    files = collect_files(files_to_process)
    if not files:
        print("No Python files found to process.")
        sys.exit(0)
    print(f"🔍 Found {len(files)} Python file(s).")
    changed_count = 0
    for file_path in files:
        if process_file(file_path, dry_run=not in_place):
            changed_count += 1
    print("\n" + "=" * 60)
    if in_place:
        print(f"✅ Refactoring complete: {changed_count} file(s) modified.")
    else:
        print(f"✅ Dry run complete: {changed_count} file(s) would change.")
    print("💡 Always review changes manually before committing!")


if __name__ == "__main__":
    main()
