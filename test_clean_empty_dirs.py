#!/usr/bin/env python3
"""clean_empty_dirs.py 测试套件"""

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from clean_empty_dirs import clean_empty_directories, is_empty_directory, parse_args


def _make_root(tmpdir):
    root = Path(tmpdir) / 'root'
    root.mkdir()
    (root / '.anchor').write_text('keep')
    return root


class TestIsEmptyDirectory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name) / 'root'
        self.root.mkdir()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_truly_empty(self):
        d = self.root / 'empty'
        d.mkdir()
        self.assertTrue(is_empty_directory(d))

    def test_contains_file(self):
        d = self.root / 'has_file'
        d.mkdir()
        (d / 'file.txt').write_text('hello')
        self.assertFalse(is_empty_directory(d))

    def test_contains_ds_store(self):
        d = self.root / 'ds_store'
        d.mkdir()
        (d / '.DS_Store').write_text('x')
        self.assertTrue(is_empty_directory(d))

    def test_contains_ignored_dir(self):
        d = self.root / 'with_ignored'
        d.mkdir()
        (d / '.workbuddy').mkdir()
        self.assertTrue(is_empty_directory(d, {'.workbuddy'}))

    def test_ignored_dir_with_files(self):
        d = self.root / 'with_ignored_files'
        d.mkdir()
        wb = d / '.workbuddy'
        wb.mkdir()
        (wb / 'config.json').write_text('{}')
        self.assertTrue(is_empty_directory(d, {'.workbuddy'}))

    def test_contains_non_ignored_nonempty_subdir(self):
        d = self.root / 'parent'
        d.mkdir()
        sub = d / 'sub'
        sub.mkdir()
        (sub / 'file.txt').write_text('x')
        self.assertFalse(is_empty_directory(d))

    def test_contains_empty_subdir(self):
        d = self.root / 'parent'
        d.mkdir()
        (d / 'sub').mkdir()
        self.assertTrue(is_empty_directory(d))

    def test_contains_symlink_file(self):
        d = self.root / 'with_symlink'
        d.mkdir()
        target = self.root / 'target.txt'
        target.write_text('x')
        (d / 'link').symlink_to(target)
        self.assertFalse(is_empty_directory(d))

    def test_is_symlink_itself(self):
        d = self.root / 'real'
        d.mkdir()
        link = self.root / 'link'
        link.symlink_to(d)
        self.assertFalse(is_empty_directory(link))

    def test_permission_denied(self):
        d = self.root / 'noperm'
        d.mkdir()
        d.chmod(0o000)
        try:
            self.assertFalse(is_empty_directory(d))
        finally:
            d.chmod(0o755)

    def test_nonexistent_path(self):
        self.assertFalse(is_empty_directory(self.root / 'nope'))


