#!/usr/bin/env python3
"""Run the await-using regression against both shipped QuickJS engines with ASan/UBSan."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--telegram', type=Path, default=Path(__file__).resolve().parents[2] / 'Telegram')
    args = parser.parse_args()
    source = Path(__file__).with_name('quickjs_await_test.c').resolve()
    roots = [args.telegram / 'TMessagesProj/jni/third_party/quickjs-ng',
             args.telegram / 'TMessagesProj/jni/twidget/widget-sandbox/packages/ios/Sources/CQuickJS/quickjs']
    with tempfile.TemporaryDirectory(prefix='tele-quickjs-await-') as temporary:
        for index, root in enumerate(roots):
            root = root.resolve()
            binary = Path(temporary) / f'await-{index}'
            subprocess.run([os.environ.get('CC', 'clang'), '-std=gnu11', '-O1', '-g',
                            '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                            '-D_GNU_SOURCE', '-DQUICKJS_NG_BUILD', '-I', str(root), str(source),
                            *(str(root / name) for name in ('quickjs.c', 'dtoa.c', 'libregexp.c', 'libunicode.c')),
                            '-lm', '-lpthread', '-o', str(binary)], check=True)
            print(f'Testing {root}', flush=True)
            subprocess.run([str(binary)], check=True,
                           env={**os.environ, 'ASAN_OPTIONS': 'detect_stack_use_after_return=1',
                                'UBSAN_OPTIONS': 'halt_on_error=1'})


if __name__ == '__main__':
    main()
