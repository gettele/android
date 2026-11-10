"""Compile TeleAccounts against focused stubs and exercise slot ownership cleanup.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache. The real Kotlin file runs against in-memory prefs and
counting helper stubs; no source text is inspected.
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
temporary = tempfile.TemporaryDirectory(prefix='tele-account-ownership-') if args.output is None else None
here=args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache=args.cache
def jar(g,a,v): return next((cache/g/a/v).glob('*/'+a+'-'+v+'.jar'))
cp=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]+[jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
sources={
'Android.kt':'''package android.content
interface SharedPreferences {
    fun getString(key:String,def:String?):String?
    interface Editor {
        fun putString(key:String,value:String?):Editor
        fun commit():Boolean
    }
    fun edit():Editor
}
class StubPreferences : SharedPreferences {
    val values=mutableMapOf<String,String?>()
    var failNextCommit=false
    override fun getString(key:String,def:String?)=if(values.containsKey(key)) values[key] else def
    override fun edit():SharedPreferences.Editor=object:SharedPreferences.Editor {
        private val pending=mutableMapOf<String,String?>()
        override fun putString(key:String,value:String?):SharedPreferences.Editor { pending[key]=value; return this }
        override fun commit():Boolean {
            if(this@StubPreferences.failNextCommit) { this@StubPreferences.failNextCommit=false; return false }
            values.putAll(pending)
            return true
        }
    }
}
class Context {
    val preferences=StubPreferences()
    fun getSharedPreferences(name:String,mode:Int):SharedPreferences=preferences
    companion object { const val MODE_PRIVATE=0 }
}
''',
'Telegram.kt':'''package org.telegram.messenger
import android.content.Context
object ApplicationLoader { var applicationContext:Context=Context() }
class UserConfig private constructor() {
    var clientUserId:Long=0
    var storedUserId:Long=0
    var loads=0
    fun loadConfig() { loads++; clientUserId=storedUserId }
    companion object {
        const val MAX_ACCOUNT_COUNT=3
        private val accounts=Array(MAX_ACCOUNT_COUNT){UserConfig()}
        fun getInstance(account:Int):UserConfig=accounts[account]
    }
}
''',
'Connections.kt':'''package org.telegram.tgnet
import org.telegram.messenger.UserConfig
class ConnectionsManager {
    var isTestBackend=false
    companion object {
        private val accounts=Array(UserConfig.MAX_ACCOUNT_COUNT){ConnectionsManager()}
        fun getInstance(account:Int):ConnectionsManager=accounts[account]
    }
}
''',
'Scripts.kt':'''package tele.scripting
object Scripts { fun onLogout(account:Int) { tele.helpers.Calls.add("Scripts",account) } }
''',
'Db.kt':'''package tele.db
object TeleDatabaseHelper {
    fun clearAccount(account:Int) { tele.helpers.Calls.add("db",account) }
    fun adoptAccount(account:Int) {}
}
''',
'Helpers.kt':'''package tele.helpers
object Calls {
    val events=mutableListOf<String>()
    fun add(label:String,account:Int) { events.add(label+":"+account) }
    fun reset()=events.clear()
    fun count(label:String,account:Int)=events.count { it==label+":"+account }
    fun size()=events.size
    fun labels(account:Int)=events.filter { it.endsWith(":"+account) }.map { it.substringBeforeLast(':') }
}
object LastSeenPeek { fun onLogout(account:Int) { Calls.add("LastSeenPeek",account) } }
object PrivacyRules { fun onAccountRemoved(account:Int) { Calls.add("PrivacyRules",account) } }
object DeletedMessages { fun onLogout(account:Int) { Calls.add("DeletedMessages",account) } }
object DeletedChats { fun onLogout(account:Int) { Calls.add("DeletedChats",account) } }
object RecoveredPosts { fun onLogout(account:Int) { Calls.add("RecoveredPosts",account) } }
object Bookmarks { fun onLogout(account:Int) { Calls.add("Bookmarks",account) } }
object ReturnPoint { fun onLogout(account:Int) { Calls.add("ReturnPoint",account) } }
object DockedMedia { fun onLogout(account:Int) { Calls.add("DockedMedia",account) } }
object SavedDrafts { fun onLogout(account:Int) { Calls.add("SavedDrafts",account) } }
object Aliases { fun onLogout(account:Int) { Calls.add("Aliases",account) } }
object FolderIcons { fun onLogout(account:Int) { Calls.add("FolderIcons",account) } }
object ObservedActivity { fun onLogout(account:Int) { Calls.add("ObservedActivity",account) } }
object ReactionStrip { fun onLogout(account:Int) { Calls.add("ReactionStrip",account) } }
object TeleChat { fun onLogout(account:Int) { Calls.add("TeleChat",account) } }
object TeleNotices { fun onLogout(account:Int) { Calls.add("TeleNotices",account) } }
object PastLimit { fun onLogout(account:Int) { Calls.add("PastLimit",account) } }
object LocalBackgrounds { fun onLogout(account:Int) { Calls.add("LocalBackgrounds",account) } }
object OnlineNotify { fun onLogout(account:Int) { Calls.add("OnlineNotify",account) } }
object GhostPending { fun onLogout(account:Int) { Calls.add("GhostPending",account) } }
object TeleMtp { fun onLogout(account:Int) { Calls.add("TeleMtp",account) } }
object LocalPins { fun onLogout(account:Int) { Calls.add("LocalPins",account) } }
object TeleSilent { fun onLogout(account:Int) { Calls.add("TeleSilent",account) } }
object TeleServerNotices { fun onLogout(account:Int) { Calls.add("TeleServerNotices",account) } }
''',
'Test.kt':'''package regression
import org.telegram.messenger.*
import tele.helpers.*
val HELPERS=listOf(
    "Scripts","LastSeenPeek","PrivacyRules","DeletedMessages","DeletedChats",
    "RecoveredPosts","Bookmarks","ReturnPoint","DockedMedia","SavedDrafts","Aliases","FolderIcons",
    "ObservedActivity","ReactionStrip","TeleChat","TeleNotices","PastLimit",
    "LocalBackgrounds","OnlineNotify","GhostPending","TeleMtp")
fun checkCleared(account:Int,label:String) {
    val labels=Calls.labels(account)
    for(entry in HELPERS+listOf("db")) check(entry in labels) { label+": "+entry+" not called" }
    check(labels.size==labels.toSet().size) { label+": duplicate cleanup calls "+Calls.events }
}
fun main() {
    val prefs=ApplicationLoader.applicationContext.preferences
    UserConfig.getInstance(0).storedUserId=1L
    UserConfig.getInstance(2).storedUserId=2L
    prefs.values["1"]="prod:5"
    prefs.values["2"]="prod:2"
    Calls.reset()
    TeleAccounts.init()
    check((0 until UserConfig.MAX_ACCOUNT_COUNT).sumOf { UserConfig.getInstance(it).loads }==UserConfig.MAX_ACCOUNT_COUNT) { "init skipped loadConfig" }
    check(UserConfig.getInstance(0).clientUserId==1L && UserConfig.getInstance(2).clientUserId==2L)
    // legacy active slot: trust reset only, archives and generation preserved
    check(TeleAccounts.generation(0)==0L)
    check(Calls.labels(0)==listOf("Scripts")) { "legacy slot leaked cleanup: "+Calls.events }
    check(prefs.values["0"]=="prod:1")
    // inactive slot: full cleanup once
    check(TeleAccounts.generation(1)==1L)
    checkCleared(1,"inactive init")
    check(prefs.values["1"]=="")
    // bound neighbour untouched
    check(TeleAccounts.generation(2)==0L)
    check(prefs.values["2"]=="prod:2")
    check(Calls.labels(2).isEmpty())
    check(TeleAccounts.isCurrent(2,0L))
    // different owner logs into slot 0: old archives cleared before success
    Calls.reset()
    UserConfig.getInstance(0).clientUserId=2L
    check(TeleAccounts.ensure(0))
    check(TeleAccounts.generation(0)==1L)
    checkCleared(0,"owner switch")
    check(prefs.values["0"]=="prod:2")
    check(TeleAccounts.isCurrent(0,1L))
    check(!TeleAccounts.isCurrent(0,0L))
    check(TeleAccounts.generation(2)==0L)
    check(prefs.values["2"]=="prod:2")
    check(Calls.labels(2).isEmpty())
    // failed owner commit: cleanup happens, success and ownership are withheld
    Calls.reset()
    UserConfig.getInstance(0).clientUserId=3L
    prefs.failNextCommit=true
    check(!TeleAccounts.ensure(0))
    check(TeleAccounts.generation(0)==2L)
    checkCleared(0,"failed owner write")
    check(prefs.values["0"]=="prod:2")
    check(!TeleAccounts.isCurrent(0,2L))
    // retry persists the new owner and marks the slot current
    Calls.reset()
    check(TeleAccounts.ensure(0))
    check(TeleAccounts.generation(0)==3L)
    checkCleared(0,"owner retry")
    check(prefs.values["0"]=="prod:3")
    check(TeleAccounts.isCurrent(0,3L))
    // logout: one cleanup, generation invalidation, old callbacks rejected
    Calls.reset()
    val oldGeneration=TeleAccounts.generation(2)
    TeleAccounts.onLogout(2)
    check(TeleAccounts.generation(2)==oldGeneration+1)
    checkCleared(2,"logout")
    check(prefs.values["2"]=="")
    check(!TeleAccounts.isCurrent(2,oldGeneration))
    check(!TeleAccounts.isCurrent(2,oldGeneration+1))
    // neighbour slot untouched by logout
    check(TeleAccounts.generation(0)==3L)
    check(prefs.values["0"]=="prod:3")
    check(Calls.labels(0).isEmpty())
    // identity drift rejects a callback holding the current generation
    val boundGeneration=TeleAccounts.generation(0)
    UserConfig.getInstance(0).clientUserId=4L
    check(!TeleAccounts.isCurrent(0,boundGeneration))
    // init is idempotent and never re-clears bound slots
    Calls.reset()
    TeleAccounts.init()
    check(Calls.size()==0) { "repeated init cleaned slots: "+Calls.events }
    check(TeleAccounts.generation(0)==3L)
    check(TeleAccounts.generation(2)==oldGeneration+1)
    println("PASS: slot ownership init/switch/logout cleanup, legacy trust reset and generation guards")
}
'''}
for name,text in sources.items(): (here/name).write_text(text)
product=root/'Telegram/TMessagesProj/src/main/java/tele/helpers'
files=[str(here/n) for n in sources]+[str(product/'TeleAccounts.kt')]
java=args.java
out=here/'test.jar'
subprocess.run([java,'-cp',os.pathsep.join(map(str,cp)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(cp[1]),'-d',str(out),*files],check=True)
subprocess.run([java,'-cp',os.pathsep.join([str(out),str(cp[1])]),'regression.TestKt'],check=True)
