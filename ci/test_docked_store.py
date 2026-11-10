#!/usr/bin/env python3
"""Exercise DockedStore persistence and the tele_docked_context migration.

The actual DockedStore.kt is compiled unchanged against focused Kotlin/Java stubs, with
the real SerializedData.java handling all bytes. The behavioural checks cover the v5
blob written before the mode/shortcut columns existed, distinct rows for dialog/thread/
mode/shortcut/account, and the asynchronous generation guard that drops stale saves.

The docked table migration is not re-implemented: createDockedTable's SQL literals are
taken from TeleDatabaseHelper.kt, the legacy table definition comes from the patch that
introduced it, and both are executed by sqlite3 in memory. The old BLOB rows must survive
the INSERT ... SELECT unchanged and receive mode 0 / shortcut '' before the legacy table
is dropped. No assertion compares source text; only executed SQL and decoded behaviour.

Run with --root pointing at the workspace containing Telegram/; the Kotlin compiler and
stdlib must already exist in --cache.
"""
from pathlib import Path
import argparse
import os
import re
import shutil
import sqlite3
import struct
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
temporary = tempfile.TemporaryDirectory(prefix='tele-docked-store-') if args.output is None else None
here = args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)

helper_source = root/'Telegram/TMessagesProj/src/main/java/tele/db/TeleDatabaseHelper.kt'
docked_source = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/DockedStore.kt'
tgnet = root/'Telegram/TMessagesProj/src/main/java/org/telegram/tgnet'
for required in (helper_source, docked_source, tgnet/'SerializedData.java',
                 tgnet/'AbstractSerializedData.java', tgnet/'InputSerializedData.java',
                 tgnet/'OutputSerializedData.java', tgnet/'TLDataSourceType.java'):
    if not required.is_file():
        raise SystemExit('Cannot find ' + str(required))


