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
 fun optBoolean(k:String)=data[k] as? Boolean ?: false
 fun opt(k:String)=data[k]
}
class JSONArray { private val data=ArrayList<Any?>(); fun put(v:Any?):JSONArray {data.add(v);return this}; fun optJSONObject(i:Int)=data[i] as? JSONObject }
''',
'Runtime.kt':'''package tele.scripting
import org.json.JSONObject
import org.json.JSONArray
class ScriptRuntime(val hosts:Set<String>) {
 @Volatile var running=true
 val checks=java.util.concurrent.CopyOnWriteArrayList<String>()
 val answers=java.util.concurrent.ConcurrentHashMap<Int,JSONObject>()
 fun dispatch(id:Int,kind:String,args:JSONArray):Boolean {if(!running)return false;answers[id]=args.optJSONObject(0)!!;return true}
 fun allows(name:String,host:String):Boolean { checks.add(host); return name=="fetch" && host in hosts }
}
class ScriptException(val errorCode:String,message:String,val extra:JSONObject?=null):RuntimeException(message)
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
class Request(val url:URL,val sentHeaders:Map<String,String>) {
 class Builder {
  private val headers=HashMap<String,String>()
  private var url:URL=URL("http://unused")
  fun url(v:URL)=apply {url=v}
  fun header(k:String,v:String)=apply {headers[k]=v}
  fun method(m:String,b:RequestBody?)=this
  fun build()=Request(url,headers.toMap())
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
private var assertions=0
private var next=1
private fun eq(expected:Any?,actual:Any?,why:String) {assertions++; check(expected==actual) {"$why: expected=$expected actual=$actual"}}
private fun args(host:String="a.test",abort:Int=0)=JSONObject().put("url","https://$host/start").put("abort",abort).put("callback",next++)
private fun code(action:()->Unit):String?=try {action();null} catch(e:ScriptException) {e.errorCode}
private fun await(r:ScriptRuntime,a:JSONObject):JSONObject {
 val end=System.nanoTime()+TimeUnit.SECONDS.toNanos(5)
 while(System.nanoTime()<end) { r.answers.remove(a.optInt("callback"))?.let{return it};Thread.sleep(2) }
 error("no callback")
}
private fun tracked():Int {
 val f=ScriptWeb.javaClass.getDeclaredField("jobs");f.isAccessible=true
 return (f.get(ScriptWeb) as Map<*,*>).size
}
fun main() {
 val streams=java.util.concurrent.ConcurrentHashMap<String,BlockingInput>()
 Fake.respond={call -> Response(call.request,input=streams.getValue(call.request.url.host))}
 val a=ScriptRuntime(setOf("a.test"));val b=ScriptRuntime(setOf("b.test"))
 streams["a.test"]=BlockingInput();streams["b.test"]=BlockingInput()
 val aa=args("a.test",7);val ab=args("b.test",7)
 val begin=System.nanoTime()
 ScriptWeb.start(a,aa);ScriptWeb.start(b,ab)
 check(System.nanoTime()-begin<TimeUnit.SECONDS.toNanos(1));assertions++
 check(streams.getValue("a.test").entered.await(3,TimeUnit.SECONDS));check(streams.getValue("b.test").entered.await(3,TimeUnit.SECONDS))
 eq(2,tracked(),"jobs tracked during response body reading")
 a.running=false;ScriptWeb.cancel(a)
 Thread.sleep(20)
 eq(0,a.answers.size,"stopped runtime receives no completion")
 eq(false,Fake.calls.first {it.request.url.host=="b.test"}.canceled,"cancel A leaves B")
 ScriptWeb.abort(a,7)
 eq(false,Fake.calls.first {it.request.url.host=="b.test"}.canceled,"abort ids isolated by runtime")
 ScriptWeb.abort(b,0)
 eq(false,Fake.calls.first {it.request.url.host=="b.test"}.canceled,"abort zero ignored")
 ScriptWeb.abort(b,7)
 eq("aborted",await(b,ab).optString("code"),"abort dispatches rejection")
 Thread.sleep(20)
 eq(0,tracked(),"aborted jobs removed")
 eq(0,b.answers.size,"stale worker result suppressed")
 eq(30000L,Fake.timeout,"call timeout configured")
 eq(false,Fake.redirects,"automatic redirects disabled")
 eq(false,Fake.sslRedirects,"automatic SSL redirects disabled")
 var before=Fake.calls.size
 Fake.respond={Response(it.request,302,"https://b.test/next")}
 val denied=ScriptRuntime(setOf("a.test"));val da=args()
 ScriptWeb.start(denied,da)
 eq("not-granted",await(denied,da).optString("code"),"redirect requires target host grant")
 eq(before+1,Fake.calls.size,"denied redirect opens no target call")
 eq(listOf("a.test","a.test","b.test"),denied.checks.toList(),"preflight and each hop check grant")
 val stopped=ScriptRuntime(setOf("a.test","b.test"));val sa=args()
 Fake.respond={Response(it.request,302,"https://b.test/next",closing={stopped.running=false})}
 before=Fake.calls.size;ScriptWeb.start(stopped,sa);Thread.sleep(40)
 eq(before+1,Fake.calls.size,"stop blocks redirect")
 eq(0,stopped.answers.size,"no stopped completion")
 Fake.respond={if(it.request.url.host=="a.test") {Thread.sleep(20);Response(it.request,302,"https://b.test/next")} else Response(it.request)}
 before=Fake.calls.size
 val allowed=ScriptRuntime(setOf("a.test","b.test"));val ok=args().put("headers",JSONObject().put("Authorization","secret").put("Cookie","secret").put("X-Test","visible"))
 ScriptWeb.start(allowed,ok)
 val answer=await(allowed,ok)
 eq(true,answer.optBoolean("ok"),"completion resolves")
 eq(200,answer.optJSONObject("value")!!.optInt("status"),"response body packaged")
 eq("secret",Fake.calls[before].request.sentHeaders["Authorization"],"original credential header allowed")
 eq(null,Fake.calls[before+1].request.sentHeaders["Authorization"],"cross-origin authorization stripped")
 eq(null,Fake.calls[before+1].request.sentHeaders["Cookie"],"cross-origin cookie stripped")
 eq("visible",Fake.calls[before+1].request.sentHeaders["X-Test"],"noncredential header retained")
 check(Fake.calls[before+1].timeout().nanos<Fake.calls[before].timeout().nanos-10000000L);assertions++
 eq(0,tracked(),"success removed job")
 val inactive=ScriptRuntime(setOf("a.test")).also {it.running=false}
 eq("stopped",code {ScriptWeb.start(inactive,args())},"inactive runtime rejected")
 eq("not-granted",code {ScriptWeb.start(ScriptRuntime(emptySet()),args())},"initial grant validated before queue")
 val blocked=BlockingInput();val queued=ScriptRuntime(setOf("limit.test"))
 Fake.respond={Response(it.request,input=blocked)}
 val requests=(1..8).map{args("limit.test",it)}
 for(req in requests)ScriptWeb.start(queued,req)
 eq("busy",code {ScriptWeb.start(queued,args("limit.test"))},"per-runtime queue bounded")
 ScriptWeb.abort(queued,8)
 eq("aborted",await(queued,requests.last()).optString("code"),"abort queued work completes immediately")
 queued.running=false;ScriptWeb.cancel(queued);Thread.sleep(30)
 eq(0,tracked(),"cancel removes queued and active work")
 println("PASS: $assertions async ScriptWeb assertions against actual product with deterministic transport")
 println("LIMIT: does not emulate real socket timeout scheduling")
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
real_test=HERE/'RealTest.kt'
real_test.write_text('''package regression
import tele.scripting.*
import org.json.JSONObject
import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import java.util.concurrent.TimeUnit
private fun awaitAnswer(runtime:ScriptRuntime, id:Int):JSONObject {
 val end=System.nanoTime()+TimeUnit.SECONDS.toNanos(5)
 while(System.nanoTime()<end) {runtime.answers.remove(id)?.let{return it};Thread.sleep(2)}
 error("no completion")
}
fun main() {
 val server=HttpServer.create(InetSocketAddress("127.0.0.1",0),0)
 val entered=java.util.concurrent.CountDownLatch(1)
 val release=java.util.concurrent.CountDownLatch(1)
 server.createContext("/slow") { exchange ->
  exchange.sendResponseHeaders(200,0)
  exchange.responseBody.write("partial".toByteArray());exchange.responseBody.flush()
  entered.countDown();release.await(5,TimeUnit.SECONDS)
  runCatching { exchange.responseBody.write("end".toByteArray());exchange.close() }
 }
 server.createContext("/ok") { exchange ->
  val data="real response".toByteArray();exchange.sendResponseHeaders(200,data.size.toLong())
  exchange.responseBody.use{it.write(data)}
 }
 server.executor=java.util.concurrent.Executors.newCachedThreadPool { task -> Thread(task).apply {isDaemon=true} }
 server.start()
 try {
  val runtime=ScriptRuntime(setOf("127.0.0.1"))
  val base="http://127.0.0.1:"+server.address.port
  ScriptWeb.start(runtime,JSONObject().put("url",base+"/slow").put("callback",1).put("abort",42))
  check(entered.await(3,TimeUnit.SECONDS))
  ScriptWeb.abort(runtime,42)
  check(awaitAnswer(runtime,1).optString("code")=="aborted")
  release.countDown()
  ScriptWeb.start(runtime,JSONObject().put("url",base+"/ok").put("callback",2))
  val answer=awaitAnswer(runtime,2)
  check(answer.optBoolean("ok"));check(answer.optJSONObject("value")!!.optString("text")=="real response")
  println("PASS: actual OkHttp loopback response and cancellation during streamed response body")
 } finally {release.countDown();server.stop(0)}
}
''')
subprocess.run(['java','-cp',os.pathsep.join(map(str,compiler)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',os.pathsep.join(map(str,[stdlib,*transport,real])),'-d',str(real),str(real_test)],check=True)
subprocess.run(['java','--add-modules','jdk.httpserver','-cp',os.pathsep.join(map(str,[real,stdlib,*transport])),'regression.RealTestKt'],check=True)
