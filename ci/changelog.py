#!/usr/bin/env python3
"""check ci/changelog.json and make the release's changelog from it.

the source is written by hand for the next release:

  {"categories": ["interface", "chats"],
   "items": [{"text": "what changed, one sentence", "where": "settings → tele → chats", "category": "chats",
              "kind": "new", "patches": ["0333-docked-complete-media-composer.patch"], "default": "off"}]}

`categories` is the order of the groups (every item's category has to be listed), `where` may be empty. an item may
list `options`: the `tele-…` ids of its settings (the ids of `tg://settings/tele?highlight=<id>` links), which the
app's what's new page shows as live toggles; without them the page matches `where` to a setting's name. `kind` is
`new` or `fix` and defaults to `fix` for the old `fixes` category, `new` otherwise. `patches` are exact filenames
from patches/android; `default` is the switch's default state in words. both are used only by the release notes.
the optional `header` and `footer` are lines put around the release notes and the channel post of this release only;
the app skips them.

`upstream` describes a move to another telegram android base:

  {"version": "13.2.1", "previous": "13.2.0", "changes": ["stock change"], "url": "https://github.com/DrKLO/Telegram"}

its version has to match the tag, the url has to point into DrKLO/Telegram and is authored by hand. an upstream
block is required when --previous has another base and rejected when the base is the same.

without --json and --notes this only validates. the limits are the app's: TeleChangelog drops what is above them.
links to patch files use --revision, the tag by default."""

import argparse
import json
import os
import re
import sys
from urllib.parse import quote, urlsplit

MAX_ITEMS = 100
MAX_CATEGORIES = 16
MAX_TITLE = 64
MAX_ITEM = 1024
MAX_OPTIONS = 16
OPTION = re.compile(r'^tele-[a-z0-9][a-z0-9-]{0,63}$')
PATCH = re.compile(r'^(\d{4})-([A-Za-z0-9][A-Za-z0-9._-]*)\.patch$')
VERSION = re.compile(r'^[0-9]+(?:\.[0-9]+)*$')
KINDS = ('new', 'fix')
UPSTREAM_KEYS = {'version', 'previous', 'changes', 'url'}
OFFICIAL = 'https://github.com/DrKLO/Telegram'
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


def base_version(tag):
    return tag.removeprefix('v').rsplit('-tele.', 1)[0]


def kind_of(item):
    kind = item.get('kind')
    if kind in KINDS:
        return kind
    return 'fix' if item.get('category') == 'fixes' else 'new'


def item_key(item):
    """The user-facing content; release-only metadata and grouping don't make an item new."""
    return (item.get('text', ''), item.get('where', ''), tuple(sorted(item.get('options', ()))))


def repeated(previous, items):
    raw = previous.get('items', []) if isinstance(previous, dict) else []
    if not isinstance(raw, list):
        return False
    before = sorted(item_key(item) for item in raw if isinstance(item, dict))
    return before == sorted(item_key(item) for item in items)


def official_url(value):
    parsed = urlsplit(value)
    path = parsed.path.rstrip('/')
    return (parsed.scheme == 'https' and parsed.netloc == 'github.com'
            and (path == '/DrKLO/Telegram' or path.startswith('/DrKLO/Telegram/')))


def upstream_of(value):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != UPSTREAM_KEYS:
        fail('upstream has to be an object with only version, previous, changes and url')
    version = text_of(value.get('version'), 'upstream version', MAX_TITLE, True)
    previous = text_of(value.get('previous'), 'upstream previous', MAX_TITLE, True)
    if not VERSION.match(version) or not VERSION.match(previous):
        fail('upstream version and previous have to be telegram versions')
    if version == previous:
        fail('upstream previous is the same version')
    raw_changes = value.get('changes')
    if not isinstance(raw_changes, list) or not raw_changes or len(raw_changes) > MAX_ITEMS:
        fail(f'upstream changes has to be a non-empty list of up to {MAX_ITEMS} lines')
    changes = [text_of(change, f'upstream change {number}', MAX_ITEM, True)
               for number, change in enumerate(raw_changes, 1)]
    url = text_of(value.get('url'), 'upstream url', MAX_ITEM, True)
    if not official_url(url):
        fail('upstream url has to be an official https://github.com/DrKLO/Telegram link')
    return {'version': version, 'previous': previous, 'changes': changes, 'url': url}