def function_block(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise SystemExit('Unclosed function ' + signature)


def unescape(literal):
    return re.sub(r'\\(["\\])', r'\1', literal)


def sql_calls(pattern, body):
    return [unescape(m.group(1)) for m in re.finditer(pattern, body)]


# ------------------------------------------------------- migration SQL in sqlite3

helper_text = helper_source.read_text(encoding='utf-8')
docked_body = function_block(helper_text, 'private fun createDockedTable(db: SQLiteDatabase)')
statements = sql_calls(r'execSQL\(\s*"((?:[^"\\]|\\.)*)"\s*\)', docked_body)
queries = sql_calls(r'rawQuery\(\s*"((?:[^"\\]|\\.)*)"', docked_body)
creates = [sql for sql in statements if re.match(r'\s*CREATE TABLE IF NOT EXISTS\s+tele_docked_context\b', sql, re.I)]
inserts = [sql for sql in statements if re.match(r'\s*INSERT OR REPLACE\b', sql, re.I)]
drops = [sql for sql in statements if re.match(r'\s*DROP TABLE\b', sql, re.I)]
if len(creates) != 1 or len(inserts) != 1 or len(drops) != 1 or len(queries) != 1:
    raise SystemExit('createDockedTable no longer has the expected create/copy/drop statements')
create_sql = creates[0]
insert_sql = inserts[0]
drop_sql = drops[0]
legacy_query = queries[0]
table_match = re.search(r'CREATE TABLE IF NOT EXISTS\s+([A-Za-z_]\w*)', create_sql)
legacy_match = re.search(r"name\s*=\s*'([^']+)'", legacy_query)
if table_match is None or legacy_match is None:
    raise SystemExit('Cannot derive table names from createDockedTable')
table = table_match.group(1)
legacy_name = legacy_match.group(1)

# The old table definition predates tele_docked_context; take it from the patch that
# created the table rather than spelling a second schema in this test.
legacy_sql = None
for patch in sorted((root/'main/patches/android').glob('*.patch')):
    match = re.search(r'CREATE TABLE IF NOT EXISTS tele_docked \([^"\n]*\)',
                      patch.read_text(encoding='utf-8', errors='ignore'))
    if match:
        legacy_sql = match.group(0)
        break
if legacy_sql is None:
    # same v1 schema as the patch; kept as a fallback for workspaces without patches
    legacy_sql = ('CREATE TABLE IF NOT EXISTS tele_docked (account INTEGER NOT NULL, '
                  'dialog_id INTEGER NOT NULL, thread_id INTEGER NOT NULL, data BLOB NOT NULL, '
                  'PRIMARY KEY (account, dialog_id, thread_id))')

legacy_rows = [
    (7, -100, 4, struct.pack('<ii', 0x444d4544, 5) + b'legacy-v5-blob-A\x00\x01'),
    (7, -200, 9, struct.pack('<ii', 0x444d4544, 5) + b'legacy-v5-blob-B\xff'),
]

conn = sqlite3.connect(':memory:')
conn.execute(legacy_sql)
conn.executemany('INSERT INTO tele_docked (account, dialog_id, thread_id, data) VALUES (?, ?, ?, ?)',
                 legacy_rows)
conn.commit()
conn.execute(create_sql)
conn.commit()
legacy_present = conn.execute(legacy_query).fetchone() is not None
check_message = 'migration skipped the existing tele_docked rows'
if not legacy_present:
    raise SystemExit(check_message)
conn.execute(insert_sql)
conn.execute(drop_sql)
conn.commit()

rows = conn.execute(
    'SELECT account, dialog_id, thread_id, mode, shortcut, data FROM ' + table +
    ' ORDER BY dialog_id').fetchall()
if len(rows) != len(legacy_rows):
    raise SystemExit('migration did not preserve every legacy row')
for (account, dialog_id, thread_id, data), row in zip(sorted(legacy_rows, key=lambda item: item[1]), rows):
    if (row[0], row[1], row[2]) != (account, dialog_id, thread_id):
        raise SystemExit('migration changed a legacy row key')
    if row[3] != 0 or row[4] != '':
        raise SystemExit('migrated row did not get the plain mode/shortcut defaults')
    if bytes(row[5]) != data:
        raise SystemExit('migration changed a legacy BLOB')

column_info = conn.execute('PRAGMA table_info(' + table + ')').fetchall()
columns = {row[1]: row for row in column_info}
for name in ('account', 'dialog_id', 'thread_id', 'mode', 'shortcut', 'data'):
    if name not in columns:
        raise SystemExit('new docked table is missing ' + name)
if columns['data'][3] != 1:
    raise SystemExit('docked data column is no longer required')
if columns['mode'][4] != '0' or columns['shortcut'][4] != "''":
    raise SystemExit('docked mode/shortcut defaults changed')
primary = [row[1] for row in sorted(column_info, key=lambda row: row[5]) if row[5] > 0]
if primary != ['account', 'dialog_id', 'thread_id', 'mode', 'shortcut']:
    raise SystemExit('docked primary key changed: ' + repr(primary))

# The same chat may now keep separate trays per mode and per quick-reply shortcut.
conn.execute('INSERT INTO ' + table +
             ' (account, dialog_id, thread_id, mode, shortcut, data) VALUES (?, ?, ?, ?, ?, ?)',
             (7, -100, 4, 5, 'work', b'quick-mode'))
conn.execute('INSERT INTO ' + table +
             ' (account, dialog_id, thread_id, mode, shortcut, data) VALUES (?, ?, ?, ?, ?, ?)',
             (7, -100, 4, 0, 'work', b'shortcut-mode'))
try:
    conn.execute('INSERT INTO ' + table +
                 ' (account, dialog_id, thread_id, mode, shortcut, data) VALUES (?, ?, ?, ?, ?, ?)',
                 (7, -100, 4, 0, '', b'duplicate'))
except sqlite3.IntegrityError:
    pass
else:
    raise SystemExit('docked primary key no longer isolates mode/shortcut rows')
conn.commit()
modes = conn.execute('SELECT mode, shortcut, data FROM ' + table +
                     ' WHERE account = 7 AND dialog_id = -100 AND thread_id = 4 ORDER BY mode, shortcut').fetchall()
if [(row[0], row[1], bytes(row[2])) for row in modes] != [
        (0, '', legacy_rows[0][3]),
        (0, 'work', b'shortcut-mode'),
        (5, 'work', b'quick-mode')]:
    raise SystemExit('docked rows for one chat did not stay distinct by mode/shortcut')
if conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
                (legacy_name,)).fetchone() is not None:
    raise SystemExit('legacy docked table was not dropped')
