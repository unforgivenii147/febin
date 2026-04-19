#!/data/data/com.termux/files/usr/bin/python

import argparse
import fnmatch
import operator
import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import regex as re
from dh import get_files, is_binary

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
}
BINARY_CHUNK = 32768
DEFAULT_THREADS = 8
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"
ANSI_HIGHLIGHT = "\033[31m"


def colorize(
    text: str,
    start: int,
    end: int,
    enable: bool = True,
) -> str:
    if not enable:
        return text
    return text[:start] + ANSI_HIGHLIGHT + ANSI_BOLD + text[start:end] + ANSI_RESET + text[end:]


def matches_any_glob(path: str, patterns: Iterable[str]) -> bool:
    basename = Path(path).name
    return any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch(basename, p) for p in patterns)


def search_file_text_mode(
    path: str,
    regex: re.Pattern | None,
    fixed: str | None,
    ignore_case: bool,
    show_line_numbers: bool,
    color: bool,
    max_matches: int | None = None,
) -> tuple[
    str,
    list[tuple[int, str, list[tuple[int, int]]]],
]:
    matches = []
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.rstrip("\n")
                spans: list[tuple[int, int]] = []
                if regex:
                    spans.extend((m.start(), m.end()) for m in regex.finditer(line))
                else:
                    hay = line.lower() if ignore_case else line
                    needle = fixed.lower() if ignore_case else fixed
                    start = 0
                    while True:
                        idx = hay.find(needle, start)
                        if idx == -1:
                            break
                        spans.append((
                            idx,
                            idx + len(needle),
                        ))
                        start = idx + max(1, len(needle))
                if spans:
                    matches.append((lineno, line, spans))
                    if max_matches and len(matches) >= max_matches:
                        break
    except Exception:
        return path, []
    return path, matches


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ripgrep-like recursive search in Python")
    p.add_argument(
        "pattern",
        nargs="?",
        help="Regex pattern (positional) or use -e",
    )
    p.add_argument(
        "-e",
        "--regexp",
        dest="pattern_e",
        help="Pattern (alternative to positional)",
    )
    p.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Case-insensitive search",
    )
    p.add_argument(
        "--fixed-strings",
        action="store_true",
        default=True,
        help="Fixed string search (no regex)",
    )
    p.add_argument(
        "-n",
        "--line-number",
        default=True,
        action="store_true",
        help="Show line numbers",
    )
    p.add_argument(
        "-l",
        "--files-with-matches",
        action="store_true",
        help="Only print filenames that match",
    )
    p.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Print count of matches per file",
    )
    p.add_argument(
        "-t",
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
        help="Number of worker threads",
    )
    p.add_argument(
        "-H",
        "--hidden",
        action="store_true",
        default=True,
        help="Search hidden files and directories",
    )
    p.add_argument(
        "-g",
        "--glob",
        action="append",
        help="Include glob (fnmatch); can be repeated",
    )
    p.add_argument(
        "-x",
        "--exclude",
        action="append",
        help="Exclude glob (fnmatch); can be repeated",
    )
    p.add_argument(
        "-C",
        "--no-color",
        action="store_true",
        help="Disable colorized output",
    )
    p.add_argument(
        "-m",
        "--max-filesize",
        type=int,
        default=10_000_000,
        help="Skip files larger than size (bytes)",
    )
    p.add_argument(
        "-F",
        "--follow",
        action="store_true",
        help="Follow symlinks",
    )
    p.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to search (default: .)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    cwd = Path.cwd()
    args = build_argparser().parse_args(argv)
    pattern = args.pattern_e or args.pattern
    if not pattern:
        print(
            "No pattern provided. Use positional PATTERN or -e PATTERN.",
            file=sys.stderr,
        )
        return 2
    ignore_case = args.ignore_case
    fixed = args.fixed_strings
    compiled = None
    if not fixed:
        flags = re.MULTILINE
        if ignore_case:
            flags |= re.IGNORECASE
        try:
            compiled = re.compile(pattern, flags)
        except re.error as ex:
            print(
                f"Invalid regex: {ex}",
                file=sys.stderr,
            )
            return 2
    include_globs = args.glob or []
    exclude_globs = args.exclude or []
    candidates = get_files(cwd, include_hidden=True)
    if not candidates:
        return 0
    color = not args.no_color and sys.stdout.isatty()
    any_match = False
    results_per_file = {}

    def worker(path: str):
        if is_binary(path):
            return path, []
        return search_file_text_mode(
            path,
            regex=compiled,
            fixed=pattern if fixed else None,
            ignore_case=ignore_case,
            show_line_numbers=args.line_number,
            color=color,
        )

    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(worker, p): p for p in candidates}
        try:
            for fut in as_completed(futures):
                path, matches = fut.result()
                if not matches:
                    continue
                any_match = True
                results_per_file[path] = matches
                if args.files_with_matches:
                    print(path)
                elif args.count:
                    print(f"{path}:{len(matches)}")
                else:
                    for (
                        lineno,
                        line,
                        spans,
                    ) in matches:
                        out_line = line
                        if color and spans:
                            for s, e in sorted(
                                spans,
                                key=operator.itemgetter(0),
                                reverse=True,
                            ):
                                out_line = colorize(
                                    out_line,
                                    s,
                                    e,
                                    enable=True,
                                )
                        if args.line_number:
                            print(f"{path}:{lineno}:{out_line}")
                        else:
                            print(f"{path}:{out_line}")
        except KeyboardInterrupt:
            print(
                "\nSearch cancelled.",
                file=sys.stderr,
            )
            return 130
    return 0 if any_match else 1


if __name__ == "__main__":
    sys.exit(main())
