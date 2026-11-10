#!/usr/bin/env python3
"""Exercise DockedIngress by compiling the actual Kotlin source against stubs.

The stubs model only the Android/Telegram surface DockedIngress touches and copy
shared URIs into a real temporary cache, so staging, generation checks and file
cleanup run for real. Every scenario drives the entry points and inspects the
tray calls and files they produce; nothing is asserted about the source text.
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
args = parser.parse_args()

root = args.root.resolve()
temporary = tempfile.TemporaryDirectory(prefix='tele-docked-ingress-') if args.output is None else None
here = args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)

ingress_source = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/DockedIngress.kt'
if not ingress_source.is_file():
    raise SystemExit('Cannot find ' + str(ingress_source))


def jar(group, artifact, version):
    found = list((args.cache/group/artifact/version).glob('*/' + artifact + '-' + version + '.jar'))
    if not found:
        raise SystemExit('Cannot find ' + artifact + '-' + version + '.jar in ' + str(args.cache))
    return found[0]


compiler = [jar('org.jetbrains.kotlin', name, '2.2.21') for name in
            ['kotlin-compiler-embeddable', 'kotlin-stdlib', 'kotlin-script-runtime', 'kotlin-reflect']]
compiler += [jar('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm', '1.8.0'),
             jar('org.jetbrains', 'annotations', '13.0')]
stdlib = compiler[1]

stubs = {
    'StubAndroidGraphics.kt': r'''package android.graphics

object BitmapFactory {
    class Options {
        var inJustDecodeBounds = false
        var outWidth = 0
        var outHeight = 0
    }

    val bounds = HashMap<String, Pair<Int, Int>>()

    fun decodeFile(path: String?, options: Options): Any? {
        val size = if (path == null) null else bounds[path]
        if (size != null) {
            options.outWidth = size.first
            options.outHeight = size.second
        }
        return null
    }
}
''',
    'StubAndroidMedia.kt': r'''package android.media

class MediaMetadataRetriever {
    private var path: String? = null

    companion object {
        const val METADATA_KEY_VIDEO_WIDTH = 1
        const val METADATA_KEY_VIDEO_HEIGHT = 2
        const val METADATA_KEY_VIDEO_ROTATION = 3
        const val METADATA_KEY_DURATION = 4

        val metadata = HashMap<String, Map<Int, String>>()
    }

    fun setDataSource(path: String?) {
        this.path = path
    }

    fun extractMetadata(key: Int): String? = path?.let { metadata[it]?.get(key) }

    fun release() {
        path = null
    }
}
''',
    'StubAndroidNet.kt': r'''package android.net

import java.io.File

class Uri(val filePath: String?, val isInternal: Boolean = false) {
    companion object {
        @JvmStatic
        fun fromFile(file: File): Uri = Uri(file.absolutePath)
    }
}
''',
    'StubAndroidText.kt': r'''package android.text

object TextUtils {
    @JvmStatic
    fun isEmpty(value: CharSequence?): Boolean = value == null || value.isEmpty()
}
''',
    'StubAndroidWebkit.kt': r'''package android.webkit

class MimeTypeMap {
    companion object {
        private val instance = MimeTypeMap()
        val extensions = HashMap<String, String>()

        fun getSingleton(): MimeTypeMap = instance
    }

    fun getExtensionFromMimeType(mime: String?): String? =
        if (mime == null) null else extensions[mime]
}
''',
    'StubMessenger.kt': r'''package org.telegram.messenger

import android.graphics.BitmapFactory
import android.media.MediaMetadataRetriever
import android.net.Uri
import java.io.File

class DispatchQueue {
    private val tasks = ArrayList<Runnable>()

    fun postRunnable(task: Runnable) {
        tasks.add(task)
    }

    fun pending(): Int = tasks.size

    fun clear() {
        tasks.clear()
    }

    fun runAll() {
        while (tasks.isNotEmpty()) {
            tasks.removeAt(0).run()
        }
    }
}

object Utilities {
    val globalQueue = DispatchQueue()
}

object AndroidUtilities {
    val uiQueue = DispatchQueue()
    val internalPaths = HashSet<String>()
    val orientations = HashMap<String, Pair<Int, Int>>()

    @JvmStatic
    fun isInternalUri(uri: Uri?): Boolean =
        uri != null && (uri.isInternal || uri.filePath != null && internalPaths.contains(uri.filePath))

    @JvmStatic
    fun runOnUIThread(task: Runnable) {
        uiQueue.postRunnable(task)
    }

    @JvmStatic
    fun getImageOrientation(path: String): Pair<Int, Int>? = orientations[path]
}

class ContentResolver {
    val types = HashMap<String, String>()

    fun getType(uri: Uri): String? = uri.filePath?.let { types[it] }
}

class ApplicationContext {
    val contentResolver = ContentResolver()
}

object ApplicationLoader {
    var applicationContext = ApplicationContext()
}

class MediaController {
    class PhotoEntry(
        val bucketId: Int,
        val imageId: Int,
        val dateTaken: Number,
        var path: String?,
        var duration: Int,
        var isVideo: Boolean,
        var width: Int,
        var height: Int,
        var size: Long
    ) {
        var orientation = 0
        var invert = 0

        fun setOrientation(rotationAndInvert: Pair<Int, Int>?): PhotoEntry {
            if (rotationAndInvert != null) {
                orientation = rotationAndInvert.first
                invert = rotationAndInvert.second
            }
            return this
        }

        fun isLivePhoto(): Boolean = false
    }

    class Copy(val source: String?, val destination: String, val ext: String?)

    companion object {
        var cacheDir: File? = null
        var copyCounter = 0
        val copies = ArrayList<Copy>()
        val failingPaths = HashSet<String>()
        val extensionsSeen = ArrayList<String?>()

        @JvmStatic
        fun copyFileToCache(uri: Uri, ext: String?): String? {
            extensionsSeen.add(ext)
            val source = uri.filePath ?: throw IllegalStateException("no source path")
            if (failingPaths.contains(source)) throw IllegalStateException("copy denied")
            val sourceFile = File(source)
            if (!sourceFile.isFile) throw IllegalStateException("missing source")
            val dir = cacheDir ?: throw IllegalStateException("no cache directory")
            dir.mkdirs()
            copyCounter++
            val destination = File(dir, "copy-" + copyCounter + "." + (ext ?: "file"))
            sourceFile.copyTo(destination, overwrite = true)
            copies.add(Copy(source, destination.absolutePath, ext))
            val copyPath = destination.absolutePath
            BitmapFactory.bounds[source]?.let { BitmapFactory.bounds[copyPath] = it }
            AndroidUtilities.orientations[source]?.let { AndroidUtilities.orientations[copyPath] = it }
            MediaMetadataRetriever.metadata[source]?.let { MediaMetadataRetriever.metadata[copyPath] = it }
            return destination.absolutePath
        }
    }
}

object R {
    object raw {
        const val error = 1
    }
}

class SendMessagesHelper {
    class SendingMediaInfo {
        var uri: Uri? = null
        var imagePath: String? = null
        var path: String? = null
        var caption: String? = null
        var isVideo = false
        var isLivePhoto = false
    }
}
''',
    'StubChatActivity.kt': r'''package org.telegram.ui

class ChatActivityEnterView {
    var isEditingMessage = false
    private var field: String = ""

    fun getFieldText(): CharSequence = field

    fun setFieldText(text: CharSequence?) {
        field = text?.toString().orEmpty()
    }
}

class ChatActivity {
    companion object {
        const val MODE_DEFAULT = 0
        const val MODE_SCHEDULED = 1
        const val MODE_PINNED = 2
        const val MODE_SAVED = 3
        const val MODE_QUICK_REPLIES = 5
    }

    var currentAccount = 0
    var dialogId = 0L
    var threadId = 0L
    var chatMode = MODE_DEFAULT
    var chatActivityEnterView: ChatActivityEnterView? = ChatActivityEnterView()
    var secret = false
    @JvmField var parentActivity: Any? = Any()
    @JvmField var fragmentView: Any? = Any()

    fun isSecretChat(): Boolean = secret

    fun getParentActivity(): Any? = parentActivity

    fun getFragmentView(): Any? = fragmentView
}
''',
    'StubBulletin.kt': r'''package org.telegram.ui.Components

import org.telegram.ui.ChatActivity

class Bulletin {
    fun show() {
        BulletinFactory.shown++
    }
}

class BulletinFactory {
    companion object {
        var shown = 0
        var lastText: CharSequence? = null
        var ofCalls = 0
        var globalCalls = 0

        @JvmStatic
        fun of(fragment: ChatActivity): BulletinFactory {
            ofCalls++
            return BulletinFactory()
        }

        @JvmStatic
        fun global(): BulletinFactory {
            globalCalls++
            return BulletinFactory()
        }
    }

    fun createSimpleBulletin(icon: Int, text: CharSequence): Bulletin {
        lastText = text
        return Bulletin()
    }
}
''',
    'StubTeleHelpers.kt': r'''package tele.helpers

import org.telegram.messenger.MediaController
import org.telegram.ui.ChatActivity

object DockedMedia {
    class Append(
        val fragment: ChatActivity,
        val entries: List<MediaController.PhotoEntry>,
        val files: List<String>,
        val names: List<String>?,
        val asFile: Boolean,
        val caption: CharSequence?
    )

    var enabledFlag = true
    var appendResult = true
    val attempts = ArrayList<Append>()
    val applied = ArrayList<Append>()

    fun enabled(): Boolean = enabledFlag

    fun appendEntries(
        fragment: ChatActivity,
        entries: List<MediaController.PhotoEntry>,
        asFile: Boolean,
        caption: CharSequence?
    ): Boolean = appendShared(fragment, entries, emptyList(), null, asFile, caption)

    fun appendShared(
        fragment: ChatActivity,
        entries: List<MediaController.PhotoEntry>,
        files: List<String>,
        names: List<String>?,
        asFile: Boolean,
        caption: CharSequence?
    ): Boolean {
        val call = Append(fragment, ArrayList(entries), ArrayList(files), names?.let { ArrayList(it) }, asFile, caption)
        attempts.add(call)
        if (!appendResult) return false
        applied.add(call)
        if (caption != null && caption.isNotEmpty()) {
            fragment.chatActivityEnterView?.setFieldText(caption)
        }
        return true
    }

    fun reset() {
        enabledFlag = true
        appendResult = true
        attempts.clear()
        applied.clear()
    }
}

object TeleAccounts {
    private val generations = HashMap<Int, Long>()
    private val valid = HashMap<Int, Boolean>()

    fun generation(account: Int): Long = generations[account] ?: 0L

    fun isCurrent(account: Int, generation: Long): Boolean =
        (generations[account] ?: 0L) == generation && (valid[account] ?: true)

    fun revoke(account: Int) {
        generations[account] = generation(account) + 1
    }

    fun setValid(account: Int, value: Boolean) {
        valid[account] = value
    }

    fun reset() {
        generations.clear()
        valid.clear()
    }
}

object TeleToast {
    val logs = ArrayList<Pair<String, CharSequence?>>()

    fun log(site: String, text: CharSequence?, title: String = "", account: Int = 0) {
        logs.add(site to text)
    }

    fun reset() {
        logs.clear()
    }
}

object TeleLowercase {
    fun lc(text: String): String = text
}
''',
    'Test.kt': r'''package regression

import android.graphics.BitmapFactory
import android.media.MediaMetadataRetriever
import android.net.Uri
import org.telegram.messenger.AndroidUtilities
import org.telegram.messenger.ApplicationLoader
import org.telegram.messenger.MediaController
import org.telegram.messenger.SendMessagesHelper
import org.telegram.messenger.Utilities
import org.telegram.ui.ChatActivity
import org.telegram.ui.ChatActivityEnterView
import org.telegram.ui.Components.BulletinFactory
import tele.helpers.DockedIngress
import tele.helpers.DockedMedia
import tele.helpers.TeleAccounts
import tele.helpers.TeleToast
import java.io.File
import java.nio.file.Files

private const val ACCOUNT = 3

private lateinit var work: File
private lateinit var cache: File

private fun reset() {
    DockedMedia.reset()
    TeleAccounts.reset()
    TeleToast.reset()
    BulletinFactory.shown = 0
    BulletinFactory.ofCalls = 0
    BulletinFactory.globalCalls = 0
    BulletinFactory.lastText = null
    Utilities.globalQueue.clear()
    AndroidUtilities.uiQueue.clear()
    AndroidUtilities.internalPaths.clear()
    AndroidUtilities.orientations.clear()
    ApplicationLoader.applicationContext.contentResolver.types.clear()
    BitmapFactory.bounds.clear()
    MediaMetadataRetriever.metadata.clear()
    MediaController.failingPaths.clear()
    MediaController.copies.clear()
    MediaController.extensionsSeen.clear()
    MediaController.copyCounter = 0
    work.deleteRecursively()
    work.mkdirs()
    cache.deleteRecursively()
    cache.mkdirs()
    MediaController.cacheDir = cache
}

private fun source(name: String, text: String = name): String {
    val file = File(work, name)
    file.parentFile?.mkdirs()
    file.writeText(text)
    return file.absolutePath
}

private fun fragment(
    account: Int = ACCOUNT,
    dialogId: Long = -100L,
    threadId: Long = 7L,
    mode: Int = ChatActivity.MODE_DEFAULT,
    text: String = ""
): ChatActivity {
    val fragment = ChatActivity()
    fragment.currentAccount = account
    fragment.dialogId = dialogId
    fragment.threadId = threadId
    fragment.chatMode = mode
    fragment.chatActivityEnterView = ChatActivityEnterView().apply { setFieldText(text) }
    return fragment
}

private fun mediaInfo(
    path: String? = null,
    uri: Uri? = null,
    video: Boolean = false,
    caption: String? = null
): SendMessagesHelper.SendingMediaInfo = SendMessagesHelper.SendingMediaInfo().apply {
    this.path = path
    this.uri = uri
    isVideo = video
    this.caption = caption
}

private fun photoEntry(
    path: String,
    video: Boolean = false,
    width: Int = 0,
    height: Int = 0,
    size: Long = 0L
): MediaController.PhotoEntry =
    MediaController.PhotoEntry(0, -1, 0, path, 0, video, width, height, size)

private fun field(fragment: ChatActivity): String =
    fragment.chatActivityEnterView?.getFieldText()?.toString().orEmpty()

private fun settle() {
    repeat(4) {
        Utilities.globalQueue.runAll()
        AndroidUtilities.uiQueue.runAll()
    }
}

private fun assertIdle(fragment: ChatActivity, text: String) {
    check(DockedMedia.attempts.isEmpty()) { "ingress attempted to dock input that belongs to the native path" }
    check(DockedMedia.applied.isEmpty()) { "ingress changed the tray on the native path" }
    check(Utilities.globalQueue.pending() == 0) { "ingress queued background work" }
    check(AndroidUtilities.uiQueue.pending() == 0) { "ingress queued UI work" }
    check(TeleToast.logs.isEmpty()) { "ingress reported an error on the native path" }
    check(field(fragment) == text) { "ingress touched the message field" }
}

private fun unsupportedFallback() {
    reset()
    var path = source("fallback.jpg")
    var f = fragment(text = "keep")
    DockedMedia.enabledFlag = false
    check(!DockedIngress.dockPaste(f, photoEntry(path)))
    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, "caption", false, true, 0))
    check(!DockedIngress.dockInputContent(f, Uri(path), "image/jpeg"))
    assertIdle(f, "keep")

    reset()
    path = source("fallback.jpg")
    f = fragment(text = "keep")
    f.chatActivityEnterView!!.isEditingMessage = true
    check(!DockedIngress.dockPaste(f, photoEntry(path)))
    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, true, 0))
    check(!DockedIngress.dockInputContent(f, Uri(path), "image/jpeg"))
    assertIdle(f, "keep")

    reset()
    path = source("fallback.jpg")
    f = fragment(text = "keep")
    f.secret = true
    check(!DockedIngress.dockPaste(f, photoEntry(path)))
    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, true, 0))
    check(!DockedIngress.dockInputContent(f, Uri(path), "image/jpeg"))
    assertIdle(f, "keep")

    reset()
    path = source("fallback.jpg")
    f = fragment(mode = ChatActivity.MODE_SAVED, text = "keep")
    check(!DockedIngress.dockPaste(f, photoEntry(path)))
    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, true, 0))
    check(!DockedIngress.dockInputContent(f, Uri(path), "image/jpeg"))
    assertIdle(f, "keep")

    reset()
    path = source("fallback.jpg")
    f = fragment(text = "keep")
    f.chatActivityEnterView = null
    check(!DockedIngress.dockPaste(f, photoEntry(path)))
    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, true, 0))
    check(!DockedIngress.dockInputContent(f, Uri(path), "image/jpeg"))
    assertIdle(f, "")

    reset()
    f = fragment()
    check(!DockedIngress.dockPaste(f, photoEntry(File(work, "missing.jpg").absolutePath)))
    check(DockedMedia.attempts.isEmpty())
    check(Utilities.globalQueue.pending() == 0)

    reset()
    path = source("internal.jpg")
    AndroidUtilities.internalPaths.add(path)
    f = fragment()
    check(!DockedIngress.dockPaste(f, photoEntry(path)))
    check(DockedMedia.attempts.isEmpty())
    check(Utilities.globalQueue.pending() == 0)
}

private fun externalNative() {
    reset()
    val path = source("native.jpg")
    val f = fragment(text = "keep")

    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, false, 0))
    assertIdle(f, "keep")
    check(!DockedIngress.dockShared(f, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, true, 4242))
    assertIdle(f, "keep")
    check(!DockedIngress.dockSendingMedia(f, arrayListOf(mediaInfo(path = path)), false, false, 0))
    assertIdle(f, "keep")
    check(!DockedIngress.dockSendingMedia(f, arrayListOf(mediaInfo(path = path)), false, true, 99))
    assertIdle(f, "keep")

    val quick = fragment(mode = ChatActivity.MODE_QUICK_REPLIES, text = "keep")
    check(!DockedIngress.dockShared(quick, arrayListOf(mediaInfo(path = path)), null, null, null, null, false, true, 0))
    assertIdle(quick, "keep")

    check(DockedIngress.dockSendingMedia(f, arrayListOf(mediaInfo(path = path)), false, true, 0))
    check(DockedMedia.attempts.isEmpty())
    settle()
    check(DockedMedia.applied.size == 1)
    check(DockedMedia.applied.single().entries.single().path == path)
}

private fun sharedMediaDocsAtomic() {
    reset()
    val photo = source("photo.jpg", "photo-bytes")
    val video = source("clip.mp4", "video-bytes")
    val document = source("notes.txt", "notes-bytes")
    val shared = source("shared.bin", "shared-bytes")
    val f = fragment(text = "hello")
    ApplicationLoader.applicationContext.contentResolver.types[shared] = "application/octet-stream"

    val media = arrayListOf(mediaInfo(path = photo), mediaInfo(path = video, video = true))
    check(DockedIngress.dockShared(
        f, media, null, arrayListOf(document), arrayListOf(Uri(shared)), "caption", false, true, 0
    )) { "shared ingress refused supported media" }
    check(Utilities.globalQueue.pending() == 1) { "shared ingress did not stage on the global queue" }
    check(DockedMedia.attempts.isEmpty()) { "shared ingress docked before staging ran" }
    check(MediaController.copies.isEmpty()) { "shared ingress copied on the caller thread" }
    check(field(f) == "hello")

    Utilities.globalQueue.runAll()
    check(DockedMedia.attempts.isEmpty()) { "shared ingress docked before the UI continuation" }
    check(AndroidUtilities.uiQueue.pending() == 1)
    check(MediaController.copies.size == 1) { "the shared document URI was not copied" }
    val copied = MediaController.copies.single().destination
    check(File(copied).readText() == "shared-bytes")

    AndroidUtilities.uiQueue.runAll()
    check(DockedMedia.attempts.size == 1) { "shared ingress committed more than one tray update" }
    check(DockedMedia.applied.size == 1) { "shared ingress did not commit the tray update" }
    val call = DockedMedia.applied.single()
    check(call.fragment === f)
    check(call.entries.size == 2 && call.files.size == 2)
    check(call.entries[0].path == photo && !call.entries[0].isVideo)
    check(call.entries[1].path == video && call.entries[1].isVideo)
    check(call.files[0] == File(document).absolutePath)
    check(call.files[1] == copied)
    check(call.names == listOf("notes.txt", File(copied).name))
    check(!call.asFile)
    check(call.caption == "caption")
    check(field(f) == "caption")
    check(File(document).readText() == "notes-bytes")
    check(File(copied).isFile && File(copied).readText() == "shared-bytes")

    reset()
    val mediaOnly = source("forced.jpg", "forced-bytes")
    val g = fragment()
    check(DockedIngress.dockShared(
        g, arrayListOf(mediaInfo(path = mediaOnly)), null, null, null, null, true, true, 0
    ))
    settle()
    check(DockedMedia.applied.single().asFile) { "force-document was not forwarded" }
    check(DockedMedia.applied.single().entries.single().path == mediaOnly)
}

private fun pendingFieldEdits() {
    reset()
    val photo = source("edit.jpg", "edit-bytes")
    val f = fragment(text = "draft")
    check(DockedIngress.dockShared(
        f, arrayListOf(mediaInfo(path = photo)), null, null, null, "shared caption", false, true, 0
    ))
    check(Utilities.globalQueue.pending() == 1)
    Utilities.globalQueue.runAll()
    check(DockedMedia.attempts.isEmpty())
    f.chatActivityEnterView!!.setFieldText("edited while pending")
    AndroidUtilities.uiQueue.runAll()
    check(DockedMedia.applied.single().caption == null) { "a pending field edit was overwritten by the share caption" }
    check(field(f) == "edited while pending")

    reset()
    val same = source("same.jpg", "same-bytes")
    val g = fragment(text = "draft")
    check(DockedIngress.dockShared(
        g, arrayListOf(mediaInfo(path = same)), null, null, null, "shared caption", false, true, 0
    ))
    Utilities.globalQueue.runAll()
    check(field(g) == "draft")
    AndroidUtilities.uiQueue.runAll()
    check(DockedMedia.applied.single().caption == "shared caption")
    check(field(g) == "shared caption")

    reset()
    val captioned = source("captioned.jpg", "captioned-bytes")
    val h = fragment()
    check(DockedIngress.dockShared(
        h, arrayListOf(mediaInfo(path = captioned, caption = "from media")), null, null, null, null, false, true, 0
    ))
    settle()
    check(DockedMedia.applied.single().caption == "from media")
}

private fun stagingFailures() {
    reset()
    val empty = fragment(text = "keep")
    check(!DockedIngress.dockShared(empty, arrayListOf(mediaInfo()), null, null, null, null, false, true, 0))
    assertIdle(empty, "keep")

    reset()
    val f = fragment(text = "keep")
    check(DockedIngress.dockShared(
        f, null, null, null, arrayListOf(Uri("/system/internal.bin", true)), "caption", false, true, 0
    ))
    check(Utilities.globalQueue.pending() == 1)
    settle()
    check(DockedMedia.attempts.isEmpty()) { "an internal URI reached the tray" }
    check(MediaController.copies.isEmpty())
    check(field(f) == "keep")
    check(TeleToast.logs.single().first == "docked-ingress-copy")
    check(BulletinFactory.shown == 1)

    reset()
    val first = source("first.bin", "first-bytes")
    val second = source("second.bin", "second-bytes")
    MediaController.failingPaths.add(second)
    val partialFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        partialFragment, null, null, null, arrayListOf(Uri(first), Uri(second)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    val partial = MediaController.copies.single().destination
    check(!File(partial).exists()) { "a partially staged copy survived the failed batch" }
    AndroidUtilities.uiQueue.runAll()
    check(DockedMedia.attempts.isEmpty())
    check(field(partialFragment) == "keep")
    check(TeleToast.logs.single().first == "docked-ingress-copy")

    reset()
    val missing = source("gone.bin", "gone-bytes")
    File(missing).delete()
    val missingFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        missingFragment, null, null, null, arrayListOf(Uri(missing)), null, false, true, 0
    ))
    settle()
    check(DockedMedia.attempts.isEmpty())
    check(MediaController.copies.isEmpty())
    check(field(missingFragment) == "keep")
    check(TeleToast.logs.single().first == "docked-ingress-copy")

    reset()
    val attach = source("attach.jpg", "attach-bytes")
    val attachDoc = source("attach-doc.bin", "attach-doc-bytes")
    DockedMedia.appendResult = false
    val attachFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        attachFragment, arrayListOf(mediaInfo(path = attach)), null, null,
        arrayListOf(Uri(attachDoc)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    val copied = MediaController.copies.single().destination
    check(File(copied).isFile)
    AndroidUtilities.uiQueue.runAll()
    check(DockedMedia.attempts.size == 1)
    check(DockedMedia.applied.isEmpty())
    check(!File(copied).exists()) { "a copied file survived an attach failure" }
    check(File(attach).isFile)
    check(field(attachFragment) == "keep")
    check(TeleToast.logs.single().first == "docked-ingress-attach")

    reset()
    val input = source("input.bin", "input-bytes")
    MediaController.failingPaths.add(input)
    val inputFragment = fragment(text = "keep")
    check(DockedIngress.dockInputContent(inputFragment, Uri(input), "application/octet-stream"))
    settle()
    check(DockedMedia.attempts.isEmpty())
    check(field(inputFragment) == "keep")
    check(TeleToast.logs.single().first == "docked-ingress-copy")
}

private fun mismatchDiscards() {
    reset()
    val first = source("one.bin", "one-bytes")
    val second = source("two.bin", "two-bytes")
    val f = fragment(text = "keep")
    check(DockedIngress.dockShared(
        f, null, null, null, arrayListOf(Uri(first), Uri(second)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    check(MediaController.copies.size == 2)
    val copied = MediaController.copies.map { it.destination }
    copied.forEach { check(File(it).isFile) { "staging did not copy a shared file" } }
    TeleAccounts.revoke(ACCOUNT)
    AndroidUtilities.uiQueue.runAll()
    copied.forEach { check(!File(it).exists()) { "a stale generation kept a copied file" } }
    check(DockedMedia.attempts.isEmpty())
    check(TeleToast.logs.isEmpty())
    check(File(first).isFile && File(second).isFile)
    check(field(f) == "keep")

    reset()
    val dialogFile = source("dialog.bin", "dialog-bytes")
    val dialogFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        dialogFragment, null, null, null, arrayListOf(Uri(dialogFile)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    val dialogCopy = MediaController.copies.single().destination
    dialogFragment.dialogId = -555L
    AndroidUtilities.uiQueue.runAll()
    check(!File(dialogCopy).exists()) { "a copy survived a changed dialog" }
    check(DockedMedia.attempts.isEmpty())
    check(TeleToast.logs.isEmpty())

    reset()
    val accountFile = source("account.bin", "account-bytes")
    val accountFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        accountFragment, null, null, null, arrayListOf(Uri(accountFile)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    val accountCopy = MediaController.copies.single().destination
    accountFragment.currentAccount = ACCOUNT + 1
    AndroidUtilities.uiQueue.runAll()
    check(!File(accountCopy).exists()) { "a copy survived a changed account" }
    check(DockedMedia.attempts.isEmpty())
    check(TeleToast.logs.isEmpty())

    reset()
    val modeFile = source("mode.bin", "mode-bytes")
    val modeFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        modeFragment, null, null, null, arrayListOf(Uri(modeFile)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    val modeCopy = MediaController.copies.single().destination
    modeFragment.chatMode = ChatActivity.MODE_SCHEDULED
    AndroidUtilities.uiQueue.runAll()
    check(!File(modeCopy).exists()) { "a copy survived a changed chat mode" }
    check(DockedMedia.attempts.isEmpty())
    check(TeleToast.logs.isEmpty())

    reset()
    val parentFile = source("parent.bin", "parent-bytes")
    val parentFragment = fragment(text = "keep")
    check(DockedIngress.dockShared(
        parentFragment, null, null, null, arrayListOf(Uri(parentFile)), null, false, true, 0
    ))
    Utilities.globalQueue.runAll()
    val parentCopy = MediaController.copies.single().destination
    parentFragment.parentActivity = null
    AndroidUtilities.uiQueue.runAll()
    check(!File(parentCopy).exists()) { "a copy survived a detached fragment" }
    check(DockedMedia.attempts.isEmpty())
    check(TeleToast.logs.isEmpty())

    reset()
    val gif = source("stale.gif", "stale-gif")
    val inputFragment = fragment(text = "keep")
    check(DockedIngress.dockInputContent(inputFragment, Uri(gif), "image/gif"))
    Utilities.globalQueue.runAll()
    val gifCopy = MediaController.copies.single().destination
    check(File(gifCopy).isFile)
    TeleAccounts.revoke(ACCOUNT)
    AndroidUtilities.uiQueue.runAll()
    check(!File(gifCopy).exists()) { "a copied input file survived a stale generation" }
    check(DockedMedia.attempts.isEmpty())
    check(TeleToast.logs.isEmpty())
    check(File(gif).isFile)
}

private fun pasteModes() {
    for (mode in listOf(ChatActivity.MODE_DEFAULT, ChatActivity.MODE_SCHEDULED, ChatActivity.MODE_QUICK_REPLIES)) {
        reset()
        val path = source("paste.jpg", "paste-bytes")
        BitmapFactory.bounds[path] = 640 to 480
        val f = fragment(mode = mode, text = "keep")
        val entry = photoEntry(path)
        check(entry.width == 0 && entry.height == 0 && entry.size == 0L)
        check(DockedIngress.dockPaste(f, entry)) { "paste was refused in chat mode " + mode }
        check(Utilities.globalQueue.pending() == 0 && AndroidUtilities.uiQueue.pending() == 0)
        check(DockedMedia.applied.size == 1)
        val call = DockedMedia.applied.single()
        check(call.fragment === f)
        check(call.entries.single() === entry)
        check(call.files.isEmpty())
        check(!call.asFile)
        check(call.caption == null)
        check(entry.width == 640 && entry.height == 480)
        check(entry.size == File(path).length())
        check(field(f) == "keep")
    }

    reset()
    val filledPath = source("filled.jpg", "filled-bytes")
    BitmapFactory.bounds[filledPath] = 900 to 700
    val filled = photoEntry(filledPath, width = 12, height = 34, size = 7L)
    check(DockedIngress.dockPaste(fragment(), filled))
    check(filled.width == 12 && filled.height == 34 && filled.size == 7L)
}

private fun gifDocument() {
    reset()
    val gif = source("anim.gif", "gif-bytes")
    val f = fragment(text = "keep")
    check(DockedIngress.dockInputContent(f, Uri(gif), "image/gif"))
    check(Utilities.globalQueue.pending() == 1)
    check(DockedMedia.attempts.isEmpty())
    Utilities.globalQueue.runAll()
    val copied = MediaController.copies.single().destination
    check(MediaController.extensionsSeen.single() == "gif")
    check(copied.endsWith(".gif"))
    check(File(copied).readText() == "gif-bytes")
    AndroidUtilities.uiQueue.runAll()
    val call = DockedMedia.applied.single()
    check(call.entries.isEmpty()) { "GIF input was docked as an image" }
    check(call.files == listOf(copied))
    check(call.names == listOf(File(copied).name))
    check(!call.asFile)
    check(call.caption == null)
    check(field(f) == "keep")
    check(File(gif).readText() == "gif-bytes")

    reset()
    val resolvedGif = source("resolved.gif", "resolved-gif")
    ApplicationLoader.applicationContext.contentResolver.types[resolvedGif] = "image/gif"
    check(DockedIngress.dockInputContent(fragment(), Uri(resolvedGif), null))
    settle()
    check(DockedMedia.applied.single().entries.isEmpty())
    check(MediaController.extensionsSeen.single() == "gif")

    reset()
    val jpg = source("photo.jpg", "jpg-bytes")
    BitmapFactory.bounds[jpg] = 1024 to 768
    AndroidUtilities.orientations[jpg] = 180 to 1
    check(DockedIngress.dockInputContent(fragment(), Uri(jpg), "image/jpeg"))
    settle()
    val imageCall = DockedMedia.applied.single()
    check(imageCall.entries.size == 1 && imageCall.files.isEmpty())
    check(!imageCall.entries[0].isVideo)
    check(imageCall.entries[0].width == 1024 && imageCall.entries[0].height == 768)
    check(imageCall.entries[0].orientation == 180 && imageCall.entries[0].invert == 1)
    check(MediaController.extensionsSeen.single() == "jpg")

    reset()
    val mp4 = source("clip.mp4", "mp4-bytes")
    MediaMetadataRetriever.metadata[mp4] = mapOf(
        MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH to "1920",
        MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT to "1080",
        MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION to "90",
        MediaMetadataRetriever.METADATA_KEY_DURATION to "4500"
    )
    check(DockedIngress.dockInputContent(fragment(), Uri(mp4), "video/mp4"))
    settle()
    val videoCall = DockedMedia.applied.single()
    check(videoCall.entries.size == 1 && videoCall.files.isEmpty())
    check(videoCall.entries[0].isVideo)
    check(videoCall.entries[0].width == 1080 && videoCall.entries[0].height == 1920)
    check(videoCall.entries[0].duration == 4)
    check(MediaController.extensionsSeen.single() == "mp4")

    reset()
    val pdf = source("doc.pdf", "pdf-bytes")
    check(DockedIngress.dockInputContent(fragment(), Uri(pdf), "application/pdf"))
    settle()
    val pdfCall = DockedMedia.applied.single()
    check(pdfCall.entries.isEmpty() && pdfCall.files.size == 1)
    check(MediaController.extensionsSeen.single() == "file")

    reset()
    val idle = fragment(text = "keep")
    check(!DockedIngress.dockInputContent(idle, null, "image/gif"))
    check(!DockedIngress.dockInputContent(idle, Uri("/system/pasted.gif", true), "image/gif"))
    assertIdle(idle, "keep")
}

fun main() {
    work = Files.createTempDirectory("docked-ingress-").toFile()
    cache = Files.createTempDirectory("docked-ingress-cache-").toFile()
    try {
        unsupportedFallback()
        externalNative()
        sharedMediaDocsAtomic()
        pendingFieldEdits()
        stagingFailures()
        mismatchDiscards()
        pasteModes()
        gifDocument()
    } finally {
        work.deleteRecursively()
        cache.deleteRecursively()
    }
    println("PASS: DockedIngress fallbacks, staged commits, copy cleanup and document routing")
}
''',
}

kotlin_files = []
for name, text in stubs.items():
    path = here/name
    path.write_text(text, encoding='utf-8')
    kotlin_files.append(path)
kotlin_files.append(ingress_source)

classes = here/'test.jar'
subprocess.run(
    [args.java, '-cp', os.pathsep.join(map(str, compiler)),
     'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
     '-no-stdlib', '-no-reflect',
     '-classpath', str(stdlib),
     '-d', str(classes)] + [str(path) for path in kotlin_files],
    check=True
)
subprocess.run(
    [args.java, '-cp', os.pathsep.join([str(classes), str(stdlib)]), 'regression.TestKt'],
    check=True
)
print('PASS: DockedIngress harness completed without assertion failures')
