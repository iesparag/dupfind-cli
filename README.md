# DupFind CLI

DupFind is a command-line tool to identify and manage duplicate files in directory trees. It helps recover disk space and keep your storage organized by reporting duplicate files via fast content hashing.

## Goals
- **Find byte-for-byte duplicate files** in any directory, recursively
- **Support SHA256, MD5, SHA1** hashing (default: SHA256)
- **Exclude small/trivial files** with `--min-size` option
- **User-friendly CLI**: progress, formatted output (text or JSON)
- **Robust**: handles unreadable files and reports errors gracefully

## Requirements
- **Python >= 3.7**

## Installation

Clone the repository:
```sh
git clone https://github.com/iesparag/dupfind-cli.git
cd dupfind-cli
```

Install using `pip`:
```sh
pip install .
```

Or for development (editable install):
```sh
pip install -e .
```

No external dependencies are required. DupFind uses only the Python standard library.

## Usage

Run DupFind on a directory, printing all sets of files that are byte-for-byte identical:

```
python -m dupfind.cli /path/to/dir [OPTIONS]
```

Or, after install:
```
dupfind /path/to/dir [OPTIONS]
```

View help:
```
python -m dupfind.cli --help
```

**Common example:**
```
python -m dupfind.cli ~/Downloads --min-size 4096 --hash sha1 --format text
```

### Arguments and Options

| Positional / Option  | Description                                                                           |
|---------------------|---------------------------------------------------------------------------------------|
| `directory`         | Directory path to scan for duplicates                                                 |
| `--min-size`        | Ignore files smaller than this many bytes (default: 1)                                |
| `--hash`            | Content hash algorithm (`sha256`, `md5`, `sha1`), default is `sha256`                 |
| `--format`          | Output format (`text` or `json`), default is `text`                                   |

- Any unreadable files are skipped with a warning.
- Symlinked files or directories are ignored (no infinite loops).

#### Example command lines and outputs

##### Find all duplicates in the `~/Documents` folder:
```
python -m dupfind.cli ~/Documents
```

_Sample output:_
```
[DupFind] Scanning directory: /Users/you/Documents
[DupFind] Minimum file size: 1 bytes
[DupFind] Hash algorithm: sha256
[DupFind] Output format: text
Hash: a9993e364706816aba3e25717850c26c9cd0d89d
    /Users/you/Documents/file1.txt
    /Users/you/Documents/notes/file1_copy.txt
Hash: 595f49e6a0d3c76e34ebc7619e38e4c1a17e3bce204e04816aef2d8dc77a46ef
    /Users/you/Documents/reports/report.docx
    /Users/you/Documents/archives/report_copy.docx
Summary: 2 duplicate sets found.
```

##### Ignore tiny files (under 10 KB), print as JSON:
```
python -m dupfind.cli ~/Pictures --min-size 10240 --format json
```
_Sample output:_
```
{
  "1ca04e6a322a51e0a711f1297ffbe08b9ef4fd9a16ccd1b7a9ae3c2b9a1d5108": [
    "/Users/you/Pictures/img1.jpg",
    "/Users/you/Pictures/old/img1_copy.jpg"
  ]
}
Summary: 1 duplicate set found.
```

##### Use MD5 for fastest hashing (less secure), show help:
```
python -m dupfind.cli --help
```
_Output:_
```
usage: cli.py [-h] [--min-size MIN_SIZE] [--hash {sha256,md5,sha1}] [--format {text,json}] directory

DupFind: Identify duplicate files in a directory recursively.

positional arguments:
  directory            Target directory to search for duplicates.

optional arguments:
  -h, --help           show this help message and exit
  --min-size MIN_SIZE  Ignore files smaller than this size in bytes (default: 1)
  --hash {sha256,md5,sha1}
                       Hash algorithm to use (sha256, md5, sha1). Default: sha256.
  --format {text,json} Output format: text (default) or json.
```

#### Exit codes

| Code | Meaning                          |
|------|----------------------------------|
| 0    | Completed successfully           |
| 2    | Input/argument error (fatal)     |

#### Error and edge case handling
- Unreadable files: warning to stderr, skipped
- Directory does not exist: fatal error, exit code 2
- No files: prints "No files found."
- No duplicates: prints "No duplicates found." and summary
- Symlinks: always skipped
- Unsupported hash/format: error and usage info

## Testing

Tests cover scanning, hashing, duplicate detection, CLI parsing, output, and integration.

Run all tests using `unittest`:
```sh
python -m unittest discover tests
```
(Alternatively, run `python -m unittest tests.test_cli` or any other individual test file.)

All provided tests must pass on Python 3.7+.

## Project Structure

```
dupfind/
├── dupfind/          # Python package (main app)
│   ├── cli.py        # CLI entrypoint
│   ├── scanner.py    # Directory scan logic
│   ├── hasher.py     # File hashing utilities
│   ├── detector.py   # Duplicate detection logic
│   └── output.py     # Output formatting
├── tests/            # Unit and integration tests
├── pyproject.toml    # Build & packaging config
├── LICENSE
├── README.md
└── .gitignore
```

## Examples

##### Find duplicates in current directory and subdirectories:
```
python -m dupfind.cli .
```

##### Only consider files at least 1 MB in size, use MD5 hash:
```
python -m dupfind.cli . --min-size 1048576 --hash md5
```

##### Output JSON for scripting, scan `/data`:
```
python -m dupfind.cli /data --format json
```

## Limitations
- Processes all candidate files in memory
- Does not follow symlinks for safety reasons
- Only considers files that are fully readable
- No file deletion/removal functionality (report only)

## License
MIT License; see [LICENSE](LICENSE)

## Development
- No external dependencies required (standard library only)
- Compatible with Windows, macOS, and Linux

## Design
See the top comments in [`cli.py`](dupfind/cli.py) and [`scanner.py`](dupfind/scanner.py) for architecture and edge case handling rationale.

## Contributing
Issues and pull requests welcome!

## FAQ

**Is the output always deterministic?**
- Yes, duplicates are sorted by hash and file path.

**How can I remove duplicates?**
- This tool only reports duplicates. Use `xargs rm`, manual review, or another tool for deletion.

**Is it fast for large folders?**
- Relatively fast due to chunked hashing, though for huge datasets consider more advanced tools.

**Minimum Python version?**
- Python 3.7 or later.

---