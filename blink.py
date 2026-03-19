#!/data/data/com.termux/files/usr/bin/python
from lazyloader import lazy_import

os = lazy_import("os")
pathlib = lazy_import("pathlib")
sys = lazy_import("sys")

if __name__ == "__main__":
    root_dir = pathlib.Path.cwd()
    files = list(root_dir.rglob("*"))
    bcount = 0
    for path in files:
        if path.is_symlink() and not path.exists():
            try:
                path.unlink()
                bcount += 1
                print(f"{os.path.relpath(path)}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")
    if not bcount:
        print("no broken link found.")
        sys.exit(0)
    print(f"{bcount} broken link removed.")
