"""Compile the actual tele DockedGridLayout.kt against the exact computeGrouped and
multiHeight extraction of RichMessageLayout.java, then exercise the grid layouts.

The stock positions are not re-implemented: the two methods are taken verbatim out of
RichMessageLayout.java by brace matching and compiled into a stub RichMessageLayout with
just the dp/displaySize/MessageObject.GroupedMessagePosition pieces they use. DockedGridLayout
is compiled as-is; only tele.helpers.DockedMedia is stubbed down to its Item fields.

Checked behaviourally:
  * album runs split on files, stickers, as-file items, view-once items and every 10 items;
  * 2/3/4/10 items with mixed aspect ratios lay out inside the album box, with positive
    cell sizes and no overlapping cells;
  * the height cap scales the album uniformly and the send order equals the grid order;
  * the rotation stored by PhotoEntry/SavedDrafts is degrees (90/270), not Exif 5..8, and a
    rotated item lays out exactly like the transposed dimensions at orientation 0;
  * computeGrouped never sets siblingHeights, as the rotation/geometry engine derives the
    row bands itself.

Run with --root pointing at the workspace containing Telegram/; the Kotlin compiler
dependencies must already be in --cache and a JDK javac must be available.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument('--output', type=Path)
parser.add_argument('--cache', type=Path, default=Path.home()/'.gradle/caches/modules-2/files-2.1')
parser.add_argument('--java', default=os.environ.get('JAVA', shutil.which('java') or 'java'))
parser.add_argument('--javac', default=os.environ.get('JAVAC', shutil.which('javac') or 'javac'))
args = parser.parse_args()

root = args.root.resolve()
temporary = tempfile.TemporaryDirectory(prefix='tele-docked-grid-') if args.output is None else None
here = args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache = args.cache

if shutil.which(args.javac) is None and not Path(args.javac).is_file():
    raise SystemExit('Missing javac; set JAVAC to a JDK javac')


def jar(group, artifact, version):
    found = list((cache/group/artifact/version).glob('*/' + artifact + '-' + version + '.jar'))
    if not found:
        raise SystemExit('Missing cached dependency ' + artifact + ' ' + version)
    return found[0]


compiler = [jar('org.jetbrains.kotlin', a, '2.2.21') for a in
            ['kotlin-compiler-embeddable', 'kotlin-stdlib', 'kotlin-script-runtime', 'kotlin-reflect']]
compiler += [jar('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm', '1.8.0'),
             jar('org.jetbrains', 'annotations', '13.0')]
stdlib = compiler[1]

layout = root/'Telegram/TMessagesProj/src/main/java/tele/ui/DockedGridLayout.kt'
rich = root/'Telegram/TMessagesProj/src/main/java/org/telegram/messenger/RichMessageLayout.java'
if not layout.is_file() or not rich.is_file():
    raise SystemExit('Cannot find DockedGridLayout.kt / RichMessageLayout.java under ' + str(root))


def extract_method(text, signature):
    start = text.index(signature)
    i = text.index('{', start)
    depth = 0
    state = None
    n = len(text)
    while i < n:
        c = text[i]
        if state == 'line':
            if c == '\n':
                state = None
        elif state == 'block':
            if text.startswith('*/', i):
                state = None
                i += 1
        elif state == 'string':
            if c == '\\':
                i += 1
            elif c == '"':
                state = None
        elif state == 'char':
            if c == '\\':
                i += 1
            elif c == "'":
                state = None
        else:
            if text.startswith('//', i):
                state = 'line'
                i += 1
            elif text.startswith('/*', i):
                state = 'block'
                i += 1
            elif c == '"':
                state = 'string'
            elif c == "'":
                state = 'char'
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    raise SystemExit('Cannot extract ' + signature)


rich_text = rich.read_text(encoding='utf-8')
grouped = extract_method(
    rich_text,
    'public static MessageObject.GroupedMessagePosition[] computeGrouped(float[] ratios)')
multi = extract_method(
    rich_text,
    'private static float multiHeight(float[] array, int start, int end, int maxSizeWidth)')
# the extraction must be the real implementation, not a leftover branch
if 'forceCalc' not in grouped or 'attemptCounts' not in grouped or 'multiHeight(croppedRatios' not in grouped:
    raise SystemExit('The extracted computeGrouped does not look like the grouped-media engine')

java_sources = {
    'org/telegram/messenger/MessageObject.java': r'''package org.telegram.messenger;

public class MessageObject {
    public static final int POSITION_FLAG_LEFT = 1;
    public static final int POSITION_FLAG_RIGHT = 2;
    public static final int POSITION_FLAG_TOP = 4;
    public static final int POSITION_FLAG_BOTTOM = 8;

    public static class GroupedMessagePosition {
        public byte minX, maxX, minY, maxY;
        public int pw;
        public float ph;
        public float aspectRatio;
        public float[] siblingHeights;
        public int spanSize;
        public int leftSpanOffset;
        public int flags;

        public void set(int minX, int maxX, int minY, int maxY, int w, float h, int flags) {
            this.minX = (byte) minX;
            this.maxX = (byte) maxX;
            this.minY = (byte) minY;
            this.maxY = (byte) maxY;
            this.pw = w;
            this.spanSize = w;
            this.ph = h;
            this.flags = (byte) flags;
        }
    }
}
''',
    'org/telegram/messenger/AndroidUtilities.java': r'''package org.telegram.messenger;

public class AndroidUtilities {
    public static final Size displaySize = new Size();

    static {
        displaySize.x = 1080;
        displaySize.y = 1920;
    }

    public static class Size {
        public int x;
        public int y;
    }

    public static int dp(float value) {
        return Math.round(value);
    }
}
''',
    'android/graphics/RectF.java': r'''package android.graphics;

public class RectF {
    public float left, top, right, bottom;

    public RectF() {}

    public RectF(float l, float t, float r, float b) {
        set(l, t, r, b);
    }

    public void set(float l, float t, float r, float b) {
        left = l;
        top = t;
        right = r;
        bottom = b;
    }

    public float width() {
        return right - left;
    }

    public float height() {
        return bottom - top;
    }
}
''',
    'org/telegram/messenger/RichMessageLayout.java': 'package org.telegram.messenger;\n\n'
        'import java.util.ArrayList;\n'
        'import static org.telegram.messenger.AndroidUtilities.dp;\n\n'
        'public class RichMessageLayout {\n' + grouped + '\n\n' + multi + '\n}\n',
}
java_dir = here/'java'
classes = here/'classes'
classes.mkdir(parents=True, exist_ok=True)
java_files = []
for name, body in java_sources.items():
    path = java_dir/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    java_files.append(str(path))
subprocess.run([args.javac, '-d', str(classes)] + java_files, check=True)

kotlin_sources = {
    'DockedMedia.kt': r'''package tele.helpers

class DockedMedia {
    class Item {
        var path: String? = null
        var isFile = false
        var asFile = false
        var ttl = 0
        var width = 0
        var height = 0
        var orientation = 0
        var document: Any? = null
        var inlineResult: Any? = null

        val isSticker: Boolean get() = document != null || inlineResult != null
    }
}
''',
    'Test.kt': r'''package regression

import org.telegram.messenger.RichMessageLayout
import tele.helpers.DockedMedia
import tele.ui.DockedGridLayout
import tele.ui.DockedSegment
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

private var checks = 0

private fun expect(ok: Boolean, message: String) {
    checks++
    if (!ok) throw IllegalStateException(message)
}

private fun media(w: Int, h: Int, orientation: Int = 0) = DockedMedia.Item().apply {
    width = w
    height = h
    this.orientation = orientation
}

private fun fileItem() = media(100, 100).apply { isFile = true }
private fun stickerItem() = media(100, 100).apply { document = Any() }
private fun asFileItem() = media(100, 100).apply { asFile = true }
private fun ttlItem() = media(100, 100).apply { ttl = 1 }

private fun segmentsOf(items: List<DockedMedia.Item>, group: Boolean = true) =
    DockedGridLayout.segments(items, group).map { listOf(it.from, it.till, if (it.album) 1 else 0) }

private fun albumOf(items: List<DockedMedia.Item>, width: Int = 900, cap: Int = 700) =
    DockedGridLayout.album(items, DockedSegment(0, items.size, true), width, cap, 4f, 12f, 3f)

private fun rectsOf(items: List<DockedMedia.Item>): List<List<Float>> {
    val album = albumOf(items)!!
    return album.cells.map {
        listOf(it.rect.left, it.rect.top, it.rect.right, it.rect.bottom, it.tl, it.tr, it.bl, it.br)
    }
}

private fun checkAlbum(items: List<DockedMedia.Item>, width: Int = 900, cap: Int = 700) {
    val album = albumOf(items, width, cap)
    expect(album != null, "album is null for " + items.size + " items")
    val a = album ?: throw IllegalStateException("album is null for " + items.size + " items")
    val cells = a.cells
    expect(cells.size == items.size, "cells " + cells.size + " != " + items.size)
    expect(cells.map { it.index } == items.indices.toList(), "cells are not in the tray order")
    expect(a.width <= width + 0.01f, "album width " + a.width + " > " + width)
    expect(a.height <= cap + 0.01f, "album height " + a.height + " > " + cap)
    expect(a.width > 0f && a.height > 0f, "empty album")
    for (cell in cells) {
        val r = cell.rect
        expect(r.width() > 0.5f && r.height() > 0.5f, "non-positive cell " + cell.index)
        expect(r.left >= -0.01f && r.top >= -0.01f, "negative cell origin " + cell.index)
        expect(r.right <= width + 0.01f && r.bottom <= cap + 0.01f,
            "cell " + cell.index + " leaves the album: " + r)
        expect(cell.tl > 0f && cell.tr > 0f && cell.bl > 0f && cell.br > 0f, "cell radius " + cell.index)
    }
    for (i in cells.indices) {
        for (j in i + 1 until cells.size) {
            val ra = cells[i].rect
            val rb = cells[j].rect
            val overlapX = min(ra.right, rb.right) - max(ra.left, rb.left)
            val overlapY = min(ra.bottom, rb.bottom) - max(ra.top, rb.top)
            expect(!(overlapX > 0.01f && overlapY > 0.01f), "cells " + i + " and " + j + " overlap")
        }
    }
    var top = Float.MAX_VALUE
    var bottom = 0f
    for (cell in cells) {
        top = min(top, cell.rect.top)
        bottom = max(bottom, cell.rect.bottom)
    }
    expect(top <= 6f, "cells do not start at the album top")
    expect(bottom >= a.height - 6f, "cells do not reach the album height")
}

fun main() {
    // ---- segments: files, stickers, as-file, view-once and the 10-item chunks
    expect(segmentsOf(List(2) { media(600, 600) }) == listOf(listOf(0, 2, 1)), "two photos")
    expect(segmentsOf(List(3) { media(600, 600) }) == listOf(listOf(0, 3, 1)), "three photos")
    expect(segmentsOf(List(4) { media(600, 600) }) == listOf(listOf(0, 4, 1)), "four photos")
    expect(segmentsOf(List(10) { media(600, 600) }) == listOf(listOf(0, 10, 1)), "ten photos")
    expect(segmentsOf(List(11) { media(600, 600) }) ==
        listOf(listOf(0, 10, 1), listOf(10, 11, 0)), "eleven photos split at ten")
    expect(segmentsOf(List(20) { media(600, 600) }) ==
        listOf(listOf(0, 10, 1), listOf(10, 20, 1)), "twenty photos split at ten")
    val stripSegments = segmentsOf(List(3) { media(600, 600) }, group = false)
    expect(stripSegments.all { it[2] == 0 }, "group off never marks an album")
    expect(stripSegments.flatMap { it[0] until it[1] } == listOf(0, 1, 2), "group off covers in order")

    val mixed = ArrayList<DockedMedia.Item>()
    mixed.add(media(600, 400))
    mixed.add(media(400, 600))
    mixed.add(fileItem())
    mixed.add(stickerItem())
    mixed.add(asFileItem())
    mixed.add(ttlItem())
    mixed.add(media(600, 600))
    mixed.add(media(700, 500))
    expect(segmentsOf(mixed) == listOf(
        listOf(0, 2, 1), listOf(2, 3, 0), listOf(3, 4, 0),
        listOf(4, 5, 0), listOf(5, 6, 0), listOf(6, 8, 1)), "mixed tray splits")
    val covered = segmentsOf(mixed).flatMap { it[0] until it[1] }
    expect(covered == mixed.indices.toList(), "segments do not cover every item once")

    expect(!DockedGridLayout.albumable(media(0, 600)), "zero width is not albumable")
    expect(!DockedGridLayout.albumable(media(600, 0)), "zero height is not albumable")
    expect(!DockedGridLayout.albumable(fileItem()), "file is not albumable")
    expect(!DockedGridLayout.albumable(stickerItem()), "sticker is not albumable")
    expect(!DockedGridLayout.albumable(asFileItem()), "as-file media is not albumable")
    expect(!DockedGridLayout.albumable(ttlItem()), "view-once is not albumable")
    expect(DockedGridLayout.albumable(media(600, 400)), "photo is albumable")
    expect(DockedGridLayout.gridAvailable(mixed, true), "grid is available")
    expect(!DockedGridLayout.gridAvailable(listOf(media(600, 400)), true), "one item has no grid")
    expect(DockedGridLayout.album(
        listOf(media(600, 400)), DockedSegment(0, 1, true), 900, 700, 4f, 12f, 3f) == null, "single album")

    // ---- geometry for 2/3/4/10 items, wide/tall/mixed ratios
    val ratios = listOf(1.0f to 1.0f, 1.6f to 1.0f, 0.6f to 1.0f, 2.4f to 1.0f, 0.75f to 1.0f, 1.33f to 1.0f)
    for (count in intArrayOf(2, 3, 4, 10)) {
        val mixedRatios = (0 until count).map {
            val (a, b) = ratios[it % ratios.size]
            media((a * 600).toInt(), (b * 600).toInt())
        }
        checkAlbum(mixedRatios)
        checkAlbum(List(count) { media(300, 900) })
        checkAlbum(List(count) { media(1200, 300) })
    }

    // ---- cap scales uniformly and the layout stays inside the box
    val full = albumOf(listOf(media(400, 900), media(400, 900)), 1000, 10000)!!
    val capped = albumOf(listOf(media(400, 900), media(400, 900)), 1000, 120)!!
    expect(capped.height <= 120.01f, "cap ignored: " + capped.height)
    expect(capped.height < full.height, "cap did not shrink the album")
    val factor = capped.height / full.height
    expect(abs(capped.width - full.width * factor) < 0.5f, "cap is not a uniform scale")
    expect(abs(factor - 120f / full.height) < 0.01f, "cap scale factor")

    // ---- the rotation in Item is degrees, not the Exif 5..8 codes
    val rotated = listOf(media(400, 200, 90), media(300, 600, 270))
    val transposed = listOf(media(200, 400, 0), media(600, 300, 180))
    val rotatedRects = rectsOf(rotated)
    val transposedRects = rectsOf(transposed)
    expect(rotatedRects.size == transposedRects.size, "rotated cell count")
    for (i in rotatedRects.indices) {
        for (k in rotatedRects[i].indices) {
            expect(abs(rotatedRects[i][k] - transposedRects[i][k]) < 0.01f,
                "90/270 degrees are not a dimension swap at " + i + "/" + k)
        }
    }
    expect(rectsOf(listOf(media(400, 200, 180), media(300, 500, 0))) ==
        rectsOf(listOf(media(400, 200, 0), media(300, 500, 0))), "180 degrees must not swap")
    expect(rectsOf(listOf(media(400, 200, 90), media(300, 500, 90))) ==
        rectsOf(listOf(media(400, 200, 270), media(300, 500, 270))), "90 and 270 are both swaps")

    // ---- the extracted stock positions are the real engine and derive their own rows
    val pair = RichMessageLayout.computeGrouped(floatArrayOf(1f, 1f))
    expect(pair.size == 2, "computeGrouped pair size")
    expect(pair[0].minY == pair[1].minY && pair[0].maxY == pair[1].maxY, "pair is one row")
    expect(pair[0].pw + pair[1].pw == 1000, "pair widths")
    expect((pair[0].flags and 1) != 0 && (pair[1].flags and 2) != 0, "pair edge flags")
    val many = RichMessageLayout.computeGrouped(FloatArray(10) { if (it % 2 == 0) 1.5f else 0.7f })
    expect(many.size == 10, "computeGrouped ten size")
    expect(many.all { it.pw > 0 && it.ph > 0 }, "computeGrouped ten cells")
    expect(many.all { it.siblingHeights == null }, "stock never sets siblingHeights; rows are derived locally")

    println("docked grid: " + checks + " checks passed")
}
''',
}
kotlin_dir = here/'kotlin'
kotlin_files = []
for name, body in kotlin_sources.items():
    path = kotlin_dir/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    kotlin_files.append(str(path))
shutil.copyfile(layout, kotlin_dir/'DockedGridLayout.kt')
kotlin_files.append(str(kotlin_dir/'DockedGridLayout.kt'))

product = here/'docked-grid.jar'
classpath = os.pathsep.join([str(classes), str(stdlib)])
subprocess.run([args.java, '-cp', os.pathsep.join(map(str, compiler)),
                'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
                '-no-stdlib', '-no-reflect', '-classpath', classpath,
                '-d', str(product)] + kotlin_files, check=True)
subprocess.run([args.java, '-cp', os.pathsep.join([str(product), classpath]),
                'regression.TestKt'], check=True)
