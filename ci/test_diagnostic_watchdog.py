#!/usr/bin/env python3
"""Compile actual TeleFreeze.kt with deterministic Android stubs; no app/device access.
TeleCrash diagnosticAllowed and full offerPending body are extracted verbatim and compiled
against focused filesystem/dialog stubs. No Android lifecycle or network sender is emulated.
"""
from pathlib import Path
import subprocess, os, re
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'scratch/diagnostic-watchdog-test'; OUT.mkdir(parents=True,exist_ok=True)
CACHE=Path.home()/'.gradle/caches/modules-2/files-2.1'
def jar(g,a,v):
 p=list((CACHE/g/a/v).glob('*/'+a+'-'+v+'.jar'))
 if not p: raise SystemExit('Missing cached dependency '+a)
 return p[0]
cp=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]+[jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
crash=(ROOT/'Telegram/TMessagesProj/src/main/java/tele/helpers/TeleCrash.kt').read_text()
policy=crash[crash.index('    private fun diagnosticAllowed'):crash.index('    // the next start after a crash asks')].strip()
start=crash.index("    fun offerPending(activity: Activity)")
brace=crash.index("{",start); depth=1; end=brace+1
while depth:
 if crash[end]=="{": depth+=1
 elif crash[end]=="}": depth-=1
 end+=1
offer=crash[start:end]
sources={
'Activity.kt':'''package android.app
class Activity(dir:java.io.File):android.content.Context(dir)
''',
'Log.kt':'''package android.util
object Log { fun i(tag:String,text:String)=0 }
''',
'Dialog.kt':'''package org.telegram.ui.ActionBar
class AlertDialog {
 fun setOnCancelListener(callback:(Any?)->Unit){}
 fun setCanceledOnTouchOutside(value:Boolean){}
 fun setOnDismissListener(callback:(Any?)->Unit){}
 fun show(){shown++}
 class Builder(activity:android.app.Activity){
 fun setTitle(text:String)=this
 fun setMessage(text:String)=this
 fun setPositiveButton(text:String,callback:(Any?,Any?)->Unit)=this
 fun setNegativeButton(text:String,callback:(Any?,Any?)->Unit)=this
 fun create()=AlertDialog()
 }
 companion object {var shown=0}
}
''',
'Lower.kt':'''package tele.helpers
object TeleLowercase {fun lc(text:String)=text}
''',
'Offer.kt':'''package regression
import android.app.Activity
import java.io.File
import tele.TeleConfig
import tele.TeleBuild
import tele.helpers.TeleLowercase
import org.telegram.ui.ActionBar.AlertDialog
object OfferHarness {
 private var offered=false
 fun reset(){offered=false;AlertDialog.shown=0}
 fun crashFile(a:Activity)=File(a.filesDir,"crash.txt")
 fun diagFile(a:Activity)=File(a.filesDir,"diag.txt")
 fun hasPending(a:Activity)=crashFile(a).exists()
 fun hasDiagnostics(a:Activity)=diagFile(a).exists()
 fun hasDump(a:Activity)=false
 fun offeredMarker(a:Activity)=File(a.filesDir,"offered")
 fun collecting()=TeleConfig.SEND_CRASH_REPORTS.value
 fun clearPending(a:Activity){crashFile(a).delete();diagFile(a).delete()}
 fun offerDump(a:Activity){}
 fun sendPendingAsync(a:Activity){}
'''+policy+'\n'+offer+'''
}
''',
'Context.kt':'''package android.content
open class Context(val filesDir: java.io.File)
''',
'Os.kt':'''package android.os
object SystemClock { @Volatile var now=1000L; fun uptimeMillis()=now }
object Build { const val MANUFACTURER="test"; const val MODEL="test"; object VERSION { const val RELEASE="test" } }
class Looper { companion object { fun getMainLooper()=Looper() } }
class Handler(looper: Looper) { fun post(r:Runnable){}; fun postDelayed(r:Runnable,d:Long){}; fun removeCallbacks(r:Runnable){} }
''',
'Messenger.kt':'''package org.telegram.messenger
object ApplicationLoader { lateinit var applicationContext: android.content.Context; @Volatile var mainInterfacePaused=true; @Volatile var isScreenOn=true }
object BuildVars { const val BUILD_VERSION_STRING="test" }
object FileLog { fun e(t:Throwable){ throw AssertionError(t) } }
''',
'Config.kt':'''package tele
class BoolItem(@Volatile var value:Boolean)
object TeleConfig { val DIAG_FREEZE=BoolItem(true); val DIAG_NO_DUMP=BoolItem(false); val SEND_CRASH_REPORTS=BoolItem(true) }
object TeleBuild { const val BUILD=0 }
''',
'Test.kt':'''package regression
import tele.helpers.TeleFreeze
import tele.TeleConfig
import android.os.SystemClock
import org.telegram.messenger.ApplicationLoader
import java.io.File
var assertions=0
fun eq(a:Any?,b:Any?,name:String){ assertions++; check(a==b){ "$name expected $a got $b" } }
'''+policy+'''
fun wanted(diagnostic:String, crash:Boolean=false):Boolean = crash || diagnosticAllowed(diagnostic)
fun main(args:Array<String>){
 val dir=File(args[0]); dir.mkdirs(); ApplicationLoader.applicationContext=android.content.Context(dir)
 val activity=android.app.Activity(dir)
 fun offerCase(note:String,noDump:Boolean,freeze:Boolean,expected:Int,name:String){
   OfferHarness.reset(); TeleConfig.DIAG_NO_DUMP.value=noDump; TeleConfig.DIAG_FREEZE.value=freeze
   OfferHarness.diagFile(activity).writeText(note)
   OfferHarness.offerPending(activity)
   eq(expected,org.telegram.ui.ActionBar.AlertDialog.shown,name)
   if(expected==0) eq(false,OfferHarness.diagFile(activity).exists(),name+" clears suppressed file")
   OfferHarness.clearPending(activity)
 }
 offerCase("Tele-Note: crash without a dump",false,true,0,"stored no dump with toggle off never offers")
 offerCase("Tele-Note: freeze killed by the system",false,true,0,"stored system ANR with no dump off never offers")
 offerCase("Tele-Note: freeze 900 s",false,true,0,"stored legacy watchdog never offers")
 offerCase("Tele-Note: freeze 16 s\\nwatchdog: foreground-uptime-v1",false,true,1,"new watchdog independent toggle offers")
 offerCase("Tele-Note: freeze 16 s\\nwatchdog: foreground-uptime-v1",true,false,0,"freeze toggle off suppresses watchdog")
 offerCase("Tele-Note: crash without a dump",true,false,1,"no dump toggle on offers")
 TeleConfig.DIAG_NO_DUMP.value=false; TeleConfig.DIAG_FREEZE.value=true
 val marker=TeleFreeze.markerFile()
 marker.writeText("Tele-Note: freeze 900 s\\n")
 eq(0,TeleFreeze.lastedSeconds(),"legacy marker suppressed"); eq(false,marker.exists(),"legacy removed")
 marker.writeText("Tele-Note: freeze 16 s\\nwatchdog: foreground-uptime-v1\\n")
 eq(16,TeleFreeze.lastedSeconds(),"versioned foreground marker accepted")
 marker.delete()
 eq(false,wanted("Tele-Note: freeze killed by the system\\nwatchdog: foreground-uptime-v1"),"system ANR obeys no dump off")
 eq(false,wanted("Tele-Note: freeze 900 s"),"old watchdog diag suppressed despite freeze on")
 eq(true,wanted("Tele-Note: freeze 16 s\\nwatchdog: foreground-uptime-v1"),"new watchdog diag follows freeze on")
 TeleConfig.DIAG_FREEZE.value=false
 eq(false,wanted("Tele-Note: freeze 16 s\\nwatchdog: foreground-uptime-v1"),"freeze off suppresses pending watchdog")
 TeleConfig.DIAG_NO_DUMP.value=true
 eq(true,wanted("Tele-Note: freeze killed by the system"),"system ANR follows no dump on")
 TeleConfig.DIAG_FREEZE.value=true; TeleConfig.DIAG_NO_DUMP.value=false
 val clazz=TeleFreeze.javaClass
 val beat=clazz.getDeclaredField("beat").apply{isAccessible=true}.get(null) as java.util.concurrent.atomic.AtomicLong
 val tick=clazz.getDeclaredField("tick").apply{isAccessible=true}.get(null) as Runnable
 // The actual product tick reads uptime, never elapsedRealtime, so deep sleep cannot advance it.
 TeleFreeze.start(); SystemClock.now=1000; tick.run(); eq(1000L,beat.get(),"tick records uptime")
 ApplicationLoader.mainInterfacePaused=true
 SystemClock.now=100000
 Thread.sleep(1200)
 eq(false,marker.exists(),"background uptime gap ignored")
 eq(100000L,beat.get(),"background resets heartbeat")
 ApplicationLoader.mainInterfacePaused=false; ApplicationLoader.isScreenOn=false; SystemClock.now=200000
 Thread.sleep(1200)
 eq(false,marker.exists(),"screen off gap ignored")
 ApplicationLoader.isScreenOn=true; TeleConfig.DIAG_FREEZE.value=false; SystemClock.now=300000
 Thread.sleep(1200)
 eq(false,marker.exists(),"live toggle off ignored")
 TeleConfig.DIAG_FREEZE.value=true; SystemClock.now=400000
 Thread.sleep(1200)
 eq(true,marker.exists(),"foreground awake stall records marker")
 eq(true,marker.readText().contains("watchdog: foreground-uptime-v1"),"new marker provenance")
 val stoppedBeat=beat.get(); TeleFreeze.stop(); marker.delete()
 SystemClock.now=500000; tick.run(); eq(stoppedBeat,beat.get(),"stopped tick does not update heartbeat")
 println("PASS $assertions assertions: actual TeleFreeze loop/tick/markers + verbatim TeleCrash offerPending and policy")
}
'''
}
for n,t in sources.items(): (OUT/n).write_text(t)
classes=OUT/'classes'; classes.mkdir(exist_ok=True)
java='/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java'
subprocess.run([java,'-cp',os.pathsep.join(map(str,cp)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(cp[1]),'-d',str(classes),str(ROOT/'Telegram/TMessagesProj/src/main/java/tele/helpers/TeleFreeze.kt'),*[str(OUT/n) for n in sources]],check=True)
subprocess.run([java,'-cp',os.pathsep.join([str(classes),str(cp[1])]),'regression.TestKt',str(OUT/'files')],check=True)
keys=['Diagnostic report','Freeze report','The last run stopped responding. Send the diagnostic report to the tele server?','The last run ended without a crash dump. Send the diagnostic report to the tele server?']
for lang in ['Ru','Uk']:
 txt=(ROOT/f'Telegram/TMessagesProj/src/main/java/tele/helpers/TeleText{lang}.kt').read_text()
 for key in keys: assert f'"{key}" to ' in txt, (lang,key)
print('PASS ru/uk diagnostic title and body translation keys')
