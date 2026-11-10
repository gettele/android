"""Compile the actual LastSeenPeek helper against focused stubs and check its journal.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache. No source text is inspected and no Android code runs:
the real Kotlin file is compiled and its private helpers are exercised through a
JVM regression harness. Covered behaviour: lossless encode/decode of restore input
rules with user access hashes, refusal to build a partial rule when a cached user is
unknown, the per owner/backend journal, and the per account single flight guard with
logout invalidation.
"""
from pathlib import Path
import argparse
import subprocess
import os
import shutil
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument('--output', type=Path)
parser.add_argument('--cache', type=Path, default=Path.home()/'.gradle/caches/modules-2/files-2.1')
parser.add_argument('--java', default=os.environ.get('JAVA', shutil.which('java') or 'java'))
args = parser.parse_args()
root = args.root.resolve()
temporary = tempfile.TemporaryDirectory(prefix='tele-security-privacy-') if args.output is None else None
here = args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache = args.cache


def jar(group, artifact, version):
    return next((cache/group/artifact/version).glob('*/'+artifact+'-'+version+'.jar'))


cp = [jar('org.jetbrains.kotlin', artifact, '2.2.21') for artifact in
      ['kotlin-compiler-embeddable', 'kotlin-stdlib', 'kotlin-script-runtime', 'kotlin-reflect']] + [
    jar('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm', '1.8.0'),
    jar('org.jetbrains', 'annotations', '13.0')]

