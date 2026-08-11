from typing import Iterable, Callable, Dict, List

class DuplicateDetectionError(Exception):
    """
    Exception indicates an error during duplicate detection (e.g. hash/read failures).
    """
    pass

def find_duplicates(files: Iterable[str], hasher_fn: Callable[[str], str]) -> Dict[str, List[str]]:
    """
    Given an iterable of file paths and a file-hashing function, return a dict mapping
    hash values to lists of file paths, but only INCLUDE hashes which have >1 file (duplicates).

    All errors (file read/hash errors) are propagated (do NOT skip silently), so the caller may
    choose to handle or fail out as appropriate.

    Args:
        files: Iterable[str] -- file paths to check
        hasher_fn: Callable[[str], str] -- function to compute file hash

    Returns:
        Dict[str, List[str]]: mapping hash -> [file1, file2, ...], only for duplicate sets
    Raises:
        Same exceptions as hasher_fn (IO, FileHashError, etc.)
    """
    groups: Dict[str, List[str]] = {}
    for path in files:
        h = hasher_fn(path)  # Let failures propagate
        groups.setdefault(h, []).append(path)
    # Only keep entries where there is more than one file (duplicates only)
    dups = { k: v for k, v in groups.items() if len(v) > 1 }
    return dups
