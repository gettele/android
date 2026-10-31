#!/usr/bin/env python3
"""Builds the compact TL index that the mtproto console ships in res/raw.

The source is the generated TL classes of the same tree, so the index always matches the layer the
app actually speaks. Usage: tl_index.py <java root, e.g. .../java/org/telegram/tgnet> <out.json>
"""

import json
import os
import re
import sys

DECL = re.compile(r"public static (?:final )?(?:abstract )?class (\w+)(?:<[^>]*>)?(?: extends (\w+)(?:<[^>]*>)?)?")
CONTAINER = re.compile(r"public (?:final |abstract )?class (\w+)")
CTOR = re.compile(r"public static final int constructor\s*=\s*(0x[0-9a-fA-F]+|\d+)\s*;")
LAYER = re.compile(r"public static final int LAYER\s*=\s*(\d+)\s*;")
PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)


def body_of(text, open_brace):
    depth = 0
    i = open_brace
    while i < len(text):
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[open_brace + 1:i]
        i += 1
    return text[open_brace + 1:]


def container_at(text, position):
    """The top-level class that holds the declaration at [position]."""
    name = ''
    for match in CONTAINER.finditer(text):
        if match.start() > position:
            break
        name = match.group(1)
    return name


def tl_name(container, simple):
    if container == 'TLRPC':
        return simple
    base = simple[3:] if simple.startswith('TL_') else simple
    return container + '.' + base


def method_of(display):
    if '.' in display and not display.startswith('TL_'):
        namespace, rest = display.split('.', 1)
        return namespace + '.' + rest
    base = display[3:] if display.startswith('TL_') else display
    dot = base.find('_')
    return base if dot < 0 else base[:dot] + '.' + base[dot + 1:]


SETFLAG = re.compile(r"setFlag\(flags, FLAG_(\d+), (\w+)\)")
GUARDED = re.compile(r"if \((\w+) != (?:0|null)\)\s*\{?\s*flags \|= (\d+);")
READ_FLAG = re.compile(r"hasFlag\(flags, FLAG_(\d+)\)\)\s*\{?\s*(\w+) =")
READ_BOOL = re.compile(r"(\w+) = hasFlag\(flags, FLAG_(\d+)\);")
WRITE_FLAG = re.compile(r"hasFlag\(flags, FLAG_(\d+)\)\)\s*\{?\s*stream\.write\w+\(([\w.]+)")


def optional_fields(body):
    """The fields the serializer only writes when a flags bit is set."""
    start = body.find('public void serializeToStream')
    if start < 0:
        return {}
    brace = body.find('{', start)
    if brace < 0:
        return {}
    method = body_of(body, brace)
    result = {}
    for bit, name in SETFLAG.findall(method):
        result[name] = int(bit)
    for name, bit in GUARDED.findall(method):
        result.setdefault(name, int(bit))
    for bit, name in WRITE_FLAG.findall(method):
        result.setdefault(name.split('.')[0], int(bit))
    # reads tell the same mapping from the other side, and cover the classes whose
    # callers set the bits
    read = body.find('public void readParams')
    if read >= 0:
        readBrace = body.find('{', read)
        if readBrace >= 0:
            reader = body_of(body, readBrace)
            for bit, name in READ_FLAG.findall(reader):
                result.setdefault(name, int(bit))
            for name, bit in READ_BOOL.findall(reader):
                result.setdefault(name, int(bit))
    return result


def scan(path, classes, layer):
    text = open(path, encoding='utf-8').read()
    package = PACKAGE.search(text)
    package = package.group(1) if package else ''
    if 'LAYER' in text:
        found = LAYER.search(text)
        if found:
            layer[0] = int(found.group(1))
    for match in DECL.finditer(text):
        simple = match.group(1)
        parent = match.group(2) or ''
        brace = text.find('{', match.end())
        if brace < 0:
            continue
        body = body_of(text, brace)
        ctor = CTOR.search(body)
        if not ctor:
            continue
        container = container_at(text, match.start())
        if not container:
            continue
        display = tl_name(container, simple)
        item = {
            'c': display,
            'f': package + '.' + container + '$' + simple,
            'p': parent,
            'id': int(ctor.group(1), 0) & 0xFFFFFFFF,
            'm': 1 if 'deserializeResponse(' in body else 0,
        }
        optional = optional_fields(body)
        if optional:
            item['o'] = optional
        classes.append(item)
    return classes


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 2
    root, target = sys.argv[1], sys.argv[2]
    layer = [0]
    classes = []
    for name in sorted(os.listdir(root)):
        if name == 'TLRPC.java':
            scan(os.path.join(root, name), classes, layer)
            break
    tl_dir = os.path.join(root, 'tl')
    if os.path.isdir(tl_dir):
        for name in sorted(os.listdir(tl_dir)):
            if name.endswith('.java'):
                scan(os.path.join(tl_dir, name), classes, layer)
    classes.sort(key=lambda item: item['c'])
    result = {'layer': layer[0], 'classes': classes}
    with open(target, 'w', encoding='utf-8') as out:
        out.write(json.dumps(result, separators=(',', ':'), ensure_ascii=False))
        out.write('\n')
    print('layer %d, %d classes, %d methods' % (
        result['layer'], len(classes), sum(item['m'] for item in classes)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
