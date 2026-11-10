"""Compile the actual DockedMedia.send contract against deterministic stubs and
exercise it behaviourally.

DockedMedia.kt is far too entangled with ChatActivity/Telegram UI to compile as a
whole. The Key/Item/Tray declarations, enabled/keyOf/supported/ensureLoaded/tray/
changed/toInfo helpers and the send method itself are taken verbatim from the
actual source and compiled into a harness object (the same approach as
test_download_bounds.py takes for TeleServerNotices). Stock send helpers are
stubs with the real signatures that merely record what the send contract handed
them. No assertion inspects source text.

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
temporary = tempfile.TemporaryDirectory(prefix='tele-docked-send-') if args.output is None else None
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


# ------------------------------------------------------------ extract the contract

source_path = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/DockedMedia.kt'
if not source_path.is_file():
    raise SystemExit('Cannot find DockedMedia.kt under ' + str(root))
source = source_path.read_text(encoding='utf-8')


def block(signature):
    """Verbatim declaration from `signature` through its matching closing brace."""
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


def statement(signature):
    """Verbatim expression-bodied declaration, stopping at the next member."""
    start = source.index(signature)
    lines = source[start:].split('\n')
    out = [lines[0]]
    for line in lines[1:]:
        stripped = line.lstrip()
        if line.startswith('    ') and not line.startswith('        ') and (
                stripped.startswith(('@', 'fun ', 'private ', 'internal ', 'public ', 'val ', 'var ', 'const ', 'class ', 'object '))):
            break
        out.append(line)
    return '\n'.join(out).rstrip()


def constant(name):
    match = re.search(r'const val ' + name + r'\s*=\s*([0-9]+)', source)
    if match is None:
        raise SystemExit('Cannot find ' + name + ' in DockedMedia.kt')
    return match.group(1)


def key_decl():
    match = re.search(r'data class Key\([^\n]*\)', source)
    if match is None:
        raise SystemExit('Cannot find DockedMedia.Key')
    return match.group(0)


send_none = constant('SEND_NONE')
send_blocked = constant('SEND_BLOCKED')
send_done = constant('SEND_DONE')
key = key_decl()
item = block('class Item {')
tray = block('class Tray {')
enabled = statement('fun enabled()')
key_of = statement('internal fun keyOf')
supported = statement('private fun supported')
ensure_loaded = block('private fun ensureLoaded')
tray_fun = block('internal fun tray')
changed = block('private fun changed')
to_info = block('private fun toInfo')
send = block('fun send(')

# ---------------------------------------------------------------- harness sources

docked = (r'''package tele.helpers

import org.telegram.messenger.AccountInstance
import org.telegram.messenger.AndroidUtilities
import org.telegram.messenger.LocaleController
import org.telegram.messenger.MediaController
import org.telegram.messenger.MediaDataController
import org.telegram.messenger.MessagesController
import org.telegram.messenger.NotificationCenter
import org.telegram.messenger.R
import org.telegram.messenger.SendMessagesHelper
import org.telegram.messenger.VideoEditedInfo
import org.telegram.messenger.tele_asVideo
import org.telegram.tgnet.TLRPC
import org.telegram.ui.ChatActivity
import org.telegram.ui.Components.BulletinFactory
import org.telegram.ui.Components.ChatActivityEnterView
import tele.TeleConfig
import tele.ui.TeleDockedStrip
import java.io.File

object DockedSend {
    const val SEND_NONE = ''' + send_none + r'''
    const val SEND_BLOCKED = ''' + send_blocked + r'''
    const val SEND_DONE = ''' + send_done + r'''

    ''' + key + r'''

    ''' + item + r'''

    ''' + tray + r'''

    private val trays = HashMap<Key, Tray>()
    private val loaded = HashSet<Int>()
    private val strips = ArrayList<TeleDockedStrip>()

    ''' + enabled + r'''

    ''' + key_of + r'''

    ''' + supported + r'''

    ''' + ensure_loaded + r'''

    ''' + tray_fun + r'''

    ''' + changed + r'''

    internal fun seed(key: Key): Tray = trays.getOrPut(key) { Tray() }

    fun reset() {
        trays.clear()
        loaded.clear()
        strips.clear()
    }

    ''' + to_info + r'''

    ''' + send + r'''
}
''')

tele_stubs = r'''package org.telegram.messenger

import org.telegram.tgnet.TLRPC
import org.telegram.ui.ChatActivity

class AccountInstance {
    companion object {
        private val instance = AccountInstance()
        fun getInstance(account: Int): AccountInstance = instance
    }
}

object AndroidUtilities {
    fun getTrimmedString(text: CharSequence): String = text.toString().trim()
    fun replaceTags(text: CharSequence): CharSequence = text
}

object LocaleController {
    fun formatPluralString(key: String, value: Int): String = key + ":" + value
}

object MediaController {
    class PhotoEntry
}

class VideoEditedInfo {
    var tele_asVideo = false
}

// Java fields are platform types in the real class, so a null-checked field is
// usable without a safe call; this extension reproduces that for the harness.
var VideoEditedInfo?.tele_asVideo: Boolean
    get() = this?.tele_asVideo ?: false
    set(value) { this?.tele_asVideo = value }

class MessageObject

object R {
    object raw { const val error = 0 }
}

class NotificationCenter {
    companion object {
        const val dialogsNeedReload = 1
        fun getInstance(account: Int): NotificationCenter = NotificationCenter()
    }
    fun postNotificationName(name: Int) {}
}

class QuickReplyMessagesLimit {
    var value = 100
    fun get(): Int = value
}

class MessagesConfig {
    val quickReplyMessagesLimit = QuickReplyMessagesLimit()
}

class MessagesController {
    var captionMaxLengthLimit = 1024
    val config = MessagesConfig()
    companion object {
        private val instance = MessagesController()
        fun getInstance(account: Int): MessagesController = instance
    }
}

class MediaDataController {
    companion object {
        private val instance = MediaDataController()
        fun getInstance(account: Int): MediaDataController = instance
    }
    fun getEntities(message: Array<CharSequence>, allowStrike: Boolean): ArrayList<TLRPC.MessageEntity> {
        Sends.entityCalls++
        return arrayListOf(TLRPC.TL_messageEntityBold())
    }
    fun addRecentGif(document: TLRPC.Document?, date: Int, force: Boolean) {
        Sends.recentGifs++
    }
}

class MediaCall(
    val infos: ArrayList<SendMessagesHelper.SendingMediaInfo>,
    val dialogId: Long,
    val notify: Boolean,
    val scheduleDate: Int,
    val repeat: Int,
    val mode: Int,
    val forceDocument: Boolean,
    val groupMedia: Boolean,
    val updateStickersOrder: Boolean,
    val effectId: Long,
    val invertMedia: Boolean,
    val payStars: Long,
    val monoForumPeerId: Long,
    val args: Any?,
    val suggestion: Any?
)

class FileCall(
    val paths: List<String>,
    val caption: String?,
    val captionEntities: List<TLRPC.MessageEntity>?,
    val notify: Boolean,
    val scheduleDate: Int,
    val repeat: Int,
    val effectId: Long,
    val invertMedia: Boolean,
    val payStars: Long,
    val monoForumPeerId: Long,
    val suggestion: Any?
)

class BotCall(
    val result: TLRPC.BotInlineResult,
    val params: Map<String, String>,
    val notify: Boolean,
    val scheduleDate: Int,
    val repeat: Int,
    val payStars: Long,
    val monoForumPeerId: Long
)

class StickerCall(val params: SendMessagesHelper.SendMessageParams)

object Sends {
    val order = ArrayList<String>()
    val media = ArrayList<MediaCall>()
    val files = ArrayList<FileCall>()
    val bots = ArrayList<BotCall>()
    val stickers = ArrayList<StickerCall>()
    val bulletins = ArrayList<String>()
    var entityCalls = 0
    var recentGifs = 0
    fun reset() {
        order.clear()
        media.clear()
        files.clear()
        bots.clear()
        stickers.clear()
        bulletins.clear()
        entityCalls = 0
        recentGifs = 0
    }
}

class SendMessagesHelper {
    class SendingMediaInfo {
        var imagePath: String? = null
        var path: String? = null
        var caption: String? = null
        var thumbPath: String? = null
        var coverPath: String? = null
        var coverPhoto: TLRPC.Photo? = null
        var ttl = 0
        var entities: ArrayList<TLRPC.MessageEntity>? = null
        var masks: ArrayList<TLRPC.InputDocument>? = null
        var videoEditedInfo: VideoEditedInfo? = null
        var isVideo = false
        var canDeleteAfter = false
        var updateStickersOrder = false
        var hasMediaSpoilers = false
        var stars = 0L
        var highQuality = false
        var originalPhotoEntry: MediaController.PhotoEntry? = null
    }

    class SendMessageParams {
        var caption: String? = null
        var notify = false
        var scheduleDate = 0
        var repeat = 0
        var replyQuote: Any? = null
        var sendMessageChatArguments: Any? = null
        var payStars = 0L
        var monoForumPeer = 0L
        var suggestionParams: Any? = null
        var effect_id = 0L
        var updateStickersOrder = false

        companion object {
            fun of(
                document: TLRPC.TL_document,
                videoEditedInfo: VideoEditedInfo?,
                path: String?,
                peer: Long,
                replyToMsg: MessageObject?,
                replyToTopMsg: MessageObject?,
                caption: String?,
                entities: ArrayList<TLRPC.MessageEntity>?,
                replyMarkup: Any?,
                params: HashMap<String, String>?,
                notify: Boolean,
                scheduleDate: Int,
                repeat: Int,
                ttl: Int,
                parentObject: Any?,
                sendAnimationData: Any?,
                updateStickersOrder: Boolean
            ): SendMessageParams = SendMessageParams().apply {
                this.caption = caption
                this.notify = notify
                this.scheduleDate = scheduleDate
                this.repeat = repeat
                this.updateStickersOrder = updateStickersOrder
            }
        }
    }

    companion object {
        fun checkUpdateStickersOrder(text: CharSequence?): Boolean = text != null && text.isNotEmpty()

        private val instance = SendMessagesHelper()

        fun getInstance(account: Int): SendMessagesHelper = instance

        fun prepareSendingBotContextResult(
            fragment: ChatActivity,
            account: AccountInstance,
            result: TLRPC.BotInlineResult,
            params: HashMap<String, String>,
            dialogId: Long,
            replyToMsg: MessageObject?,
            replyToTopMsg: MessageObject?,
            storyItem: Any?,
            quote: ChatActivity.ReplyQuote?,
            notify: Boolean,
            scheduleDate: Int,
            repeat: Int,
            args: Any?,
            stars: Long,
            monoForumPeerId: Long
        ) {
            Sends.bots.add(BotCall(result, params, notify, scheduleDate, repeat, stars, monoForumPeerId))
            Sends.order.add("bot:" + (result.id ?: ""))
        }

        fun prepareSendingDocuments(
            account: AccountInstance,
            paths: ArrayList<String>,
            originalPaths: ArrayList<String>,
            uris: ArrayList<Any>?,
            caption: String?,
            captionEntities: ArrayList<TLRPC.MessageEntity>?,
            mime: String?,
            dialogId: Long,
            replyToMsg: MessageObject?,
            replyToTopMsg: MessageObject?,
            storyItem: Any?,
            quote: ChatActivity.ReplyQuote?,
            editing: MessageObject?,
            notify: Boolean,
            scheduleDate: Int,
            repeat: Int,
            inputContent: Any?,
            args: Any?,
            effectId: Long,
            invertMedia: Boolean,
            payStars: Long,
            monoForumPeerId: Long,
            suggestionParams: Any?
        ) {
            Sends.files.add(FileCall(paths, caption, captionEntities, notify, scheduleDate, repeat, effectId, invertMedia, payStars, monoForumPeerId, suggestionParams))
            Sends.order.add("files:" + paths.joinToString("+"))
        }

        fun prepareSendingMedia(
            account: AccountInstance,
            media: ArrayList<SendingMediaInfo>,
            dialogId: Long,
            replyToMsg: MessageObject?,
            replyToTopMsg: MessageObject?,
            storyItem: Any?,
            quote: ChatActivity.ReplyQuote?,
            forceDocument: Boolean,
            groupMedia: Boolean,
            editing: MessageObject?,
            notify: Boolean,
            scheduleDate: Int,
            repeat: Int,
            mode: Int,
            updateStickersOrder: Boolean,
            inputContent: Any?,
            args: Any?,
            effectId: Long,
            invertMedia: Boolean,
            payStars: Long,
            monoForumPeerId: Long,
            suggestionParams: Any?
        ) {
            Sends.media.add(MediaCall(media, dialogId, notify, scheduleDate, repeat, mode, forceDocument, groupMedia, updateStickersOrder, effectId, invertMedia, payStars, monoForumPeerId, args, suggestionParams))
            Sends.order.add("media:" + media.joinToString("+") { it.path ?: "" })
        }
    }

    fun sendMessage(params: SendMessageParams) {
        Sends.stickers.add(StickerCall(params))
        Sends.order.add("sticker")
    }
}
'''

tgnet_stubs = r'''package org.telegram.tgnet

object TLRPC {
    open class MessageEntity
    class TL_messageEntityBold : MessageEntity()

    open class InputDocument
    open class Document
    class TL_document : Document()

    open class Photo
    class TL_photo : Photo()

    class TL_draftMessage

    open class BotInlineMessage
    class TL_botInlineMessageMediaAuto : BotInlineMessage() {
        var message: String? = null
        var entities: ArrayList<MessageEntity>? = null
        var flags = 0
    }

    open class BotInlineResult {
        var id: String? = null
        var query_id = 0L
        var type: String? = null
        var send_message: BotInlineMessage? = null
        var document: Document? = null
        var photo: Photo? = null
        var content: Any? = null

        companion object {
            fun TLdeserialize(stream: Any?, constructor: Int, exception: Boolean): BotInlineResult? = null
        }
    }
}

object TLObject {
    fun <T> deepCopy(value: T, deserializer: (Any?, Int, Boolean) -> T?): T? = null
}
'''

chat_stubs = r'''package org.telegram.ui

import org.telegram.messenger.MessageObject
import org.telegram.messenger.MessagesController

class ChatActivity {
    companion object {
        const val MODE_DEFAULT = 0
        const val MODE_SCHEDULED = 1
        const val MODE_QUICK_REPLIES = 2
    }

    var currentAccount = 0
    var dialogId = 0L
    var threadId = 0L
    var chatMode = MODE_DEFAULT
    var quickReplyShortcut: String? = null
    var replyMessage: MessageObject? = null
    var threadMessage: MessageObject? = null
    var replyQuote: ReplyQuote? = null
    var messageChatSendParams: Any? = null
    var chatActivityEnterView: Any? = null
    var messagesController = MessagesController()
    val messages = ArrayList<MessageObject>()
    var allowSlowMode = true
    var slowModeChecks = 0

    fun checkSlowModeAlert(): Boolean {
        slowModeChecks++
        return allowSlowMode
    }

    class ReplyQuote
}
'''

view_stubs = r'''package org.telegram.ui.Components

import org.telegram.messenger.Sends
import org.telegram.ui.ChatActivity

class ChatActivityEnterView {
    companion object {
        var premiumAnimated = false
        var premiumChecks = 0
        fun checkPremiumAnimatedEmoji(
            account: Int,
            dialogId: Long,
            fragment: ChatActivity?,
            parent: Any?,
            message: CharSequence
        ): Boolean {
            premiumChecks++
            return premiumAnimated
        }
    }

    var editing = false
    val isEditingMessage: Boolean
        get() = editing

    var effectId = 0L
    var sendMonoForumPeerId = 0L
    var sendMessageSuggestionParams: Any? = null
}

class BulletinFactory {
    companion object {
        fun of(fragment: ChatActivity): BulletinFactory = BulletinFactory()
    }

    fun createSimpleBulletin(icon: Int, text: CharSequence): Bulletin {
        Sends.bulletins.add(text.toString())
        return Bulletin()
    }

    class Bulletin {
        fun show() {}
    }
}
'''

tele_config_stubs = r'''package tele

object TeleConfig {
    object DOCKED_MEDIA { var value = true }
    object DOCKED_GRID { var value = true }
}
'''

dock_stubs = r'''package tele.helpers

object DockedStore {
    fun load(account: Int): Map<DockedSend.Key, DockedSend.Tray> = emptyMap()
    fun save(key: DockedSend.Key, tray: DockedSend.Tray?) {}
}

object TeleLowercase {
    fun lc(text: String): String = text
}

object TeleToast {
    val logs = ArrayList<Pair<String, String>>()
    fun log(tag: String, text: String, account: Int = 0) {
        logs.add(tag to text)
    }
}
'''

strip_stubs = r'''package tele.ui

class TeleDockedStrip {
    var key: Any? = null
    fun sync(force: Boolean) {}
}
'''

main = r'''package regression

import org.telegram.messenger.MessageObject
import org.telegram.messenger.Sends
import org.telegram.tgnet.TLRPC
import org.telegram.ui.ChatActivity
import org.telegram.ui.Components.ChatActivityEnterView
import tele.TeleConfig
import tele.helpers.DockedSend
import tele.helpers.TeleToast
import java.io.File
import java.nio.file.Files

private val rootDir = Files.createTempDirectory("tele-docked-send-").toFile()
private var fileCounter = 0

private fun file(): String {
    val file = File(rootDir, "f" + fileCounter++ + ".jpg")
    file.writeText("x")
    return file.absolutePath
}

private fun gone(): String = File(rootDir, "missing" + fileCounter++ + ".jpg").absolutePath

private fun chat(mode: Int = ChatActivity.MODE_DEFAULT): ChatActivity = ChatActivity().apply {
    currentAccount = 1
    dialogId = -100123L
    threadId = 7L
    chatMode = mode
    messageChatSendParams = "args"
}

private fun enter(): ChatActivityEnterView = ChatActivityEnterView().apply {
    effectId = 9L
    sendMonoForumPeerId = 11L
    sendMessageSuggestionParams = "suggestion"
}

private fun keyOf(fragment: ChatActivity): DockedSend.Key = DockedSend.keyOf(fragment)

private fun seed(key: DockedSend.Key, vararg items: DockedSend.Item): DockedSend.Tray {
    val tray = DockedSend.seed(key)
    tray.items.addAll(items)
    return tray
}

private fun media(path: String, doc: Boolean = false, ttl: Int = 0): DockedSend.Item = DockedSend.Item().apply {
    this.path = path
    this.imagePath = path
    this.width = 640
    this.height = 480
    this.size = 1234L
    this.asFile = doc
    this.ttl = ttl
}

private fun fileItem(path: String): DockedSend.Item = DockedSend.Item().apply {
    this.path = path
    this.isFile = true
    this.fileName = path.substringAfterLast('/')
}

private fun stickerDocument(): DockedSend.Item = DockedSend.Item().apply {
    this.document = TLRPC.TL_document()
}

private fun inlineSticker(): DockedSend.Item = DockedSend.Item().apply {
    val result = TLRPC.BotInlineResult()
    result.id = "gif1"
    result.query_id = 3L
    result.type = "gif"
    result.document = TLRPC.TL_document()
    result.send_message = TLRPC.TL_botInlineMessageMediaAuto()
    this.inlineResult = result
}

private fun reset() {
    Sends.reset()
    TeleToast.logs.clear()
    TeleConfig.DOCKED_MEDIA.value = true
    ChatActivityEnterView.premiumAnimated = false
    ChatActivityEnterView.premiumChecks = 0
    DockedSend.reset()
}

fun main() {
    // mixed media / document / sticker order; the caption goes once to the first attachment
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val a = media(file()).apply { spoiler = true; stars = 4L; highQuality = true }
        val document = fileItem(file())
        val b = media(file())
        val sticker = stickerDocument()
        val c = media(file())
        val tray = seed(key, a, document, b, sticker, c)
        tray.invert = true

        check(DockedSend.send(fragment, view, " hello ", true, 0, 4, 55L) == DockedSend.SEND_DONE)
        check(Sends.order == listOf(
            "media:" + a.path,
            "files:" + document.path,
            "media:" + b.path,
            "sticker",
            "media:" + c.path
        ))
        check(Sends.media.size == 3)
        val firstMedia = Sends.media[0]
        check(firstMedia.infos.size == 1)
        check(firstMedia.infos[0].path == a.path && firstMedia.infos[0].imagePath == a.path)
        check(firstMedia.infos[0].caption == "hello")
        check(firstMedia.infos[0].entities?.size == 1)
        check(firstMedia.infos[0].hasMediaSpoilers)
        check(firstMedia.infos[0].stars == 4L)
        check(firstMedia.infos[0].highQuality)
        check(firstMedia.notify && firstMedia.repeat == 4 && firstMedia.payStars == 55L && firstMedia.monoForumPeerId == 11L)
        check(firstMedia.suggestion == "suggestion")
        check(firstMedia.effectId == 9L)
        check(firstMedia.invertMedia)
        check(firstMedia.updateStickersOrder)
        check(firstMedia.mode == ChatActivity.MODE_DEFAULT)
        check(firstMedia.dialogId == fragment.dialogId)
        check(Sends.media[1].infos[0].caption == null)
        check(Sends.media[1].effectId == 0L)
        check(Sends.files.size == 1)
        check(Sends.files[0].caption == null)
        check(Sends.files[0].notify && Sends.files[0].repeat == 4 && Sends.files[0].payStars == 55L)
        check(Sends.files[0].effectId == 0L)
        check(Sends.files[0].invertMedia)
        check(Sends.stickers.size == 1)
        check(Sends.stickers[0].params.caption == null)
        check(Sends.stickers[0].params.notify)
        check(Sends.stickers[0].params.repeat == 4)
        check(Sends.stickers[0].params.payStars == 55L)
        check(Sends.stickers[0].params.monoForumPeer == 11L)
        check(Sends.stickers[0].params.suggestionParams == "suggestion")
        check(Sends.stickers[0].params.effect_id == 0L)
        check(DockedSend.tray(key) == null)
    }

    // an inline sticker first owns the caption and the bot result carries it
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val inline = inlineSticker()
        val picture = media(file())
        seed(key, inline, picture)

        check(DockedSend.send(fragment, view, "cap", false, 0, 2, 3L) == DockedSend.SEND_DONE)
        check(Sends.order == listOf("bot:gif1", "media:" + picture.path))
        check(Sends.bots.size == 1)
        val bot = Sends.bots[0]
        val auto = bot.result.send_message as TLRPC.TL_botInlineMessageMediaAuto
        check(auto.message == "cap")
        check(auto.entities?.size == 1)
        check((auto.flags and 1) == 1)
        check(!bot.notify && bot.repeat == 2 && bot.payStars == 3L && bot.monoForumPeerId == 11L)
        check(bot.params["id"] == "gif1")
        check(bot.params["query_id"] == "3")
        check(bot.params["force_gif"] == "1")
        check(Sends.recentGifs == 1)
        check(Sends.media[0].infos[0].caption == null)
        check(Sends.entityCalls == 1)
    }

    // quick replies carry their own key, schedule/repeat/stars travel intact, slow mode is skipped
    reset()
    run {
        val fragment = chat(ChatActivity.MODE_QUICK_REPLIES)
        fragment.quickReplyShortcut = "hello"
        fragment.threadId = 44L
        val view = enter()
        val key = keyOf(fragment)
        check(key.threadId == 0L && key.shortcut == "hello")
        seed(key, media(file()), fileItem(file()))

        check(DockedSend.send(fragment, view, "", true, 777, 5, 12L) == DockedSend.SEND_DONE)
        check(fragment.slowModeChecks == 0)
        check(Sends.media.size == 1 && Sends.files.size == 1)
        check(Sends.media[0].mode == ChatActivity.MODE_QUICK_REPLIES)
        check(Sends.media[0].scheduleDate == 777 && Sends.media[0].repeat == 5 && Sends.media[0].payStars == 12L)
        check(Sends.files[0].scheduleDate == 777 && Sends.files[0].repeat == 5 && Sends.files[0].payStars == 12L)
    }

    // quick replies stop at the account limit: exactly at it sends, one over keeps the tray and dispatches nothing
    reset()
    run {
        val fragment = chat(ChatActivity.MODE_QUICK_REPLIES)
        val view = enter()
        val key = keyOf(fragment)
        fragment.messagesController.config.quickReplyMessagesLimit.value = 3
        fragment.messages.add(MessageObject())
        seed(key, media(file()), fileItem(file()))

        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_DONE)
        check(Sends.order.isNotEmpty())
        check(DockedSend.tray(key) == null)
    }
    reset()
    run {
        val fragment = chat(ChatActivity.MODE_QUICK_REPLIES)
        val view = enter()
        val key = keyOf(fragment)
        fragment.messagesController.config.quickReplyMessagesLimit.value = 3
        fragment.messages.add(MessageObject())
        seed(key, media(file()), fileItem(file()), media(file()))

        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_BLOCKED)
        check(Sends.order.isEmpty())
        val tray = DockedSend.tray(key) ?: error("over-limit send dropped the tray")
        check(tray.items.size == 3)
        check(TeleToast.logs.any { it.first == "docked-send" && it.second.contains("BusinessRepliesToastLimit:3") })
        check(Sends.bulletins.any { it.contains("BusinessRepliesToastLimit:3") })
    }

    // a missing file fails preflight: nothing is sent and the tray is kept whole
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val missing = media(gone())
        val present = media(file())
        seed(key, present, missing)

        check(DockedSend.send(fragment, view, "cap", true, 0, 0, 0L) == DockedSend.SEND_BLOCKED)
        check(Sends.order.isEmpty())
        check(Sends.media.isEmpty() && Sends.files.isEmpty() && Sends.bots.isEmpty())
        val tray = DockedSend.tray(key) ?: error("blocked send dropped the tray")
        check(tray.items.size == 2)
        check(tray.items[1] === missing)
        check(TeleToast.logs.any { it.first == "docked-send" && it.second.contains("gone") })
        check(Sends.bulletins.any { it.contains("gone") })
    }

    // scheduling self-destructing media is refused before any send; without a schedule ttl is carried on
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file(), ttl = 5))

        check(DockedSend.send(fragment, view, "", true, 123, 0, 0L) == DockedSend.SEND_BLOCKED)
        check(Sends.order.isEmpty())
        check(TeleToast.logs.any { it.second.contains("self-destructing") })
        check(DockedSend.tray(key)?.items?.size == 1)
    }
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file(), ttl = 5))
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_DONE)
        check(Sends.media[0].infos[0].ttl == 5)
    }

    // more than ten media are split into ten-ten-three, order kept and the caption once
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val paths = (1..23).map { file() }
        seed(key, *paths.map { media(it) }.toTypedArray())

        check(DockedSend.send(fragment, view, "cap", true, 0, 0, 0L) == DockedSend.SEND_DONE)
        check(Sends.media.size == 3)
        check(Sends.media.map { it.infos.size } == listOf(10, 10, 3))
        check(Sends.media[0].infos[0].caption == "cap")
        check(Sends.media[1].infos[0].caption == null)
        check(Sends.media[2].infos[0].caption == null)
        val flat = ArrayList<String>()
        for (call in Sends.media) for (info in call.infos) flat.add(info.path!!)
        check(flat == paths)
        check(Sends.entityCalls == 1)
    }

    // documents group only when the tray asks for it
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val paths = listOf(file(), file(), file())
        seed(key, *paths.map { fileItem(it) }.toTypedArray())
        DockedSend.seed(key).group = false

        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_DONE)
        check(Sends.files.size == 3)
        check(Sends.files.all { it.paths.size == 1 })
        check(Sends.files.map { it.paths[0] } == paths)
    }
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val paths = listOf(file(), file(), file())
        seed(key, *paths.map { fileItem(it) }.toTypedArray())

        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_DONE)
        check(Sends.files.size == 1)
        check(Sends.files[0].paths == paths)
    }

    // as-file boundaries split media runs and forceDocument follows each run
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        val t1 = media(file(), doc = true)
        val t2 = media(file(), doc = true)
        val m1 = media(file(), doc = false)
        val m2 = media(file(), doc = false)
        val t3 = media(file(), doc = true)
        seed(key, t1, t2, m1, m2, t3)

        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_DONE)
        check(Sends.media.size == 3)
        check(Sends.media.map { it.infos.size } == listOf(2, 2, 1))
        check(Sends.media.map { it.forceDocument } == listOf(true, false, true))
        check(Sends.media[0].infos[0].path == t1.path && Sends.media[0].infos[1].path == t2.path)
        check(Sends.media[1].infos[0].path == m1.path && Sends.media[1].infos[1].path == m2.path)
        check(Sends.media[2].infos[0].path == t3.path)
    }

    // unsupported chat modes and a disabled dock leave the tray untouched
    reset()
    run {
        val fragment = chat(99)
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file()))
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_NONE)
        check(Sends.order.isEmpty())
        check(DockedSend.tray(key)?.items?.size == 1)
    }
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file()))
        TeleConfig.DOCKED_MEDIA.value = false
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_NONE)
        check(Sends.order.isEmpty())
        check(DockedSend.tray(key)?.items?.size == 1)
    }

    // editing, premium emoji, slow mode and an empty tray all block without sending
    reset()
    run {
        val fragment = chat()
        val view = enter().apply { editing = true }
        val key = keyOf(fragment)
        seed(key, media(file()))
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_NONE)
        check(Sends.order.isEmpty())
        check(DockedSend.tray(key)?.items?.size == 1)
    }
    reset()
    run {
        val fragment = chat()
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file()))
        ChatActivityEnterView.premiumAnimated = true
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_BLOCKED)
        check(ChatActivityEnterView.premiumChecks == 1)
        check(Sends.order.isEmpty())
        check(DockedSend.tray(key)?.items?.size == 1)
    }
    reset()
    run {
        val fragment = chat()
        fragment.allowSlowMode = false
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file()))
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_BLOCKED)
        check(fragment.slowModeChecks == 1)
        check(Sends.order.isEmpty())
        check(DockedSend.tray(key)?.items?.size == 1)
    }
    reset()
    run {
        val fragment = chat()
        val view = enter()
        check(DockedSend.send(fragment, view, "", true, 0, 0, 0L) == DockedSend.SEND_NONE)
        check(Sends.order.isEmpty())
    }

    // scheduled chats are supported and skip the slow-mode check
    reset()
    run {
        val fragment = chat(ChatActivity.MODE_SCHEDULED)
        val view = enter()
        val key = keyOf(fragment)
        seed(key, media(file()))
        check(DockedSend.send(fragment, view, "", true, 500, 0, 0L) == DockedSend.SEND_DONE)
        check(fragment.slowModeChecks == 0)
        check(Sends.media[0].mode == ChatActivity.MODE_SCHEDULED)
        check(Sends.media[0].scheduleDate == 500)
    }

    println("PASS: docked media send ordering, caption, arguments, preflight, chunks, as-file and modes")
}
'''

build('docked-send', {
    'DockedSend.kt': docked,
    'Telegram.kt': tele_stubs,
    'Tgnet.kt': tgnet_stubs,
    'Chat.kt': chat_stubs,
    'View.kt': view_stubs,
    'TeleConfig.kt': tele_config_stubs,
    'Dock.kt': dock_stubs,
    'Strip.kt': strip_stubs,
    'Main.kt': main,
}, None, 'regression.MainKt')

print('PASS: DockedMedia.send contract')
