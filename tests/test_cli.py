import os
import sys
import tempfile
import shutil
import unittest
import io
from dupfind import cli

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

if __name__ == '__main__':
    unittest.main()
