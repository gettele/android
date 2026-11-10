"""Compile the actual TeleUpdater.kt and the actual bounds/loadPhoto helpers of
TeleServerNotices.kt against deterministic stubs, then exercise them.

SEC-10 is checked behaviourally: the release feed tag is allow-listed before any
local path exists, update target/temp files stay inside the canonical update dir,
and notice photo bounds reject oversized or overflowing images while loadPhoto
samples valid ones down to the UI limit (the stub BitmapFactory records decodes).

Only TeleUpdater.kt is compiled as a whole; TeleServerNotices.kt is far too
entangled with Android/Telegram UI to stub completely, so its private
validBounds/bounds constants and the loadPhoto body are taken verbatim from the
actual source and compiled in a harness. No assertion inspects source text.

Run with --root pointing at the workspace containing Telegram/; the Kotlin
compiler dependencies must already be in --cache.
"""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument('--output', type=Path)
parser.add_argument('--cache', type=Path, default=Path.home()/'.gradle/caches/modules-2/files-2.1')
parser.add_argument('--java', default=os.environ.get('JAVA', shutil.which('java') or 'java'))
args = parser.parse_args()

root = args.root.resolve()
temporary = tempfile.TemporaryDirectory(prefix='tele-download-bounds-') if args.output is None else None
here = args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache = args.cache


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


def build(name, sources, product, main_class):
    workdir = here/name
    workdir.mkdir(parents=True, exist_ok=True)
    files = []
    for filename, text in sources.items():
        path = workdir/filename
        path.write_text(text, encoding='utf-8')
        files.append(str(path))
    if product is not None:
        files.append(str(product))
    out = workdir/'classes.jar'
    subprocess.run([args.java, '-cp', os.pathsep.join(map(str, compiler)),
                    'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
                    '-no-stdlib', '-no-reflect', '-classpath', str(stdlib),
                    '-d', str(out)] + files, check=True)
    subprocess.run([args.java, '-cp', os.pathsep.join([str(out), str(stdlib)]), main_class], check=True)


# ---------------------------------------------------------------- TeleUpdater

updater = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/TeleUpdater.kt'
notices = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/TeleServerNotices.kt'
if not updater.is_file() or not notices.is_file():
    raise SystemExit('Cannot find TeleUpdater.kt / TeleServerNotices.kt under ' + str(root))

