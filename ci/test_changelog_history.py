#!/usr/bin/env python3
"""fixture tests of changelog_history.py: python3 -m unittest ci/test_changelog_history.py (no network, no gh)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import changelog_history as history  # noqa: E402

REPO = 'gettele/android'


def source(number, items=None):
    return {
        'tag': f'v13.0.3-tele.{number}',
        'title': f'tele {number}',
        'items': items if items is not None else [{'text': 'one thing', 'where': 'settings → tele', 'category': 'chats'}],
    }


class NormalizeTest(unittest.TestCase):
    def test_categories_come_from_items(self):
        release = history.normalize(source(5), REPO)
        self.assertEqual(release['version'], 5)
        self.assertEqual(release['categories'], ['chats'])
        self.assertEqual(release['url'], f'https://github.com/{REPO}/releases/tag/v13.0.3-tele.5')

    def test_missing_category_is_invalid(self):
        with self.assertRaises(history.Invalid):
            history.normalize(source(5, [{'text': 'x', 'where': ''}]), REPO)

    def test_long_item_is_invalid(self):
        with self.assertRaises(history.Invalid):
            history.normalize(source(5, [{'text': 'x' * 1025, 'where': '', 'category': 'a'}]), REPO)

    def test_bad_tag_and_expected_tag(self):
        with self.assertRaises(history.Invalid):
            history.normalize({**source(5), 'tag': 'v1'}, REPO)
        with self.assertRaises(history.Invalid):
            history.normalize(source(5), REPO, 'v13.0.3-tele.4')

    def test_options_are_validated_and_deduplicated(self):
        item = {'text': 'x', 'where': '', 'category': 'a', 'options': ['tele-a-b', 'tele-a-b']}
        self.assertEqual(history.normalize(source(5, [item]), REPO)['items'][0]['options'], ['tele-a-b'])
        item['options'] = ['not an id']
        with self.assertRaises(history.Invalid):
            history.normalize(source(5, [item]), REPO)


class MergeTest(unittest.TestCase):
    def test_duplicate_tags_keep_the_first_and_order_is_newest_first(self):
        first = history.normalize(source(5), REPO)
        again = history.normalize(source(5, [{'text': 'other', 'where': '', 'category': 'a'}]), REPO)
        older = history.normalize(source(2), REPO)
        merged = history.merge([older, first, again])['releases']
        self.assertEqual([release['version'] for release in merged], [5, 2])
        self.assertEqual(merged[0]['items'][0]['text'], 'one thing')


if __name__ == '__main__':
    unittest.main()
