import os
import sys
from typing import Iterator


def walk_directory(path: str) -> Iterator[str]:
    """
    Recursively yield file paths under the given directory, skipping symlinks.
    Unreadable files or directories are logged as warnings to stderr.

    Args:
        path (str): Root directory path to start scanning.

    Yields:
        str: Path to a regular file.
    """
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    # Skip any symlinks (to dir or file)
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        # Recurse into subdirectory
                        yield from walk_directory(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        yield entry.path
                except PermissionError as e:
                    print(f"[WARNING] Cannot access entry: {entry.path}: {e}", file=sys.stderr)
                except OSError as e:
                    print(f"[WARNING] OSError for entry: {entry.path}: {e}", file=sys.stderr)
    except PermissionError as e:
        print(f"[WARNING] Cannot access directory: {path}: {e}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"[WARNING] Directory not found: {path}: {e}", file=sys.stderr)
