#!/usr/bin/env python3
"""behaviour tests of changelog.py and announce.py: python3 -m unittest ci/test_changelog.py."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import announce  # noqa: E402
import changelog  # noqa: E402

REPO = 'gettele/android'
TAG = 'v13.2.1-tele.11'
PATCH = '0333-docked-complete-media-composer.patch'
OFFICIAL = 'https://github.com/DrKLO/Telegram'


def item(text='one change', category='chats', where='settings → tele', **extra):
    value = {'text': text, 'where': where, 'category': category}
    value.update(extra)
    return value


def upstream(version='13.2.1', previous='13.2.0', changes=None, url=OFFICIAL):
    return {'version': version, 'previous': previous,
            'changes': ['stock change'] if changes is None else changes, 'url': url}


def previous(tag='v13.2.1-tele.10', items=None):
    return {'tag': tag, 'items': items if items is not None else [item()]}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = self.temp.name
        self.ci = os.path.join(self.repo, 'ci')
        self.patches = os.path.join(self.repo, 'patches', 'android')
        os.makedirs(self.ci)
        os.makedirs(self.patches)
        with open(os.path.join(self.patches, PATCH), 'w', encoding='utf-8') as file:
            file.write('patch')

    def tearDown(self):
        self.temp.cleanup()

    def write(self, source, name='changelog.json'):
        path = os.path.join(self.ci, name)
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(source, file)
        return path

    def load(self, source):
        return changelog.load(self.write(source))

    def built(self, items, categories=None, upstream_value=None, revision='abc123', count=333):
        if categories is None:
            categories = list(dict.fromkeys(value['category'] for value in items))
        frame = {'header': 'careful, this one moves data', 'footer': 'thanks for testing'}
        return changelog.build(categories, items, frame, upstream_value, TAG, REPO,
                               patch_count=count, revision=revision)


class LoadTest(Fixture):
    def test_legacy_items_get_a_kind_and_keep_the_source_fields(self):
        categories, items, frame, value = self.load({
            'categories': ['fixes', 'chats'],
            'items': [item('fixed', 'fixes'), item('added', 'chats')],
        })
        self.assertEqual(categories, ['fixes', 'chats'])
        self.assertEqual([entry['kind'] for entry in items], ['fix', 'new'])
        self.assertEqual(items[0]['where'], 'settings → tele')
        self.assertNotIn('patches', items[0])
        self.assertNotIn('default', items[0])
        self.assertEqual(frame, {'header': '', 'footer': ''})
        self.assertIsNone(value)

    def test_new_metadata_is_retained(self):
        categories, items, _, _ = self.load({
            'categories': ['chats'],
            'items': [item('docked media', 'chats', 'settings → tele → sending',
                           kind='new', patches=[PATCH], default='off')],
        })
        self.assertEqual(categories, ['chats'])
        self.assertEqual(items[0]['kind'], 'new')
        self.assertEqual(items[0]['patches'], [PATCH])
        self.assertEqual(items[0]['default'], 'off')

    def test_kind_is_limited_to_new_and_fix(self):
        for kind in ('changed', '', 'NEW', 1):
            with self.subTest(kind=kind):
                with self.assertRaises(SystemExit):
                    self.load({'items': [item(kind=kind)]})

    def test_patch_names_are_plain_existing_filenames(self):
        for name in ('../0333-docked.patch', 'sub/0333-docked.patch',
                     '/tmp/0333-docked.patch', '0333-docked.patch/../x.patch',
                     '0333-docked.patch', 'docked.patch', '0333-docked.txt',
                     '0999-no-such-patch.patch'):
            with self.subTest(name=name):
                with self.assertRaises(SystemExit):
                    self.load({'items': [item(patches=[name])]})

    def test_patch_count_counts_only_numbered_patch_files(self):
        with open(os.path.join(self.patches, 'notes.txt'), 'w', encoding='utf-8') as file:
            file.write('x')
        with open(os.path.join(self.patches, 'docked.patch'), 'w', encoding='utf-8') as file:
            file.write('x')
        self.assertEqual(changelog.count_patches(os.path.join(self.ci, 'changelog.json')), 1)

    def test_patch_list_must_be_a_list(self):
        with self.assertRaises(SystemExit):
            self.load({'items': [item(patches=PATCH)]})

    def test_duplicate_and_unknown_categories_still_fail(self):
        with self.assertRaises(SystemExit):
            self.load({'categories': ['chats', 'chats'], 'items': [item()]})
        with self.assertRaises(SystemExit):
            self.load({'categories': ['chats'], 'items': [item(category='calls')]})


class UpstreamTest(Fixture):
    def test_missing_upstream_is_fine_when_the_base_is_the_same(self):
        changelog.check_upstream(None, TAG, previous('v13.2.1-tele.10'))

    def test_missing_upstream_is_rejected_when_the_base_changed(self):
        with self.assertRaises(SystemExit):
            changelog.check_upstream(None, TAG, previous('v13.2.0-tele.9'))

    def test_upstream_is_rejected_when_the_release_is_on_the_same_base(self):
        with self.assertRaises(SystemExit):
            changelog.check_upstream(upstream(previous='13.2.0'), TAG, previous('v13.2.1-tele.10'))

    def test_upstream_is_accepted_when_the_base_changed(self):
        changelog.check_upstream(upstream(previous='13.2.0'), TAG, previous('v13.2.0-tele.9'))

    def test_upstream_version_has_to_match_the_tag_base(self):
        with self.assertRaises(SystemExit):
            changelog.check_upstream(upstream(version='13.2.0'), TAG)

    def test_upstream_previous_has_to_match_the_previous_release(self):
        with self.assertRaises(SystemExit):
            changelog.check_upstream(upstream(previous='13.1.9'), TAG, previous('v13.2.0-tele.9'))

    def test_upstream_url_has_to_be_the_official_repository(self):
        for url in ('https://example.com/DrKLO/Telegram',
                    'http://github.com/DrKLO/Telegram',
                    'https://github.com/DrKLO/Telegram-evil',
                    'https://github.com/other/Telegram',
                    'ftp://github.com/DrKLO/Telegram'):
            with self.subTest(url=url):
                with self.assertRaises(SystemExit):
                    changelog.upstream_of(upstream(url=url))

    def test_official_upstream_links_are_accepted(self):
        for url in (OFFICIAL, OFFICIAL + '/', OFFICIAL + '/releases/tag/v13.2.1',
                    OFFICIAL + '/tree/v13.2.1'):
            with self.subTest(url=url):
                self.assertEqual(changelog.upstream_of(upstream(url=url))['url'], url)

    def test_upstream_fields_are_strict(self):
        for value in ({**upstream(), 'extra': 'x'},
                      {**upstream(), 'changes': 'one change'},
                      upstream(changes=[]),
                      upstream(version='13.2.1', previous='13.2.1'),
                      {key: val for key, val in upstream().items() if key != 'changes'}):
            with self.subTest(value=value):
                with self.assertRaises(SystemExit):
                    changelog.upstream_of(value)

    def test_source_with_upstream_keeps_it(self):
        _, _, _, value = self.load({'items': [item()], 'upstream': upstream()})
        self.assertEqual(value, upstream())


class PreviousTest(Fixture):
    def test_metadata_only_changes_do_not_look_like_a_new_release(self):
        added = changelog.item_key(item())
        self.assertEqual(added, changelog.item_key(item(kind='fix', patches=[PATCH], default='off')))
        self.assertTrue(changelog.repeated(previous(items=[item()]),
                                          [item(kind='fix', patches=[PATCH], default='off', category='sending')]))
        self.assertTrue(changelog.repeated(previous(items=[item('a'), item('b')]),
                                          [item('b'), item('a')]))
        self.assertFalse(changelog.repeated(previous(items=[item()]), [item('other')]))


class NotesTest(Fixture):
    def test_new_and_fix_sections_hold_categories(self):
        items = [item('new thing', 'interface'), item('old fix', 'fixes'),
                 item('another fix', 'sending', kind='fix', where='', default='always on')]
        rendered = changelog.notes(self.built(items), REPO)
        self.assertIn('## new\n', rendered)
        self.assertIn('## fixes\n', rendered)
        self.assertIn('### interface\n', rendered)
        self.assertIn('### sending\n', rendered)
        self.assertNotIn('### fixes\n', rendered)
        self.assertLess(rendered.index('## new\n'), rendered.index('## fixes\n'))
        self.assertIn('another fix (always on)', rendered)
        self.assertIn('## download\n', rendered)

    def test_intro_counts_patches_and_links_the_upstream(self):
        rendered = changelog.notes(self.built([item()]), REPO)
        self.assertIn('telegram android [13.2.1](https://github.com/DrKLO/Telegram)', rendered)
        self.assertIn('333 patches', rendered)
        moved = changelog.notes(self.built([item()], upstream_value=upstream()), REPO)
        self.assertIn(OFFICIAL, moved)
        self.assertIn('## telegram android 13.2.1', moved)
        self.assertIn('- stock change', moved)
        empty = changelog.notes(self.built([item()], upstream_value=upstream(changes=[])), REPO)
        self.assertNotIn('## telegram android', empty)

    def test_patch_links_use_the_revision_and_keep_where_and_default(self):
        entry = item('docked media', 'sending', patches=[PATCH], default='off')
        rendered = changelog.notes(self.built([entry], revision='deadbeef'), REPO)
        link = f'[0333](https://github.com/{REPO}/blob/deadbeef/patches/android/{PATCH})'
        self.assertIn(link, rendered)
        self.assertIn(f'{link}, settings → tele, off', rendered)
        default = changelog.notes(self.built([entry], revision=''), REPO)
        self.assertIn(f'/blob/{TAG}/patches/android/{PATCH}', default)

    def test_empty_groups_are_omitted_and_header_footer_kept(self):
        rendered = changelog.notes(self.built([item('only new', 'chats')]), REPO)
        self.assertNotIn('## fixes', rendered)
        self.assertTrue(rendered.startswith('careful, this one moves data\n'))
        self.assertTrue(rendered.rstrip().endswith('thanks for testing'))


class AnnounceTest(Fixture):
    def test_grouping_and_escaping_for_the_channel(self):
        items = [item('use *stars* [now] <b>', 'interface'),
                 item('fixed path', 'fixes')]
        message = announce.message(self.built(items), REPO)
        self.assertIn('## tele for android 11 · 13.2.1', message)
        self.assertIn('## new', message)
        self.assertIn('## fixes', message)
        self.assertIn('**interface**', message)
        self.assertIn('\\*stars\\*', message)
        self.assertIn('\\[now\\]', message)
        self.assertIn('&#60;b>', message)
        self.assertNotIn('### fixes', message)
        self.assertIn('<footer>#android</footer>', message)

    def test_patch_links_and_header_in_the_channel(self):
        message = announce.message(self.built([item(patches=[PATCH], default='off')]), REPO)
        link = f'[0333](https://github.com/{REPO}/blob/abc123/patches/android/{PATCH})'
        self.assertIn(link, message)
        self.assertIn(f'{link}, settings → tele, off', message)
        self.assertNotIn('all 333 patches', message)
        self.assertIn('careful, this one moves data', message)
        self.assertIn('thanks for testing', message)
        self.assertTrue(message.endswith('<footer>#android</footer>'))

    def test_patch_links_quote_the_revision(self):
        message = announce.message(self.built([item(patches=[PATCH])], revision='feature/branch'), REPO)
        self.assertIn('/blob/feature%2Fbranch/patches/android/', message)

    def test_legacy_changelog_without_a_patch_count(self):
        legacy = {
            'tag': TAG,
            'title': 'tele 11',
            'categories': ['chats'],
            'items': [item()],
            'url': f'https://github.com/{REPO}/releases/tag/{TAG}',
        }
        message = announce.message(legacy, REPO)
        self.assertIn('telegram android 13.2.1.', message)
        self.assertNotIn('0 patches', message)

    def test_upstream_and_empty_sections(self):
        moved = announce.message(self.built([item('only fix', 'fixes')],
                                            upstream_value=upstream()), REPO)
        self.assertIn('## telegram android 13.2.1', moved)
        self.assertIn('new in [telegram android 13.2.1]', moved)
        self.assertNotIn('## new\n', moved)
        plain = announce.message(self.built([item('only new', 'chats')]), REPO)
        self.assertNotIn('## fixes', plain)
        self.assertNotIn('## telegram android', plain)


if __name__ == '__main__':
    unittest.main()
