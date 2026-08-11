import hashlib
import os

class FileHashError(Exception):
    """
    Specific exception for file hash failures (IO or unsupported alg).
    """
    pass

SUPPORTED_ALGORITHMS = {"sha256", "md5", "sha1"}
CHUNK_SIZE = 65536  # 64KB

def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    """
    Compute the hash digest of a file using a specified algorithm.

    Args:
        filepath (str): Path to the file to hash.
        algorithm (str): Hash algorithm to use ('sha256', 'md5', or 'sha1').
    Returns:
        str: Hexadecimal hash digest string.
    Raises:
        FileHashError: if the file cannot be read or algorithm not supported.
    """
    # Validate algorithm parameter
    algorithm = algorithm.lower()
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise FileHashError(f"Unsupported hash algorithm: {algorithm}")
    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        raise FileHashError(f"Unsupported hash algorithm: {algorithm}")
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, IOError) as e:
        raise FileHashError(f"Failed to read file for hashing: {filepath}: {e}")
