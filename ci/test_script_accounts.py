"""Compile account-scoped Kotlin helpers against focused stubs, not Android/JNI.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache. Native grant checks below are source contracts only.
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
temporary = tempfile.TemporaryDirectory(prefix='tele-script-accounts-') if args.output is None else None
here=args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache=args.cache
def jar(g,a,v): return next((cache/g/a/v).glob('*/'+a+'-'+v+'.jar'))
cp=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]+[jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
sources={
'Json.kt':'''package org.json
class JSONArray
class JSONObject {
 val data=mutableMapOf<String,Any?>()
 constructor()
 constructor(text:String)
 fun put(k:String,v:Any?):JSONObject { data[k]=v; return this }
 override fun toString()=data.toString()
 companion object { val NULL=Any() }
}
''',
'Handler.kt':'''package android.os
class Looper { companion object { fun getMainLooper()=Looper() } }
class Handler(looper:Looper) { fun post(r:Runnable) {} ; fun postDelayed(r:Runnable,ms:Long) {} }
''',
'Messenger.kt':'''package org.telegram.messenger
object AndroidUtilities {
 val work=mutableListOf<()->Unit>()
 fun runOnUIThread(r:()->Unit) { work.add(r) }
 fun runOnUIThread(r:()->Unit,ms:Long) { work.add(r) }
 fun flush() { while(work.isNotEmpty()) work.removeAt(0)() }
}
class NotificationCenter
class User(val id:Long=1)
object UserObject { fun getUserName(u:User)="user" }
class Document(val id:Long=9)
class MessageObject(val currentAccount:Int) {
 var audioProgress=0.5f
 fun getDocument()=Document()
 fun getDuration()=10
 fun isVoice()=false
 fun isRoundVideo()=false
 fun getMusicTitle()="title"
 fun getMusicAuthor()="author"
 fun getDialogId()=10L
 fun getId()=20
}
class MediaController {
 var message:MessageObject?=null
 var controls=0
 fun getPlayingMessageObject()=message
 fun isPlayingMessage(m:MessageObject)=true
 fun playMessage(m:MessageObject) { controls++ }
 fun pauseMessage(m:MessageObject) { controls++ }
 fun cleanup() { controls++ }
 fun playNextMessage() { controls++ }
 fun playPreviousMessage() { controls++ }
 companion object { val singleton=MediaController(); fun getInstance()=singleton }
}
''',
'VoIP.kt':'''package org.telegram.messenger.voip
import org.telegram.messenger.User
class VoIPService(val account:Int) {
 var controls=0
 fun getCallState()=STATE_ESTABLISHED
 fun getUser()=User()
 fun isMicMute()=false
 fun isCallingVideo()=false
 fun isOutgoing()=true
 fun acceptIncomingCall() {controls++}
 fun hangUp() {controls++}
 fun setMicMute(a:Boolean,b:Boolean,c:Boolean) {controls++}
 companion object {
 var instance:VoIPService?=null
 fun getSharedInstance()=instance
 const val STATE_WAITING_INCOMING=1
 const val STATE_RINGING=2
 const val STATE_ESTABLISHED=3
 const val STATE_ENDED=4
 }
}
''',
'View.kt':'''package org.telegram.ui.Components
class Parent(val currentAccount:Int)
class Edit(var text:CharSequence="")
class ChatActivityEnterView(val parentFragment:Parent?, val peer:Long) {
 val messageEditText=Edit()
 fun tele_getDialogId()=peer
 fun tele_setComposeText(text:String) {messageEditText.text=text}
}
''',
'Runtime.kt':'''package tele.scripting
import org.json.JSONObject
class ScriptRuntime(val account:Int,val id:String="test") {
 var alive=true
 var dispatches=0
 fun isRunning()=alive
 fun hasComposeHandlers()=true
 fun dispatchCompose(context:JSONObject) {dispatches++}
 fun dispatchCall(id:Int,call:Any) {dispatches++}
 fun dispatchPlayer(id:Int,track:Any) {dispatches++}
}
object ScriptStore { fun addLog(a:Int,id:String,text:String) {} }
''',
'Test.kt':'''package regression
import tele.scripting.*
import org.telegram.messenger.*
import org.telegram.messenger.voip.VoIPService
import org.telegram.ui.Components.*
fun main() {
 val a=ScriptRuntime(0); val b=ScriptRuntime(1)
 val service=VoIPService(1); VoIPService.instance=service
 check(ScriptCalls.current(0)==null)
 check(ScriptCalls.current(1)!=null)
 check(!ScriptCalls.control(a,"hangup"))
 check(service.controls==0)
 check(ScriptCalls.control(b,"hangup"))
 check(service.controls==1)
 b.alive=false
 check(!ScriptCalls.control(b,"mute"))
 b.alive=true
 val player=MediaController.singleton
 player.message=MessageObject(1)
 check(ScriptPlayer.current(0)==null)
 check(ScriptPlayer.current(1)!=null)
 ScriptPlayer.control(a,"pause"); AndroidUtilities.flush()
 check(player.controls==0)
 ScriptPlayer.control(b,"pause"); AndroidUtilities.flush()
 check(player.controls==1)
 ScriptPlayer.control(b,"pause"); b.alive=false; AndroidUtilities.flush()
 check(player.controls==1)
 b.alive=true
 ScriptPlayer.control(b,"pause"); player.message=MessageObject(0); AndroidUtilities.flush()
 check(player.controls==1)
 val view=ChatActivityEnterView(Parent(1),10)
 view.messageEditText.text="secret B"
 ScriptCompose.register(a); ScriptCompose.register(b)
 ScriptCompose.inputChanged(view,10,"secret B")
 check(a.dispatches==0); check(b.dispatches==1)
 check(ScriptCompose.text(0)==null); check(ScriptCompose.text(1)=="secret B")
 check(ScriptCompose.chatId(0)==0L); check(ScriptCompose.chatId(1)==10L)
 ScriptCompose.setText(a,10,"A write"); AndroidUtilities.flush()
 check(view.messageEditText.text=="secret B")
 ScriptCompose.setText(b,10,"B write"); AndroidUtilities.flush()
 check(view.messageEditText.text=="B write")
 check(!ScriptCompose.insert(a," leak"))
 check(ScriptCompose.insert(b," allowed")); AndroidUtilities.flush()
 check(view.messageEditText.text=="B write allowed")
 ScriptCompose.setText(b,10,"stopped"); b.alive=false; AndroidUtilities.flush()
 check(view.messageEditText.text=="B write allowed")
 println("PASS: account-isolated calls/player/compose, queued-action stop and account-switch rechecks")
}
'''}
for name,text in sources.items(): (here/name).write_text(text)
product=root/'Telegram/TMessagesProj/src/main/java/tele/scripting'
files=[str(here/n) for n in sources]+[str(product/n) for n in ['ScriptCalls.kt','ScriptPlayer.kt','ScriptCompose.kt']]
java=args.java
out=here/'test.jar'
subprocess.run([java,'-cp',os.pathsep.join(map(str,cp)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(cp[1]),'-d',str(out),*files],check=True)
subprocess.run([java,'-cp',os.pathsep.join([str(out),str(cp[1])]),'regression.TestKt'],check=True)
runtime=(product/'ScriptRuntime.kt').read_text()
required={
 'call.current': 'allows("calls")', 'call.listen': 'allows("calls")', 'call.control': 'allows("calls")',
 'player.current': 'allows("app")', 'player.listen': 'allows("app")', 'player.control': 'allows("app")',
 'compose.get': 'allows("account.read", "draft")', 'compose.register': 'allows("account.read", "draft")',
 'compose.set': 'allows("account.write", "draft")', 'compose.insert': 'allows("account.write", "draft")',
 'message.cached': 'allows("account.read", "messages")',
 'drop.register': 'allows("interceptDrop")', 'link.register': 'allows("interceptLink")',
 'notification.register': 'allows("interceptNotification")',
 'update.register': 'allows("onUpdate")',
}
for branch,gate in required.items():
 start=runtime.index('"'+branch+'" ->')
 end=runtime.index('\n                "',start+len(branch)+5)
 assert gate in runtime[start:end], (branch, 'native grant gate missing')
scripts=(product/'Scripts.kt').read_text()
assert 'messages["$account:$peerId:${message.id}"]' in scripts
assert 'messages["$account:$peerId:$id"]' in scripts
assert 'MessageObject.getDialogId(message)' in scripts
assert 'bus[key(runtime.account, event)]' in scripts
assert 'it.first === runtime && it.second == callback' in scripts
assert 'for (list in bus.values) list.removeAll { it.first === runtime }' in scripts
print('PASS: native grant/cache/bus source contracts (not runtime security integration)')