conn.execute(create_sql)
conn.commit()
if conn.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] != 4:
    raise SystemExit('re-running the docked migration disturbed existing rows')

# A fresh install has no legacy table: the copy must be skipped entirely.
fresh = sqlite3.connect(':memory:')
fresh.execute(create_sql)
fresh.execute(create_sql)
if fresh.execute(legacy_query).fetchone() is not None:
    raise SystemExit('fresh docked database unexpectedly has a legacy table')
fresh.execute('INSERT INTO ' + table +
              ' (account, dialog_id, thread_id, mode, shortcut, data) VALUES (?, ?, ?, ?, ?, ?)',
              (1, 2, 3, 0, '', b'fresh'))
if fresh.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] != 1:
    raise SystemExit('fresh docked table is not writable')

print('PASS: docked migration preserves blobs and isolates mode/shortcut rows')


# ------------------------------------------------------- compile the actual store

def jar(group, artifact, version):
    found = list((args.cache/group/artifact/version).glob('*/' + artifact + '-' + version + '.jar'))
    if not found:
        raise SystemExit('Missing cached dependency ' + artifact + ' ' + version)
    return found[0]


compiler = [jar('org.jetbrains.kotlin', a, '2.2.21') for a in
            ['kotlin-compiler-embeddable', 'kotlin-stdlib', 'kotlin-script-runtime', 'kotlin-reflect']]
compiler += [jar('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm', '1.8.0'),
             jar('org.jetbrains', 'annotations', '13.0')]
stdlib = compiler[1]

java_stubs = {
    'BuildVars.java': '''package org.telegram.messenger;

public class BuildVars {
    public static boolean LOGS_ENABLED = false;
}
''',
    'FileLog.java': '''package org.telegram.messenger;

public class FileLog {
    public static void e(String message) {}
    public static void e(Throwable throwable) {}
}
''',
    'NativeByteBuffer.java': '''package org.telegram.tgnet;

public class NativeByteBuffer {}
''',
}

