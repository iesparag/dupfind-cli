# Build plan

### 1. Setup project structure and dependencies
- Create repository folders.
- Create pyproject.toml for packaging.
- Create main source package and tests folder.
- Create basic CLI entrypoint placeholder.
- Add LICENSE (MIT) and README with install instructions.

### 2. Implement directory scanning
- Implement scanner.walk_directory(path: str) -> Iterator[str].
- Recursively scan, skip symlinks, handle unreadable files with warnings.
- Add unit tests with mock filesystem.

### 3. Implement file hashing utility
- Implement hasher.hash_file(filepath: str, algorithm: str) -> str.
- Support sha256 (default), md5, sha1.
- Read in chunks for large files.
- Handle IO errors gracefully.
- Add unit tests including empty and large virtual files.

### 4. Implement duplicate detection logic
- Implement detector.find_duplicates(files: Iterable[str], hasher_fn) -> Dict[str, List[str]].
- Group files by hash from hasher.
- Add unit tests with known hash sets.

### 5. Implement CLI argument parsing and input validation
- Use argparse in cli.py.
- Validate directory exists and is readable.
- Validate min-size is positive int.
- Validate hash algorithm choice.
- Validate output format.
- Handle errors with messages and exit codes.
- Add CLI tests for various arg combos and error states.

### 6. Implement output formatting and printing
- Implement output.print_duplicates(duplicates: dict, format: str).
- Format in text or JSON.
- If no duplicates, print appropriate message.
- Add tests validating output correctness.

### 7. Add error handling and edge case coverage
- Handle permissions errors when reading files.
- Warn on unreadable files, skip them.
- Handle empty directories gracefully.
- Handle unsupported hash algorithm error.
- Add integration tests for these scenarios.

### 8. Write integration tests
- Create temporary directories with files including duplicates.
- Run CLI end-to-end with assertions on output and exit code.
- Test permission denied files using mocks or chmod.

### 9. Add documentation and usage examples
- Complete README with detailed usage, examples, install, and test instructions.
- Include explanation of options and expected output.

