#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from dh import get_random_name
from termcolor import cprint

from dhh import get_files, mpf3

MAX_QUEUE = 16


def save_script(str1):
    fn = "js/"
    fn += get_random_name(10)
    fn += ".js"
    fn = Path(fn)
    if fn.exists():
        cprint(f"[{fn}] exists.", "red")
        return False
    if not fn.exists():
        fn.write_text("\n".join(list(str1)), encoding="utf-8")
        cprint(f"{[fn]} created.", "cyan")
    return True


def process_file(fp):
    html_content = fp.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    scripts = soup.find_all("script")
    if scripts:
        cprint(
            f"{[fp.name]} : {len(scripts)} scripts found.",
            "magenta",
        )
        for script in scripts:
            save_script(script.contents)
    return True


def main():
    if not Path("js").exists():
        Path("js").mkdir()
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".html", "htm"])
    mpf3(process_file, files)


if __name__ == "__main__":
    main()
