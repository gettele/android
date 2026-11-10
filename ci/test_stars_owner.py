"""Compile and run the actual StarsLock.kt owner policy, no Android/JNI.

The device-side Android/Telegram/tele dependencies are replaced by minimal Kotlin stubs;
the production StarsLock.kt itself is compiled unchanged and checked behaviourally:
the owner is captured before the async kdf and survives an account switch, only a signed-in
activated account owns the lock (backend included), an absent/legacy/unknown owner cannot
reset by countdown or cloud password, and a reset cannot clear a lock replaced while its
dialog/request was in flight. StarsLockUi is stubbed only to observe which reset dialog the
core opens; its own Android view code is not part of this check.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache.
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
temporary = tempfile.TemporaryDirectory(prefix='tele-stars-owner-') if args.output is None else None
here = args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache = args.cache


def jar(group, artifact, version):
    return next((cache/group/artifact/version).glob('*/'+artifact+'-'+version+'.jar'))


cp = [jar('org.jetbrains.kotlin', a, '2.2.21') for a in
      ['kotlin-compiler-embeddable', 'kotlin-stdlib', 'kotlin-script-runtime', 'kotlin-reflect']]
cp += [jar('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm', '1.8.0'),
       jar('org.jetbrains', 'annotations', '13.0')]

sources = {}

sources['StubAndroidApp.kt'] = r'''package android.app

import android.content.Context

open class Activity : Context() {
    open val isFinishing: Boolean get() = false
}
'''

sources['StubAndroidContent.kt'] = r'''package android.content

open class Context
'''

sources['StubAndroidOs.kt'] = r'''package android.os

class Looper private constructor() {
    companion object {
        private val main = Looper()
        @JvmStatic fun myLooper(): Looper? = main
        @JvmStatic fun getMainLooper(): Looper = main
    }
}

object SystemClock {
    @JvmStatic fun elapsedRealtime(): Long = System.nanoTime() / 1_000_000L
}
'''

sources['StubAndroidUtil.kt'] = r'''package android.util

import java.util.Base64 as JBase64

object Base64 {
    const val NO_WRAP = 0
    @JvmStatic fun encodeToString(input: ByteArray, flags: Int): String =
        JBase64.getEncoder().encodeToString(input)
    @JvmStatic fun decode(input: String, flags: Int): ByteArray =
        JBase64.getDecoder().decode(input)
}
'''

sources['StubBiometric.kt'] = r'''package androidx.biometric

import android.app.Activity
import android.content.Context
import java.util.concurrent.Executor

class BiometricManager private constructor() {
    fun canAuthenticate(authenticators: Int): Int = BIOMETRIC_ERROR_NONE_ENROLLED

    object Authenticators {
        const val BIOMETRIC_STRONG = 15
    }

    companion object {
        const val BIOMETRIC_SUCCESS = 0
        const val BIOMETRIC_ERROR_NONE_ENROLLED = 11
        @JvmStatic fun from(context: Context): BiometricManager = BiometricManager()
    }
}

class BiometricPrompt(activity: Activity, executor: Executor, callback: AuthenticationCallback) {
    open class AuthenticationCallback {
        open fun onAuthenticationSucceeded(result: AuthenticationResult) {}
        open fun onAuthenticationError(errorCode: Int, errString: CharSequence) {}
    }

    class AuthenticationResult

    class PromptInfo {
        class Builder {
            fun setTitle(title: CharSequence): Builder = this
            fun setNegativeButtonText(text: CharSequence): Builder = this
            fun setAllowedAuthenticators(authenticators: Int): Builder = this
            fun build(): PromptInfo = PromptInfo()
        }
    }

    fun authenticate(info: PromptInfo) {}

    companion object {
        const val ERROR_USER_CANCELED = 13
        const val ERROR_CANCELED = 5
    }
}
'''

sources['StubContextCompat.kt'] = r'''package androidx.core.content

import android.content.Context
import java.util.concurrent.Executor

object ContextCompat {
    @JvmStatic fun getMainExecutor(context: Context): Executor = Executor { it.run() }
}
'''

sources['StubMessenger.kt'] = r'''package org.telegram.messenger

import android.app.Activity
import android.content.Context
import java.security.MessageDigest
import org.telegram.tgnet.TLRPC

object AndroidUtilities {
    @JvmStatic fun runOnUIThread(runnable: Runnable) { runnable.run() }
    @JvmStatic fun findActivity(context: Context): Activity? = context as? Activity
    @JvmStatic fun getStringBytes(value: String): ByteArray = value.toByteArray(Charsets.UTF_8)
}

object FileLog {
    @JvmStatic fun e(error: Throwable) {}
    @JvmStatic fun e(message: String) {}
}

object R {
    object raw {
        const val error = 1
        const val info = 2
    }
}

object SRPHelper {
    @JvmStatic fun startCheck(
        x: ByteArray,
        srpId: Long,
        b: ByteArray,
        algo: TLRPC.TL_passwordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow
    ): Any? = Any()

    @JvmStatic fun getX(
        bytes: ByteArray,
        algo: TLRPC.TL_passwordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow
    ): ByteArray = bytes
}

class UserConfig private constructor() {
    @JvmField var clientUserId: Long = 0
    var activated: Boolean = true

    val isClientActivated: Boolean get() = activated && clientUserId != 0L

    fun getClientUserId(): Long = clientUserId

    companion object {
        @JvmStatic var selectedAccount: Int = 0
        const val MAX_ACCOUNT_COUNT = 8
        private val instances = Array(MAX_ACCOUNT_COUNT) { UserConfig() }
        @JvmStatic fun getInstance(num: Int): UserConfig = instances[num]
    }
}

class Utilities private constructor() {
    class Queue {
        private val tasks = ArrayList<Runnable>()
        fun postRunnable(runnable: Runnable) { tasks.add(runnable) }
        fun flush() { while (tasks.isNotEmpty()) tasks.removeAt(0).run() }
        fun clear() { tasks.clear() }
    }

    companion object {
        @JvmField val globalQueue = Queue()
        @JvmStatic fun runAll() = globalQueue.flush()
        @JvmStatic fun clearAll() = globalQueue.clear()

        @JvmStatic fun computePBKDF2(password: ByteArray, salt: ByteArray): ByteArray {
            val digest = MessageDigest.getInstance("SHA-256")
            digest.update(salt)
            return digest.digest(password)
        }
    }
}
'''

sources['StubTgnet.kt'] = r'''package org.telegram.tgnet

class TLRPC {
    class TL_passwordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow
}

class TL_error {
    var text: String? = null
}

class ConnectionsManager private constructor(val index: Int) {
    var test = false
    val isTestBackend: Boolean get() = test
    var requests = 0
    private var pending: ((Any?, TL_error?) -> Unit)? = null
    private val seen = ArrayList<Any?>()
    val requestsSeen: List<Any?> get() = seen

    fun sendRequest(request: Any?, callback: (Any?, TL_error?) -> Unit, flags: Int) {
        requests++
        seen.add(request)
        pending = callback
    }

    fun respond(response: Any?, error: TL_error?) {
        val callback = pending
        pending = null
        callback?.invoke(response, error)
    }

    fun reset() {
        test = false
        requests = 0
        pending = null
        seen.clear()
    }

    companion object {
        const val RequestFlagFailOnServerErrors = 1
        private val instances = Array(org.telegram.messenger.UserConfig.MAX_ACCOUNT_COUNT) {
            ConnectionsManager(it)
        }
        @JvmStatic fun getInstance(num: Int): ConnectionsManager = instances[num]
        @JvmStatic fun all(): List<ConnectionsManager> = instances.toList()
    }
}
'''

sources['StubTlAccount.kt'] = r'''package org.telegram.tgnet.tl

object TL_account {
    class Password {
        var has_password: Boolean = false
        var hint: String? = null
        var current_algo: Any? = null
        var srp_id: Long = 0
        var srp_B: ByteArray = ByteArray(0)
    }

    class GetPasswordRequest

    class GetPasswordSettingsRequest {
        var password: Any? = null
    }

    @JvmStatic fun getPassword(): GetPasswordRequest = GetPasswordRequest()
    @JvmStatic fun getPasswordSettings(): GetPasswordSettingsRequest = GetPasswordSettingsRequest()
}
'''

sources['StubActionBar.kt'] = r'''package org.telegram.ui.ActionBar

import android.app.Activity
import android.content.Context

class Theme {
    class ResourcesProvider
}

open class BaseFragment {
    open val parentActivity: Activity? get() = null
    open val resourceProvider: Theme.ResourcesProvider? get() = null
}

class AlertDialog(context: Context?, type: Int) {
    fun showDelayed(delay: Long) {}
    fun dismiss() {}

    companion object {
        const val ALERT_TYPE_SPINNER = 0
    }
}
'''

sources['StubComponents.kt'] = r'''package org.telegram.ui.Components

class BulletinFactory private constructor() {
    inner class Bulletin {
        fun show() {}
    }

    fun createSimpleBulletin(icon: Int, text: String): Bulletin = Bulletin()

    companion object {
        @JvmStatic fun global(): BulletinFactory = BulletinFactory()
    }
}
'''

sources['StubTwoStep.kt'] = r'''package org.telegram.ui

import android.app.Activity
import org.telegram.tgnet.tl.TL_account

object LaunchActivity {
    @JvmField var instance: Activity? = null
}

object TwoStepVerificationActivity {
    @JvmStatic fun canHandleCurrentPassword(password: TL_account.Password, whatever: Boolean): Boolean = true
}
'''

sources['StubTele.kt'] = r'''package tele

class StringItem(var value: String)
class BoolItem(var value: Boolean = false)

object TeleConfig {
    @JvmField val LOCAL_PASSWORD_HASH = StringItem("")
    @JvmField val LOCAL_PASSWORD_OWNER = StringItem("")
    @JvmField val LOCAL_PASSWORD_BIOMETRIC = BoolItem(false)
    @JvmField val LOCAL_PASSWORD_TRANSFER = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_CONVERT = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_SELL = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_UPGRADE = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_BUY = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_SEND = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_REACTIONS = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_PAID_MEDIA = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_PAID_MESSAGES = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_SUBSCRIPTIONS = BoolItem(true)
    @JvmField val LOCAL_PASSWORD_BOT_PAYMENTS = BoolItem(true)

    @JvmStatic fun set(item: Any?, value: Any?) {
        when (item) {
            is StringItem -> item.value = value as String
            is BoolItem -> item.value = value as Boolean
        }
    }
}
'''

sources['StubTeleHelpers.kt'] = r'''package tele.helpers

object TeleLowercase {
    @JvmStatic fun lc(text: String): String = text.lowercase()
}

object TeleToast {
    var lastSite: String? = null
    var lastText: String? = null
    var count = 0

    @JvmStatic fun log(site: String, text: String) {
        lastSite = site
        lastText = text
        count++
    }

    @JvmStatic fun reset() {
        lastSite = null
        lastText = null
        count = 0
    }
}
'''

sources['StubStarsLockUi.kt'] = r'''package tele.ui

import android.app.Activity
import org.telegram.ui.ActionBar.AlertDialog
import org.telegram.ui.ActionBar.Theme
import tele.helpers.StarsLock

// Only the calls the StarsLock core makes; the real Android dialog code is elsewhere.
object StarsLockUi {
    var promptCalls = 0
    var cloudAccount = -1
    var cloudHint: String? = null
    internal var cloudSnapshot: StarsLock.Snapshot? = null
    var countdownAccount = -1
    internal var countdownSnapshot: StarsLock.Snapshot? = null

    fun prompt(host: Activity, resources: Theme.ResourcesProvider?, current: Int): AlertDialog {
        promptCalls++
        return AlertDialog(host, 0)
    }

    internal fun resetWithCloud(
        host: Activity,
        resources: Theme.ResourcesProvider?,
        account: Int,
        hint: String,
        snapshot: StarsLock.Snapshot
    ) {
        cloudAccount = account
        cloudHint = hint
        cloudSnapshot = snapshot
    }

    internal fun resetWithCountdown(
        host: Activity,
        resources: Theme.ResourcesProvider?,
        account: Int,
        snapshot: StarsLock.Snapshot
    ) {
        countdownAccount = account
        countdownSnapshot = snapshot
    }

    fun resetState() {
        promptCalls = 0
        cloudAccount = -1
        cloudHint = null
        cloudSnapshot = null
        countdownAccount = -1
        countdownSnapshot = null
    }
}
'''

sources['Test.kt'] = r'''package regression

import android.app.Activity
import org.telegram.messenger.UserConfig
import org.telegram.messenger.Utilities
import org.telegram.tgnet.ConnectionsManager
import org.telegram.tgnet.tl.TL_account
import tele.TeleConfig
import tele.helpers.StarsLock
import tele.helpers.TeleToast
import tele.ui.StarsLockUi

private fun resetState() {
    TeleConfig.LOCAL_PASSWORD_HASH.value = ""
    TeleConfig.LOCAL_PASSWORD_OWNER.value = ""
    TeleConfig.LOCAL_PASSWORD_BIOMETRIC.value = false
    StarsLockUi.resetState()
    TeleToast.reset()
    Utilities.clearAll()
    for (account in 0 until UserConfig.MAX_ACCOUNT_COUNT) {
        UserConfig.getInstance(account).apply {
            clientUserId = 0
            activated = false
        }
        ConnectionsManager.getInstance(account).reset()
    }
    UserConfig.selectedAccount = 0
}

private fun login(account: Int, id: Long, test: Boolean = false, activated: Boolean = true) {
    UserConfig.getInstance(account).apply {
        clientUserId = id
        this.activated = activated
    }
    ConnectionsManager.getInstance(account).test = test
}

private fun savePassword(password: String, account: Int = 0): Boolean {
    UserConfig.selectedAccount = account
    var saved = false
    StarsLock.save(password) { saved = it }
    Utilities.runAll()
    return saved
}

private fun totalRequests(): Int = ConnectionsManager.all().sumOf { it.requests }

private fun ownerFollowsSavingAccount() {
    resetState()
    login(0, 111L)
    login(1, 222L)
    check(savePassword("secret", 0))
    check(TeleConfig.LOCAL_PASSWORD_HASH.value.isNotEmpty())
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value == "prod:111")

    // the selected account is B now; the lock must still resolve to A
    UserConfig.selectedAccount = 1
    check(StarsLock.ownerAccount() == 0)
    StarsLock.reset(Activity(), null)
    check(ConnectionsManager.getInstance(0).requests == 1)
    check(ConnectionsManager.getInstance(1).requests == 0)

    ConnectionsManager.getInstance(0).respond(
        TL_account.Password().apply {
            has_password = true
            hint = "cloud hint"
        },
        null
    )
    check(StarsLockUi.cloudAccount == 0)
    check(StarsLockUi.cloudHint == "cloud hint")
    check(StarsLockUi.cloudSnapshot?.owner == "prod:111")
    check(StarsLockUi.countdownAccount == -1)
}

private fun saveCapturesOwnerBeforeAsync() {
    resetState()
    login(0, 111L)
    login(1, 222L)
    UserConfig.selectedAccount = 0
    var saved = false
    StarsLock.save("pw") { saved = it }
    // the kdf is still queued; the owner must have been captured as A
    UserConfig.selectedAccount = 1
    Utilities.runAll()
    check(saved)
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value == "prod:111")
}

private fun ownerMustBeActivated() {
    resetState()
    login(0, 111L, activated = false)
    UserConfig.selectedAccount = 0
    var saved = true
    StarsLock.save("pw") { saved = it }
    Utilities.runAll()
    check(!saved)
    check(TeleConfig.LOCAL_PASSWORD_HASH.value.isEmpty())
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value.isEmpty())
}

private fun legacyOwnerDeniedUntilPasswordVerified() {
    resetState()
    login(0, 111L)
    login(1, 222L)
    check(savePassword("pw", 0))
    // a password from an older build has no owner
    TeleConfig.LOCAL_PASSWORD_OWNER.value = ""
    UserConfig.selectedAccount = 1

    StarsLock.reset(Activity(), null)
    check(TeleToast.lastSite == "stars-lock-reset-owner")
    check(totalRequests() == 0)
    check(StarsLockUi.cloudAccount == -1)
    check(StarsLockUi.countdownAccount == -1)

    var ok = true
    StarsLock.verify("wrong") { ok = it }
    Utilities.runAll()
    check(!ok)
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value.isEmpty())

    StarsLock.verify("pw") { ok = it }
    Utilities.runAll()
    check(ok)
    // only the verified password binds the legacy lock, to the account that verified it
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value == "prod:222")

    StarsLock.reset(Activity(), null)
    check(ConnectionsManager.getInstance(1).requests == 1)
    check(ConnectionsManager.getInstance(0).requests == 0)
}

private fun unknownAndBackendMismatchedOwnersDenied() {
    resetState()
    login(0, 111L, test = false)
    login(1, 222L, test = true)
    check(savePassword("pw", 0))

    TeleConfig.LOCAL_PASSWORD_OWNER.value = "prod:999"
    check(StarsLock.ownerAccount() == -1)
    StarsLock.reset(Activity(), null)
    check(TeleToast.lastSite == "stars-lock-reset-owner")
    check(totalRequests() == 0)

    // the same user id on another backend is not the owner
    TeleConfig.LOCAL_PASSWORD_OWNER.value = "test:111"
    check(StarsLock.ownerAccount() == -1)
    StarsLock.reset(Activity(), null)
    check(totalRequests() == 0)

    // the test-backend account with that id does own it
    login(0, 111L, test = true)
    check(StarsLock.ownerAccount() == 0)
    StarsLock.reset(Activity(), null)
    check(ConnectionsManager.getInstance(0).requests == 1)
}

private fun countdownUsesOwnerNotSelectedAccount() {
    resetState()
    login(0, 111L)
    login(1, 222L)
    check(savePassword("pw", 0))
    UserConfig.selectedAccount = 1

    StarsLock.reset(Activity(), null)
    ConnectionsManager.getInstance(0).respond(
        TL_account.Password().apply { has_password = false },
        null
    )
    check(StarsLockUi.countdownAccount == 0)
    check(StarsLockUi.countdownSnapshot?.owner == "prod:111")
    check(ConnectionsManager.getInstance(1).requests == 0)
}

private fun staleSnapshotClearRejected() {
    resetState()
    login(0, 111L)
    check(savePassword("old", 0))
    val snapshot = StarsLock.snapshot()
    check(savePassword("new", 0))

    check(!StarsLock.clear(snapshot))
    check(StarsLock.isSet())
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value == "prod:111")

    check(StarsLock.clear(StarsLock.snapshot()))
    check(!StarsLock.isSet())
    check(TeleConfig.LOCAL_PASSWORD_OWNER.value.isEmpty())
}

private fun signedOutOwnerRejectsClear() {
    resetState()
    login(0, 111L)
    check(savePassword("pw", 0))
    val snapshot = StarsLock.snapshot()
    UserConfig.getInstance(0).activated = false
    check(!StarsLock.clear(snapshot))
    check(StarsLock.isSet())
}

private fun replacedLockFailsVerification() {
    resetState()
    login(0, 111L)
    check(savePassword("one", 0))
    val first = TeleConfig.LOCAL_PASSWORD_HASH.value
    check(savePassword("two", 0))
    val second = TeleConfig.LOCAL_PASSWORD_HASH.value
    check(first != second)

    TeleConfig.LOCAL_PASSWORD_HASH.value = first
    var ok = true
    StarsLock.verify("one") { ok = it }
    // the verifier is replaced while its pbkdf2 check is queued
    TeleConfig.LOCAL_PASSWORD_HASH.value = second
    Utilities.runAll()
    check(!ok)
}

private fun resetRejectsLockReplacedDuringRequest() {
    resetState()
    login(0, 111L)
    check(savePassword("one", 0))
    StarsLock.reset(Activity(), null)
    check(ConnectionsManager.getInstance(0).requests == 1)

    // another save replaces the lock while getPassword is in flight
    check(savePassword("two", 0))
    ConnectionsManager.getInstance(0).respond(
        TL_account.Password().apply { has_password = true },
        null
    )
    check(TeleToast.lastSite == "stars-lock-reset-changed")
    check(StarsLockUi.cloudAccount == -1)
    check(StarsLockUi.countdownAccount == -1)
    check(StarsLock.isSet())
}

fun main() {
    ownerFollowsSavingAccount()
    saveCapturesOwnerBeforeAsync()
    ownerMustBeActivated()
    legacyOwnerDeniedUntilPasswordVerified()
    unknownAndBackendMismatchedOwnersDenied()
    countdownUsesOwnerNotSelectedAccount()
    staleSnapshotClearRejected()
    signedOutOwnerRejectsClear()
    replacedLockFailsVerification()
    resetRejectsLockReplacedDuringRequest()
    println("PASS: StarsLock owner binding, legacy/unknown denial, backend identity, stale reset rejection")
}
'''

for name, text in sources.items():
    (here/name).write_text(text, encoding='utf-8')

product = root/'Telegram/TMessagesProj/src/main/java/tele/helpers/StarsLock.kt'
java = args.java
out = here/'test.jar'
inputs = [str(here/name) for name in sources] + [str(product)]
subprocess.run(
    [java, '-cp', os.pathsep.join(map(str, cp)),
     'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
     '-no-stdlib', '-no-reflect', '-classpath', str(cp[1]), '-d', str(out)] + inputs,
    check=True
)
subprocess.run([java, '-cp', os.pathsep.join([str(out), str(cp[1])]), 'regression.TestKt'], check=True)
print('PASS: StarsLock owner policy')