class TestCleanEmptyDirectories(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = _make_root(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_single_empty_dir(self):
        empty = self.root / 'empty'
        empty.mkdir()
        deleted = clean_empty_directories(self.root)
        self.assertFalse(empty.exists())
        self.assertEqual(deleted, 1)

    def test_nested_empty_dirs(self):
        a = self.root / 'a'
        b = a / 'b'
        c = b / 'c'
        c.mkdir(parents=True)
        deleted = clean_empty_directories(self.root)
        self.assertFalse(a.exists())
        self.assertEqual(deleted, 3)

    def test_mixed_structure(self):
        a = self.root / 'a'
        a.mkdir()
        (a / 'file.txt').write_text('x')
        b = self.root / 'b'
        b.mkdir()
        deleted = clean_empty_directories(self.root)
        self.assertTrue(a.exists())
        self.assertFalse(b.exists())
        self.assertEqual(deleted, 1)

    def test_ignored_dir(self):
        a = self.root / 'a'
        a.mkdir()
        (a / '.workbuddy').mkdir()
        deleted = clean_empty_directories(self.root, ignore_names={'.workbuddy'})
        self.assertFalse(a.exists())
        self.assertEqual(deleted, 1)

    def test_ignored_dir_with_files(self):
        a = self.root / 'a'
        a.mkdir()
        wb = a / '.workbuddy'
        wb.mkdir()
        (wb / 'config.json').write_text('{}')
        deleted = clean_empty_directories(self.root, ignore_names={'.workbuddy'})
        self.assertFalse(a.exists())
        self.assertEqual(deleted, 1)

    def test_ignored_dir_with_real_file_preserves_parent(self):
        a = self.root / 'a'
        a.mkdir()
        (a / '.workbuddy').mkdir()
        (a / 'file.txt').write_text('x')
        deleted = clean_empty_directories(self.root, ignore_names={'.workbuddy'})
        self.assertTrue(a.exists())
        self.assertEqual(deleted, 0)

    def test_depth_limit(self):
        a = self.root / 'a'
        b = a / 'b'
        c = b / 'c'
        c.mkdir(parents=True)
        deleted = clean_empty_directories(self.root, max_depth=1)
        self.assertFalse(a.exists())
        self.assertGreaterEqual(deleted, 2)

    def test_ds_store_dir(self):
        a = self.root / 'a'
        a.mkdir()
        (a / '.DS_Store').write_text('x')
        deleted = clean_empty_directories(self.root)
        self.assertFalse(a.exists())
        self.assertEqual(deleted, 1)

    def test_symlink_dir_skipped(self):
        real = self.root / 'real'
        real.mkdir()
        (real / 'file.txt').write_text('x')
        link = self.root / 'link'
        link.symlink_to(real)
        deleted = clean_empty_directories(self.root)
        self.assertTrue(link.exists() or link.is_symlink())
        self.assertEqual(deleted, 0)

    def test_root_is_cwd_not_deleted(self):
        deleted = clean_empty_directories(Path.cwd())
        self.assertTrue(Path.cwd().exists())
        self.assertEqual(deleted, 0)

    def test_non_cwd_empty_root_deleted(self):
        empty_root = self.root / 'empty_root'
        empty_root.mkdir()
        deleted = clean_empty_directories(empty_root)
        self.assertFalse(empty_root.exists())
        self.assertEqual(deleted, 1)

    def test_nonexistent_root(self):
        deleted = clean_empty_directories(self.root / 'nope')
        self.assertEqual(deleted, 0)


class TestParseArgs(unittest.TestCase):
    def test_no_args(self):
        args = parse_args([])
        self.assertEqual(args.directory, '.')
        self.assertIsNone(args.depth)
        self.assertEqual(args.ignore, '')

    def test_directory_arg(self):
        args = parse_args(['/tmp/test'])
        self.assertEqual(args.directory, '/tmp/test')

    def test_depth(self):
        args = parse_args(['--depth', '3'])
        self.assertEqual(args.depth, 3)

    def test_ignore(self):
        args = parse_args(['--ignore', '.git'])
        self.assertEqual(args.ignore, '.git')

    def test_ignore_short(self):
        args = parse_args(['-i', '.git,.workbuddy'])
        self.assertEqual(args.ignore, '.git,.workbuddy')

    def test_combined_args(self):
        args = parse_args(['/tmp', '--depth', '2', '-i', '.git'])
        self.assertEqual(args.directory, '/tmp')
        self.assertEqual(args.depth, 2)
        self.assertEqual(args.ignore, '.git')


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = _make_root(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_empty_string_ignore(self):
        d = self.root / 'empty'
        d.mkdir()
        ignore_names = set(''.split(',')) if '' else set()
        deleted = clean_empty_directories(self.root, ignore_names=ignore_names)
        self.assertFalse(d.exists())
        self.assertEqual(deleted, 1)

    def test_deep_nested_dirs(self):
        current = self.root
        for i in range(100):
            current = current / f'level{i}'
        current.mkdir(parents=True)
        deleted = clean_empty_directories(self.root)
        self.assertGreater(deleted, 0)

    def test_concurrent_deletion(self):
        a = self.root / 'a'
        a.mkdir()
        a.rmdir()
        deleted = clean_empty_directories(self.root)
        self.assertEqual(deleted, 0)

    def test_permission_denied_dir(self):
        d = self.root / 'noperm'
        d.mkdir()
        (d / 'sub').mkdir()
        d.chmod(0o000)
        try:
            deleted = clean_empty_directories(self.root)
            self.assertGreaterEqual(deleted, 0)
        finally:
            d.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
