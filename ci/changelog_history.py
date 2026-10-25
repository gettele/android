#!/usr/bin/env python3
"""write the changelog history the app bundles: res/raw/changelog_history.json.

it merges the tele-changelog.json of every published release of the repo (downloaded with `gh`, public assets only)
with the changelog of the release being built (--current), newest first:

  {"releases": [{"version": 5, "tag": "v13.0.3-tele.5", "title": "tele 5", "url": "https://github.com/...",
                 "categories": ["messages"], "items": [{"text": "...", "where": "...", "category": "messages",
                                                        "options": ["tele-multi-quote"]}]}]}

`options` is optional. an old release without a changelog asset is skipped with a warning, a malformed old one too;
a malformed --current fails. the limits are the app's (TeleChangelogHistory drops what is above them).
needs `gh` with GH_TOKEN (or a login) and no android sdk: run it before the build. `--verify-apk` checks afterwards
that the apk carries the history of its release (the resource path may be shortened, so it looks at the content)."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

MAX_RELEASES = 200
MAX_ITEMS = 100
MAX_CATEGORIES = 16
MAX_OPTIONS = 16
MAX_TITLE = 64
MAX_ITEM = 1024
MAX_SIZE = 256 * 1024
ASSET = 'tele-changelog.json'
TAG = re.compile(r'^v[0-9][0-9.]*-tele\.([1-9][0-9]*)$')
OPTION = re.compile(r'^tele-[a-z0-9][a-z0-9-]{0,63}$')


class Invalid(Exception):
    pass


def text_of(value, where, limit, required):
    if not isinstance(value, str):
        raise Invalid(f'{where} has to be a string')
    value = value.strip()
    if required and not value:
        raise Invalid(f'{where} is empty')
    if len(value) > limit:
        raise Invalid(f'{where} is longer than {limit} characters')
    return value


def normalize(source, repo, expected=None):
    """one release of the history out of a tele-changelog.json, or Invalid."""
    if not isinstance(source, dict):
        raise Invalid('not an object')
    tag = source.get('tag')
    match = TAG.match(tag) if isinstance(tag, str) else None
    if not match:
        raise Invalid('bad tag')
    if expected and tag != expected:
        raise Invalid(f'tag {tag} is not {expected}')
    raw_items = source.get('items')
    if not isinstance(raw_items, list) or not raw_items:
        raise Invalid('items has to be a non-empty list')
    if len(raw_items) > MAX_ITEMS:
        raise Invalid(f'more than {MAX_ITEMS} items')
    items = []
    for number, raw in enumerate(raw_items, 1):
        if not isinstance(raw, dict):
            raise Invalid(f'item {number} is not an object')
        item = {
            'text': text_of(raw.get('text'), f'item {number} text', MAX_ITEM, True),
            'where': text_of(raw.get('where', ''), f'item {number} where', MAX_ITEM, False),
            'category': text_of(raw.get('category'), f'item {number} category', MAX_TITLE, True),
        }
        options = raw.get('options', [])
        if not isinstance(options, list) or len(options) > MAX_OPTIONS or not all(
                isinstance(option, str) and OPTION.match(option) for option in options):
            raise Invalid(f'item {number} options are not a short list of tele-… ids')
        if options:
            item['options'] = list(dict.fromkeys(options))
        items.append(item)
    categories = []
    for item in items:
        if item['category'] not in categories:
            categories.append(item['category'])
    if len(categories) > MAX_CATEGORIES:
        raise Invalid(f'more than {MAX_CATEGORIES} categories')
    number = match.group(1)
    title = source.get('title')
    if not isinstance(title, str) or not title.strip() or len(title.strip()) > MAX_TITLE:
        title = f'tele {number}'
    return {
        'version': int(number),
        'tag': tag,
        'title': title.strip(),
        'url': f'https://github.com/{repo}/releases/tag/{tag}',
        'categories': categories,
        'items': items,
    }


def merge(releases):
    """newest first, one release per version (the first one given wins), bounded."""
    seen = {}
    for release in releases:
        seen.setdefault(release['version'], release)
    ordered = [seen[version] for version in sorted(seen, reverse=True)]
    return {'releases': ordered[:MAX_RELEASES]}


def gh(*args):
    return subprocess.run(['gh', *args], check=True, capture_output=True, text=True).stdout


def published_tags(repo):
    listed = gh('release', 'list', '--repo', repo, '--limit', '1000', '--json', 'tagName,isDraft')
    return [entry['tagName'] for entry in json.loads(listed) if not entry['isDraft'] and TAG.match(entry['tagName'])]


def download(repo, tag):
    with tempfile.TemporaryDirectory() as directory:
        try:
            gh('release', 'download', tag, '--repo', repo, '--pattern', ASSET, '--dir', directory)
        except subprocess.CalledProcessError:
            return None
        path = os.path.join(directory, ASSET)
        if not os.path.isfile(path) or os.path.getsize(path) > MAX_SIZE:
            return None
        with open(path, encoding='utf-8') as file:
            return json.load(file)


def verify_apk(path, tag):
    needle = f'"tag": "{tag}"'.encode()
    with zipfile.ZipFile(path) as apk:
        for info in apk.infolist():
            if info.filename.startswith('res/') and info.file_size <= 4 * 1024 * 1024:
                data = apk.read(info)
                if b'"releases"' in data and needle in data:
                    return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='', help='owner/name the releases are published in')
    parser.add_argument('--current', default='', help="the tele-changelog.json of the release being built")
    parser.add_argument('--out', default='', help='where to write changelog_history.json')
    parser.add_argument('--verify-apk', default='', help='check that this apk holds the history, with --tag')
    parser.add_argument('--tag', default='', help='the release tag --verify-apk looks for')
    args = parser.parse_args()
    if args.verify_apk:
        if not args.tag or not verify_apk(args.verify_apk, args.tag):
            sys.exit('changelog history: the apk has no changelog history of its release')
        print('changelog history: found in the apk')
        return
    if not args.repo or not args.out:
        parser.error('--repo and --out are required')

    releases = []
    current_tag = ''
    if args.current:
        with open(args.current, encoding='utf-8') as file:
            try:
                current = normalize(json.load(file), args.repo)
            except (Invalid, json.JSONDecodeError) as error:
                sys.exit(f'changelog history: the current changelog is invalid: {error}')
        releases.append(current)
        current_tag = current['tag']
    for tag in published_tags(args.repo):
        if tag == current_tag:
            continue
        try:
            source = download(args.repo, tag)
            if source is None:
                print(f'changelog history: warning: {tag} has no {ASSET}', file=sys.stderr)
                continue
            releases.append(normalize(source, args.repo, tag))
        except (Invalid, json.JSONDecodeError) as error:
            print(f'changelog history: warning: {tag} skipped: {error}', file=sys.stderr)
    history = merge(releases)
    if not history['releases']:
        sys.exit('changelog history: no release changelogs at all')
    rendered = json.dumps(history, ensure_ascii=False, indent=1, sort_keys=True) + '\n'
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as file:
        file.write(rendered)
    print(f'changelog history: {len(history["releases"])} releases, {len(rendered.encode()) // 1024} KiB')


if __name__ == '__main__':
    main()
