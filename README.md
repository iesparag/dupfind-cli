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

From source (cloned repo):
```sh
pip install .
```

Or for development (editable install):
```sh
pip install -e .
```

## Usage

```
python -m dupfind.cli --help
```

Example:
```
python -m dupfind.cli /path/to/dir --min-size 1024 --hash sha256 --format json
```

### Arguments/Options
- `directory` (positional): Directory path to scan for duplicates
- `--min-size`: Ignore files smaller than this many bytes (default 1)
- `--hash`: Content hash algorithm (`sha256`, `md5`, `sha1`), default is `sha256`
- `--format`: Output format (`text` or `json`), default is `text`

## Project Structure

```
dupfind/
├── dupfind/          # Python package
│   ├── __init__.py
│   └── cli.py        # CLI entrypoint
├── tests/            # Unit/integration tests
├── pyproject.toml    # Build & packaging config
├── LICENSE
├── README.md
└── .gitignore
```

## Tests

Tests are placed in `tests/`. To run all tests:
```sh
python -m unittest discover tests
```

## License
MIT License; see [LICENSE](LICENSE)

---

## Design/Development Notes
- No third-party dependencies: uses only Python standard library (argparse for opt parsing, hashlib for content hashing, unittest for tests).
- The actual duplicate scanning logic will be implemented and tested in future commits.
- Fully cross-platform; just needs Python >= 3.7.
