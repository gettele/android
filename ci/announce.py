#!/usr/bin/env python3
"""post a rich message about a published tele release to the telegram channel, made from its tele-changelog.json.

the channel also gets tele desktop's releases, so the post is titled `tele for android N · <version>` and ends
with a #android footer. the changes use the same new/fix grouping as the release notes, without the patch list.
needs BOT_TOKEN and CHANNEL in the environment unless --dry-run."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import quote

from changelog import PATCH, android_url, base_version, grouped, patch_url, section_title


def escape(text):
    text = re.sub(r'([\\`*_\[\]()~=|$!#+\-])', r'\\\1', text)
    return text.replace('<', '&#60;')


def item_line(item, repo, revision):
    links = [f'[{escape(android_id)}]({android_url(repo, revision, android_id)})'
             for android_id in item.get('android_ids', [])]
    for name in item.get('patches', []):
        match = PATCH.match(name)
        number = match.group(1) if match else name
        links.append(f'[{number}]({patch_url(repo, revision, name)})')
    meta = links + [escape(value) for value in (item.get('where', ''), item.get('default', '')) if value]
    suffix = f' ({", ".join(meta)})' if meta else ''
    return f'- {escape(item["text"])}{suffix}'


def message(changelog, repo):
    tag = changelog['tag']
    version, number = tag.removeprefix('v').rsplit('-tele.', 1)
    upstream = changelog.get('upstream')
    count = changelog.get('patch_count')
    revision = changelog.get('revision') or tag
    lines = [escape(changelog['header']), ''] if changelog.get('header') else []
    lines.append(f'## tele for android {escape(number)} · {escape(version)}')
    if count is None:
        lines += ['', escape(f'telegram android {base_version(tag)}.')]
    else:
        lines += ['', escape(f'telegram android {base_version(tag)} with {count} '
                             f'patch{"" if count == 1 else "es"}.')]
    if upstream and upstream.get('changes'):
        lines += [
            '',
            f'## telegram android {escape(upstream["version"])}',
            '',
            f'new in [telegram android {escape(upstream["version"])}]({upstream["url"]}) '
            f'since {escape(upstream["previous"])}:',
            '',
            *[f'- {escape(change)}' for change in upstream['changes']],
        ]
    for section, categories in grouped(changelog):
        title = section_title(section)
        lines += ['', f'## {title}']
        for category, items in categories:
            if category.lower() != title:
                lines += ['', f'**{escape(category)}**', '']
            lines += [item_line(item, repo, revision) for item in items]
    lines += [
        '',
        'the apk is in the release: install it over your tele. a running tele finds this release within 3 hours.',
        '',
        '<tg-button-row>'
        f'<tg-button type="url" url="https://github.com/{quote(repo, safe="/")}/releases/tag/{quote(tag, safe="")}">download</tg-button>'
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
