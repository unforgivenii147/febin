#!/usr/bin/env bash
#
# mypy_strict_check.sh
# ---------------------
# Helper used for the task: "fix any errors (ignore-missing-imports) in the
# Python files of this repo and save fully annotated / documented code in place".
#
# What it does
# ============
#   1. Discovers every REAL Python file in the repository root, i.e. regular
#      files ending in ".py".  Symbolic links (there are ~560 of them, each
#      pointing at a ".py" file) and everything under ".git" are skipped, as
#      requested.
#   2. Runs mypy on each file individually with:
#         --ignore-missing-imports  -> third-party / termux-only modules such as
#                                      `dh`, `regex`, `termcolor`, `PIL` ... are
#                                      not installed here, so their imports are
#                                      suppressed (this is the requested flag).
#         --strict                  -> demands full annotations, so the code can
#                                      be brought up to a fully-typed standard.
#   3. Prints a per-file error count and a grand total so progress can be
#      tracked while files are annotated in batches.
#
# Findings (recorded in arena/REPORT.md):
#   * Under plain `mypy --ignore-missing-imports` the repo already has ZERO
#     errors -- the only diagnostics that ever appear are missing-import ones,
#     which that flag exists to silence.  So the *strict* bar below is what
#     actually surfaces work (missing annotations, undefined names, etc.).
#
# Usage
# =====
#   arena/mypy_strict_check.sh            # check every real .py file
#   arena/mypy_strict_check.sh a.py b.py  # check only the given files
#
set -euo pipefail

# Resolve the repository root (this script lives in <root>/arena).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Run mypy through the interpreter so it works even when the console script
# shim is not on PATH.
MYPY=(python3 -m mypy --strict --ignore-missing-imports --no-error-summary)

# Build the file list: explicit args, or every non-symlink *.py at the root.
if [[ "$#" -gt 0 ]]; then
    mapfile -t FILES < <(printf '%s\n' "$@")
else
    mapfile -t FILES < <(find . -maxdepth 1 -type f -name '*.py' ! -path './.git/*' | sort)
fi

total=0
bad_files=0
for f in "${FILES[@]}"; do
    out="$("${MYPY[@]}" "$f" 2>&1 || true)"
    n="$(printf '%s\n' "$out" | grep -c ': error:' || true)"
    if [[ "$n" -gt 0 ]]; then
        printf '%4d  %s\n' "$n" "$f"
        printf '%s\n' "$out" | sed 's/^/        /'
        bad_files=$((bad_files + 1))
    fi
    total=$((total + n))
done

echo "--------------------------------------------------"
echo "files checked : ${#FILES[@]}"
echo "files w/ errs : ${bad_files}"
echo "total errors  : ${total}"
