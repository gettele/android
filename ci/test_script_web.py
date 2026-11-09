#!/usr/bin/env python3
"""Compile current ScriptWeb.kt against deterministic transport stubs; no Android build/network."""
from pathlib import Path
import subprocess, os
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT / "scratch/script-web-regression"
HERE.mkdir(parents=True, exist_ok=True)
CACHE=Path.home()/'.gradle/caches/modules-2/files-2.1'
def jar(group, artifact, version):
    matches=list((CACHE/group/artifact/version).glob('*/'+artifact+'-'+version+'.jar'))
    if not matches: raise SystemExit("Missing cached dependency: "+artifact+" "+version)
    return matches[0]
compiler=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]
compiler += [jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
stdlib=compiler[1]
sources={
'Json.kt':'''package org.json
class JSONObject {
 private val data=HashMap<String,Any?>()
 fun put(k:String,v:Any?):JSONObject {data[k]=v;return this}
 fun optString(k:String,default:String="")=data[k] as? String ?: default
 fun optInt(k:String,default:Int=0)=(data[k] as? Number)?.toInt() ?: default
 fun optJSONObject(k:String)=data[k] as? JSONObject
 fun keys()=data.keys.iterator()
}
''',
'Runtime.kt':'''package tele.scripting
import org.json.JSONObject
class ScriptRuntime(val hosts:Set<String>) {
 @Volatile var running=true
 val checks=java.util.concurrent.CopyOnWriteArrayList<String>()
 fun allows(name:String,host:String):Boolean { checks.add(host); return name=="fetch" && host in hosts }
}
class ScriptException(val errorCode:String,message:String,val details:JSONObject?=null):RuntimeException(message)
''',
'FileLog.kt':'''package org.telegram.messenger
object FileLog
''',
'Timeout.kt':'''package okio
class Timeout {
 var nanos=0L
 fun timeout(value:Long,unit:java.util.concurrent.TimeUnit):Timeout {nanos=unit.toNanos(value);return this}
}
''',
'OkHttp.kt':'''package okhttp3
import java.net.URL
import java.io.InputStream
import java.io.ByteArrayInputStream
import java.io.IOException
import java.util.concurrent.TimeUnit
import java.util.concurrent.CountDownLatch
class Request(val url:URL) {
 class Builder {
  private var url:URL=URL("http://unused")
  fun url(v:URL)=apply {url=v}
  fun header(k:String,v:String)=this
  fun method(m:String,b:RequestBody?)=this
  fun build()=Request(url)
 }
}
class RequestBody {companion object { fun String.toRequestBody(type:Any?)=RequestBody() }}
class Headers(private val values:Map<String,String>) {
 fun names()=values.keys
 fun values(name:String)=listOfNotNull(values[name])
}
class ResponseBody(val stream:InputStream) {fun byteStream()=stream}
class Response(val request:Request,val code:Int=200,val location:String?=null,val input:InputStream=ByteArrayInputStream("ok".toByteArray()),val closing:()->Unit={}):java.io.Closeable {
 val message="response"
 val isRedirect get()=code in 300..399
 val body=ResponseBody(input)
 val headers=Headers(if(location==null) emptyMap() else mapOf("Location" to location))
 fun header(name:String)=if(name=="Location") location else null
 override fun close() {input.close();closing()}
}
class Call(val request:Request) {
 private val time=okio.Timeout()
 fun timeout()=time
 @Volatile var canceled=false
 var response:Response?=null
 fun execute():Response { if(canceled) throw IOException("canceled"); return Fake.respond(this).also { response=it } }
 fun cancel() {canceled=true;(response?.input as? BlockingInput)?.release?.countDown()}
}
class BlockingInput:InputStream() {
 val entered=CountDownLatch(1)
 val release=CountDownLatch(1)
 override fun read():Int {entered.countDown();check(release.await(5,TimeUnit.SECONDS));throw IOException("body released")}
 override fun read(b:ByteArray,off:Int,len:Int)=read()
}
object Fake {
 val calls=java.util.concurrent.CopyOnWriteArrayList<Call>()
 var timeout=0L
 var redirects=true
 var sslRedirects=true
 var respond:(Call)->Response={Response(it.request)}
}
class OkHttpClient {
 class Builder {
  fun connectTimeout(n:Long,u:TimeUnit)=this
  fun readTimeout(n:Long,u:TimeUnit)=this
  fun writeTimeout(n:Long,u:TimeUnit)=this
  fun callTimeout(n:Long,u:TimeUnit)=apply {Fake.timeout=u.toMillis(n)}
  fun followRedirects(v:Boolean)=apply {Fake.redirects=v}
  fun followSslRedirects(v:Boolean)=apply {Fake.sslRedirects=v}
  fun build()=OkHttpClient()
 }
 fun newCall(request:Request)=Call(request).also {Fake.calls.add(it)}
}
''',
'Test.kt':'''package regression
import tele.scripting.*
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
private var assertions=0
private fun eq(expected:Any?,actual:Any?,why:String) {assertions++; check(expected==actual) {"$why: expected=$expected actual=$actual"}}
private fun args(host:String="a.test",abort:Int=0)=JSONObject().put("url","https://$host/start").put("abort",abort)
private fun code(action:()->Unit):String?=try {action();null} catch(e:ScriptException) {e.errorCode}
private fun fetchThread(r:ScriptRuntime,a:JSONObject):Pair<Thread,AtomicReference<String?>> {
 val result=AtomicReference<String?>()
 val thread=Thread {result.set(code {ScriptWeb.fetch(r,a)})}.also {it.start()}
 return thread to result
}
private fun tracked():Int {
 val f=ScriptWeb.javaClass.getDeclaredField("calls"); f.isAccessible=true
 return (f.get(ScriptWeb) as Map<*,*>).size
}
fun main() {
 // Both calls return headers then block inside result() body reading.
 val streams=java.util.concurrent.ConcurrentHashMap<String,BlockingInput>()
 Fake.respond={call -> Response(call.request,input=streams.getValue(call.request.url.host))}
 val a=ScriptRuntime(setOf("a.test")); val b=ScriptRuntime(setOf("b.test"))
 streams["a.test"]=BlockingInput();streams["b.test"]=BlockingInput()
 val (ta,ea)=fetchThread(a,args("a.test",7));val (tb,eb)=fetchThread(b,args("b.test",7))
 check(streams.getValue("a.test").entered.await(3,TimeUnit.SECONDS));check(streams.getValue("b.test").entered.await(3,TimeUnit.SECONDS))
 eq(2,tracked(),"calls tracked while response body is being read")
 ScriptWeb.cancel(a)
 ta.join(3000)
 eq(false,ta.isAlive,"cancel A interrupts A body")
 eq("network",ea.get(),"cancel of still-running A reports network")
 eq(false,Fake.calls.first { it.request.url.host == "b.test" }.canceled,"cancel A never cancels B")
 eq(true,tb.isAlive,"B keeps reading")
 eq(1,tracked(),"only B remains tracked")
 ScriptWeb.abort(a,7)
 eq(false,Fake.calls.first { it.request.url.host == "b.test" }.canceled,"abort A id collision cannot cancel B")
 ScriptWeb.abort(b,0)
 eq(false,Fake.calls.first { it.request.url.host == "b.test" }.canceled,"abort zero ignored")
 ScriptWeb.abort(b,7)
 tb.join(3000)
 eq(false,tb.isAlive,"matching runtime+abort stops body")
 eq("network",eb.get(),"explicit abort reports current network error contract")
 eq(0,tracked(),"calls removed after body failure")
 val stopping=ScriptRuntime(setOf("stop.test"))
 val stopBody=BlockingInput()
 Fake.respond={Response(it.request,input=stopBody)}
 val (ts,es)=fetchThread(stopping,args("stop.test",9))
 check(stopBody.entered.await(3,TimeUnit.SECONDS))
 stopping.running=false
 ScriptWeb.cancel(stopping)
 ts.join(3000)
 eq(false,ts.isAlive,"stopping runtime interrupts body")
 eq("stopped",es.get(),"stopped runtime reports stopped instead of network")
 eq(0,tracked(),"stopped runtime cleaned")
 eq(30000L,Fake.timeout,"30 second per-call total timeout configured")
 eq(false,Fake.redirects,"automatic redirects disabled")
 eq(false,Fake.sslRedirects,"automatic SSL redirects disabled")
 // Each redirect validates a new host before creating its request.
 var before=Fake.calls.size
 Fake.respond={Response(it.request,302,"https://b.test/next")}
 val denied=ScriptRuntime(setOf("a.test"))
 eq("not-granted",code {ScriptWeb.fetch(denied,args())},"redirect must obtain target grant")
 eq(before+1,Fake.calls.size,"denied redirect never opens target call")
 eq(listOf("a.test","b.test"),denied.checks.toList(),"both grant checks")
 eq(0,tracked(),"redirect grant failure cleans calls")
 before=Fake.calls.size
 val stopped=ScriptRuntime(setOf("a.test","b.test"))
 Fake.respond={Response(it.request,302,"https://b.test/next",closing={stopped.running=false})}
 eq("stopped",code {ScriptWeb.fetch(stopped,args())},"stopped runtime cannot follow next redirect")
 eq(before+1,Fake.calls.size,"no request after redirect stops runtime")
 eq(0,tracked(),"stop after redirect cleans calls")
 before=Fake.calls.size
 Fake.respond={if(it.request.url.host=="a.test") { Thread.sleep(20); Response(it.request,302,"https://b.test/next") } else Response(it.request)}
 val allowed=ScriptRuntime(setOf("a.test","b.test"))
 eq(200,ScriptWeb.fetch(allowed,args()).optInt("status"),"allowed redirect succeeds")
 eq(before+2,Fake.calls.size,"manual redirect creates second call")
 check(Fake.calls[before+1].timeout().nanos < Fake.calls[before].timeout().nanos - 10000000L) {"redirect timeout must consume fetch-wide budget"}
 assertions++
 check(Fake.calls[before].timeout().nanos in 1L..30000000000L) {"initial timeout bounded by total budget"}
 assertions++
 eq(0,tracked(),"successful body read removes calls")
 val inactive=ScriptRuntime(setOf("a.test")).also {it.running=false}
 before=Fake.calls.size
 eq("stopped",code {ScriptWeb.fetch(inactive,args())},"inactive runtime rejected")
 eq(before,Fake.calls.size,"inactive runtime opens no call")
 println("PASS: $assertions assertions against current ScriptWeb.kt with deterministic transport stubs")
 println("LIMIT: stub validates shrinking timeout budget but does not emulate wall-clock timeout or real socket close")
}
'''}
for name,text in sources.items(): (HERE/name).write_text(text)
classes=HERE/'classes';classes.mkdir(exist_ok=True)
product=ROOT/'Telegram/TMessagesProj/src/main/java/tele/scripting/ScriptWeb.kt'
subprocess.run(['java','-cp',os.pathsep.join(map(str,compiler)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(stdlib),'-d',str(classes),str(product),*[str(HERE/n) for n in sources]],check=True)
subprocess.run(['java','-cp',os.pathsep.join([str(classes),str(stdlib)]),'regression.TestKt'],check=True)
real=HERE/'real-classes';real.mkdir(exist_ok=True)
transport=[jar('com.squareup.okhttp3','okhttp','4.12.0'),jar('com.squareup.okio','okio-jvm','3.6.0')]
subprocess.run(['java','-cp',os.pathsep.join(map(str,compiler)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',os.pathsep.join(map(str,[stdlib,*transport])),'-d',str(real),str(product),*[str(HERE/n) for n in ['Json.kt','Runtime.kt','FileLog.kt']]],check=True)
print('PASS: current ScriptWeb.kt also compiles against real cached OkHttp 4.12.0 / Okio 3.6.0')
