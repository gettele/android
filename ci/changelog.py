#!/usr/bin/env python3
"""check ci/changelog.json and make the release's changelog from it.

the source is written by hand for the next release:

  {"categories": ["interface", "chats"],
   "items": [{"text": "what changed, one sentence", "where": "settings → tele → chats", "category": "chats"}]}

`categories` is the order of the groups (every item's category has to be listed), `where` may be empty. without
--json and --notes this only validates. the limits are the app's: TeleChangelog drops what is above them."""

import argparse
import json
import sys

MAX_ITEMS = 100
MAX_CATEGORIES = 16
MAX_TITLE = 64
MAX_ITEM = 1024
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
    if not isinstance(source, dict) or set(source) - {'categories', 'items'}:
        fail('the top level has to be an object with only categories and items')
    raw_items = source.get('items')
    if not isinstance(raw_items, list) or not raw_items:
        fail('items has to be a non-empty list')
    if len(raw_items) > MAX_ITEMS:
        fail(f'more than {MAX_ITEMS} items')
    items = []
    for number, raw in enumerate(raw_items, 1):
        if not isinstance(raw, dict) or set(raw) - {'text', 'where', 'category'}:
            fail(f'item {number} has to be an object with text, where and category')
        items.append({
            'text': text_of(raw.get('text'), f'item {number} text', MAX_ITEM, True),
            'where': text_of(raw.get('where', ''), f'item {number} where', MAX_ITEM, False),
            'category': text_of(raw.get('category'), f'item {number} category', MAX_TITLE, True),
        })
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
    return categories, items


def build(categories, items, tag, repo):
    number = tag.rsplit('-tele.', 1)[-1]
    return {
        'tag': tag,
        'title': f'tele {number}',
        'categories': categories,
        'items': items,
        'url': f'https://github.com/{repo}/releases/tag/{tag}',
    }


def notes(changelog, repo):
    tag = changelog['tag']
    lines = []
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

    categories, items = load(args.source)
    changelog = build(categories, items, args.tag, args.repo)
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
