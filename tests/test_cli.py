import os
import sys
import tempfile
import shutil
import stat
import unittest
import io
import contextlib
import json
from dupfind import cli
from dupfind.output import print_duplicates

class TestCliArgParsing(unittest.TestCase):
    def setUp(self):
        # Create a temp directory structure
        self.tempdir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.tempdir, 'afile.txt')
        with open(self.file_path, 'w') as f:
            f.write('hello')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def run_cli_parse(self, argv):
        # Patch sys.argv with dummy program name + argv
        return cli.parse_args(argv)

    def test_accepts_valid_args_defaults(self):
        args = self.run_cli_parse([self.tempdir])
        self.assertEqual(args.directory, self.tempdir)
        self.assertEqual(args.min_size, 1)
        self.assertEqual(args.hash_alg, 'sha256')
        self.assertEqual(args.out_format, 'text')

    def test_accepts_valid_all_options(self):
        args = self.run_cli_parse([
            self.tempdir, '--min-size', '1024', '--hash', 'md5', '--format', 'json'])
        self.assertEqual(args.directory, self.tempdir)
        self.assertEqual(args.min_size, 1024)
        self.assertEqual(args.hash_alg, 'md5')
        self.assertEqual(args.out_format, 'json')

    def test_fails_if_directory_not_given(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_directory_does_not_exist(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args(['/no/such/dir'])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_path_is_file_not_dir(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([self.file_path])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_min_size_negative(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([self.tempdir, '--min-size', '-5'])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_min_size_zero(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([self.tempdir, '--min-size', '0'])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_min_size_not_integer(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([self.tempdir, '--min-size', 'abc'])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_hash_not_allowed(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([self.tempdir, '--hash', 'crc32'])
        self.assertEqual(e.exception.code, 2)

    def test_fails_if_format_not_allowed(self):
        with self.assertRaises(SystemExit) as e:
            cli.parse_args([self.tempdir, '--format', 'xml'])
        self.assertEqual(e.exception.code, 2)

    def test_help_output(self):
        # Simulate running with --help, expect help printed and sys.exit(0)
        saved = sys.argv
        sys.argv = ['cli.py', '--help']
        try:
            stderr = io.StringIO()
            stdout = io.StringIO()
            real_stdout, real_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = stdout, stderr
            with self.assertRaises(SystemExit) as ctx:
                # The CLI will print help and exit(0)
                cli.main()
            output = stdout.getvalue() + stderr.getvalue()
            self.assertIn('Identify duplicate files', output)
            self.assertEqual(ctx.exception.code, 0)
        finally:
            sys.stdout = real_stdout
            sys.stderr = real_stderr
            sys.argv = saved

    def test_help_output_no_args(self):
        # Simulate: $ python -m dupfind.cli (no args), should get help and exit 0
        saved = sys.argv
        sys.argv = ['cli.py']
        try:
            out = io.StringIO()
            real_stdout = sys.stdout
            sys.stdout = out
            with self.assertRaises(SystemExit) as ctx:
                cli.main()
            text = out.getvalue()
            self.assertIn('Usage:', text or '')  # argparse's help contains Usage
            self.assertEqual(ctx.exception.code, 0)
        finally:
            sys.stdout = real_stdout
            sys.argv = saved

class TestOutputFormatting(unittest.TestCase):
    def test_print_duplicates_text_empty(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_duplicates({}, format='text')
        out = buf.getvalue()
        self.assertIn('No duplicates found.', out)
        self.assertIn('Summary: 0 duplicate', out)

    def test_print_duplicates_json_empty(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_duplicates({}, format='json')
        out = buf.getvalue()
        self.assertIn('No duplicates found.', out)
        self.assertIn('Summary: 0 duplicate', out)

    def test_print_duplicates_text(self):
        dups = {
            'abcd1234': ['/foo/file1.txt', '/foo/file2.txt'],
            'deadbeef': ['/bar/imgA.png', '/bar/imgB.png']
        }
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_duplicates(dups, format='text')
        out = buf.getvalue()
        # Hash lines
        self.assertIn('Hash: abcd1234', out)
        self.assertIn('Hash: deadbeef', out)
        # File paths, indented
        self.assertIn('    /foo/file1.txt', out)
        self.assertIn('    /foo/file2.txt', out)
        self.assertIn('    /bar/imgA.png', out)
        self.assertIn('    /bar/imgB.png', out)
        # Summary
        self.assertIn('Summary: 2 duplicate sets found.', out)

    def test_print_duplicates_json(self):
        dups = {
            'abcd1234': ['/foo/file1.txt', '/foo/file2.txt'],
            'deadbeef': ['/bar/imgA.png', '/bar/imgB.png', '/bar/imgC.png']
        }
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_duplicates(dups, format='json')
        out = buf.getvalue()
        output_json_portion = out.split('Summary:')[0].strip()
        js = json.loads(output_json_portion)
        self.assertIn('abcd1234', js)
        self.assertIn('deadbeef', js)
        self.assertEqual(set(js['abcd1234']), {'/foo/file1.txt', '/foo/file2.txt'})
        self.assertEqual(set(js['deadbeef']), {'/bar/imgA.png', '/bar/imgB.png', '/bar/imgC.png'})
        self.assertIn('Summary: 2 duplicate sets found.', out)

    def test_print_duplicates_text_pluralization(self):
        dups = {
            'abcd1234': ['/foo/file1.txt', '/foo/file2.txt']
        }
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_duplicates(dups, format='text')
        out = buf.getvalue()
        # 'set' not 'sets'
        self.assertIn('Summary: 1 duplicate set found.', out)

    def test_print_duplicates_json_pluralization(self):
        dups = {
            'abcdef': ['/bar/a', '/bar/b']
        }
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_duplicates(dups, format='json')
        out = buf.getvalue()
        self.assertIn('Summary: 1 duplicate set found.', out)

    def test_print_duplicates_invalid_format(self):
        dups = {
            'h': ['/x', '/y']
        }
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), io.StringIO() as errbuf, contextlib.redirect_stderr(errbuf):
            print_duplicates(dups, 'xml')
            err_out = errbuf.getvalue()
        out = buf.getvalue()
        self.assertIn('Output format not supported', out or err_out)
        self.assertIn('Summary: 0 duplicate sets found.', out)

##############################################
# INTEGRATION TESTS: END-TO-END CLI SCENARIOS
##############################################
import subprocess

class TestEndToEndIntegration(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        # Create files:
        #   a.txt, a2.txt   (duplicates)
        #   b.txt           (unique)
        #   subdir1/c.txt, subdir2/d.txt
        #   e.txt, e_dupe.txt (duplicates, different content than a.txt)
        #   f.txt (empty)
        #   unread.txt (unreadable on POSIX)
        #   linkfile.txt (symlink to a.txt, should be skipped)
        self.f1 = os.path.join(self.tempdir, 'a.txt')
        self.f2 = os.path.join(self.tempdir, 'a2.txt')
        with open(self.f1, 'w') as f:
            f.write('dupe content')
        with open(self.f2, 'w') as f:
            f.write('dupe content')
        self.f3 = os.path.join(self.tempdir, 'b.txt')
        with open(self.f3, 'w') as f:
            f.write('unique content')
        sub1 = os.path.join(self.tempdir, 'subdir1')
        sub2 = os.path.join(self.tempdir, 'subdir2')
        os.mkdir(sub1)
        os.mkdir(sub2)
        self.f4 = os.path.join(sub1, 'c.txt')
        self.f5 = os.path.join(sub2, 'd.txt')
        with open(self.f4, 'w') as f:
            f.write('something else')
        with open(self.f5, 'w') as f:
            f.write('unique again')
        self.f6 = os.path.join(self.tempdir, 'e.txt')
        self.f7 = os.path.join(self.tempdir, 'e_dupe.txt')
        with open(self.f6, 'w') as f:
            f.write('barley pop')
        with open(self.f7, 'w') as f:
            f.write('barley pop')
        # Empty file
        self.f8 = os.path.join(self.tempdir, 'f.txt')
        open(self.f8, 'w').close()
        # Unreadable file
        self.f9 = os.path.join(self.tempdir, 'unread.txt')
        with open(self.f9, 'w') as f:
            f.write('no read')
        try:
            os.chmod(self.f9, 0)
            self._needs_fix_unread = True
        except Exception:
            self._needs_fix_unread = False
        # Symlink (if supported)
        self.f10 = os.path.join(self.tempdir, 'linkfile.txt')
        try:
            os.symlink(self.f1, self.f10)
        except (AttributeError, NotImplementedError, OSError):
            pass

    def tearDown(self):
        def _fixperm(p):
            try:
                os.chmod(p, stat.S_IWUSR | stat.S_IRUSR)
            except Exception:
                pass
        if hasattr(self, '_needs_fix_unread') and self._needs_fix_unread:
            _fixperm(self.f9)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def run_cli_module(self, args, expect_code=0):
        # Run using current python interpreter in-module mode
        cmd = [sys.executable, '-m', 'dupfind.cli'] + args
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        if proc.returncode != expect_code:
            print(f"STDOUT: {out}")
            print(f"STDERR: {err}")
        self.assertEqual(proc.returncode, expect_code)
        return out, err

    def test_find_duplicates_default_options(self):
        # Should find two duplicate sets: {a.txt,a2.txt}, {e.txt,e_dupe.txt}
        out, err = self.run_cli_module([self.tempdir])
        # Text output contains both sets
        self.assertIn('Hash:', out)
        self.assertIn('a.txt', out)
        self.assertIn('a2.txt', out)
        self.assertIn('e.txt', out)
        self.assertIn('e_dupe.txt', out)
        self.assertIn('Summary: 2 duplicate sets found.', out)
        # Symlink should not occur
        self.assertNotIn('linkfile.txt', out)
        # Unreadable file warning on stderr (optional on some systems)
        if os.name != 'nt':
            self.assertTrue(
                'unread.txt' in err or self.f9 not in out)

    def test_find_duplicates_json_output(self):
        out, err = self.run_cli_module([self.tempdir, '--format', 'json'])
        # Should be valid json followed by summary
        pieces = out.split('Summary:')
        js = pieces[0].strip()
        data = json.loads(js)
        # Should have two duplicate sets
        self.assertEqual(len(data), 2)
        flatvals = sum((v for v in data.values()), [])
        expect_dupe = sorted([os.path.join(self.tempdir, 'a.txt'), os.path.join(self.tempdir, 'a2.txt')])
        found = [p for p in flatvals if os.path.basename(p) in ('a.txt','a2.txt')]
        self.assertEqual(sorted(found), expect_dupe)
        self.assertIn('Summary: 2 duplicate sets found.', out)

    def test_min_size_excludes_small(self):
        # All files <12 bytes (except 'a.txt','a2.txt','e.txt','e_dupe.txt')
        # Exclude those unless min-size=20
        out, err = self.run_cli_module([self.tempdir, '--min-size', '20'])
        # No files big enough for duplicates
        self.assertIn('No duplicates found.', out)
        self.assertIn('Summary: 0 duplicate sets found.', out)

    def test_no_duplicates(self):
        # Remove one of e_dupe.txt to only have one set
        os.remove(self.f2)
        os.remove(self.f7)
        out, err = self.run_cli_module([self.tempdir])
        # Now only one set (a.txt & e.txt are both unique)
        self.assertTrue('No duplicates found.' in out or 'Summary: 0 duplicate sets found.' in out)

    def test_empty_dir(self):
        # New empty dir
        emptydir = tempfile.mkdtemp()
        out, err = self.run_cli_module([emptydir])
        self.assertIn('No files found.', out)
        shutil.rmtree(emptydir)

    def test_permission_errors(self):
        # Should WARN on unreadable file, but still process others, and not crash
        out, err = self.run_cli_module([self.tempdir])
        # If error reported, must mention 'WARNING' and the file
        if os.name != 'nt':
            self.assertTrue('WARNING' in err or not os.access(self.f9, os.R_OK))

    def test_invalid_hash_algorithm(self):
        out, err = self.run_cli_module([self.tempdir, '--hash', 'crc32'], expect_code=2)
        self.assertIn('hash must be one of', err)

    def test_invalid_format(self):
        out, err = self.run_cli_module([self.tempdir, '--format', 'xml'], expect_code=2)
        self.assertIn('format must be one of', err)

    def test_invalid_directory(self):
        out, err = self.run_cli_module(['/no/such/dir'], expect_code=2)
        self.assertIn('Directory does not exist', err)

    def test_file_as_directory(self):
        out, err = self.run_cli_module([
            os.path.join(self.tempdir, 'a.txt')], expect_code=2)
        self.assertIn('Path is not a directory', err)

    def test_min_size_zero(self):
        out, err = self.run_cli_module([self.tempdir, '--min-size', '0'], expect_code=2)
        self.assertIn('min-size must be a positive integer', err)

    def test_help_option(self):
        out, err = self.run_cli_module(['--help'], expect_code=0)
        self.assertIn('Identify duplicate files', out)
        self.assertIn('directory', out)

if __name__ == '__main__':
    unittest.main()
