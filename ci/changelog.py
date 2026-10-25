#!/usr/bin/env python3
"""check ci/changelog.json and make the release's changelog from it.

the source is written by hand for the next release:

  {"categories": ["interface", "chats"],
   "items": [{"text": "what changed, one sentence", "where": "settings → tele → chats", "category": "chats"}]}

`categories` is the order of the groups (every item's category has to be listed), `where` may be empty. an item may
list `options`: the `tele-…` ids of its settings (the ids of `tg://settings/tele?highlight=<id>` links), which the
app's what's new page shows as live toggles; without them the page matches `where` to a setting's name. the optional
`header` and `footer` are lines put around the release notes and the channel post of this release only; the app skips
them. without --json and --notes this only validates. the limits are the app's: TeleChangelog drops what is above them."""

import argparse
import json
import re
import sys

MAX_ITEMS = 100
MAX_CATEGORIES = 16
MAX_TITLE = 64
MAX_ITEM = 1024
MAX_OPTIONS = 16
OPTION = re.compile(r'^tele-[a-z0-9][a-z0-9-]{0,63}$')
MAX_SIZE = 256 * 1024


def fail(message):
    sys.exit(f'changelog: {message}')


def text_of(value, where, limit, required):
    if not isinstance(value, str):
        fail(f'{where} has to be a string')
    value = value.strip()
    if required and not value:
        fail(f'{where} is empty')
    if len(value) > limit:
        fail(f'{where} is longer than {limit} characters')
    return value


def load(path):
    with open(path, encoding='utf-8') as file:
        try:
            source = json.load(file)
        except json.JSONDecodeError as error:
            fail(f'{path} is not json: {error}')
    if not isinstance(source, dict) or set(source) - {'categories', 'items', 'header', 'footer'}:
        fail('the top level has to be an object with only categories, items, header and footer')
    raw_items = source.get('items')
    if not isinstance(raw_items, list) or not raw_items:
        fail('items has to be a non-empty list')
    if len(raw_items) > MAX_ITEMS:
        fail(f'more than {MAX_ITEMS} items')
    items = []
    for number, raw in enumerate(raw_items, 1):
        if not isinstance(raw, dict) or set(raw) - {'text', 'where', 'category', 'options'}:
            fail(f'item {number} has to be an object with text, where, category and optionally options')
        item = {
            'text': text_of(raw.get('text'), f'item {number} text', MAX_ITEM, True),
            'where': text_of(raw.get('where', ''), f'item {number} where', MAX_ITEM, False),
            'category': text_of(raw.get('category'), f'item {number} category', MAX_TITLE, True),
        }
        options = raw.get('options', [])
        if not isinstance(options, list) or len(options) > MAX_OPTIONS or not all(
                isinstance(option, str) and OPTION.match(option) for option in options):
            fail(f'item {number} options have to be a list of up to {MAX_OPTIONS} tele-… ids')
        if options:
            item['options'] = options
        items.append(item)
    raw_categories = source.get('categories', [])
    if not isinstance(raw_categories, list):
        fail('categories has to be a list')
    categories = [text_of(name, 'a category', MAX_TITLE, True) for name in raw_categories]
    if len(set(categories)) != len(categories):
        fail('a category is listed twice')
    for item in items:
        if categories and item['category'] not in categories:
            fail(f'category {item["category"]!r} is not in categories')
        if item['category'] not in categories:
            categories.append(item['category'])
    used = {item['category'] for item in items}
    categories = [name for name in categories if name in used]
    if len(categories) > MAX_CATEGORIES:
        fail(f'more than {MAX_CATEGORIES} categories')
    # the lines around the notes and the announcement of one release; the app doesn't show them
    frame = {key: text_of(source.get(key, ''), key, MAX_TITLE, False) for key in ('header', 'footer')}
    return categories, items, frame


def build(categories, items, frame, tag, repo):
    number = tag.rsplit('-tele.', 1)[-1]
    changelog = {
        'tag': tag,
        'title': f'tele {number}',
        'categories': categories,
        'items': items,
        'url': f'https://github.com/{repo}/releases/tag/{tag}',
    }
    changelog.update({key: value for key, value in frame.items() if value})
    return changelog


def notes(changelog, repo):
    tag = changelog['tag']
    lines = [changelog['header'], ''] if changelog.get('header') else []
    for category in changelog['categories']:
        lines += [f'## {category}', '']
        for item in changelog['items']:
            if item['category'] == category:
                where = f' ({item["where"]})' if item['where'] else ''
                lines.append(f'- {item["text"]}{where}')
        lines.append('')
    name = f'tele-{tag}.apk'
    lines += [
        '## install',
        '',
        f'[{name}](https://github.com/{repo}/releases/download/{tag}/{name}): install it over your tele. '
        'a running tele finds this release within 3 hours, or right away with settings → tele → check for updates.',
    ]
    if changelog.get('footer'):
        lines += ['', changelog['footer']]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--tag', required=True)
    parser.add_argument('--repo', required=True, help='owner/name the release is published in')
    parser.add_argument('--previous', default='', help="the previous release's tele-changelog.json: the items must differ")
    parser.add_argument('--json', default='', help='write tele-changelog.json here')
    parser.add_argument('--notes', default='', help='write the release notes (markdown) here')
    args = parser.parse_args()

    categories, items, frame = load(args.source)
    changelog = build(categories, items, frame, args.tag, args.repo)
    rendered = json.dumps(changelog, ensure_ascii=False, indent=2) + '\n'
    if len(rendered.encode()) > MAX_SIZE:
        fail(f'the result is larger than {MAX_SIZE // 1024} KiB')
    if args.previous:
        with open(args.previous, encoding='utf-8') as file:
            if json.load(file).get('items') == items:
                fail('the items are the previous release\'s: write this release\'s changes into ci/changelog.json')
    if args.json:
        with open(args.json, 'w', encoding='utf-8', newline='\n') as file:
            file.write(rendered)
    if args.notes:
        with open(args.notes, 'w', encoding='utf-8', newline='\n') as file:
            file.write(notes(changelog, args.repo))


if __name__ == '__main__':
    main()