def check_upstream(upstream, tag, previous=None):
    version = base_version(tag)
    if upstream and upstream['version'] != version:
        fail(f'upstream version {upstream["version"]} is not the tag\'s base {version}')
    previous_tag = previous.get('tag') if isinstance(previous, dict) else ''
    previous_version = base_version(previous_tag) if isinstance(previous_tag, str) and previous_tag else ''
    if not previous_version and isinstance(previous, dict):
        known = previous.get('upstream')
        if isinstance(known, dict) and isinstance(known.get('version'), str):
            previous_version = known['version']
    if previous_version:
        if previous_version == version and upstream:
            fail(f'upstream is for another base: the previous release is already on {version}')
        if previous_version != version and not upstream:
            fail(f'upstream is required: the previous release is on {previous_version}, not {version}')
        if upstream and upstream['previous'] != previous_version:
            fail(f'upstream previous is {upstream["previous"]}, not the previous release\'s {previous_version}')


def patch_dir(source):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(source))), 'patches', 'android')


def count_patches(source):
    folder = patch_dir(source)
    try:
        names = os.listdir(folder)
    except OSError:
        return 0
    return sum(1 for name in names if PATCH.match(name) and os.path.isfile(os.path.join(folder, name)))


def patches_of(value, where, source):
    if value is None:
        return []
    if not isinstance(value, list):
        fail(f'{where} has to be a list of patch filenames')
    result = []
    folder = patch_dir(source)
    for name in value:
        if not isinstance(name, str) or not PATCH.match(name):
            fail(f'{where} has an invalid patch filename: {name!r}')
        if not os.path.isfile(os.path.join(folder, name)):
            fail(f'{where} names a missing patch: {name}')
        result.append(name)
    return result


def load(path):
    with open(path, encoding='utf-8') as file:
        try:
            source = json.load(file)
        except json.JSONDecodeError as error:
            fail(f'{path} is not json: {error}')
    if not isinstance(source, dict) or set(source) - {'categories', 'items', 'header', 'footer', 'upstream'}:
        fail('the top level has to be an object with only categories, items, header, footer and upstream')
    raw_items = source.get('items')
    if not isinstance(raw_items, list) or not raw_items:
        fail('items has to be a non-empty list')
    if len(raw_items) > MAX_ITEMS:
        fail(f'more than {MAX_ITEMS} items')
    items = []
    for number, raw in enumerate(raw_items, 1):
        if not isinstance(raw, dict) or set(raw) - {'text', 'where', 'category', 'options', 'kind', 'patches', 'default'}:
            fail(f'item {number} has to be an object with text, where, category and optionally options, kind, patches and default')
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
        kind = raw.get('kind')
        if kind is not None and kind not in KINDS:
            fail(f'item {number} kind has to be new or fix')
        item['kind'] = kind or ('fix' if item['category'] == 'fixes' else 'new')
        item['patches'] = patches_of(raw.get('patches'), f'item {number} patches', path)
        default = text_of(raw.get('default', ''), f'item {number} default', MAX_ITEM, False)
        if default:
            item['default'] = default
        if not item['patches']:
            del item['patches']
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
    upstream = upstream_of(source.get('upstream'))
    return categories, items, frame, upstream


