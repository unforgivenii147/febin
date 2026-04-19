from pathlib import Path

BASHBIN: Path = Path.home() / "bashbin"
BIN: Path = Path.home() / "bin"


def process_dir(root_dir, ext):
    for path in root_dir.glob(f"*.{ext}"):
        symlink_path = path.with_name(path.stem)
        if not symlink_path.exists():
            symlink_path.symlink_to(path)
            print(f"Created symlink: {link_name} -> {src_file}")
        else:
            continue


if __name__ == "__main__":
    process_dir(BASHBIN, ".sh")
    process_dir(BIN, ".py")
