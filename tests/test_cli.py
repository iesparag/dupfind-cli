import os
import sys
import tempfile
import shutil
import unittest
import io
import contextlib
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
        import json
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

if __name__ == '__main__':
    unittest.main()
