"""Compile script interceptor Kotlin helpers against focused stubs, not Android/JNI.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache. Covers notification/link interceptors and ScriptReplies:
account isolation, grant-scoped verdicts, owner/token rejection, timeout and stop cleanup.
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
temporary = tempfile.TemporaryDirectory(prefix='tele-script-interceptors-') if args.output is None else None
here=args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache=args.cache
def jar(g,a,v): return next((cache/g/a/v).glob('*/'+a+'-'+v+'.jar'))
cp=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]+[jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
sources={
'Json.kt':'''package org.json
class JSONObject {
 val data=mutableMapOf<String,Any?>()
 fun put(k:String,v:Any?):JSONObject { data[k]=v; return this }
 fun optString(k:String)=data[k] as? String ?: ""
 fun optBoolean(k:String)=data[k] as? Boolean ?: false
 fun optInt(k:String)=(data[k] as? Number)?.toInt() ?: 0
 fun optLong(k:String)=(data[k] as? Number)?.toLong() ?: 0L
 fun has(k:String)=data.containsKey(k)
 companion object { val NULL=Any() }
}
''',
'Uri.kt':'''package android.net
class Uri private constructor(private val text:String) {
 override fun toString()=text
 companion object { fun parse(s:String)=Uri(s) }
}
''',
'Runtime.kt':'''package tele.scripting
import org.json.JSONObject
import java.util.concurrent.LinkedBlockingQueue
class ScriptRuntime(val account:Int,val id:String="test") {
 var alive=true
 val grants=mutableSetOf<String>()
 var notificationHandlers=true
 var linkHandlers=true
 val notificationRequests=LinkedBlockingQueue<JSONObject>()
 val linkRequests=LinkedBlockingQueue<Pair<Int,String>>()
 fun isRunning()=alive
 fun hasNotificationInterceptors()=notificationHandlers
 fun hasLinkInterceptors()=linkHandlers
 fun allows(name:String,scope:String?=null)=grants.contains(name)
 fun requestNotification(token:Int,payload:JSONObject):Boolean { notificationRequests.add(payload); return true }
 fun requestLink(token:Int,url:String):Boolean { linkRequests.add(token to url); return true }
}
''',
'Test.kt':'''package regression
import android.net.Uri
import org.json.JSONObject
import tele.scripting.*
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit

private class Outcome<T> { var value:T?=null; var failure:Throwable?=null }

@Suppress("UNCHECKED_CAST")
private fun <T> onThread(block:()->T):Pair<Thread,()->T> {
    val outcome=Outcome<T>()
    val thread=Thread {
        try { outcome.value=block() } catch (t:Throwable) { outcome.failure=t }
    }
    thread.start()
    val finish:()->T = {
        thread.join(5000)
        check(!thread.isAlive) { "worker did not finish" }
        outcome.failure?.let { throw it }
        outcome.value as T
    }
    return thread to finish
}

private fun <T> take(q:LinkedBlockingQueue<T>):T = q.poll(3,TimeUnit.SECONDS) ?: error("interceptor was not called")

private fun elapsedMs(start:Long) = (System.nanoTime()-start)/1_000_000

fun main() {
    // Notification account isolation: only the runtime of the targeted account is asked.
    val a=ScriptRuntime(0).apply { grants.add("interceptNotification") }
    val b=ScriptRuntime(1).apply { grants.add("interceptNotification") }
    ScriptNotifications.register(a); ScriptNotifications.register(b)
    val (t1,done1)=onThread { ScriptNotifications.intercept(1,77L,88L,"message",true,"hi") }
    val p1=take(b.notificationRequests)
    check(a.notificationRequests.isEmpty()) { "account 0 runtime must not see account 1 notification" }
    check(p1.optLong("chatId")==77L); check(p1.optLong("fromId")==88L)
    check(p1.optString("kind")=="message"); check(p1.optBoolean("mentioned"))
    check(p1.optString("text")=="hi")
    check(ScriptNotifications.verdict(b,p1.optInt("token"),false)) { "granted allow verdict rejected" }
    check(done1()==true) { "allow verdict must keep the notification" }
    t1.join(); ScriptNotifications.unregister(a); ScriptNotifications.unregister(b)

    // Missing interceptNotification grant: verdict is refused, notification fails open.
    val c=ScriptRuntime(1)
    ScriptNotifications.register(c)
    val (t2,done2)=onThread { ScriptNotifications.intercept(1,1L,2L,"message",false,null) }
    val p2=take(c.notificationRequests)
    check(!ScriptNotifications.verdict(c,p2.optInt("token"),true)) { "ungranted verdict must be rejected" }
    check(done2()==true) { "rejected verdict must fail open" }
    t2.join(); ScriptNotifications.unregister(c)

    // Owner mismatch, unknown token and repeated answers are all rejected.
    val d=ScriptRuntime(1).apply { grants.add("interceptNotification") }
    val e=ScriptRuntime(0).apply { grants.add("interceptNotification") }
    ScriptNotifications.register(d); ScriptNotifications.register(e)
    val (t3,done3)=onThread { ScriptNotifications.intercept(1,3L,4L,"message",false,"x") }
    val p3=take(d.notificationRequests)
    val token3=p3.optInt("token")
    check(!ScriptNotifications.verdict(e,token3,true)) { "foreign owner answered a notification" }
    check(!ScriptNotifications.verdict(d,999999,true)) { "unknown token accepted" }
    check(ScriptNotifications.verdict(d,token3,false)) { "owner verdict rejected" }
    check(!ScriptNotifications.verdict(d,token3,true)) { "repeat verdict accepted" }
    check(done3()==true)
    t3.join(); ScriptNotifications.unregister(d); ScriptNotifications.unregister(e)

    // Silence times out and fails open after the 500ms interceptor budget.
    val f=ScriptRuntime(2).apply { grants.add("interceptNotification") }
    ScriptNotifications.register(f)
    val start4=System.nanoTime()
    val (t4,done4)=onThread { ScriptNotifications.intercept(2,5L,6L,"message",false,"y") }
    take(f.notificationRequests)
    check(done4()==true) { "timeout must show the notification" }
    check(elapsedMs(start4)>=450) { "timeout returned before the budget" }
    t4.join(); ScriptNotifications.unregister(f)

    // Unregister cancels the pending notification and returns before the timeout.
    val g=ScriptRuntime(3).apply { grants.add("interceptNotification") }
    ScriptNotifications.register(g)
    val (t5,done5)=onThread { ScriptNotifications.intercept(3,7L,8L,"message",false,"z") }
    val p5=take(g.notificationRequests)
    val token5=p5.optInt("token")
    val start5=System.nanoTime()
    ScriptNotifications.unregister(g)
    check(done5()==true) { "cancel must fail open" }
    check(elapsedMs(start5)<450) { "unregister waited for the timeout" }
    check(!ScriptNotifications.verdict(g,token5,true)) { "cancelled token still answerable" }
    t5.join()

    // Link rewrite: the answered url replaces the original.
    val h=ScriptRuntime(4).apply { grants.add("interceptLink") }
    ScriptLinks.register(h)
    val original=Uri.parse("https://a.test/x")
    val (t6,done6)=onThread { ScriptLinks.intercept(original) }
    val r6=take(h.linkRequests)
    check(r6.second=="https://a.test/x")
    check(ScriptLinks.verdict(h,r6.first,JSONObject().put("url","https://b.test/y")))
    check(done6()?.toString()=="https://b.test/y") { "rewritten link ignored" }
    t6.join()

    // Drop verdict removes the link entirely.
    val (t7,done7)=onThread { ScriptLinks.intercept(original) }
    val r7=take(h.linkRequests)
    check(ScriptLinks.verdict(h,r7.first,JSONObject().put("drop",true)))
    check(done7()==null) { "drop verdict must suppress the link" }
    t7.join()

    // Missing interceptLink grant cannot drop the link; original url survives.
    h.grants.clear()
    val start8=System.nanoTime()
    val (t8,done8)=onThread { ScriptLinks.intercept(original) }
    val r8=take(h.linkRequests)
    check(!ScriptLinks.verdict(h,r8.first,JSONObject().put("drop",true)))
    check(done8()?.toString()=="https://a.test/x") { "ungranted verdict altered the link" }
    check(elapsedMs(start8)>=450) { "ungranted verdict bypassed the timeout" }
    t8.join()

    // Timeout and unregister both fail open on links too.
    h.grants.add("interceptLink")
    val start9=System.nanoTime()
    val (t9,done9)=onThread { ScriptLinks.intercept(original) }
    take(h.linkRequests)
    check(done9()?.toString()=="https://a.test/x") { "link timeout must fail open" }
    check(elapsedMs(start9)>=450) { "link timeout returned early" }
    t9.join()
    val (t10,done10)=onThread { ScriptLinks.intercept(original) }
    take(h.linkRequests)
    val start10=System.nanoTime()
    ScriptLinks.unregister(h)
    check(done10()?.toString()=="https://a.test/x") { "cancelled link must fail open" }
    check(elapsedMs(start10)<450) { "link unregister waited for the timeout" }
    t10.join()

    // Stopped runtimes and runtimes without link handlers are skipped without being asked.
    h.alive=false; ScriptLinks.register(h)
    check(ScriptLinks.intercept(original).toString()=="https://a.test/x")
    check(h.linkRequests.isEmpty()) { "stopped runtime was asked about a link" }
    h.alive=true; ScriptLinks.unregister(h)
    val k=ScriptRuntime(5).apply { grants.add("interceptLink"); linkHandlers=false }
    ScriptLinks.register(k)
    check(ScriptLinks.intercept(original).toString()=="https://a.test/x")
    check(k.linkRequests.isEmpty()) { "handler-less runtime was asked about a link" }
    ScriptLinks.unregister(k)

    // ScriptReplies internals: owner, repeat, unknown token and stop semantics.
    val replies=ScriptReplies<String>()
    val owner=ScriptRuntime(0)
    val first=replies.open(owner)
    check(first!=replies.open(owner)) { "tokens must be unique" }
    check(!replies.answer(ScriptRuntime(0),first,"x")) { "foreign owner answered" }
    check(!replies.answer(owner,999999,"x")) { "unknown token answered" }
    check(replies.answer(owner,first,"x"))
    check(!replies.answer(owner,first,"y")) { "repeat answer accepted" }
    check(replies.await(first,1000)=="x")
    check(!replies.answer(owner,first,"z")) { "closed token answered" }
    check(replies.await(first,10)==null) { "closed token awaited" }

    val stopped=replies.open(owner)
    check(replies.answer(owner,stopped,"v"))
    owner.alive=false
    check(replies.await(stopped,1000)==null) { "stopped owner answer leaked" }
    owner.alive=true

    val timed=replies.open(owner)
    val start11=System.nanoTime()
    check(replies.await(timed,50)==null)
    check(elapsedMs(start11)>=45) { "await returned before its timeout" }
    check(!replies.answer(owner,timed,"late")) { "timed-out token answered" }

    val cancelled=replies.open(owner)
    val foreign=ScriptRuntime(1)
    val kept=replies.open(foreign)
    replies.cancel(owner)
    check(replies.await(cancelled,10)==null) { "cancelled token awaited" }
    check(replies.answer(foreign,kept,"keep"))
    check(replies.await(kept,100)=="keep") { "cancel touched another owner" }

    println("PASS: interceptor account isolation, grant/owner/token rejection, timeout and stop cleanup")
}
'''}
for name,text in sources.items(): (here/name).write_text(text)
product=root/'Telegram/TMessagesProj/src/main/java/tele/scripting'
files=[str(here/n) for n in sources]+[str(product/n) for n in ['ScriptReplies.kt','ScriptNotifications.kt','ScriptLinks.kt']]
java=args.java
out=here/'test.jar'
subprocess.run([java,'-cp',os.pathsep.join(map(str,cp)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(cp[1]),'-d',str(out),*files],check=True)
subprocess.run([java,'-cp',os.pathsep.join([str(out),str(cp[1])]),'regression.TestKt'],check=True)
print('PASS: interceptor regression')