updater_sources = {
    'Context.kt': r'''package android.content

import java.io.File

open class Context(val filesDir: File = File(".")) {
    val packageName = "tele.test"
    val packageManager = PackageManager()
}

class PackageManager {
    fun getPackageInfo(name: String, flags: Int): PackageInfo = PackageInfo()
}

class PackageInfo {
    var versionCode = 100
    var longVersionCode = 100L
}
''',
    'Activity.kt': r'''package android.app

class Activity : android.content.Context()
''',
    'Build.kt': r'''package android.os

object Build {
    object VERSION { const val SDK_INT = 34 }
}
''',
    'Log.kt': r'''package android.util

object Log {
    fun d(tag: String, message: String): Int = 0
}
''',
    'Json.kt': r'''package org.json

// flat feed json only: strings, numbers, booleans and null
class JSONObject(text: String = "{}") {
    private val values = HashMap<String, Any?>()

    init {
        val pair = Regex("\"((?:[^\"\\\\]|\\\\.)*)\"\\s*:\\s*(\"(?:[^\"\\\\]|\\\\.)*\"|-?[0-9]+(?:\\.[0-9]+)?|true|false|null)")
        for (match in pair.findAll(text)) {
            val key = unescape(match.groupValues[1])
            val raw = match.groupValues[2]
            values[key] = when {
                raw == "null" -> null
                raw == "true" -> true
                raw == "false" -> false
                raw.startsWith("\"") -> unescape(raw.substring(1, raw.length - 1))
                raw.contains('.') -> raw.toDouble()
                else -> raw.toLong()
            }
        }
    }

    fun optString(name: String): String {
        val value = values[name] ?: return ""
        return if (value is String) value else value.toString()
    }

    fun opt(name: String): Any? = values[name]

    private fun unescape(text: String): String {
        val out = StringBuilder(text.length)
        var index = 0
        while (index < text.length) {
            val char = text[index++]
            if (char != '\\' || index >= text.length) {
                out.append(char)
                continue
            }
            when (val next = text[index++]) {
                'n' -> out.append('\n')
                'r' -> out.append('\r')
                't' -> out.append('\t')
                '"' -> out.append('"')
                '\\' -> out.append('\\')
                '/' -> out.append('/')
                'u' -> {
                    val hex = text.substring(index, minOf(index + 4, text.length))
                    out.append(hex.toIntOrNull(16)?.toChar() ?: '?')
                    index += hex.length
                }
                else -> out.append(next)
            }
        }
        return out.toString()
    }
}
''',
    'Telegram.kt': r'''package org.telegram.messenger

import android.content.Context
import java.io.File

object AndroidUtilities {
    fun runOnUIThread(runnable: Runnable) { runnable.run() }
    fun openForView(file: File, name: String, mime: String, activity: android.app.Activity?, extra: Any?, flag: Boolean): Boolean = true
}

object ApplicationLoader {
    @JvmStatic
    var applicationContext: Context = Context(File("."))
}

object BuildVars {
    @JvmStatic
    var BUILD_VERSION_STRING = "13.2.1"
}

class DispatchQueue(name: String) {
    fun postRunnable(runnable: Runnable) {}
    fun postRunnable(runnable: Runnable, delay: Long) {}
    fun cancelRunnable(runnable: Runnable) {}
}

object FileLog {
    fun e(text: String) {}
    fun e(t: Throwable) {}
}
''',
    'Browser.kt': r'''package org.telegram.messenger.browser

object Browser {
    fun openUrl(context: android.content.Context, url: String) {}
}
''',
    'Ui.kt': r'''package org.telegram.ui

class Fragment {
    fun presentFragment(fragment: Any) {}
}

object LaunchActivity {
    @JvmStatic
    fun getSafeLastFragment(): Fragment? = null
}
''',
    'Settings.kt': r'''package tele.ui.settings

class TeleSettingsActivity(mode: Int) {
    companion object { const val MODE_UPDATES = 1 }
}
''',
    'Tele.kt': r'''package tele

object TeleBuild { var BUILD = 42 }

object TeleConfig {
    object AUTO_UPDATE { var value = true }
}
''',
    'Lower.kt': r'''package tele.helpers

object TeleLowercase {
    fun lc(text: String): String = text
}

object TeleNoticeSources {
    fun update(tag: String) {}
}
''',
    'Test.kt': r'''package regression

import android.content.Context
import org.telegram.messenger.ApplicationLoader
import tele.helpers.TeleUpdater
import java.io.File
import java.lang.reflect.Method
import java.nio.file.Files

private const val DOWNLOAD_PREFIX = "https://github.com/gettele/android/releases/download/"

private fun feed(
    tag: String,
    urlTag: String = tag,
    suffix: String = ".apk",
    sha: String = "a".repeat(64),
    base: Long = 13,
    counter: Long = 42
): String = "{\"tag\":\"$tag\",\"base\":$base,\"counter\":$counter,\"url\":\"$DOWNLOAD_PREFIX$urlTag/tele$suffix\",\"apk_sha256\":\"$sha\"}"

private fun accepted(
    parse: Method,
    tag: String,
    urlTag: String = tag,
    suffix: String = ".apk",
    sha: String = "a".repeat(64),
    base: Long = 13,
    counter: Long = 42
): Boolean = parse.invoke(TeleUpdater, feed(tag, urlTag, suffix, sha, base, counter)) != null

fun main() {
    val filesDir = Files.createTempDirectory("tele-updater-test").toFile()
    ApplicationLoader.applicationContext = Context(filesDir)

    val type = TeleUpdater::class.java
    val parse = type.getDeclaredMethod("parse", String::class.java).apply { isAccessible = true }

    // the shape the release workflow publishes
    check(accepted(parse, "v13.2.1-tele.42"))
    check(accepted(parse, "v1-tele.1"))
    check(accepted(parse, "v1.2-tele.7", sha = "0123456789abcdef".repeat(4)))

    // the maximum allowed length is still accepted
    val tag96 = "v1" + ".1".repeat(43) + "-tele.42"
    check(tag96.length == 96)
    check(accepted(parse, tag96))

    // unsafe or off-format tags are rejected by the allowlist
    val unsafe = listOf(
        "../escape",
        "v1-tele.1/../../escape",
        "v1-tele.1/",
        "v1-tele.1 ",
        " v1-tele.1",
        "V1-tele.1",
        "v1-tele.",
        "v1-tele.1.apk",
        "v1_tele.1",
        "v1.2.3",
        "tele.1",
        "v1..2-tele.1",
        "v1-tele.1\n"
    )
    for (tag in unsafe) check(!accepted(parse, tag))

    // one char over the limit is rejected even when the shape matches
    val tag97 = "v1" + ".1".repeat(44) + "-tele.4"
    check(tag97.length == 97)
    check(!accepted(parse, tag97))
    check(!accepted(parse, "v" + "1.".repeat(60) + "1-tele.1"))
    check(!accepted(parse, ""))

    // the feed still has to point at the release download of the accepted tag
    check(!accepted(parse, "v1-tele.1", urlTag = "v2-tele.2"))
    check(!accepted(parse, "v1-tele.1", suffix = ".zip"))
    check(!accepted(parse, "v1-tele.1", sha = "a".repeat(63)))
    check(!accepted(parse, "v1-tele.1", sha = "z".repeat(64)))
    check(!accepted(parse, "v1-tele.1", base = 0))
    check(!accepted(parse, "v1-tele.1", counter = 0))

    // rejected feeds never built a local path
    val updatesDir = type.getDeclaredMethod("updatesDir").apply { isAccessible = true }.invoke(TeleUpdater) as File
    check(updatesDir.listFiles().isNullOrEmpty())
    updatesDir.mkdirs()

    val updateFile = type.getDeclaredMethod("updateFile", String::class.java).apply { isAccessible = true }
    fun resolved(name: String): File? = updateFile.invoke(TeleUpdater, name) as File?

    val target = resolved("tele-v13.2.1-tele.42.apk") ?: error("safe tag name was rejected")
    check(target.name == "tele-v13.2.1-tele.42.apk")
    check(target.canonicalFile.parentFile == updatesDir.canonicalFile)
    check(resolved(target.name + ".part")?.canonicalFile?.parentFile == updatesDir.canonicalFile)

    // traversal and subdirectories stay out
    check(resolved("../escape.apk") == null)
    check(resolved("tele/../../escape.apk") == null)
    check(resolved("nested/tele.apk") == null)
    check(resolved("/tmp/tele.apk") == null)
    check(resolved("") == null)
    // names that canonically stay inside are allowed
    check(resolved("sub/../tele.apk") != null)

    // a symlink planted in the cache dir may not pull the target outside either
    val outside = Files.createTempDirectory("tele-updater-outside").toFile()
    File(outside, "evil.apk").writeText("x")
    val link = File(updatesDir, "link.apk")
    val linked = runCatching { Files.createSymbolicLink(link.toPath(), File(outside, "evil.apk").toPath()) }.isSuccess
    if (linked) check(resolved("link.apk") == null)

    println("PASS: TeleUpdater tag allowlist, URL constraints, canonical path containment")
}
''',
}

