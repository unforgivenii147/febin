#!/data/data/com.termux/files/usr/bin/python
"""Watch the current directory and print filesystem changes as they happen.

Thin wrapper around :func:`watchfiles.watch`; runs until interrupted, printing
each batch of change events to stdout.
"""

from collections.abc import Iterable

from watchfiles import watch

if __name__ == "__main__":
    # ``watch`` yields a set of (Change, path) tuples for every batch of events.
    changes: Iterable[object]
    for changes in watch("."):
        print(changes)
