#!/usr/bin/env python3
"""write tele-update-android.json: the feed the in-app updater reads from releases/latest/download/."""

import argparse
import hashlib
import json
import re


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True, help='v<APP_VERSION_NAME>-tele.<N>')
    parser.add_argument('--base', required=True, type=int, help='APP_VERSION_CODE, without the abi digit')
    parser.add_argument('--apk', required=True, help='the apk, named tele-<tag>.apk')
    parser.add_argument('--repo', required=True, help='owner/name the release is published in')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    match = re.fullmatch(r'v[0-9][0-9.]*-tele\.([1-9][0-9]*)', args.tag)
    if not match:
        raise SystemExit(f'bad tag {args.tag!r}')
    name = f'tele-{args.tag}.apk'
    if args.apk.rsplit('/', 1)[-1] != name:
        raise SystemExit(f'the apk has to be named {name}')
    feed = {
        'tag': args.tag,
        'base': args.base,
        'counter': int(match.group(1)),
        'url': f'https://github.com/{args.repo}/releases/download/{args.tag}/{name}',
        'apk_sha256': sha256(args.apk),
    }
    with open(args.out, 'w', encoding='utf-8', newline='\n') as file:
        json.dump(feed, file, indent=2)
        file.write('\n')


if __name__ == '__main__':
    main()
