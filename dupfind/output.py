import sys
import json
from typing import Dict, List

def print_duplicates(duplicates: Dict[str, List[str]], format: str = 'text'):
    """
    Print the duplicate files grouped by hash in the specified format.
    - Text: List hash and indent files.
    - JSON: { hash1: [file1, ...], ... }
    - If no duplicates, print suitable message and return.
    - Always print a summary line with the count of duplicate sets.

    Args:
        duplicates (Dict[str, List[str]]): dict of hash -> list of file paths.
        format (str): Output format ('text' or 'json').
    """
    if not duplicates or len(duplicates) == 0:
        print("No duplicates found.")
        print("Summary: 0 duplicate sets found.")
        return

    if format == 'text':
        total_sets = 0
        for digest, files in sorted(duplicates.items()):
            print(f"Hash: {digest}")
            for fpath in sorted(files):
                print(f"    {fpath}")
            total_sets += 1
        print(f"Summary: {total_sets} duplicate set{'s' if total_sets != 1 else ''} found.")
    elif format == 'json':
        # Dump hashes as keys, sorted by key for stable output, pretty print
        print(json.dumps({k: files for k, files in sorted(duplicates.items())}, indent=2))
        print(f"Summary: {len(duplicates)} duplicate set{'s' if len(duplicates) != 1 else ''} found.")
    else:
        print(f"[ERROR] Output format not supported: {format}", file=sys.stderr)
        print("Summary: 0 duplicate sets found.")
