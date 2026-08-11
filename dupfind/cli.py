import argparse
import sys
import os
from dupfind import scanner, hasher, detector, output

def error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(2)

ALLOWED_HASH = ['sha256', 'md5', 'sha1']
ALLOWED_FORMAT = ['text', 'json']

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='DupFind: Identify duplicate files in a directory recursively.'
    )
    parser.add_argument(
        'directory', nargs='?', default=None, help='Target directory to search for duplicates.'
    )
    parser.add_argument(
        '--min-size', type=int, default=1,
        help='Ignore files smaller than this size in bytes (default: 1)'
    )
    parser.add_argument(
        '--hash', dest='hash_alg', default='sha256', choices=ALLOWED_HASH,
        help='Hash algorithm to use (sha256, md5, sha1). Default: sha256.'
    )
    parser.add_argument(
        '--format', dest='out_format', default='text', choices=ALLOWED_FORMAT,
        help='Output format: text (default) or json.'
    )
    args = parser.parse_args(argv)
    # Argument validation
    if not args.directory:
        error("No directory specified. Please provide a directory path.")
    if not os.path.exists(args.directory):
        error(f"Directory does not exist: {args.directory}")
    if not os.path.isdir(args.directory):
        error(f"Path is not a directory: {args.directory}")
    if args.min_size is None or not isinstance(args.min_size, int) or args.min_size < 1:
        error("--min-size must be a positive integer (>= 1).")
    if args.hash_alg not in ALLOWED_HASH:
        error(f"--hash must be one of: {', '.join(ALLOWED_HASH)}")
    if args.out_format not in ALLOWED_FORMAT:
        error(f"--format must be one of: {', '.join(ALLOWED_FORMAT)}")
    return args

def main():
    # If called as script with no args or only --help, let argparse handle it
    if ('-h' in sys.argv or '--help' in sys.argv) or len(sys.argv) == 1:
        parser = argparse.ArgumentParser(
            description='DupFind: Identify duplicate files in a directory recursively.'
        )
        parser.add_argument('directory', nargs='?', default=None, help='Target directory to search for duplicates.')
        parser.add_argument('--min-size', type=int, default=1, help='Ignore files smaller than this size in bytes (default: 1)')
        parser.add_argument('--hash', dest='hash_alg', default='sha256', choices=ALLOWED_HASH,
                            help='Hash algorithm to use (sha256, md5, sha1). Default: sha256.')
        parser.add_argument('--format', dest='out_format', default='text', choices=ALLOWED_FORMAT,
                            help='Output format: text (default) or json.')
        parser.print_help()
        sys.exit(0)

    args = parse_args()

    print(f"[DupFind] Scanning directory: {args.directory}")
    print(f"[DupFind] Minimum file size: {args.min_size} bytes")
    print(f"[DupFind] Hash algorithm: {args.hash_alg}")
    print(f"[DupFind] Output format: {args.out_format}")

    # 1. Scan for candidate files, recursively, skipping symlinks
    found_files = []
    for file_path in scanner.walk_directory(args.directory):
        try:
            if not os.path.isfile(file_path):
                continue
            try:
                size = os.path.getsize(file_path)
            except OSError as e:
                print(f"[WARNING] Cannot access file size: {file_path}: {e}", file=sys.stderr)
                continue
            if size < args.min_size:
                continue
            found_files.append(file_path)
        except Exception as e:
            print(f"[WARNING] Error checking file: {file_path}: {e}", file=sys.stderr)
            continue
    if not found_files:
        print("No files found.")
        return
    # 2. Hash files, with permission/IO error handling, skipping on error
    hash_results = []
    for fpath in found_files:
        try:
            digest = hasher.hash_file(fpath, args.hash_alg)
            hash_results.append((digest, fpath))
        except hasher.FileHashError as e:
            print(f"[WARNING] Failed to hash file: {fpath}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[WARNING] Unexpected error hashing file: {fpath}: {e}", file=sys.stderr)
    if not hash_results:
        print("No files found.")
        return
    # 3. Group and detect duplicates
    from collections import defaultdict
    hash_to_files = defaultdict(list)
    for digest, path in hash_results:
        hash_to_files[digest].append(path)
    # Only duplicates (more than one file per hash)
    duplicates = {h: lst for h, lst in hash_to_files.items() if len(lst) > 1}
    # 4. Print results
    output.print_duplicates(duplicates, format=args.out_format)

if __name__ == '__main__':
    main()
