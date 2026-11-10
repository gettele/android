#!/usr/bin/env python3
"""behaviour tests of android_patches.py: python3 -m unittest ci/test_android_patches.py."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import android_patches  # noqa: E402

P1 = '0001-original-change.patch'
P2 = '0002-adaptation.patch'
P3 = '0003-third-change.patch'


def entry(android_id='A001', patches=None, status='active', **extra):
    if patches is None:
        patches = [P1] if status == 'active' else []
    value = {
        'id': android_id,
        'title': 'one logical change',
        'type': 'original',
        'status': status,
        'desktop': [],
        'description': 'does one thing',
        'patches': patches,
    }
    value.update(extra)
    return value


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = self.temp.name
        self.ci = os.path.join(self.repo, 'ci')
        self.patches = os.path.join(self.repo, 'patches', 'android')
        os.makedirs(self.ci)
        os.makedirs(self.patches)
        self.add_patch(P1)
        self.registry_path = os.path.join(self.ci, 'android-patches.json')

    def tearDown(self):
        self.temp.cleanup()

    def add_patch(self, name):
        with open(os.path.join(self.patches, name), 'w', encoding='utf-8') as file:
            file.write('patch')

    def write(self, source):
        with open(self.registry_path, 'w', encoding='utf-8') as file:
            json.dump(source, file)
        return self.registry_path

    def registry(self, entries):
        return self.write({'entries': entries})

    def load(self, entries):
        return android_patches.load(self.registry(entries))


class RegistryTest(Fixture):
    def test_active_entries_may_share_patches(self):
        self.add_patch(P2)
        self.add_patch(P3)
        entries = self.load([
            entry('A001', [P1, P2]),
            entry('A002', [P2, P3], type='adaptation', desktop=['0068-a-desktop.patch'],
                  description='adapts the original behavior'),
        ])
        self.assertEqual([value['id'] for value in entries], ['A001', 'A002'])
        self.assertEqual(entries[1]['type'], 'adaptation')
        self.assertEqual(entries[1]['desktop'], ['0068-a-desktop.patch'])
        self.assertEqual(set(entries[0]['patches']) & set(entries[1]['patches']), {P2})

    def test_removed_tombstone_keeps_no_patches_and_a_reason(self):
        entries = self.load([
            entry('A001'),
            entry('A002', status='removed', reason='merged into A001'),
        ])
        self.assertEqual(entries[1]['status'], 'removed')
        self.assertEqual(entries[1]['patches'], [])
        self.assertEqual(entries[1]['reason'], 'merged into A001')

    def test_removed_entries_require_a_reason(self):
        for value in (entry('A002', status='removed'),
                      entry('A002', status='removed', reason=''),
                      entry('A002', status='removed', reason='   ')):
            with self.subTest(value=value):
                with self.assertRaises(android_patches.RegistryError):
                    self.load([value])

    def test_removed_entries_reject_patches(self):
        with self.assertRaises(android_patches.RegistryError):
            self.load([entry('A002', [P1], status='removed', reason='gone')])

    def test_active_entries_need_exact_existing_patches(self):
        for value in (entry(patches=[]),
                      entry(patches=[P2]),
                      entry(patches=['misc.patch']),
                      entry(patches=['sub/0001-original-change.patch']),
                      entry(patches=[P1, P1]),
                      entry(patches=[P1, 2])):
            with self.subTest(value=value):
                with self.assertRaises(android_patches.RegistryError):
                    self.load([value])

    def test_ids_are_positive_ordered_and_unique(self):
        self.add_patch(P2)
        for values in ([entry('A12')], [entry('a001')], [entry('A000')], [entry('001')],
                       [entry('A0001')], [entry('A0010')],
                       [entry('A001'), entry('A0001')],
                       [entry('A001'), entry('A001', [P2])],
                       [entry('A002', [P2]), entry('A001')]):
            with self.subTest(ids=[value['id'] for value in values]):
                with self.assertRaises(android_patches.RegistryError):
                    self.load(values)

    def test_numeric_aliases_are_not_separate_ids(self):
        for value in ('A0001', 'A00001', 'A0010', 'A0000'):
            with self.subTest(id=value):
                self.assertFalse(android_patches.is_id(value))
        self.assertTrue(android_patches.is_id('A001'))
        self.assertTrue(android_patches.is_id('A999'))
        self.assertTrue(android_patches.is_id('A1000'))

    def test_large_ids_are_allowed(self):
        entries = self.load([entry('A1000')])
        self.assertEqual(entries[0]['id'], 'A1000')

    def test_entry_shape_is_strict(self):
        missing_title = entry()
        del missing_title['title']
        missing_desktop = entry()
        del missing_desktop['desktop']
        missing_description = entry()
        del missing_description['description']
        for value in (missing_title, missing_desktop, missing_description,
                      entry(extra='no'), entry(type='port'), entry(status='draft'),
                      entry(desktop='0068-a-desktop.patch'), entry(description='')):
            with self.subTest(value=value):
                with self.assertRaises(android_patches.RegistryError):
                    self.load([value])

    def test_top_level_is_an_entries_object(self):
        for value in ([entry()], {'entries': []}, {'entries': [entry()], 'extra': []},
                      {'patches': [entry()]}):
            if value == {'entries': []}:
                self.assertEqual(android_patches.load(self.write(value)), [])
                continue
            with self.subTest(value=value):
                with self.assertRaises(android_patches.RegistryError):
                    android_patches.load(self.write(value))

    def test_a_renamed_patch_keeps_the_same_id(self):
        self.assertEqual(android_patches.load(self.registry([entry('A001', [P1])]))[0]['id'], 'A001')
        self.add_patch(P2)
        entries = android_patches.load(self.registry([entry('A001', [P2])]))
        self.assertEqual(entries[0]['id'], 'A001')
        self.assertEqual(entries[0]['patches'], [P2])

    def test_docs_anchors_are_checked_when_the_page_exists(self):
        self.add_patch(P2)
        path = self.registry([entry('A001'), entry('A002', [P2]),
                              entry('A003', status='removed', reason='gone')])
        docs = os.path.join(self.repo, 'docs')
        os.makedirs(docs)
        page = os.path.join(docs, 'android-patches.md')
        with open(page, 'w', encoding='utf-8') as file:
            file.write('<a id="a001"></a>\n<a id="a002"></a>\n')
        self.assertEqual([value['id'] for value in android_patches.load(path)], ['A001', 'A002', 'A003'])
        with open(page, 'w', encoding='utf-8') as file:
            file.write('<a id="a001"></a>\n')
        with self.assertRaises(android_patches.RegistryError):
            android_patches.load(path)

    def test_missing_docs_page_is_only_skipped(self):
        entries = self.load([entry()])
        self.assertEqual(entries[0]['id'], 'A001')

    def test_invalid_json_is_reported(self):
        with open(self.registry_path, 'w', encoding='utf-8') as file:
            file.write('{')
        with self.assertRaises(android_patches.RegistryError):
            android_patches.load(self.registry_path)


class CliTest(Fixture):
    def test_cli_validates_the_registry(self):
        path = self.registry([entry()])
        output = io.StringIO()
        with redirect_stdout(output):
            android_patches.main([path])
        self.assertIn('1 entries ok', output.getvalue())

    def test_cli_uses_the_sibling_registry_by_default(self):
        path = self.registry([entry()])
        original = android_patches.DEFAULT_REGISTRY
        android_patches.DEFAULT_REGISTRY = path
        try:
            with redirect_stdout(io.StringIO()):
                android_patches.main([])
        finally:
            android_patches.DEFAULT_REGISTRY = original

    def test_cli_fails_on_a_bad_registry(self):
        path = self.registry([entry('A001', [P2])])
        with self.assertRaises(SystemExit):
            android_patches.main([path])


if __name__ == '__main__':
    unittest.main()
