#!/usr/bin/env python3
"""validate ci/android-patches.json, the registry of logical original android changes.

the registry gives every original change or significant adaptation a stable `A001`-style id, whether its queue
patch is renamed or split. entries are ordered by id and keep removed changes as tombstones:

  {"entries": [
    {"id": "A001", "title": "docked media composer", "type": "original", "status": "active",
     "desktop": [], "description": "one plain sentence",
     "patches": ["0333-docked-complete-media-composer.patch"]},
    {"id": "A002", "title": "old experiment", "type": "adaptation", "status": "removed",
     "desktop": [], "description": "no longer shipped", "patches": [], "reason": "merged into A001"}
  ]}

an id is `A` plus its numeric value, zero-padded to at least three digits (`A001`, `A999`, `A1000`; `A0001` is
the same number with a non-canonical spelling and is rejected), positive and never reused; active entries must
name existing exact files from patches/android, removed entries keep no patches and say why. a patch may belong to
several entries, but an entry can't list the same patch twice. `python3 ci/android_patches.py [registry]` validates
the registry in this repository's patch queue."""

import argparse
import json
import os
import re
import sys

ID = re.compile(r'^A([0-9]{3,})$')
PATCH = re.compile(r'^(\d{4})-([A-Za-z0-9][A-Za-z0-9._-]*)\.patch$')
TYPES = ('original', 'adaptation')
STATUSES = ('active', 'removed')
FIELDS = {'id', 'title', 'type', 'status', 'desktop', 'description', 'patches', 'reason'}
REQUIRED = {'id', 'title', 'type', 'status', 'desktop', 'description', 'patches'}
DEFAULT_REGISTRY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'android-patches.json')
ANCHOR = re.compile(r'(?:<a\s[^>]*\b(?:id|name)\s*=\s*["\'](?P<tag>A[0-9]{3,})["\']|\{#(?P<hash>A[0-9]{3,})\})',
                    re.IGNORECASE)


class RegistryError(ValueError):
    pass


def is_id(value):
    match = ID.match(value) if isinstance(value, str) else None
    if not match:
        return False
    number = int(match.group(1))
    return number > 0 and f'A{number:03d}' == value


def number_of(android_id):
    return int(ID.match(android_id).group(1))


def text_of(value, where, required=True):
    if not isinstance(value, str):
        raise RegistryError(f'{where} has to be a string')
    value = value.strip()
    if required and not value:
        raise RegistryError(f'{where} is empty')
    return value


def desktop_of(value, where):
    if not isinstance(value, list):
        raise RegistryError(f'{where} has to be a list of desktop patch references')
    return [text_of(item, f'{where} {number}') for number, item in enumerate(value, 1)]


def patches_of(value, where, folder, status):
    if not isinstance(value, list):
        raise RegistryError(f'{where} has to be a list of patch filenames')
    result = []
    for name in value:
        if not isinstance(name, str) or not PATCH.match(name):
            raise RegistryError(f'{where} has an invalid patch filename: {name!r}')
        if name in result:
            raise RegistryError(f'{where} lists the patch twice: {name}')
        result.append(name)
    if status == 'removed':
        if result:
            raise RegistryError(f'{where} is removed and has to keep patches empty')
        return result
    if not result:
        raise RegistryError(f'{where} is active and has no patches')
    for name in result:
        if not os.path.isfile(os.path.join(folder, name)):
            raise RegistryError(f'{where} names a missing patch: {name}')
    return result


def patch_folder(registry):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(registry))), 'patches', 'android')


def docs_anchors(registry):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(registry))),
                        'docs', 'android-patches.md')
    try:
        with open(path, encoding='utf-8') as file:
            source = file.read()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise RegistryError(f'{path} cannot be read: {error}') from error
    anchors = set()
    for match in ANCHOR.finditer(source):
        anchors.add((match.group('tag') or match.group('hash')).lower())
    return anchors


def entries_of(source):
    if isinstance(source, dict) and set(source) == {'entries'} and isinstance(source['entries'], list):
        return source['entries']
    raise RegistryError('the top level has to be an object with only an entries list')


def load(path, folder=None):
    try:
        with open(path, encoding='utf-8') as file:
            try:
                source = json.load(file)
            except json.JSONDecodeError as error:
                raise RegistryError(f'{path} is not json: {error}') from error
    except OSError as error:
        raise RegistryError(f'{path} cannot be read: {error}') from error
    folder = folder or patch_folder(path)
    entries = []
    seen = set()
    previous = 0
    for number, raw in enumerate(entries_of(source), 1):
        if not isinstance(raw, dict):
            raise RegistryError(f'entry {number} has to be an object')
        unknown = set(raw) - FIELDS
        if unknown:
            raise RegistryError(f'entry {number} has unknown keys: {", ".join(sorted(unknown))}')
        missing = REQUIRED - set(raw)
        if missing:
            raise RegistryError(f'entry {number} is missing: {", ".join(sorted(missing))}')
        android_id = raw['id']
        if not is_id(android_id):
            raise RegistryError(f'entry {number} id is not a canonical positive A-number: {android_id!r}')
        if android_id in seen:
            raise RegistryError(f'entry {number} repeats the id {android_id}')
        value = number_of(android_id)
        if value <= previous:
            raise RegistryError(f'entry {number} id {android_id} is not above the previous id')
        seen.add(android_id)
        previous = value
        kind = raw['type']
        if kind not in TYPES:
            raise RegistryError(f'entry {number} type has to be original or adaptation')
        status = raw['status']
        if status not in STATUSES:
            raise RegistryError(f'entry {number} status has to be active or removed')
        entry = {
            'id': android_id,
            'title': text_of(raw['title'], f'entry {number} title'),
            'type': kind,
            'status': status,
            'desktop': desktop_of(raw['desktop'], f'entry {number} desktop'),
            'description': text_of(raw['description'], f'entry {number} description'),
            'patches': patches_of(raw['patches'], f'entry {number} patches', folder, status),
        }
        if status == 'removed' and not text_of(raw.get('reason', ''), f'entry {number} reason', False):
            raise RegistryError(f'entry {number} is removed and needs a reason')
        if 'reason' in raw:
            entry['reason'] = text_of(raw['reason'], f'entry {number} reason')
        entries.append(entry)
    anchors = docs_anchors(path)
    if anchors is not None:
        missing = [entry['id'] for entry in entries
                   if entry['status'] == 'active' and entry['id'].lower() not in anchors]
        if missing:
            raise RegistryError(f'docs/android-patches.md has no #{missing[0].lower()} anchor')
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description='validate the android patch registry against patches/android')
    parser.add_argument('registry', nargs='?', default=DEFAULT_REGISTRY, help='registry, ci/android-patches.json')
    args = parser.parse_args(argv)
    try:
        entries = load(args.registry)
    except RegistryError as error:
        sys.exit(f'android-patches: {error}')
    print(f'{args.registry}: {len(entries)} entries ok')


if __name__ == '__main__':
    main()
