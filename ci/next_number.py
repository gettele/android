#!/usr/bin/env python3
"""print the number of the next tele release.

reads tag names (one per line, `refs/tags/` allowed) on stdin and prints one above the highest `v*-tele.<N>`.
--number asks for a specific number, which has to be above every existing one."""

import argparse
import re
import sys

TAG = re.compile(r'^(?:refs/tags/)?v[0-9][0-9.]*-tele\.([0-9]+)$')


def highest(lines):
    numbers = [int(match.group(1)) for line in lines if (match := TAG.match(line.strip()))]
    return max(numbers, default=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--number', default='', help='release number to use, empty for the next free one')
    args = parser.parse_args()
    last = highest(sys.stdin)
    if not args.number:
        print(last + 1)
        return
    if not re.fullmatch(r'[1-9][0-9]*', args.number) or int(args.number) <= last:
        sys.exit(f'the release number has to be above {last}, got {args.number!r}')
    print(args.number)


if __name__ == '__main__':
    main()
