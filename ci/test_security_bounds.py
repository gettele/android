"""Compile and run the actual BoundedRegex Kotlin helper, no Android/JNI.

Run with --root pointing to the workspace containing Telegram/; compiler dependencies
must already exist in --cache. The helper is checked behaviourally: unicode matching,
the shared deterministic read cap, the guarded sub sequence and fail-open on time/stack.
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
temporary = tempfile.TemporaryDirectory(prefix='tele-security-bounds-') if args.output is None else None
here=args.output.resolve() if args.output else Path(temporary.name)
here.mkdir(parents=True, exist_ok=True)
cache=args.cache
def jar(g,a,v): return next((cache/g/a/v).glob('*/'+a+'-'+v+'.jar'))
cp=[jar('org.jetbrains.kotlin',a,'2.2.21') for a in ['kotlin-compiler-embeddable','kotlin-stdlib','kotlin-script-runtime','kotlin-reflect']]+[jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.8.0'),jar('org.jetbrains','annotations','13.0')]
sources={
'Test.kt':r'''package regression

import tele.helpers.BoundedRegex
import java.util.regex.Pattern

private class Counted(private val value: CharSequence) : CharSequence {
    var reads = 0
        private set

    override val length: Int get() = value.length

    override fun get(index: Int): Char {
        reads++
        return value[index]
    }

    override fun subSequence(startIndex: Int, endIndex: Int): CharSequence = Counted(value.subSequence(startIndex, endIndex))

    override fun toString(): String = value.toString()
}

private class SimulatedStackOverflow : CharSequence {
    override val length: Int get() = 16

    override fun get(index: Int): Char = throw StackOverflowError("simulated")

    override fun subSequence(startIndex: Int, endIndex: Int): CharSequence = this

    override fun toString(): String = "simulated"
}

private fun readUntilCap(): Int {
    val pattern = Pattern.compile("b")
    val text = Counted("a".repeat(BoundedRegex.MAX_READS * 2))
    val budget = BoundedRegex.newBudget()
    check(!BoundedRegex.find(pattern, text, budget))
    check(budget.expired())
    return text.reads
}

private fun subsequenceKeepsBudget() {
    val guardedClass = Class.forName("tele.helpers.BoundedRegex\$Guarded")
    val constructor = guardedClass.getDeclaredConstructor(
        CharSequence::class.java,
        Int::class.javaPrimitiveType!!,
        Int::class.javaPrimitiveType!!,
        BoundedRegex.Budget::class.java
    )
    constructor.isAccessible = true
    val source = Counted("x".repeat(BoundedRegex.MAX_READS + 20_000))
    val budget = BoundedRegex.newBudget()
    val guarded = constructor.newInstance(source, 0, source.length, budget) as CharSequence
    val sub = guarded.subSequence(1_000, source.length - 1_000)
    check(sub.length == source.length - 2_000)
    check(sub.toString().length == sub.length)
    check(source.reads == 0)

    var tripped = false
    var index = 0
    try {
        while (index < sub.length) {
            sub[index]
            index++
        }
    } catch (t: Throwable) {
        tripped = true
    }
    check(tripped)
    check(budget.expired())
    check(source.reads > BoundedRegex.MAX_READS)
    check(source.reads <= BoundedRegex.MAX_READS + 1024)

    // the parent view shares the exhausted budget
    var parentTripped = false
    try {
        repeat(600) { guarded[0] }
    } catch (t: Throwable) {
        parentTripped = true
    }
    check(parentTripped)
}

private fun failOpen() {
    // simulated stack exhaustion fails open without a dangerous payload
    val stackBudget = BoundedRegex.newBudget()
    check(!BoundedRegex.find(Pattern.compile("b"), SimulatedStackOverflow(), stackBudget))
    check(stackBudget.expired())

    // an old budget fails open before reading any text
    val text = Counted("a".repeat(10))
    val timeBudget = BoundedRegex.newBudget()
    Thread.sleep(BoundedRegex.TIME_NANOS / 1_000_000 + 20)
    check(!BoundedRegex.find(Pattern.compile("a"), text, timeBudget))
    check(timeBudget.expired())
    check(text.reads == 0)
}

fun main() {
    val literal = Pattern.compile("привет")
    val folded = Pattern.compile("ПРИВЕТ", Pattern.CASE_INSENSITIVE or Pattern.UNICODE_CASE)
    val emoji = Pattern.compile("😀")
    val letters = Pattern.compile("\\p{L}+-\\d+")
    val absent = Pattern.compile("нет")
    val budget = BoundedRegex.newBudget()
    check(BoundedRegex.find(literal, "до привет после", budget))
    check(BoundedRegex.find(folded, "ПРИВЕТ", budget))
    check(BoundedRegex.find(emoji, "a😀b", budget))
    check(BoundedRegex.find(letters, "тест-42", budget))
    check(!BoundedRegex.find(absent, "привет", budget))
    check(!budget.expired())

    // one budget across two scans stops at the shared read cap
    val first = Counted("a".repeat(BoundedRegex.MAX_READS / 2 + 10_000))
    val second = Counted("a".repeat(BoundedRegex.MAX_READS / 2 + 10_000))
    val shared = BoundedRegex.newBudget()
    check(!BoundedRegex.find(absent, first, shared))
    val afterFirst = first.reads
    check(afterFirst > 0)
    check(!shared.expired())
    check(!BoundedRegex.find(absent, second, shared))
    check(shared.expired())
    check(first.reads == afterFirst)
    check(afterFirst + second.reads > BoundedRegex.MAX_READS)
    check(second.reads > 0)

    // an expired budget fails open without touching the text again
    val untouched = Counted("abc")
    check(!BoundedRegex.find(literal, untouched, shared))
    check(untouched.reads == 0)

    // the same payload always stops after the same number of char reads
    val firstRun = readUntilCap()
    val secondRun = readUntilCap()
    check(firstRun == secondRun)
    check(firstRun > BoundedRegex.MAX_READS)
    check(firstRun <= BoundedRegex.MAX_READS + 1024)

    subsequenceKeepsBudget()
    failOpen()
    println("PASS: BoundedRegex unicode, shared deterministic read cap, sub sequence guard, stack/time fail-open")
}
'''}
for name,text in sources.items(): (here/name).write_text(text, encoding='utf-8')
product=root/'Telegram/TMessagesProj/src/main/java/tele/helpers/BoundedRegex.kt'
java=args.java
out=here/'test.jar'
subprocess.run([java,'-cp',os.pathsep.join(map(str,cp)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',str(cp[1]),'-d',str(out),str(here/'Test.kt'),str(product)],check=True)
subprocess.run([java,'-cp',os.pathsep.join([str(out),str(cp[1])]),'regression.TestKt'],check=True)
print('PASS: BoundedRegex behavioural security bounds')
