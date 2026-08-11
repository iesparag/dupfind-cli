import unittest
from dupfind.detector import find_duplicates

class DummyHashError(Exception):
    pass

def make_hasher(mapping):
    """
    Helper: returns a fake hasher_fn accepting a filepath and returning a preset hash,
    or raising DummyHashError if not found.
    mapping: dict of filepath -> hash value (str)
    """
    def _hasher(f):
        if f in mapping:
            v = mapping[f]
            if isinstance(v, Exception):
                raise v
            else:
                return v
        raise DummyHashError(f"File: {f} not in mapping")
    return _hasher

class TestFindDuplicates(unittest.TestCase):
    def test_no_files(self):
        hasher = make_hasher({})
        self.assertEqual(find_duplicates([], hasher), {})

    def test_all_unique(self):
        files = ['a.txt', 'b.txt', 'c.txt']
        hasher = make_hasher({'a.txt': 'aaa', 'b.txt': 'bbb', 'c.txt': 'ccc'})
        self.assertEqual(find_duplicates(files, hasher), {})

    def test_simple_dup_pair(self):
        files = ['one', 'two', 'three']
        hashes = {'one': 'X', 'two': 'Y', 'three': 'X'}
        # one and three are dups
        hasher = make_hasher(hashes)
        result = find_duplicates(files, hasher)
        self.assertIn('X', result)
        self.assertEqual(set(result['X']), {'one', 'three'})
        # Only 'X' group appears, 'Y' has single file
        self.assertEqual(len(result), 1)

    def test_multiple_duplicate_sets(self):
        files = ['a','b','c','d','e']
        hashes = {'a':'X','b':'Y','c':'Y','d':'Z','e':'Z'}
        hasher = make_hasher(hashes)
        result = find_duplicates(files, hasher)
        self.assertCountEqual(list(result.keys()), ['Y','Z'])
        self.assertCountEqual(result['Y'], ['b', 'c'])
        self.assertCountEqual(result['Z'], ['d', 'e'])

    def test_triplet_duplicate(self):
        files = ['f1','f2','f3','g1']
        hashes = {'f1':'T', 'f2':'T', 'f3':'T', 'g1':'S'}
        hasher = make_hasher(hashes)
        result = find_duplicates(files, hasher)
        self.assertEqual(len(result), 1)
        self.assertEqual(set(result['T']), {'f1','f2','f3'})

    def test_error_propagation(self):
        files = ['ok1','fail','ok2']
        hashes = {'ok1':'A', 'fail': DummyHashError('boom'), 'ok2':'B'}
        hasher = make_hasher(hashes)
        with self.assertRaises(DummyHashError):
            _ = find_duplicates(files, hasher)
        # Ensure error propagates immediately, so 'ok2' is not processed at all
        # (Order is preserved)

    def test_duplicate_with_self(self):
        # Path repeated in input = counted as a duplicate (intentionally)
        files = ['foo','bar','foo']
        hashes = {'foo':'Z', 'bar':'Y'}
        hasher = make_hasher(hashes)
        res = find_duplicates(files, hasher)
        self.assertIn('Z', res)
        self.assertEqual(res['Z'].count('foo'), 2)

if __name__ == '__main__':
    unittest.main()
