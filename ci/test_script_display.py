#!/usr/bin/env python3
"""Compile the CURRENT product ScriptDisplay.kt with isolated Kotlin stubs.
Only writes under scratch/script-display-regression; reads compiler dependencies from Gradle caches.
Run: python3 main/ci/test_script_display.py
"""
from pathlib import Path
import subprocess
import os

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "scratch/script-display-regression"
HERE.mkdir(parents=True, exist_ok=True)
CACHE = Path.home() / '.gradle/caches/modules-2/files-2.1'

def jar(group, artifact, version):
    matches = list((CACHE/group/artifact/version).glob('*/'+artifact+'-'+version+'.jar'))
    if not matches:
        raise SystemExit('Missing cached dependency: '+artifact+' '+version)
    return matches[0]

compiler = [jar('org.jetbrains.kotlin', a, '2.2.21') for a in ['kotlin-compiler-embeddable', 'kotlin-stdlib', 'kotlin-script-runtime', 'kotlin-reflect']]
compiler += [jar('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm', '1.8.0'), jar('org.jetbrains', 'annotations', '13.0')]
stdlib = compiler[1]
sources = {
'AndroidText.kt': '''package android.text
class SpannableStringBuilder(private val text: String): CharSequence {
 override val length get() = text.length
 override fun get(index: Int) = text[index]
 override fun subSequence(startIndex: Int, endIndex: Int): CharSequence = text.subSequence(startIndex,endIndex)
 override fun toString() = text
}
''',
'Json.kt': '''package org.json
class JSONObject {
 private val data = HashMap<String,Any?>()
 fun put(key: String, value: Any?): JSONObject { data[key]=value; return this }
 fun opt(key: String): Any? = data[key]
 fun optString(key: String, fallback: String = "") = data[key] as? String ?: fallback
 fun optDouble(key: String, fallback: Double) = (data[key] as? Number)?.toDouble() ?: fallback
 fun optBoolean(key: String, fallback: Boolean) = data[key] as? Boolean ?: fallback
 companion object { val NULL = Any() }
}
''',
'Config.kt': '''package tele
class BoolItem(var value: Boolean)
object TeleConfig { val SCRIPTING = BoolItem(true) }
''',
'Scripts.kt': '''package tele.scripting
import org.telegram.messenger.MessageObject
object Scripts {
 var decorateCalls = 0
 var decorate: (Int,MessageObject)->Decoration? = { _,_ -> null }
 fun decorateSync(account: Int, message: MessageObject): Decoration? { decorateCalls++; return decorate(account,message) }
}
''',
'Messenger.kt': '''package org.telegram.messenger
import tele.TeleConfig
import tele.scripting.ScriptDisplay
class Owner(var message: String?, var edit_date: Int = 0)
class MessageObject(val currentAccount: Int, private val peer: Long, private val id: Int, initial: String) {
 var messageOwner = Owner(initial)
 var messageText: CharSequence = initial
 var translated = false
 var summarized = false
 var forceUpdate = false
 var layoutCalls = 0
 var resetCalls = 0
 var failLayout = false
 var entities = listOf("stock-entity")
 fun getDialogId() = peer
 fun getId() = id
 // Mirror the exact generateLayout guard in MessageObject.java; full layout is not emulated.
 fun generateLayout(fromUser: Any?) { layoutCalls++; if(failLayout) error("test layout failure"); if (TeleConfig.SCRIPTING.value) ScriptDisplay.apply(currentAccount,this) }
 fun resetLayout() { resetCalls++ }
 // Mirror MessageObject.getEntities: the real ScriptDisplay marker is under test.
 fun getEffectiveEntities(): List<String> = if(TeleConfig.SCRIPTING.value && ScriptDisplay.hasReplacement(this)) emptyList() else entities
}
object FileLog { val errors = ArrayList<Throwable>(); fun e(error: Throwable) { errors.add(error) } }
object AndroidUtilities { fun runOnUIThread(action: ()->Unit) = action() }
class NotificationCenter {
 data class Event(val account: Int, val id: Int, val peer: Long, val updated: List<MessageObject>)
 private var account: Int = 0
 fun postNotificationName(id: Int, peer: Long, updated: ArrayList<MessageObject>) { events.add(Event(account,id,peer,updated.toList())) }
 companion object {
  const val replaceMessagesObjects = 1
  val events = ArrayList<Event>()
  fun getInstance(account: Int) = NotificationCenter().also { it.account = account }
 }
}
''',
'Test.kt': '''package regression
import org.json.JSONObject
import org.telegram.messenger.MessageObject
import org.telegram.messenger.NotificationCenter
import tele.TeleConfig
import tele.scripting.ScriptDisplay
import tele.scripting.Scripts
private var assertions = 0
private fun checkEq(expected: Any?, actual: Any?, description: String) {
 assertions++
 check(expected == actual) { "$description: expected <$expected>, got <$actual>" }
}
private fun text(s: String) = JSONObject().put("text",s)
fun main() {
 val message = MessageObject(0, 100, 1, "original")
 val otherAccount = MessageObject(1, 100, 1, "other-account")
 val otherPeer = MessageObject(0, 200, 1, "other-peer")
 for(m in listOf(message,otherAccount,otherPeer)) m.generateLayout(null)
 ScriptDisplay.set(0,"translate",100,1,text("translation"))
 checkEq("translation",message.messageText.toString(),"set refreshes loaded object")
 checkEq("original",message.messageOwner.message,"source TL text remains untouched")
 checkEq("original",ScriptDisplay.editingText(message).toString(),"editor receives server text rather than decoration")
 checkEq(true,ScriptDisplay.hasReplacement(message),"replacement marker set")
 checkEq(emptyList<String>(),message.getEffectiveEntities(),"replacement suppresses old entity offsets")
 checkEq("other-account",otherAccount.messageText.toString(),"account filtering")
 checkEq("other-peer",otherPeer.messageText.toString(),"peer filtering")
 checkEq(0,otherAccount.resetCalls,"other account not invalidated")
 checkEq(0,otherPeer.resetCalls,"other peer not invalidated")
 checkEq(100L,NotificationCenter.events.last().peer,"correct peer notification")
 checkEq(listOf(message),NotificationCenter.events.last().updated,"correct objects notified")
 repeat(20) {
  message.generateLayout(null)
  checkEq("translation",message.messageText.toString(),"repeat layout replacement")
 }
 ScriptDisplay.set(0,"translate",100,1,null)
 checkEq("original",message.messageText.toString(),"clear restores original after repeated layouts")
 checkEq(false,ScriptDisplay.hasReplacement(message),"marker removed")
 checkEq(listOf("stock-entity"),message.getEffectiveEntities(),"stock entities restored")
 ScriptDisplay.set(0,"translate",100,1,text("second"))
 ScriptDisplay.set(0,"translate",100,1,text("third"))
 ScriptDisplay.clearScript(0,"translate")
 checkEq("original",message.messageText.toString(),"repeated set does not capture previous replacement")
 ScriptDisplay.set(0,"translate",100,1,text("translated-before-edit"))
 message.messageOwner.message="edited server text"
 message.messageOwner.edit_date=1
 message.messageText="edited stock layout"
 ScriptDisplay.set(0,"translate",100,1,null)
 checkEq("edited stock layout",message.messageText.toString(),"clear does not restore stale source after edit")
 ScriptDisplay.set(0,"translate",100,1,text("translated-edited"))
 ScriptDisplay.set(0,"translate",100,1,null)
 checkEq("edited stock layout",message.messageText.toString(),"fresh source remains restorable")
 ScriptDisplay.set(0,"translate",100,1,text("pre-stock-translation"))
 message.translated=true
 message.messageText="stock translated text"
 ScriptDisplay.set(0,"translate",100,1,null)
 checkEq("stock translated text",message.messageText.toString(),"stock translation change not overwritten")
 ScriptDisplay.set(0,"translate",100,1,text("master-on"))
 TeleConfig.SCRIPTING.value=false
 ScriptDisplay.clearScript(0,"translate")
 checkEq("stock translated text",message.messageText.toString(),"master off plus clearScript restores text")
 checkEq(false,ScriptDisplay.hasReplacement(message),"master off marker removed")
 val calls=Scripts.decorateCalls
 ScriptDisplay.apply(0,message)
 checkEq(calls,Scripts.decorateCalls,"master off does not invoke JS")
 TeleConfig.SCRIPTING.value=true
 ScriptDisplay.set(0,"translate",100,1,text("script-restart"))
 ScriptDisplay.clearScript(1,"translate")
 checkEq("script-restart",message.messageText.toString(),"clearScript account filtering")
 ScriptDisplay.clearScript(0,"translate")
 checkEq("stock translated text",message.messageText.toString(),"script stop/source reload restores")
 ScriptDisplay.set(0,"translate",100,1,JSONObject().put("badge","tag"))
 checkEq(false,ScriptDisplay.hasReplacement(message),"badge-only decoration does not suppress entities")
 ScriptDisplay.clearScript(0,"translate")
 val callbackMessage=MessageObject(2,300,9,"callback-source")
 Scripts.decorate={ account, _ -> if(account==2) ScriptDisplay.parse(text("callback-text")) else null }
 callbackMessage.generateLayout(null)
 checkEq("callback-text",callbackMessage.messageText.toString(),"callback decoration")
 Scripts.decorate={ _,_ -> null }
 ScriptDisplay.clearScript(2,"callback")
 checkEq("callback-source",callbackMessage.messageText.toString(),"callback cache invalidated on stop")
 val firstToken=ScriptDisplay.set(0,"ownerA",100,1,text("owner-a"))
 val secondToken=ScriptDisplay.set(0,"ownerB",100,1,text("owner-b"))
 ScriptDisplay.set(0,"ownerA",100,1,null,firstToken)
 checkEq("owner-b",message.messageText.toString(),"wrong owner disposer ignored")
 ScriptDisplay.set(0,"ownerB",100,1,null,firstToken)
 checkEq("owner-b",message.messageText.toString(),"wrong token ignored")
 val thirdToken=ScriptDisplay.set(0,"ownerB",100,1,text("owner-b-new"))
 ScriptDisplay.set(0,"ownerB",100,1,null,secondToken)
 checkEq("owner-b-new",message.messageText.toString(),"old same-owner disposer ignored")
 ScriptDisplay.set(0,"ownerB",100,1,null,thirdToken)
 checkEq("stock translated text",message.messageText.toString(),"current token restores")
 val explicitEdit=MessageObject(3,400,1,"before-edit")
 explicitEdit.generateLayout(null)
 ScriptDisplay.set(3,"owner",400,1,text("explicit-before-edit"))
 explicitEdit.messageOwner.message="server-edit"
 explicitEdit.messageOwner.edit_date=2
 explicitEdit.messageText="server-edit"
 explicitEdit.generateLayout(null)
 checkEq("server-edit",explicitEdit.messageText.toString(),"source edit invalidates explicit decoration")
 checkEq(false,ScriptDisplay.hasReplacement(explicitEdit),"edited source clears replacement marker")
 val cached=MessageObject(4,500,2,"cache-source")
 Scripts.decorate={ account, m -> if(account==4) ScriptDisplay.parse(text("callback:"+m.messageOwner.message)) else null }
 cached.generateLayout(null)
 checkEq("callback:cache-source",cached.messageText.toString(),"callback cached initial text")
 val callsBeforeCacheHit=Scripts.decorateCalls
 cached.generateLayout(null)
 checkEq(callsBeforeCacheHit,Scripts.decorateCalls,"callback cache hit skips JS")
 cached.messageOwner.message="cache-edit"
 cached.messageOwner.edit_date=3
 cached.messageText="cache-edit"
 cached.generateLayout(null)
 checkEq("callback:cache-edit",cached.messageText.toString(),"source edit invalidates callback cache")
 checkEq(callsBeforeCacheHit+1,Scripts.decorateCalls,"source edit reruns decorator")
 Scripts.decorate={ _,_ -> null }
 ScriptDisplay.invalidate(4)
 checkEq("cache-edit",cached.messageText.toString(),"unregister invalidation refresh restores original")
 val nullCalls=Scripts.decorateCalls
 cached.generateLayout(null)
 cached.generateLayout(null)
 checkEq(nullCalls,Scripts.decorateCalls,"null callback result cached without repeat JS")
 Scripts.decorate={ account,_ -> if(account==4) ScriptDisplay.parse(text("registered")) else null }
 ScriptDisplay.invalidate(4)
 checkEq("registered",cached.messageText.toString(),"register invalidation refreshes visible objects")
 Scripts.decorate={ _,_ -> null }
 ScriptDisplay.invalidate(4)
 checkEq("cache-edit",cached.messageText.toString(),"unregister refreshes visible objects")
 ScriptDisplay.set(0,"translate",100,1,text("clear-me"))
 ScriptDisplay.set(1,"translate",100,1,text("clear-other-account"))
 ScriptDisplay.clear()
 checkEq("stock translated text",message.messageText.toString(),"clear restores loaded text")
 checkEq("other-account",otherAccount.messageText.toString(),"clear restores all accounts")
 checkEq(false,ScriptDisplay.hasReplacement(message),"clear removes marker")
 ScriptDisplay.set(0,"translate",100,1,text("before-text-change"))
 ScriptDisplay.onTextChanged(message)
 message.messageText="new-stock-text-same-source"
 ScriptDisplay.set(0,"translate",100,1,null)
 checkEq("new-stock-text-same-source",message.messageText.toString(),"stock text hook discards old original")
 checkEq(0,org.telegram.messenger.FileLog.errors.size,"no rendering errors caught")
 ScriptDisplay.set(5,"unloaded",600,3,text("first-bind"))
 val unloaded=MessageObject(5,600,3,"unloaded-source")
 unloaded.generateLayout(null)
 checkEq("first-bind",unloaded.messageText.toString(),"unloaded explicit entry binds on first render")
 unloaded.messageOwner.message="first-bind-edited"
 unloaded.messageOwner.edit_date=1
 unloaded.messageText="first-bind-edited"
 unloaded.generateLayout(null)
 checkEq("first-bind-edited",unloaded.messageText.toString(),"first-bound explicit entry expires on edit")
 val failing=MessageObject(6,700,4,"failing-source")
 failing.generateLayout(null)
 failing.failLayout=true
 ScriptDisplay.set(6,"failing",700,4,text("failing-replacement"))
 checkEq(1,org.telegram.messenger.FileLog.errors.size,"rendering exception is contained and logged")
 checkEq(0,failing.resetCalls,"failed rendering not reported as updated")
 println("PASS: $assertions assertions against current ScriptDisplay.kt")
}
'''
}
for name, content in sources.items():
    (HERE/name).write_text(content)
output = HERE/'classes'
output.mkdir(exist_ok=True)
product = ROOT/'Telegram/TMessagesProj/src/main/java/tele/scripting/ScriptDisplay.kt'
cmd = ['java', '-cp', os.pathsep.join(map(str,compiler)), 'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler', '-no-stdlib', '-no-reflect', '-classpath', str(stdlib), '-d', str(output), str(product)]
cmd.extend(str(HERE/name) for name in sources)
subprocess.run(cmd,check=True,cwd=HERE)
subprocess.run(['java','-cp',os.pathsep.join([str(output),str(stdlib)]),'regression.TestKt'],check=True,cwd=HERE)