kotlin_stubs = {
    'StubChat.kt': r'''package org.telegram.ui

object ChatActivity {
    const val MODE_DEFAULT = 0
    const val MODE_QUICK_REPLIES = 5
}
''',
    'StubMessenger.kt': r'''package org.telegram.messenger

import org.telegram.tgnet.SerializedData

object Utilities {
    val globalQueue = GlobalQueue()

    class GlobalQueue {
        private val tasks = ArrayDeque<Runnable>()

        fun postRunnable(runnable: Runnable) {
            tasks.addLast(runnable)
        }

        fun runAll() {
            while (tasks.isNotEmpty()) tasks.removeFirst().run()
        }

        fun clear() {
            tasks.clear()
        }
    }
}

class VideoEditedInfo {
    var value: String = ""

    fun getString(): String = value

    fun parseString(string: String): Boolean {
        if (string == "broken") return false
        value = string
        return true
    }
}

class MediaController {
    class PhotoEntry(
        val id: Int,
        val imageId: Int,
        val account: Int,
        var path: String?,
        var orientation: Int,
        var isVideo: Boolean,
        var width: Int,
        var height: Int,
        var size: Long
    ) {
        var imagePath: String? = null
        var filterPath: String? = null
        var paintPath: String? = null
        var fullPaintPath: String? = null
        var croppedPaintPath: String? = null
        var isFiltered = false
        var isPainted = false
        var isCropped = false
        var highQuality = false
        var savedFilterState: SavedFilterState? = null
        var cropState: CropState? = null
    }

    class SavedFilterState {
        var marker = ""

        fun serializeToStream(stream: SerializedData) {
            stream.writeString(marker)
        }

        fun readParams(stream: SerializedData, exception: Boolean) {
            marker = stream.readString(false) ?: ""
        }
    }

    class CropState {
        var cropPx = 0f
        var cropPy = 0f
        var cropScale = 0f
        var cropRotate = 0f
        var cropPw = 0f
        var cropPh = 0f
        var transformWidth = 0
        var transformHeight = 0
        var transformRotation = 0
        var mirrored = false
        var stateScale = 0f
        var scale = 0f
        var width = 0
        var height = 0
        var freeform = false
        var lockedAspectRatio = 0f
        var orientation = 0
    }
}
''',
    'StubTgnet.kt': r'''package org.telegram.tgnet

open class TLObject {
    open fun serializeToStream(stream: SerializedData) {}
}

object TLRPC {
    class MessageEntity : TLObject() {
        var marker = ""

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(0x12345678)
            stream.writeString(marker)
        }

        companion object {
            @JvmStatic
            fun TLdeserialize(stream: SerializedData, constructor: Int, exception: Boolean): MessageEntity? =
                MessageEntity().also { it.marker = stream.readString(false) ?: "" }
        }
    }

    class InputDocument : TLObject() {
        var marker = ""

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(0x12345678)
            stream.writeString(marker)
        }

        companion object {
            @JvmStatic
            fun TLdeserialize(stream: SerializedData, constructor: Int, exception: Boolean): InputDocument? =
                InputDocument().also { it.marker = stream.readString(false) ?: "" }
        }
    }

    class Document : TLObject() {
        var marker = ""

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(0x12345678)
            stream.writeString(marker)
        }

        companion object {
            @JvmStatic
            fun TLdeserialize(stream: SerializedData, constructor: Int, exception: Boolean): Document? =
                Document().also { it.marker = stream.readString(false) ?: "" }
        }
    }

    class BotInlineResult : TLObject() {
        var marker = ""

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(0x12345678)
            stream.writeString(marker)
        }

        companion object {
            @JvmStatic
            fun TLdeserialize(stream: SerializedData, constructor: Int, exception: Boolean): BotInlineResult? =
                BotInlineResult().also { it.marker = stream.readString(false) ?: "" }
        }
    }
}
''',
    'StubDockedMedia.kt': r'''package tele.helpers

import org.telegram.messenger.MediaController
import org.telegram.messenger.VideoEditedInfo
import org.telegram.tgnet.TLRPC
import org.telegram.ui.ChatActivity

object DockedMedia {
data class Key(
    val account: Int,
    val dialogId: Long,
    val threadId: Long,
    val mode: Int = ChatActivity.MODE_DEFAULT,
    val shortcut: String = ""
)

class Item {
    var path: String? = null
    var imagePath: String? = null
    var thumbPath: String? = null
    var coverPath: String? = null
    var imageId = 0
    var isVideo = false
    var width = 0
    var height = 0
    var duration = 0
    var size = 0L
    var orientation = 0
    var invert = 0
    var ttl = 0
    var spoiler = false
    var highQuality = false
    var canDeleteAfter = false
    var asFile = false
    var stars = 0L
    var videoInfo: VideoEditedInfo? = null
    var caption: String? = null
    var entities: ArrayList<TLRPC.MessageEntity>? = null
    var masks: ArrayList<TLRPC.InputDocument>? = null
    var document: TLRPC.Document? = null
    var inlineResult: TLRPC.BotInlineResult? = null
    var isFile = false
    var fileName: String? = null
    var original: MediaController.PhotoEntry? = null
}

class Tray {
    val items = ArrayList<Item>()
    var group = true
    var invert = false
    var date = 0
}
}
''',
    'StubTeleAccounts.kt': r'''package tele.helpers

object TeleAccounts {
    private val generations = HashMap<Int, Long>()
    private val enabled = HashMap<Int, Boolean>()

    @JvmStatic
    fun generation(account: Int): Long = generations[account] ?: 0L

    @JvmStatic
    fun isCurrent(account: Int, generation: Long): Boolean =
        generation(account) == generation && (enabled[account] ?: true)

    fun revoke(account: Int) {
        generations[account] = generation(account) + 1
    }

    fun setEnabled(account: Int, value: Boolean) {
        enabled[account] = value
    }

    fun reset() {
        generations.clear()
        enabled.clear()
    }
}
''',
    'StubTeleDatabase.kt': r'''package tele.db

object TeleDatabaseHelper {
    class DockedRow(
        val dialogId: Long,
        val threadId: Long,
        val data: ByteArray,
        val mode: Int = 0,
        val shortcut: String = ""
    )

    private data class RowKey(
        val account: Int,
        val dialogId: Long,
        val threadId: Long,
        val mode: Int,
        val shortcut: String
    )

    private class Row(
        val account: Int,
        val dialogId: Long,
        val threadId: Long,
        val mode: Int,
        val shortcut: String,
        val data: ByteArray
    )

    private val rows = LinkedHashMap<RowKey, Row>()
    var putCalls = 0
    var putFailure: RuntimeException? = null

    fun putDocked(account: Int, dialogId: Long, threadId: Long, mode: Int, shortcut: String, data: ByteArray?) {
        putCalls++
        putFailure?.let { throw it }
        val key = RowKey(account, dialogId, threadId, mode, shortcut)
        if (data == null) {
            rows.remove(key)
            return
        }
        rows[key] = Row(account, dialogId, threadId, mode, shortcut, data.copyOf())
    }

    fun getDocked(account: Int): List<DockedRow> =
        rows.values.filter { it.account == account }.map {
            DockedRow(it.dialogId, it.threadId, it.data.copyOf(), it.mode, it.shortcut)
        }

    fun count(): Int = rows.size

    fun reset() {
        rows.clear()
        putCalls = 0
        putFailure = null
    }
}
''',
    'Test.kt': r'''package regression

import org.telegram.messenger.MediaController
import org.telegram.messenger.Utilities
import org.telegram.messenger.VideoEditedInfo
import org.telegram.tgnet.SerializedData
import org.telegram.tgnet.TLRPC
import org.telegram.ui.ChatActivity
import tele.db.TeleDatabaseHelper
import tele.helpers.DockedMedia
import tele.helpers.DockedStore
import tele.helpers.TeleAccounts

private const val ACCOUNT = 3
private const val MAGIC = 0x444d4544
private const val VERSION = 5

private fun reset() {
    TeleDatabaseHelper.reset()
    Utilities.globalQueue.clear()
    TeleAccounts.reset()
}

private fun trayNamed(name: String): DockedMedia.Tray {
    val tray = DockedMedia.Tray()
    val item = DockedMedia.Item()
    item.path = "/" + name
    tray.items.add(item)
    return tray
}

private fun sampleItem(): DockedMedia.Item {
    val item = DockedMedia.Item()
    item.path = "/media/photo.jpg"
    item.imagePath = "/media/photo-edited.jpg"
    item.thumbPath = "/media/thumb.jpg"
    item.coverPath = "/media/cover.jpg"
    item.imageId = 42
    item.isVideo = true
    item.width = 640
    item.height = 480
    item.duration = 9000
    item.size = 123456789L
    item.orientation = 90
    item.invert = 3
    item.ttl = 60
    item.spoiler = true
    item.highQuality = true
    item.canDeleteAfter = true
    item.asFile = true
    item.stars = 17L
    item.videoInfo = VideoEditedInfo().apply { value = "video-meta" }
    item.caption = "caption text"
    item.entities = arrayListOf(
        TLRPC.MessageEntity().apply { marker = "entity-one" },
        TLRPC.MessageEntity().apply { marker = "entity-two" }
    )
    item.masks = arrayListOf(
        TLRPC.InputDocument().apply { marker = "mask-one" }
    )
    item.document = TLRPC.Document().apply { marker = "document-marker" }
    item.inlineResult = TLRPC.BotInlineResult().apply { marker = "inline-marker" }
    item.isFile = true
    item.fileName = "notes.bin"

    val original = MediaController.PhotoEntry(0, item.imageId, 0, "/orig/source.jpg",
        item.orientation, item.isVideo, item.width, item.height, item.size)
    original.imagePath = "/orig/frame.jpg"
    original.filterPath = "/orig/filter.jpg"
    original.paintPath = "/orig/paint.png"
    original.fullPaintPath = "/orig/full-paint.png"
    original.croppedPaintPath = "/orig/cropped-paint.png"
    original.isFiltered = true
    original.isPainted = true
    original.isCropped = true
    original.savedFilterState = MediaController.SavedFilterState().apply { marker = "filter-state" }
    original.cropState = MediaController.CropState().apply {
        cropPx = 1.5f
        cropPy = -2.25f
        cropScale = 0.75f
        cropRotate = 45.5f
        cropPw = 3.5f
        cropPh = 4.25f
        transformWidth = 1920
        transformHeight = 1080
        transformRotation = 90
        mirrored = true
        stateScale = 1.25f
        scale = 2.0f
        width = 640
        height = 480
        freeform = true
        lockedAspectRatio = 1.5f
        orientation = 1
    }
    item.original = original
    return item
}

private fun v5RoundTrip() {
    reset()
    val key = DockedMedia.Key(ACCOUNT, -100123L, 77L)
    val tray = DockedMedia.Tray().apply {
        group = false
        invert = true
        date = 171717
    }
    tray.items.add(sampleItem())
    DockedStore.save(key, tray)
    check(TeleDatabaseHelper.putCalls == 0) { "save wrote before the global queue" }
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.putCalls == 1)

    val stored = TeleDatabaseHelper.getDocked(ACCOUNT).single()
    check(stored.dialogId == key.dialogId && stored.threadId == key.threadId)
    check(stored.mode == 0 && stored.shortcut == "")
    val header = SerializedData(stored.data)
    try {
        check(header.readInt32(false) == MAGIC) { "wrong docked magic" }
        check(header.readInt32(false) == VERSION) { "docked blob is not v5" }
    } finally {
        header.cleanup()
    }

    // an old v5 row has no modes: put the same blob back under the default key
    TeleDatabaseHelper.reset()
    TeleDatabaseHelper.putDocked(ACCOUNT, key.dialogId, key.threadId, 0, "", stored.data.copyOf())
    val loaded = DockedStore.load(ACCOUNT)
    check(loaded.size == 1)
    val restored = loaded[key] ?: error("v5 tray was not restored")
    check(!restored.group && restored.invert && restored.date == 171717)
    check(restored.items.size == 1)
    val item = restored.items.single()
    check(item.path == "/media/photo.jpg")
    check(item.imagePath == "/media/photo-edited.jpg")
    check(item.thumbPath == "/media/thumb.jpg")
    check(item.coverPath == "/media/cover.jpg")
    check(item.imageId == 42)
    check(item.isVideo)
    check(item.width == 640 && item.height == 480)
    check(item.duration == 9000)
    check(item.size == 123456789L)
    check(item.orientation == 90 && item.invert == 3 && item.ttl == 60)
    check(item.spoiler && item.highQuality && item.canDeleteAfter && item.asFile)
    check(item.stars == 17L)
    check(item.videoInfo?.value == "video-meta")
    check(item.caption == "caption text")
    check(item.entities?.map { it.marker } == listOf("entity-one", "entity-two"))
    check(item.masks?.map { it.marker } == listOf("mask-one"))
    check(item.document?.marker == "document-marker")
    check(item.inlineResult?.marker == "inline-marker")
    check(item.isFile && item.fileName == "notes.bin")
    val original = item.original ?: error("edited original was not restored")
    check(original.path == "/orig/source.jpg")
    check(original.imagePath == "/orig/frame.jpg")
    check(original.filterPath == "/orig/filter.jpg")
    check(original.paintPath == "/orig/paint.png")
    check(original.fullPaintPath == "/orig/full-paint.png")
    check(original.croppedPaintPath == "/orig/cropped-paint.png")
    check(original.isFiltered && original.isPainted && original.isCropped)
    check(original.highQuality)
    check(original.savedFilterState?.marker == "filter-state")
    val crop = original.cropState ?: error("crop state was not restored")
    check(crop.cropPx == 1.5f && crop.cropPy == -2.25f)
    check(crop.cropScale == 0.75f && crop.cropRotate == 45.5f)
    check(crop.cropPw == 3.5f && crop.cropPh == 4.25f)
    check(crop.transformWidth == 1920 && crop.transformHeight == 1080)
    check(crop.transformRotation == 90 && crop.mirrored)
    check(crop.stateScale == 1.25f && crop.scale == 2.0f)
    check(crop.width == 640 && crop.height == 480)
    check(crop.freeform && crop.lockedAspectRatio == 1.5f && crop.orientation == 1)
}

private fun keyIsolation() {
    reset()
    val dialogId = -777L
    val threadId = 11L
    val account = 2
    val plain = DockedMedia.Key(account, dialogId, threadId)
    val quick = DockedMedia.Key(account, dialogId, threadId, ChatActivity.MODE_QUICK_REPLIES, "work")
    val shortcut = DockedMedia.Key(account, dialogId, threadId, 0, "work")
    val otherAccount = DockedMedia.Key(9, dialogId, threadId)
    val keys = listOf(plain, quick, shortcut, otherAccount)
    val names = listOf("plain", "quick", "shortcut", "other-account")
    keys.forEachIndexed { index, key -> DockedStore.save(key, trayNamed(names[index])) }
    check(TeleDatabaseHelper.putCalls == 0)
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 4) { "mode/shortcut/account rows overwrote each other" }

    val loaded = DockedStore.load(account)
    check(loaded.size == 3)
    for (index in 0..2) {
        check(loaded[keys[index]]?.items?.single()?.path == "/" + names[index])
    }
    check(DockedStore.load(9).size == 1)

    DockedStore.save(quick, null)
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 3)
    val afterDelete = DockedStore.load(account)
    check(afterDelete.size == 2 && !afterDelete.containsKey(quick))
    check(afterDelete.containsKey(plain) && afterDelete.containsKey(shortcut))
    check(DockedStore.load(9).size == 1)

    DockedStore.save(plain, DockedMedia.Tray())
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 2) { "an empty tray did not delete only its key" }
    check(!DockedStore.load(account).containsKey(plain))
    check(DockedStore.load(account).containsKey(shortcut))

    DockedStore.save(shortcut, trayNamed("replaced"))
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 2)
    check(DockedStore.load(account)[shortcut]?.items?.single()?.path == "/replaced")
    check(DockedStore.load(9)[otherAccount]?.items?.single()?.path == "/other-account")
}

private fun asyncGenerationBlocks() {
    reset()
    val account = 4
    val key = DockedMedia.Key(account, -55L, 6L)

    DockedStore.save(key, trayNamed("stale"))
    check(TeleDatabaseHelper.putCalls == 0)
    TeleAccounts.revoke(account)
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 0) { "a save from the old generation reached the database" }

    DockedStore.save(key, trayNamed("stale-again"))
    TeleAccounts.revoke(account)
    DockedStore.save(key, trayNamed("fresh"))
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 1) { "the stale write was not skipped" }
    check(DockedStore.load(account)[key]?.items?.single()?.path == "/fresh")

    DockedStore.save(key, null)
    TeleAccounts.revoke(account)
    Utilities.globalQueue.runAll()
    check(TeleDatabaseHelper.count() == 1) { "a stale delete removed the current tray" }
    check(DockedStore.load(account).size == 1)

    DockedStore.save(key, trayNamed("newest"))
    Utilities.globalQueue.runAll()
    check(DockedStore.load(account)[key]?.items?.single()?.path == "/newest")
}

fun main() {
    v5RoundTrip()
    keyIsolation()
    asyncGenerationBlocks()
    println("PASS: DockedStore v5 roundtrip, mode/shortcut/account keys, async generation gating")
}
''',
}

javaout = here/'java-classes'
javaout.mkdir(exist_ok=True)
java_sources = [tgnet/'SerializedData.java', tgnet/'AbstractSerializedData.java',
                tgnet/'InputSerializedData.java', tgnet/'OutputSerializedData.java',
                tgnet/'TLDataSourceType.java']
for name, text in java_stubs.items():
    path = here/name
    path.write_text(text, encoding='utf-8')
    java_sources.append(path)
subprocess.run([args.javac, '-d', str(javaout)] + [str(path) for path in java_sources], check=True)

kotlin_files = []
for name, text in kotlin_stubs.items():
    path = here/name
    path.write_text(text, encoding='utf-8')
    kotlin_files.append(path)
kotlin_files.append(docked_source)

classes = here/'test.jar'
subprocess.run(
    [args.java, '-cp', os.pathsep.join(map(str, compiler)),
     'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
     '-no-stdlib', '-no-reflect',
     '-classpath', os.pathsep.join([str(javaout), str(stdlib)]),
     '-d', str(classes)] + [str(path) for path in kotlin_files],
    check=True
)
subprocess.run(
    [args.java, '-cp', os.pathsep.join([str(classes), str(javaout), str(stdlib)]), 'regression.TestKt'],
    check=True
)
