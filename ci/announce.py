#!/usr/bin/env python3
"""post a rich message about a published tele release to the telegram channel, made from its tele-changelog.json.

the channel also gets tele desktop's releases, so the post is titled `tele for android N · <version>` and ends
with a #android footer. needs BOT_TOKEN and CHANNEL in the environment unless --dry-run."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


def escape(text):
    text = re.sub(r'([\\`*_\[\]()~=|$!#+\-])', r'\\\1', text)
    return text.replace('<', '&#60;')


def message(changelog, repo):
    tag = changelog['tag']
    version, number = tag.removeprefix('v').rsplit('-tele.', 1)
    lines = [escape(changelog['header']), ''] if changelog.get('header') else []
    lines.append(f'## tele for android {escape(number)} · {escape(version)}')
    for category in changelog['categories']:
        lines += ['', f'**{escape(category)}**', '']
        for item in changelog['items']:
            if item['category'] == category:
                where = f' ({escape(item["where"])})' if item['where'] else ''
                lines.append(f'- {escape(item["text"])}{where}')
    lines += [
        '',
        'the apk is in the release: install it over your tele. a running tele finds this release within 3 hours.',
        '',
        '<tg-button-row>'
        f'<tg-button type="url" url="https://github.com/{repo}/releases/tag/{tag}">download</tg-button>'
        '</tg-button-row>',
    ]
    if changelog.get('footer'):
        lines += ['', escape(changelog['footer'])]
    lines += [
        '',
        '<footer>#android</footer>',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('changelog', help="the release's tele-changelog.json")
    parser.add_argument('--repo', required=True, help='owner/name the release is published in')
    parser.add_argument('--dry-run', action='store_true', help='print the request instead of sending it')
    args = parser.parse_args()

    with open(args.changelog, encoding='utf-8') as file:
        changelog = json.load(file)
    payload = {
        'chat_id': os.environ.get('CHANNEL', ''),
        'rich_message': {'markdown': message(changelog, args.repo)},
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    request = urllib.request.Request(
        f'https://api.telegram.org/bot{os.environ["BOT_TOKEN"]}/sendRichMessage',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        result = json.load(error)
    if not result.get('ok'):
        print(f'::warning::the announcement failed: {result.get("description")}')
        sys.exit(1)
    print(f'announced {changelog["tag"]} as message {result["result"]["message_id"]}')


if __name__ == '__main__':
    main()
