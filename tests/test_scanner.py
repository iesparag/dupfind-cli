import os
import tempfile
import shutil
import stat
import sys
import io
import unittest

from dupfind.scanner import walk_directory

class TestWalkDirectory(unittest.TestCase):
    def setUp(self):
        # Create a temp directory tree
        self.tempdir = tempfile.mkdtemp()
        # Structure:
        # tempdir/
        #   file1.txt
        #   file2.txt
        #   subdir/
        #     file3.txt
        #   unreadable.txt
        #   link_to_file2 (symlink to file2.txt)
        #   subdir2/
        #   link_to_subdir (symlink to subdir)

        open(os.path.join(self.tempdir, 'file1.txt'), 'w').write('abc')
        open(os.path.join(self.tempdir, 'file2.txt'), 'w').write('def')
        subdir = os.path.join(self.tempdir, 'subdir')
        os.makedirs(subdir)
        open(os.path.join(subdir, 'file3.txt'), 'w').write('ghi')
        # Unreadable file
        unreadable_path = os.path.join(self.tempdir, 'unreadable.txt')
        open(unreadable_path, 'w').write('xxx')
        os.chmod(unreadable_path, 0)  # Remove all permissions
        # Symlink to file
        try:
            os.symlink(os.path.join(self.tempdir, 'file2.txt'), os.path.join(self.tempdir, 'link_to_file2'))
        except (AttributeError, NotImplementedError, OSError):
            # Symlinks not supported, skip
            pass
        # Empty dir
        os.makedirs(os.path.join(self.tempdir, 'subdir2'))
        # Symlink to dir
        try:
            os.symlink(subdir, os.path.join(self.tempdir, 'link_to_subdir'))
        except (AttributeError, NotImplementedError, OSError):
            pass

    def tearDown(self):
        # Fix permission so we can clean up
        unreadable_path = os.path.join(self.tempdir, 'unreadable.txt')
        if os.path.exists(unreadable_path):
            os.chmod(unreadable_path, stat.S_IWUSR | stat.S_IRUSR)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_scans_all_files_recursive(self):
        files = set(walk_directory(self.tempdir))
        expected = {
            os.path.join(self.tempdir, 'file1.txt'),
            os.path.join(self.tempdir, 'file2.txt'),
            os.path.join(self.tempdir, 'unreadable.txt'),
            os.path.join(self.tempdir, 'subdir', 'file3.txt'),
        }
        # Unreadable may not be listed if unable to access, so check subset
        self.assertTrue(expected - files in (set(), {os.path.join(self.tempdir, 'unreadable.txt')}))
        # Symlink file and symlink dir are not included
        self.assertFalse(any('link_to_file2' in f or 'link_to_subdir' in f for f in files))

    def test_unreadable_file_logs_warning(self):
        # Capture stderr
        unreadable_path = os.path.join(self.tempdir, 'unreadable.txt')
        # Remove all permissions
        os.chmod(unreadable_path, 0)
        stderr = io.StringIO()
        sys_stderr_orig = sys.stderr
        sys.stderr = stderr
        found = list(walk_directory(self.tempdir))
        sys.stderr = sys_stderr_orig
        output = stderr.getvalue()
        # Must report a warning for unreadable.txt OR skip it silently if not os.stat-able on some systems
        self.assertTrue('[WARNING]' in output or unreadable_path not in found)

    def test_symlink_files_skipped(self):
        # There should be no file in result with 'link_to_file2' or 'link_to_subdir' in name
        files = set(walk_directory(self.tempdir))
        self.assertFalse(any('link_to_file2' in f or 'link_to_subdir' in f for f in files))

    def test_empty_directory_outputs_none(self):
        # Create a new temp dir with no files
        temp_empty = tempfile.mkdtemp()
        files = list(walk_directory(temp_empty))
        self.assertEqual(files, [])
        shutil.rmtree(temp_empty)

if __name__ == '__main__':
    unittest.main()
