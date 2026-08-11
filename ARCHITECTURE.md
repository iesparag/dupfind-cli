# Architecture

## Components

- **CLI Interface:** parses user arguments, validates inputs, and triggers scanning and reporting.
- **Scanner Module:** recursively walks a directory yielding file paths, filtering by minimum size, skipping unreadable files and symlinks.
- **Hasher Module:** provides hashing of files with support for SHA256(default), MD5, SHA1; reads files in chunks.
- **Detector Module:** groups files by hash to identify duplicates.
- **Output Module:** formats and prints duplicates in text or JSON format; handles empty or error states.

## Folder Structure

```
dupfind/
├── dupfind/          # source code package
│   ├── __init__.py
│   ├── cli.py
│   ├── scanner.py
│   ├── hasher.py
│   ├── detector.py
│   └── output.py
├── tests/            # unit + integration tests
│   ├── test_cli.py
│   ├── test_scanner.py
│   ├── test_hasher.py
│   └── test_detector.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Data Flow

1. CLI parses args: directory, min-size, hash algorithm, output format.
2. Validator ensures arguments valid, dir exists.
3. Scanner walks directory recursively, filters by min-size, yields files.
4. For each file, Hasher computes selected hash.
5. Detector groups files by hash to find duplicates.
6. Output module prints duplicates or suitable messages.

## Key Decisions

- Python chosen for CLI ease, widespread use.
- No persistent storage; all in-memory to keep it small.
- Use standard library only (argparse, hashlib, unittest) to reduce dependency overhead.
- Edges and errors handled via warnings to stderr; process continues as much as possible.
- Support text and JSON output for usability and scripting.