sources = {
'Os.kt': r'''package android.os

class Looper {
    companion object {
        fun getMainLooper(): Looper = Looper()
    }
}

class Handler(looper: Looper) {
    fun post(runnable: Runnable) {
        runnable.run()
    }

    fun postDelayed(runnable: Runnable, delayMillis: Long) {
        runnable.run()
    }
}
''',
'App.kt': r'''package android.app

open class Activity
''',
'Widget.kt': r'''package android.widget

import android.app.Activity

class Toast {
    fun show() {}

    companion object {
        const val LENGTH_SHORT = 0

        fun makeText(context: Activity, text: CharSequence, duration: Int): Toast = Toast()
    }
}
''',
'Util.kt': r'''package android.util

object Base64 {
    const val NO_WRAP = 2

    fun encodeToString(bytes: ByteArray, flags: Int): String =
        java.util.Base64.getEncoder().encodeToString(bytes)

    fun decode(str: String, flags: Int): ByteArray =
        java.util.Base64.getDecoder().decode(str)
}
''',
'Json.kt': r'''package org.json

class JSONException(message: String) : RuntimeException(message)

class JSONObject {
    private val values = LinkedHashMap<String, Any?>()

    constructor()

    constructor(json: String) {
        val parsed = JsonParser(json).parse()
        if (parsed !is Map<*, *>) throw JSONException("not an object")
        for ((key, value) in parsed) values[key.toString()] = value
    }

    fun put(key: String, value: Any?): JSONObject {
        values[key] = value
        return this
    }

    fun optInt(key: String, fallback: Int): Int = (values[key] as? Number)?.toInt() ?: fallback

    fun optLong(key: String, fallback: Long): Long = (values[key] as? Number)?.toLong() ?: fallback

    fun optBoolean(key: String, fallback: Boolean): Boolean = when (val value = values[key]) {
        is Boolean -> value
        is String -> value.toBooleanStrictOrNull() ?: fallback
        else -> fallback
    }

    fun optString(key: String): String = values[key]?.toString() ?: ""

    fun optString(key: String, fallback: String): String = values[key]?.toString() ?: fallback

    fun optJSONArray(key: String): JSONArray? = values[key] as? JSONArray

    override fun toString(): String = JsonParser.serialize(values)
}

class JSONArray {
    private val values = ArrayList<Any?>()

    constructor(json: String) {
        val parsed = JsonParser(json).parse()
        if (parsed !is List<*>) throw JSONException("not an array")
        values.addAll(parsed)
    }

    fun length(): Int = values.size

    fun getJSONObject(index: Int): JSONObject =
        values[index] as? JSONObject ?: throw JSONException("not an object")

    fun optJSONArray(index: Int): JSONArray? = values.getOrNull(index) as? JSONArray

    fun optLong(index: Int): Long = (values.getOrNull(index) as? Number)?.toLong() ?: 0L

    override fun toString(): String = JsonParser.serialize(values)
}

internal class JsonParser(private val text: String) {
    private var pos = 0

    fun parse(): Any? {
        val value = value()
        ws()
        if (pos != text.length) throw JSONException("trailing data")
        return value
    }

    private fun ws() {
        while (pos < text.length && text[pos].isWhitespace()) pos++
    }

    private fun value(): Any? {
        ws()
        if (pos >= text.length) throw JSONException("end of input")
        return when (val c = text[pos]) {
            '{' -> obj()
            '[' -> arr()
            '"' -> str()
            't' -> { literal("true"); true }
            'f' -> { literal("false"); false }
            'n' -> { literal("null"); null }
            else -> if (c == '-' || c.isDigit()) num() else throw JSONException("unexpected " + c)
        }
    }

    private fun literal(word: String) {
        if (!text.startsWith(word, pos)) throw JSONException("bad literal")
        pos += word.length
    }

    private fun obj(): Map<String, Any?> {
        pos++
        val map = LinkedHashMap<String, Any?>()
        ws()
        if (pos < text.length && text[pos] == '}') {
            pos++
            return map
        }
        while (true) {
            ws()
            val key = str()
            ws()
            if (pos >= text.length || text[pos] != ':') throw JSONException("missing colon")
            pos++
            map[key] = value()
            ws()
            if (pos >= text.length) throw JSONException("unterminated object")
            when (text[pos]) {
                ',' -> pos++
                '}' -> { pos++; return map }
                else -> throw JSONException("bad object")
            }
        }
    }

    private fun arr(): List<Any?> {
        pos++
        val list = ArrayList<Any?>()
        ws()
        if (pos < text.length && text[pos] == ']') {
            pos++
            return list
        }
        while (true) {
            list.add(value())
            ws()
            if (pos >= text.length) throw JSONException("unterminated array")
            when (text[pos]) {
                ',' -> pos++
                ']' -> { pos++; return list }
                else -> throw JSONException("bad array")
            }
        }
    }

    private fun str(): String {
        if (pos >= text.length || text[pos] != '"') throw JSONException("not a string")
        pos++
        val sb = StringBuilder()
        while (true) {
            if (pos >= text.length) throw JSONException("unterminated string")
            val c = text[pos++]
            when (c) {
                '"' -> return sb.toString()
                '\\' -> {
                    if (pos >= text.length) throw JSONException("bad escape")
                    when (val e = text[pos++]) {
                        '"', '\\', '/' -> sb.append(e)
                        'b' -> sb.append('\b')
                        'f' -> sb.append('\u000C')
                        'n' -> sb.append('\n')
                        'r' -> sb.append('\r')
                        't' -> sb.append('\t')
                        'u' -> {
                            if (pos + 4 > text.length) throw JSONException("bad unicode escape")
                            sb.append(text.substring(pos, pos + 4).toInt(16).toChar())
                            pos += 4
                        }
                        else -> throw JSONException("bad escape " + e)
                    }
                }
                else -> sb.append(c)
            }
        }
    }

    private fun num(): Number {
        val start = pos
        if (text[pos] == '-') pos++
        while (pos < text.length && (text[pos].isDigit() || text[pos] == '.' ||
                    text[pos] == 'e' || text[pos] == 'E' || text[pos] == '+' || text[pos] == '-')) pos++
        val raw = text.substring(start, pos)
        return if (raw.contains('.') || raw.contains('e') || raw.contains('E')) raw.toDouble() else raw.toLong()
    }

    companion object {
        fun serialize(value: Any?): String = when (value) {
            null -> "null"
            is String -> quote(value)
            is Boolean, is Number -> value.toString()
            is JSONObject, is JSONArray -> value.toString()
            is Map<*, *> -> value.entries.joinToString(",", "{", "}") { quote(it.key.toString()) + ":" + serialize(it.value) }
            is Iterable<*> -> value.joinToString(",", "[", "]") { serialize(it) }
            else -> quote(value.toString())
        }

        private fun quote(value: String): String {
            val sb = StringBuilder("\"")
            for (c in value) {
                when (c) {
                    '"' -> sb.append("\\\"")
                    '\\' -> sb.append("\\\\")
                    '\n' -> sb.append("\\n")
                    '\r' -> sb.append("\\r")
                    '\t' -> sb.append("\\t")
                    else -> if (c < ' ') sb.append(String.format("\\u%04x", c.code)) else sb.append(c)
                }
            }
            return sb.append('"').toString()
        }
    }
}
''',
'Tg.kt': r'''package org.telegram.tgnet

open class TLObject {
    open fun getObjectSize(): Int = 64
}

class SerializedData {
    private var buffer: ByteArray
    private var size = 0
    private var position = 0

    constructor(size: Int) {
        buffer = ByteArray(maxOf(size, 16))
    }

    constructor(data: ByteArray) {
        buffer = data.copyOf()
        size = data.size
    }

    private fun ensure(extra: Int) {
        if (size + extra > buffer.size) buffer = buffer.copyOf(maxOf(buffer.size * 2, size + extra))
    }

    fun writeInt32(value: Int) {
        ensure(4)
        buffer[size++] = (value ushr 24).toByte()
        buffer[size++] = (value ushr 16).toByte()
        buffer[size++] = (value ushr 8).toByte()
        buffer[size++] = value.toByte()
    }

    fun writeInt64(value: Long) {
        writeInt32((value ushr 32).toInt())
        writeInt32(value.toInt())
    }

    fun readInt32(exception: Boolean): Int {
        if (position + 4 > size) {
            if (exception) throw RuntimeException("end of data")
            return 0
        }
        val value = ((buffer[position].toInt() and 0xFF) shl 24) or
            ((buffer[position + 1].toInt() and 0xFF) shl 16) or
            ((buffer[position + 2].toInt() and 0xFF) shl 8) or
            (buffer[position + 3].toInt() and 0xFF)
        position += 4
        return value
    }

    fun readInt64(exception: Boolean): Long =
        (readInt32(exception).toLong() shl 32) or (readInt32(exception).toLong() and 0xFFFFFFFFL)

    fun remaining(): Int = size - position

    fun toByteArray(): ByteArray = buffer.copyOf(size)

    fun cleanup() {}
}

object TLRPC {
    open class PrivacyRule

    open class InputPrivacyRule : TLObject() {
        open fun serializeToStream(stream: SerializedData) {}

        open fun readParams(stream: SerializedData) {}

        companion object {
            fun TLdeserialize(stream: SerializedData, constructor: Int, exception: Boolean): InputPrivacyRule? {
                val rule = when (constructor) {
                    TL_inputPrivacyValueAllowAll.CONSTRUCTOR -> TL_inputPrivacyValueAllowAll()
                    TL_inputPrivacyValueAllowContacts.CONSTRUCTOR -> TL_inputPrivacyValueAllowContacts()
                    TL_inputPrivacyValueAllowUsers.CONSTRUCTOR -> TL_inputPrivacyValueAllowUsers()
                    TL_inputPrivacyValueAllowChatParticipants.CONSTRUCTOR -> TL_inputPrivacyValueAllowChatParticipants()
                    TL_inputPrivacyValueAllowCloseFriends.CONSTRUCTOR -> TL_inputPrivacyValueAllowCloseFriends()
                    TL_inputPrivacyValueAllowPremium.CONSTRUCTOR -> TL_inputPrivacyValueAllowPremium()
                    TL_inputPrivacyValueAllowBots.CONSTRUCTOR -> TL_inputPrivacyValueAllowBots()
                    TL_inputPrivacyValueDisallowAll.CONSTRUCTOR -> TL_inputPrivacyValueDisallowAll()
                    TL_inputPrivacyValueDisallowContacts.CONSTRUCTOR -> TL_inputPrivacyValueDisallowContacts()
                    TL_inputPrivacyValueDisallowUsers.CONSTRUCTOR -> TL_inputPrivacyValueDisallowUsers()
                    TL_inputPrivacyValueDisallowChatParticipants.CONSTRUCTOR -> TL_inputPrivacyValueDisallowChatParticipants()
                    TL_inputPrivacyValueDisallowBots.CONSTRUCTOR -> TL_inputPrivacyValueDisallowBots()
                    else -> return null
                }
                rule.readParams(stream)
                return rule
            }
        }
    }

    open class InputUser : TLObject() {
        var user_id = 0L
        var access_hash = 0L

        open fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(CONSTRUCTOR)
            stream.writeInt64(user_id)
            stream.writeInt64(access_hash)
        }

        companion object {
            const val CONSTRUCTOR = 0x2001

            fun read(stream: SerializedData): InputUser {
                stream.readInt32(false)
                val user = TL_inputUser()
                user.user_id = stream.readInt64(false)
                user.access_hash = stream.readInt64(false)
                return user
            }
        }
    }

    class TL_inputUser : InputUser()

    class TL_inputPrivacyValueAllowAll : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1001 }
    }

    class TL_inputPrivacyValueAllowContacts : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1002 }
    }

    class TL_inputPrivacyValueAllowUsers : InputPrivacyRule() {
        val users = ArrayList<InputUser>()

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(CONSTRUCTOR)
            stream.writeInt32(users.size)
            for (user in users) user.serializeToStream(stream)
        }

        override fun readParams(stream: SerializedData) {
            repeat(stream.readInt32(false)) { users.add(InputUser.read(stream)) }
        }

        companion object { const val CONSTRUCTOR = 0x1003 }
    }

    class TL_inputPrivacyValueAllowChatParticipants : InputPrivacyRule() {
        val chats = ArrayList<Long>()

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(CONSTRUCTOR)
            stream.writeInt32(chats.size)
            for (chat in chats) stream.writeInt64(chat)
        }

        override fun readParams(stream: SerializedData) {
            repeat(stream.readInt32(false)) { chats.add(stream.readInt64(false)) }
        }

        companion object { const val CONSTRUCTOR = 0x1004 }
    }

    class TL_inputPrivacyValueAllowCloseFriends : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1005 }
    }

    class TL_inputPrivacyValueAllowPremium : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1006 }
    }

    class TL_inputPrivacyValueAllowBots : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1007 }
    }

    class TL_inputPrivacyValueDisallowAll : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1008 }
    }

    class TL_inputPrivacyValueDisallowContacts : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x1009 }
    }

    class TL_inputPrivacyValueDisallowUsers : InputPrivacyRule() {
        val users = ArrayList<InputUser>()

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(CONSTRUCTOR)
            stream.writeInt32(users.size)
            for (user in users) user.serializeToStream(stream)
        }

        override fun readParams(stream: SerializedData) {
            repeat(stream.readInt32(false)) { users.add(InputUser.read(stream)) }
        }

        companion object { const val CONSTRUCTOR = 0x100A }
    }

    class TL_inputPrivacyValueDisallowChatParticipants : InputPrivacyRule() {
        val chats = ArrayList<Long>()

        override fun serializeToStream(stream: SerializedData) {
            stream.writeInt32(CONSTRUCTOR)
            stream.writeInt32(chats.size)
            for (chat in chats) stream.writeInt64(chat)
        }

        override fun readParams(stream: SerializedData) {
            repeat(stream.readInt32(false)) { chats.add(stream.readInt64(false)) }
        }

        companion object { const val CONSTRUCTOR = 0x100B }
    }

    class TL_inputPrivacyValueDisallowBots : InputPrivacyRule() {
        override fun serializeToStream(stream: SerializedData) { stream.writeInt32(CONSTRUCTOR) }
        companion object { const val CONSTRUCTOR = 0x100C }
    }

    class TL_privacyValueAllowAll : PrivacyRule()
    class TL_privacyValueAllowContacts : PrivacyRule()
    class TL_privacyValueAllowUsers : PrivacyRule() { val users = ArrayList<Long>() }
    class TL_privacyValueAllowChatParticipants : PrivacyRule() { val chats = ArrayList<Long>() }
    class TL_privacyValueAllowCloseFriends : PrivacyRule()
    class TL_privacyValueAllowPremium : PrivacyRule()
    class TL_privacyValueAllowBots : PrivacyRule()
    class TL_privacyValueDisallowAll : PrivacyRule()
    class TL_privacyValueDisallowContacts : PrivacyRule()
    class TL_privacyValueDisallowUsers : PrivacyRule() { val users = ArrayList<Long>() }
    class TL_privacyValueDisallowChatParticipants : PrivacyRule() { val chats = ArrayList<Long>() }
    class TL_privacyValueDisallowBots : PrivacyRule()

    class User : TLObject() {
        var id = 0L
        var access_hash = 0L
        var bot = false
        var self = false
        var fromMessageDialogId = 0L
        var fromMessageId = 0
        var status: UserStatus? = null
    }

    class UserStatus : TLObject()

    class Chat : TLObject()

    class TL_error : TLObject() {
        var text: String? = null
    }

    class TL_inputPrivacyKeyStatusTimestamp : TLObject()
}
''',
'Connections.kt': r'''package org.telegram.tgnet

import org.telegram.messenger.UserConfig
import org.telegram.tgnet.tl.TL_account

class ConnectionsManager {
    var testBackend = false
    var sent = 0
    var lastRules = ArrayList<TLRPC.InputPrivacyRule>()

    fun isTestBackend(): Boolean = testBackend

    fun sendRequest(request: TLObject, callback: (Any?, TLRPC.TL_error?) -> Unit, flags: Int) {
        sent++
        if (request is TL_account.setPrivacy) lastRules = request.rules
    }

    companion object {
        const val RequestFlagFailOnServerErrors = 4
        private val accounts = Array(UserConfig.MAX_ACCOUNT_COUNT) { ConnectionsManager() }
        fun getInstance(account: Int): ConnectionsManager = accounts[account]
    }
}
''',
'TlAccount.kt': r'''package org.telegram.tgnet.tl

import org.telegram.tgnet.TLObject
import org.telegram.tgnet.TLRPC

object TL_account {
    class setPrivacy : TLObject() {
        var key: TLRPC.TL_inputPrivacyKeyStatusTimestamp? = null
        val rules = ArrayList<TLRPC.InputPrivacyRule>()
    }

    class privacyRules : TLObject() {
        var users = ArrayList<TLRPC.User>()
        var chats = ArrayList<TLRPC.Chat>()
        var rules = ArrayList<TLRPC.PrivacyRule>()
    }
}
''',
'Telegram.kt': r'''package org.telegram.messenger

import org.telegram.tgnet.TLRPC

class UserConfig {
    var clientUserId = 0L

    companion object {
        const val MAX_ACCOUNT_COUNT = 3
        private val accounts = Array(MAX_ACCOUNT_COUNT) { UserConfig() }

        fun getInstance(account: Int): UserConfig = accounts[account]
    }
}

class MessagesController {
    val users = HashMap<Long, TLRPC.User>()

    fun getUser(id: Long): TLRPC.User? = users[id]

    fun getInputUser(user: TLRPC.User): TLRPC.InputUser {
        val input = TLRPC.TL_inputUser()
        input.user_id = user.id
        input.access_hash = user.access_hash
        return input
    }

    fun putUsers(users: ArrayList<TLRPC.User>, fromCache: Boolean) {}

    fun putChats(chats: ArrayList<TLRPC.Chat>, fromCache: Boolean) {}

    companion object {
        private val accounts = Array(UserConfig.MAX_ACCOUNT_COUNT) { MessagesController() }
        fun getInstance(account: Int): MessagesController = accounts[account]
    }
}

class ContactsController {
    val rules = ArrayList<TLRPC.PrivacyRule>()

    fun getPrivacyRules(type: Int): ArrayList<TLRPC.PrivacyRule>? = rules

    fun loadPrivacySettings(force: Boolean) {}

    fun setPrivacyRules(rules: ArrayList<TLRPC.PrivacyRule>, type: Int) {}

    companion object {
        const val PRIVACY_RULES_TYPE_LASTSEEN = 0
        private val accounts = Array(UserConfig.MAX_ACCOUNT_COUNT) { ContactsController() }
        fun getInstance(account: Int): ContactsController = accounts[account]
    }
}

object LocaleController {
    fun formatUserStatus(account: Int, user: TLRPC.User?, isOnline: BooleanArray?, madeShorter: BooleanArray?): String =
        "status"
}
''',
'Ui.kt': r'''package org.telegram.ui.ActionBar

import android.app.Activity

open class BaseFragment {
    var parentActivity: Activity? = null
    var currentAccount: Int = 0
}
''',
'Tele.kt': r'''package tele

class BoolItem(val key: String, val defaultValue: Boolean) {
    var value: Boolean = defaultValue
}

object TeleConfig {
    @JvmField
    val LAST_SEEN_RESTORE = BoolItem("last_seen_restore", false)
}
''',
'Db.kt': r'''package tele.db

object TeleDatabaseHelper {
    val values = HashMap<String, String>()

    fun put(key: String, value: String?) {
        if (value == null) values.remove(key) else values[key] = value
    }

    fun get(key: String, default: String? = null): String? =
        if (values.containsKey(key)) values[key] else default
}
''',
'Helpers.kt': r'''package tele.helpers

object TeleLowercase {
    fun lc(text: String): String = text
}

object TeleToast {
    fun log(site: String, text: CharSequence?, title: String = "", account: Int = 0) {}
}
''',
'Test.kt': r'''package regression

import org.json.JSONObject
import org.telegram.tgnet.ConnectionsManager
import org.telegram.messenger.MessagesController
import org.telegram.messenger.UserConfig
import org.telegram.tgnet.TLRPC
import tele.db.TeleDatabaseHelper
import tele.helpers.LastSeenPeek
import java.lang.reflect.Method

private val journalClass = Class.forName("tele.helpers.LastSeenPeek\$Journal")
private val guardClass = Class.forName("tele.helpers.LastSeenPeek\$Guard")

private fun peekMethod(name: String, vararg types: Class<*>): Method =
    LastSeenPeek::class.java.getDeclaredMethod(name, *types).apply { isAccessible = true }

private val acquireMethod = peekMethod("acquire", Int::class.javaPrimitiveType!!)
private val releaseMethod = peekMethod("release", Int::class.javaPrimitiveType!!, guardClass)
private val holdsMethod = peekMethod("holds", Int::class.javaPrimitiveType!!, guardClass)
private val buildMethod = peekMethod(
    "buildRules", ArrayList::class.java, Int::class.javaPrimitiveType!!, Long::class.javaPrimitiveType!!
)
private val encodeMethod = peekMethod("encodeRules", ArrayList::class.java)
private val decodeRulesMethod = peekMethod("decodeRules", String::class.java)
private val decodeMethod = peekMethod("decode", String::class.java)
private val restoreMethod = peekMethod(
    "restore", Int::class.javaPrimitiveType!!, journalClass, guardClass
)

private fun acquireGuard(account: Int): Any? = acquireMethod.invoke(LastSeenPeek, account)

private fun releaseGuard(account: Int, guard: Any) {
    releaseMethod.invoke(LastSeenPeek, account, guard)
}

private fun isHeld(account: Int, guard: Any): Boolean =
    holdsMethod.invoke(LastSeenPeek, account, guard) as Boolean

private fun journalField(journal: Any, name: String): Any? =
    journalClass.getDeclaredField(name).apply { isAccessible = true }.get(journal)

private fun journalKey(account: Int): String = "privacy_last_seen:" + account

private fun version(): Int =
    LastSeenPeek::class.java.getDeclaredField("VERSION").apply { isAccessible = true }.getInt(null)

private fun user(id: Long, hash: Long): TLRPC.User = TLRPC.User().also {
    it.id = id
    it.access_hash = hash
}

private fun rules(vararg values: TLRPC.PrivacyRule): ArrayList<TLRPC.PrivacyRule> =
    ArrayList(values.toList())

private fun journalJson(owner: Long, testBackend: Boolean, encoded: String): String =
    JSONObject()
        .put("v", version())
        .put("owner", owner)
        .put("test", testBackend)
        .put("rules", encoded)
        .toString()

private fun denyIds(input: Any): List<Long> =
    (input as TLRPC.TL_inputPrivacyValueDisallowUsers).users.map { it.user_id }

private fun denyHashes(input: Any): List<Long> =
    (input as TLRPC.TL_inputPrivacyValueDisallowUsers).users.map { it.access_hash }

fun main() {
    val controller = MessagesController.getInstance(0)
    controller.users[10L] = user(10L, 1000L)
    controller.users[20L] = user(20L, 2000L)
    controller.users[30L] = user(30L, 3000L)

    val deny = TLRPC.TL_privacyValueDisallowUsers().also {
        it.users.add(10L)
        it.users.add(20L)
    }
    val original = rules(TLRPC.TL_privacyValueAllowAll(), deny)

    // a cached deny list keeps every user and access hash
    val built = buildMethod.invoke(LastSeenPeek, original, 0, 0L) as ArrayList<*>?
    check(built != null) { "a fully cached deny rule must build" }
    val builtDeny = built!!.filterIsInstance<TLRPC.TL_inputPrivacyValueDisallowUsers>().single()
    check(denyIds(builtDeny) == listOf(10L, 20L)) { "deny ids changed" }
    check(denyHashes(builtDeny) == listOf(1000L, 2000L)) { "deny access hashes lost" }

    // the restore journal round-trips the same users
    val encoded = encodeMethod.invoke(LastSeenPeek, built) as String?
    check(encoded != null) { "restore rules did not encode" }
    val decoded = decodeRulesMethod.invoke(LastSeenPeek, encoded) as ArrayList<*>?
    check(decoded != null) { "restore rules did not decode" }
    val restored = decoded!!.filterIsInstance<TLRPC.TL_inputPrivacyValueDisallowUsers>().single()
    check(denyIds(restored) == listOf(10L, 20L)) { "restored deny ids changed" }
    check(denyHashes(restored) == listOf(1000L, 2000L)) { "restored access hashes lost" }

    // a user missing from the cache fails the whole rule, never a partial one
    controller.users.remove(20L)
    check(buildMethod.invoke(LastSeenPeek, original, 0, 0L) == null) {
        "a missing deny user produced a partial rule"
    }
    controller.users[20L] = user(20L, 2000L)

    // peek target is added, existing allow users stay complete
    val allowUser = TLRPC.TL_privacyValueAllowUsers().also { it.users.add(10L) }
    val permit = rules(TLRPC.TL_privacyValueAllowContacts(), allowUser)
    val peekRules = buildMethod.invoke(LastSeenPeek, permit, 0, 30L) as ArrayList<*>?
    check(peekRules != null) { "peek rules did not build" }
    val peekAllow = peekRules!!.filterIsInstance<TLRPC.TL_inputPrivacyValueAllowUsers>().single()
    check(peekAllow.users.map { it.user_id }.toSet() == setOf(10L, 30L)) { "peek dropped an allow user" }

    // journal binds owner, backend and the full restore rules
    val json = journalJson(7L, true, encoded)
    val journal = decodeMethod.invoke(LastSeenPeek, json)
    check(journal != null) { "journal did not decode" }
    check(journalField(journal!!, "owner") == 7L) { "journal owner lost" }
    check(journalField(journal, "testBackend") == true) { "journal backend lost" }
    val journalRules = journalField(journal, "rules") as ArrayList<*>
    check(denyHashes(journalRules.filterIsInstance<TLRPC.TL_inputPrivacyValueDisallowUsers>().single()) ==
        listOf(1000L, 2000L)) { "journal lost access hashes" }

    // an older journal layout is not silently applied
    val old = "{\"v\":2,\"owner\":7,\"dc\":4,\"rules\":\"" + encoded + "\"}"
    check(decodeMethod.invoke(LastSeenPeek, old) == null) { "old journal format accepted" }

    UserConfig.getInstance(0).clientUserId = 7L
    val connections = ConnectionsManager.getInstance(0)
    connections.testBackend = false
    connections.sent = 0

    // single flight per account
    val first = acquireGuard(0)
    check(first != null) { "first acquire refused" }
    check(acquireGuard(0) == null) { "second acquire must be refused" }
    check(isHeld(0, first!!)) { "held guard lost" }
    releaseGuard(0, first)
    val second = acquireGuard(0)
    check(second != null) { "acquire after release refused" }

    // owner change invalidates the guard, restoring it clears the invalidation
    UserConfig.getInstance(0).clientUserId = 8L
    check(!isHeld(0, second!!)) { "owner change kept the guard alive" }
    UserConfig.getInstance(0).clientUserId = 7L
    check(isHeld(0, second)) { "owner restore lost the guard" }
    releaseGuard(0, second)

    // backend switch invalidates the guard even with the same numeric user
    val backendGuard = acquireGuard(0)
    check(backendGuard != null) { "acquire for backend check refused" }
    connections.testBackend = true
    check(!isHeld(0, backendGuard!!)) { "backend switch kept the guard alive" }
    connections.testBackend = false
    check(isHeld(0, backendGuard)) { "backend restore lost the guard" }
    releaseGuard(0, backendGuard)

    // foreign owner journal: no send, journal removed, guard released
    TeleDatabaseHelper.put(journalKey(0), journalJson(99L, false, encoded!!))
    var guard = acquireGuard(0)
    check(guard != null)
    restoreMethod.invoke(LastSeenPeek, 0, null, guard)
    check(TeleDatabaseHelper.get(journalKey(0)) == null) { "foreign owner journal survived" }
    check(connections.sent == 0) { "foreign owner rules were sent" }
    var fresh = acquireGuard(0)
    check(fresh != null) { "foreign owner restore kept the guard" }
    releaseGuard(0, fresh!!)

    // same id on the other backend: isolated, no send
    TeleDatabaseHelper.put(journalKey(0), journalJson(7L, true, encoded))
    guard = acquireGuard(0)
    check(guard != null)
    restoreMethod.invoke(LastSeenPeek, 0, null, guard)
    check(TeleDatabaseHelper.get(journalKey(0)) == null) { "backend mismatch journal survived" }
    check(connections.sent == 0) { "backend mismatch rules were sent" }
    fresh = acquireGuard(0)
    check(fresh != null) { "backend mismatch restore kept the guard" }
    releaseGuard(0, fresh!!)

    // the matching journal is sent but kept until the server confirms
    TeleDatabaseHelper.put(journalKey(0), journalJson(7L, false, encoded))
    guard = acquireGuard(0)
    check(guard != null)
    restoreMethod.invoke(LastSeenPeek, 0, null, guard)
    check(connections.sent == 1) { "matching journal was not restored" }
    check(connections.lastRules.filterIsInstance<TLRPC.TL_inputPrivacyValueDisallowUsers>()
        .single().users.map { it.access_hash } == listOf(1000L, 2000L)) { "restore sent lossy rules" }
    check(TeleDatabaseHelper.get(journalKey(0)) != null) { "journal removed before confirmation" }

    // logout drops the journal and invalidates the pending callback
    LastSeenPeek.onLogout(0)
    check(TeleDatabaseHelper.get(journalKey(0)) == null) { "logout kept the journal" }
    check(!isHeld(0, guard!!)) { "logout kept a pending callback alive" }
    val after = acquireGuard(0)
    check(after != null) { "logout left the account locked" }
    releaseGuard(0, after!!)

    println("PASS: LastSeenPeek lossless restore rules, owner/backend journal and single flight logout")
}
''',
}

for name, text in sources.items():
    (here/name).write_text(text, encoding='utf-8')

product = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/LastSeenPeek.kt'
java = args.java
out = here/'test.jar'
files = [str(here/name) for name in sources] + [str(product)]
subprocess.run([java, '-cp', os.pathsep.join(map(str, cp)),
                'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
                '-no-stdlib', '-no-reflect', '-classpath', str(cp[1]),
                '-d', str(out), *files], check=True)
subprocess.run([java, '-cp', os.pathsep.join([str(out), str(cp[1])]), 'regression.TestKt'], check=True)
print('PASS: LastSeenPeek behavioural security checks')
