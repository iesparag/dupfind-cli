import argparse
import sys


def main():
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
        '--hash', dest='hash_alg', default='sha256', choices=['sha256', 'md5', 'sha1'],
        help='Hash algorithm to use (sha256, md5, sha1). Default: sha256.'
    )
    parser.add_argument(
        '--format', dest='out_format', default='text', choices=['text', 'json'],
        help='Output format: text (default) or json.'
    )

    if ('-h' in sys.argv or '--help' in sys.argv) or len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    print(f"[DupFind] Scanning directory: {args.directory}")
    print(f"[DupFind] Minimum file size: {args.min_size} bytes")
    print(f"[DupFind] Hash algorithm: {args.hash_alg}")
    print(f"[DupFind] Output format: {args.out_format}")
    print('---\n(Basic CLI stub. Full duplicate search logic will be implemented in later versions.)')

if __name__ == '__main__':
    main()
