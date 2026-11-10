"""Compile Scripts/ScriptStore against focused stubs and exercise source trust.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache. The real Kotlin files run against in-memory prefs,
a mutable script scanner and counting runtime stubs; no source text is inspected.
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
root=args.root.resolve()
temporary = tempfile.TemporaryDirectory(prefix='tele-script-trust-') if args.output is None else None
here=args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache=args.cache
def jar(g,a,v): return next((cache/g/a/v).glob('*/'+a+'-'+v+'.jar'))
cp=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]+[jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
sources={
'Json.kt':'''package org.json
class JSONObject {
    private val values=linkedMapOf<String,Any?>()
    constructor()
    constructor(text:String)
    fun put(key:String,value:Any?):JSONObject { values[key]=value; return this }
    fun opt(key:String):Any? = values[key]
    fun optString(key:String):String = values[key]?.toString() ?: ""
    fun optInt(key:String):Int = (values[key] as? Number)?.toInt() ?: 0
    fun remove(key:String) { values.remove(key) }
    override fun toString():String=values.toString()
    companion object { val NULL:Any=Any() }
}
class JSONArray {
    private val values=mutableListOf<Any?>()
    constructor()
    constructor(text:String) {
        val body=text.trim().removePrefix("[").removeSuffix("]")
        if(body.isNotBlank()) body.split(",").forEach { values.add(it.trim().trim('\"')) }
    }
    constructor(items:Collection<*>){values.addAll(items)}
    fun put(value:Any?):JSONArray { values.add(value); return this }
    fun length():Int = values.size
    fun optString(index:Int):String = values.getOrNull(index)?.toString() ?: ""
    override fun toString():String=values.toString()
}
''',
'Android.kt':'''package android.content
interface SharedPreferences {
    val all:Map<String,Any?>
    fun getString(key:String,def:String?):String?
    fun getBoolean(key:String,def:Boolean):Boolean
    interface Editor {
        fun putString(key:String,value:String?):Editor
        fun putBoolean(key:String,value:Boolean):Editor
        fun remove(key:String):Editor
        fun clear():Editor
        fun apply()
        fun commit():Boolean
    }
    fun edit():Editor
}
class StubPreferences : SharedPreferences {
    override val all=mutableMapOf<String,Any?>()
    override fun getString(key:String,def:String?):String?=all[key] as? String ?: def
    override fun getBoolean(key:String,def:Boolean):Boolean=all[key] as? Boolean ?: def
    override fun edit():SharedPreferences.Editor = object:SharedPreferences.Editor {
        private val values=mutableMapOf<String,Any?>()
        private val removals=mutableSetOf<String>()
        private var wipe=false
        override fun putString(key:String,value:String?):SharedPreferences.Editor { values[key]=value; removals.remove(key); return this }
        override fun putBoolean(key:String,value:Boolean):SharedPreferences.Editor { values[key]=value; removals.remove(key); return this }
        override fun remove(key:String):SharedPreferences.Editor { values.remove(key); removals.add(key); return this }
        override fun clear():SharedPreferences.Editor { wipe=true; values.clear(); removals.clear(); return this }
        override fun apply()=write()
        override fun commit():Boolean { write(); return true }
        private fun write() {
            if(wipe) all.clear()
            for(key in removals) all.remove(key)
            all.putAll(values)
        }
    }
}
class Context {
    private val files=mutableMapOf<String,StubPreferences>()
    fun getSharedPreferences(name:String,mode:Int):SharedPreferences = files.getOrPut(name){StubPreferences()}
    companion object { const val MODE_PRIVATE=0 }
}
''',
'Net.kt':'''package android.net
class Uri
''',
'Log.kt':'''package android.util
object Log { fun d(tag:String,message:String) {} }
''',
'Telegram.kt':'''package org.telegram.messenger
import android.content.Context
object ApplicationLoader { var applicationContext:Context=Context() }
object FileLog { fun e(error:Throwable) {} }
object MessageObject { fun getDialogId(message: org.telegram.tgnet.TLRPC.Message):Long = 0L }
class UserConfig {
    var isClientActivated=true
    companion object {
        const val MAX_ACCOUNT_COUNT=8
        var selectedAccount=0
        private val accounts=Array(MAX_ACCOUNT_COUNT){UserConfig()}
        fun getInstance(account:Int):UserConfig = accounts[account]
    }
}
object Utilities {
    object globalQueue { fun postRunnable(task:java.lang.Runnable) {} }
}
''',
'Tl.kt':'''package org.telegram.tgnet
class TLRPC {
    open class Update
    class User
    class Chat
    class Peer { @JvmField var channel_id:Long=0 }
    class Message { @JvmField var id:Int=0; @JvmField var peer_id:Peer?=null }
    open class Updates {
        open val users:List<User> = emptyList()
        open val chats:List<Chat> = emptyList()
    }
    class TL_updateShort(@JvmField val update:Update):Updates()
    class TL_updates(@JvmField val updates:MutableList<Update>):Updates()
    class TL_updatesCombined(@JvmField val updates:MutableList<Update>):Updates()
    class TL_updateShortMessage:Updates()
    class TL_updateShortChatMessage:Updates()
}
''',
'TlUpdate.kt':'''package org.telegram.tgnet.tl
import org.telegram.tgnet.TLRPC
class TL_update {
    class TL_updateNewMessage(@JvmField val message:TLRPC.Message):TLRPC.Update()
    class TL_updateNewChannelMessage(@JvmField val message:TLRPC.Message):TLRPC.Update()
    class TL_updateEditMessage(@JvmField val message:TLRPC.Message):TLRPC.Update()
    class TL_updateEditChannelMessage(@JvmField val message:TLRPC.Message):TLRPC.Update()
    class TL_updateDeleteChannelMessages(@JvmField val messages:List<Int>,@JvmField val channel_id:Long):TLRPC.Update()
    class TL_updateDeleteMessages(@JvmField val messages:List<Int>):TLRPC.Update()
}
''',
'Config.kt':'''package tele
object TeleConfig {
    class Item(var value:Boolean)
    val SCRIPTING=Item(true)
}
''',
'Accounts.kt':'''package tele.helpers
object TeleAccounts {
    var initialized=true
    private val generations=LongArray(8)
    fun ensure(account:Int):Boolean = initialized
    fun generation(account:Int):Long = generations[account]
    fun isCurrent(account:Int,generation:Long):Boolean = initialized && generations[account]==generation
}
''',
'ScriptRuntime.kt':'''package tele.scripting
import org.json.JSONArray
import org.json.JSONObject
import org.telegram.tgnet.TLRPC
class Decoration
class ScriptMenuItem
class ScriptRuntime(@JvmField val account:Int,@JvmField val id:String,@JvmField val script:ScriptFile,@JvmField val grants:List<String>) {
    companion object { var started=0; var stopped=0 }
    @Volatile var running=false
    fun start() { running=true; started++ }
    fun stop() { running=false; stopped++ }
    fun isRunning():Boolean = running
    fun notifyUpdate(update:JSONObject) {}
    fun notify(kind:String,update:JSONObject,peers:JSONObject) {}
    fun decorationFor(message:TLRPC.Message,text:String?,editDate:Int,callback:(Decoration?)->Unit):Boolean = true
    fun dispatch(callback:Int,kind:String,args:JSONArray) {}
}
''',
'ScriptEnv.kt':'''package tele.scripting
import org.json.JSONObject
import org.telegram.tgnet.TLRPC
class ScriptFile(
    @JvmField val id:String,
    @JvmField val file:java.io.File?,
    @JvmField val uri:android.net.Uri?,
    @JvmField val fileName:String,
    @JvmField val name:String,
    @JvmField val grants:List<String>,
    @JvmField val source:String,
    @JvmField val error:String?
)
class ScriptException(val errorCode:String,message:String,val extra:JSONObject?=null):Exception(message)
object ScriptScanner {
    var files:List<ScriptFile> = emptyList()
    val deleted=mutableListOf<String>()
    fun scan():List<ScriptFile> = files
    fun delete(id:String):Boolean { deleted.add(id); return true }
}
object ScriptFolder { fun display():String = "/scripts" }
object ScriptTypes { var writes=0; fun write() { writes++ } }
object ScriptSources { fun remove(name:String) {} }
object ScriptTl {
    fun json(value:Any?):JSONObject = JSONObject()
    fun messageJson(message:TLRPC.Message?):JSONObject? = null
}
object ScriptMenu {
    fun list(account:Int,chatKind:String?=null):List<ScriptMenuItem> = emptyList()
    fun invoke(account:Int,script:String,callback:Int,context:JSONObject):Boolean = true
}
''',
'Test.kt':'''package regression
import org.telegram.messenger.ApplicationLoader
import tele.TeleConfig
import tele.scripting.*
fun prefs(account:Int)=ApplicationLoader.applicationContext.getSharedPreferences("tele_scripts_$account",android.content.Context.MODE_PRIVATE)
fun source(id:String,text:String)=ScriptFile(id,java.io.File("/scripts/"+id),null,id,id,listOf("notify"),text,null)
fun enable(account:Int) {
    Scripts.approve(account,"a.js",listOf("notify"))
    Scripts.setEnabled(account,"a.js",true)
}
fun cleared(account:Int)=!ScriptStore.enabled(account,"a.js") && ScriptStore.grants(account,"a.js").isEmpty()
fun main() {
    TeleConfig.SCRIPTING.value=true
    ScriptScanner.files=listOf(source("a.js","one"))
    Scripts.refresh(0)
    check(ScriptStore.fingerprint(0,"a.js")!=null) { "refresh did not bind the source" }
    enable(0)
    enable(1)
    check(Scripts.runtime(0,"a.js")?.running==true) { "approved script did not start" }
    Scripts.revokeEverywhere("a.js")
    for(account in 0..1) {
        check(cleared(account)) { "identical import kept trust in slot $account" }
        check(ScriptStore.fingerprint(account,"a.js")==null) { "identical import kept the binding in slot $account" }
        check(Scripts.runtime(account,"a.js")==null) { "identical import kept the runtime in slot $account" }
    }
    Scripts.refresh(0)
    check(!ScriptStore.enabled(0,"a.js")) { "refresh resurrected revoked trust" }
    enable(0)
    Scripts.refresh(0)
    check(ScriptStore.enabled(0,"a.js")) { "unchanged source lost its trust" }
    check(ScriptStore.grants(0,"a.js")==listOf("notify")) { "unchanged source lost its grants" }
    ScriptScanner.files=listOf(source("a.js","two"))
    Scripts.refresh(0)
    check(cleared(0)) { "changed source kept its trust" }
    check(ScriptStore.fingerprint(0,"a.js")!=null) { "changed source was not rebound" }
    enable(0)
    ScriptStore.setFingerprint(0,"a.js",null)
    Scripts.refresh(0)
    check(cleared(0)) { "legacy unbound source kept its trust" }
    Scripts.setEnabled(0,"ghost",true)
    check(!ScriptStore.enabled(0,"ghost")) { "unknown id was enabled" }
    Scripts.approve(0,"ghost",listOf("notify"))
    check(ScriptStore.grants(0,"ghost").isEmpty()) { "unknown id got grants" }
    check(Scripts.runtime(0,"ghost")==null) { "unknown id got a runtime" }
    ScriptScanner.files=listOf(source("a.js","three"))
    Scripts.refresh(0)
    enable(0)
    enable(1)
    ScriptScanner.deleted.clear()
    check(Scripts.delete(0,"a.js")) { "delete failed" }
    for(account in 0..1) check(cleared(account)) { "delete kept trust in slot $account" }
    check(ScriptScanner.deleted==listOf("a.js")) { "delete did not remove the source" }
    ScriptScanner.files=listOf(source("a.js","four"))
    Scripts.refresh(0)
    enable(0)
    enable(1)
    val writes=ScriptTypes.writes
    Scripts.folderChanged()
    check(ScriptTypes.writes==writes+1) { "folder change did not rewrite the typings" }
    for(account in 0..1) check(cleared(account)) { "folder change kept trust in slot $account" }
    ScriptScanner.files=listOf(source("a.js","five"))
    Scripts.refresh(0)
    enable(0)
    ScriptStore.addLog(0,"a.js","hello")
    check(prefs(0).all.isNotEmpty()) { "logout fixture is empty" }
    val stopped=ScriptRuntime.stopped
    Scripts.onLogout(0)
    check(ScriptRuntime.stopped>stopped) { "logout did not stop the runtime" }
    check(prefs(0).all.isEmpty()) { "logout kept script prefs" }
    check(Scripts.runtime(0,"a.js")==null) { "logout kept the runtime" }
    println("PASS: source fingerprint binding, replacement revoke, folder/delete resets and logout cleanup")
}
'''}
for name,text in sources.items(): (here/name).write_text(text)
product=root/'Telegram/TMessagesProj/src/main/java/tele/scripting'
files=[str(here/n) for n in sources]+[str(product/n) for n in ['Scripts.kt','ScriptStore.kt','ScriptGrants.kt']]
java=args.java
out=here/'test.jar'
subprocess.run([java,'-cp',os.pathsep.join(map(str,cp)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(cp[1]),'-d',str(out),*files],check=True)
subprocess.run([java,'-cp',os.pathsep.join([str(out),str(cp[1])]),'regression.TestKt'],check=True)
