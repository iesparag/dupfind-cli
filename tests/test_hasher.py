import os
import tempfile
import unittest
from dupfind.hasher import hash_file, FileHashError

class TestHashFile(unittest.TestCase):
    def setUp(self):
        # Create test files
        self.tempdir = tempfile.mkdtemp()
        # Text content
        self.f1_path = os.path.join(self.tempdir, "file1.txt")
        with open(self.f1_path, "w") as f:
            f.write("hello world\n")
        self.f2_path = os.path.join(self.tempdir, "file2.txt")
        with open(self.f2_path, "w") as f:
            f.write("hello world\n")  # Same as f1, should match
        self.f3_path = os.path.join(self.tempdir, "file3.txt")
        with open(self.f3_path, "w") as f:
            f.write("different content\n")
        # Large file (120 KB)
        self.large_path = os.path.join(self.tempdir, "large.bin")
        with open(self.large_path, "wb") as f:
            f.write(b"x" * 120 * 1024)
        # Empty file
        self.empty_path = os.path.join(self.tempdir, "empty.txt")
        open(self.empty_path, "w").close()
        
    def tearDown(self):
        # Remove files
        for fname in os.listdir(self.tempdir):
            p = os.path.join(self.tempdir, fname)
            try:
                os.remove(p)
            except Exception:
                pass
        os.rmdir(self.tempdir)

    def test_sha256_hash(self):
        h1 = hash_file(self.f1_path, "sha256")
        h2 = hash_file(self.f2_path, "sha256")
        self.assertEqual(h1, h2)
        h3 = hash_file(self.f3_path, "sha256")
        self.assertNotEqual(h1, h3)

    def test_md5_hash(self):
        h1 = hash_file(self.f1_path, "md5")
        h2 = hash_file(self.f2_path, "md5")
        self.assertEqual(h1, h2)
        h3 = hash_file(self.f3_path, "md5")
        self.assertNotEqual(h1, h3)

    def test_sha1_hash(self):
        h1 = hash_file(self.f1_path, "sha1")
        h2 = hash_file(self.f2_path, "sha1")
        self.assertEqual(h1, h2)
        h3 = hash_file(self.f3_path, "sha1")
        self.assertNotEqual(h1, h3)

    def test_large_file(self):
        # Ensure hashes for large file are correct and not crashy
        h_sha256 = hash_file(self.large_path, "sha256")
        h_md5 = hash_file(self.large_path, "md5")
        h_sha1 = hash_file(self.large_path, "sha1")
        # For fixed content, hash is deterministic
        self.assertIsInstance(h_sha256, str)
        self.assertIsInstance(h_md5, str)
        self.assertIsInstance(h_sha1, str)
        # Spot-check output length
        self.assertEqual(len(h_sha256), 64)
        self.assertEqual(len(h_md5), 32)
        self.assertEqual(len(h_sha1), 40)

    def test_empty_file_hashes(self):
        # Hash for empty file is always the same
        sha256 = hash_file(self.empty_path, "sha256")
        md5 = hash_file(self.empty_path, "md5")
        sha1 = hash_file(self.empty_path, "sha1")
        self.assertEqual(sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(md5, "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(sha1, "da39a3ee5e6b4b0d3255bfef95601890afd80709")

    def test_unsupported_algorithm(self):
        with self.assertRaises(FileHashError):
            hash_file(self.f1_path, "crc32")

    def test_file_not_found(self):
        fake_path = os.path.join(self.tempdir, "nope.txt")
        with self.assertRaises(FileHashError):
            hash_file(fake_path, "sha256")

    def test_unreadable_file(self):
        unreadable_path = os.path.join(self.tempdir, "unreadable.txt")
        with open(unreadable_path, "w") as f:
            f.write("abc")
        # Remove permissions
        os.chmod(unreadable_path, 0)
        try:
            with self.assertRaises(FileHashError):
                hash_file(unreadable_path, "sha256")
        finally:
            os.chmod(unreadable_path, 0o600)

if __name__ == "__main__":
    unittest.main()