def build(categories, items, frame, upstream, tag, repo, patch_count=0, revision=''):
    number = tag.rsplit('-tele.', 1)[-1]
    changelog = {
        'tag': tag,
        'title': f'tele {number}',
        'categories': categories,
        'items': items,
        'patch_count': patch_count,
        'url': f'https://github.com/{repo}/releases/tag/{tag}',
        'revision': revision or tag,
    }
    if upstream:
        changelog['upstream'] = upstream
    changelog.update({key: value for key, value in frame.items() if value})
    return changelog


def section_title(kind):
    return 'fixes' if kind == 'fix' else kind


def grouped(changelog):
    """[(section, [(category, items)])] in the source's category order, empty groups left out."""
    order = list(changelog.get('categories', []))
    items = changelog.get('items', [])
    for item in items:
        if item['category'] not in order:
            order.append(item['category'])
    result = []
    for section in KINDS:
        categories = []
        for category in order:
            selected = [item for item in items
                        if item['category'] == category and kind_of(item) == section]
            if selected:
                categories.append((category, selected))
        if categories:
            result.append((section, categories))
    return result


def patch_url(repo, revision, name):
    revision = quote(revision, safe='')
    name = quote(name, safe='')
    return f'https://github.com/{repo}/blob/{revision}/patches/android/{name}'


def bullet(item, repo, revision):
    links = []
    for name in item.get('patches', []):
        match = PATCH.match(name)
        number = match.group(1) if match else name
        links.append(f'[{number}]({patch_url(repo, revision, name)})')
    meta = links + [value for value in (item.get('where', ''), item.get('default', '')) if value]
    suffix = f' ({", ".join(meta)})' if meta else ''
    return f'- {item["text"]}{suffix}'


def notes(changelog, repo, revision=''):
    tag = changelog['tag']
    revision = revision or changelog.get('revision') or tag
    version = base_version(tag)
    count = changelog.get('patch_count', 0)
    upstream = changelog.get('upstream')
    url = upstream['url'] if upstream else OFFICIAL
    lines = [changelog['header'], ''] if changelog.get('header') else []
    lines.append(f'telegram android [{version}]({url}) with {count} patch{"" if count == 1 else "es"}.')
    if upstream and upstream.get('changes'):
        lines += [
            '',
            f'## telegram android {upstream["version"]}',
            '',
            f'new in [telegram android {upstream["version"]}]({upstream["url"]}) since {upstream["previous"]}:',
            '',
            *[f'- {change}' for change in upstream['changes']],
        ]
    for section, categories in grouped(changelog):
        title = section_title(section)
        lines += ['', f'## {title}']
        for category, items in categories:
            if category.lower() != title:
                lines += ['', f'### {category}']
            lines += ['']
            lines += [bullet(item, repo, revision) for item in items]
    name = f'tele-{tag}.apk'
    lines += [
        '',
        '## download',
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
    parser.add_argument('--revision', default='', help='commit the patch links point at, the tag by default')
    parser.add_argument('--json', default='', help='write tele-changelog.json here')
    parser.add_argument('--notes', default='', help='write the release notes (markdown) here')
    args = parser.parse_args()

    categories, items, frame, upstream = load(args.source)
    previous = None
    if args.previous:
        with open(args.previous, encoding='utf-8') as file:
            previous = json.load(file)
        if repeated(previous, items):
            fail('the items are the previous release\'s: write this release\'s changes into ci/changelog.json')
    check_upstream(upstream, args.tag, previous)
    changelog = build(categories, items, frame, upstream, args.tag, args.repo,
                      count_patches(args.source), args.revision)
    rendered = json.dumps(changelog, ensure_ascii=False, indent=2) + '\n'
    if len(rendered.encode()) > MAX_SIZE:
        fail(f'the result is larger than {MAX_SIZE // 1024} KiB')
    if args.json:
        with open(args.json, 'w', encoding='utf-8', newline='\n') as file:
            file.write(rendered)
    if args.notes:
        with open(args.notes, 'w', encoding='utf-8', newline='\n') as file:
            file.write(notes(changelog, args.repo, args.revision))


if __name__ == '__main__':
    main()