build('updater', updater_sources, updater, 'regression.TestKt')


# ------------------------------------------------- TeleServerNotices photo bits

source = notices.read_text(encoding='utf-8')


def method(signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    index = brace
    while True:
        char = source[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                break
        index += 1
    return source[start:index + 1]


valid_bounds = method('private fun validBounds(width: Int, height: Int): Boolean')
load_photo = method('fun loadPhoto(name: String, done: (Bitmap?) -> Unit)')


def constant(name):
    match = re.search(r'private const val ' + name + r'\s*=\s*([^\n]+)', source)
    if match is None:
        raise SystemExit('Cannot find ' + name + ' in TeleServerNotices.kt')
    return match.group(1).strip()


max_dimension = constant('MAX_PHOTO_DIMENSION')
max_pixels = constant('MAX_PHOTO_PIXELS')

bounds_sources = {
    'Bitmap.kt': r'''package android.graphics

class Bitmap

object BitmapFactory {
    class Options {
        var inJustDecodeBounds = false
        var inSampleSize = 1
        var outWidth = -1
        var outHeight = -1
        var outMimeType: String? = null
    }

    var width = 0
    var height = 0
    var outMime: String? = "image/png"
    val decodes = ArrayList<Options>()

    fun decodeFile(path: String, options: Options): Bitmap? {
        decodes.add(Options().apply {
            inJustDecodeBounds = options.inJustDecodeBounds
            inSampleSize = options.inSampleSize
        })
        if (options.inJustDecodeBounds) {
            options.outWidth = width
            options.outHeight = height
            options.outMimeType = outMime
            return null
        }
        return Bitmap()
    }
}
''',
    'Cache.kt': r'''package android.util

class LruCache<K, V>(size: Int) {
    private val values = HashMap<K, V>()

    fun get(key: K): V? = values[key]
    fun put(key: K, value: V): V? = values.put(key, value)
    fun clear() = values.clear()
}
''',
    'Telegram.kt': r'''package org.telegram.messenger

class DisplaySize {
    var x = 1080
    var y = 1920
}

object AndroidUtilities {
    val displaySize = DisplaySize()
    fun dp(value: Float): Int = value.toInt()
    fun runOnUIThread(runnable: Runnable) { runnable.run() }
}

class DispatchQueue {
    fun postRunnable(runnable: Runnable) { runnable.run() }
}

object FileLog {
    fun e(t: Throwable) {}
}
''',
    'Harness.kt': r'''package regression

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import org.telegram.messenger.AndroidUtilities
import org.telegram.messenger.DispatchQueue
import org.telegram.messenger.FileLog
import java.io.File
import java.nio.file.Files

object PhotoBounds {
    private const val MAX_PHOTO_DIMENSION = ''' + max_dimension + r'''
    private const val MAX_PHOTO_PIXELS = ''' + max_pixels + r'''

    var root: File = File(".")
    val photos = LruCache<String, Bitmap>(8)
    val photoQueue = DispatchQueue()

    fun photoDir(): File = root

''' + valid_bounds + r'''

''' + load_photo + r'''
}

private val boundsMethod = PhotoBounds::class.java.getDeclaredMethod(
    "validBounds",
    Int::class.javaPrimitiveType!!,
    Int::class.javaPrimitiveType!!
).apply { isAccessible = true }

private fun bounds(width: Int, height: Int): Boolean =
    boundsMethod.invoke(PhotoBounds, width, height) as Boolean

private fun decode(width: Int, height: Int, mime: String? = "image/png"): Pair<Int, Bitmap?> {
    BitmapFactory.width = width
    BitmapFactory.height = height
    BitmapFactory.outMime = mime
    BitmapFactory.decodes.clear()
    PhotoBounds.photos.clear()
    var result: Bitmap? = null
    var calls = 0
    PhotoBounds.loadPhoto("tele_notice_1_1") { result = it; calls++ }
    check(calls == 1)
    return BitmapFactory.decodes.last().inSampleSize to result
}

fun main() {
    PhotoBounds.root = Files.createTempDirectory("tele-notice-photos").toFile()
    AndroidUtilities.displaySize.x = 600

    // dimensions and the pixel budget, including products that overflow Int
    check(bounds(1, 1))
    check(bounds(16384, 2048)) // exactly MAX_PHOTO_PIXELS
    check(!bounds(16384, 2049))
    check(!bounds(0, 10))
    check(!bounds(10, 0))
    check(!bounds(-1, 10))
    check(!bounds(10, -1))
    check(!bounds(16385, 1))
    check(!bounds(1, 16385))
    check(!bounds(46341, 46341))
    check(!bounds(65535, 65535))

    // loadPhoto refuses before the real decode and samples the rest under the ui limit
    val (sample, bitmap) = decode(1201, 1201)
    check(bitmap != null)
    check(BitmapFactory.decodes.size == 2)
    check(BitmapFactory.decodes[0].inJustDecodeBounds)
    check(BitmapFactory.decodes[1].inSampleSize == sample)
    check(sample == 4) // ceil(1201 / 2) = 601 > 600
    check((1201 + sample - 1) / sample <= 600)

    check(decode(1000, 1000).first == 2)
    check(decode(600, 600).first == 1)
    check(decode(3000, 100).first == 8)

    val tooWide = decode(20000, 10)
    check(tooWide.second == null)
    check(BitmapFactory.decodes.size == 1)


    val overflowing = decode(46341, 46341)
    check(overflowing.second == null)
    check(BitmapFactory.decodes.size == 1)

    println("PASS: notice photo bounds, Int overflow guard, ceil sampling")
}
''',
}

build('bounds', bounds_sources, None, 'regression.HarnessKt')

print('PASS: SEC-10 updater path containment and notice photo bounds')
