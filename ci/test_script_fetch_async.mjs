import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'

const assets = new URL('../../Telegram/TMessagesProj/src/main/assets/tele/scripting/', import.meta.url)
const jobs = new Map()
const started = []
let context
let rejectStart = false
let aborted = 0
context = vm.createContext({
  AbortController, AbortSignal, URL, DOMException,
  __teleHost(name, raw) {
    const args = raw == null ? null : JSON.parse(raw)
    if (name === 'fetch.start') {
      if (rejectStart) return JSON.stringify({ ok: false, code: 'not-granted', error: 'host denied' })
      jobs.set(args.callback, args)
      started.push(args)
    } else if (name === 'fetchAbort') {
      aborted++
      for (const [callback, request] of jobs) {
        if (request.abort === args) {
          jobs.delete(callback)
          queueMicrotask(() => complete(callback, { ok: false, code: 'aborted', error: 'aborted' }))
        }
      }
    } else if (name === 'timer.set') {
      setTimeout(() => vm.runInContext(`__teleTimer(${JSON.stringify(JSON.stringify(args.id))})`, context), args.ms)
    }
    const value = name === 'selfId' ? { $b: '1' } : name === 'randomId' ? '2' : name === 'scriptName' ? 'test' : true
    return JSON.stringify({ ok: true, value })
  },
})
vm.runInContext(fs.readFileSync(new URL('bootstrap.js', assets), 'utf8'), context)
vm.runInContext(fs.readFileSync(new URL('runtime.js', assets), 'utf8'), context)
// Run the actual web fetch extension without unrelated QuickJS-specific typed-array polyfills.
const web = fs.readFileSync(new URL('web.js', assets), 'utf8')
const extension = web.slice(web.indexOf('\tglobalThis.__teleExtensions.push({'), web.lastIndexOf('\n})();'))
vm.runInContext(`(() => {
 const define = (name, value) => { globalThis[name] = value };
 const isSignal = signal => signal instanceof AbortSignal;
 const signalReason = signal => signal.reason ?? new DOMException('Aborted', 'AbortError');
 const followSignal = (signal, callback) => signal.addEventListener('abort', callback, { once: true });
 const unfollowSignal = (signal, callback) => signal.removeEventListener('abort', callback);
 ${extension}
})()`, context)
vm.runInContext('__teleInit()', context)
function complete(callback, result) {
  vm.runInContext(`__teleDispatch(${JSON.stringify(JSON.stringify({ id: callback, args: [result] }))})`, context)
}
const response = { status: 200, text: 'done', headers: { 'x-test': 'yes' }, base64: 'ZG9uZQ==' }
const pending = vm.runInContext('fetch("https://a.test")', context)
assert.equal(typeof pending.then, 'function')
assert.equal(started.length, 1)
let settled = false
pending.then(() => { settled = true })
vm.runInContext('globalThis.timerRan = false; setTimeout(() => { globalThis.timerRan = true }, 1)', context)
await new Promise(resolve => setTimeout(resolve, 15))
assert.equal(vm.runInContext('timerRan', context), true, 'script timers run during pending fetch')
assert.equal(settled, false)
const id = started.at(-1).callback
complete(id, { ok: true, value: response })
const result = await pending
assert.equal(await result.text(), 'done')
assert.equal(result.headers.get('X-Test'), 'yes')
complete(id, { ok: false, code: 'network', error: 'late stale completion' })
assert.equal(await result.text(), 'done')

vm.runInContext('globalThis.controller = new AbortController()', context)
const aborting = vm.runInContext('fetch("https://a.test/abort", { signal: controller.signal })', context)
const rejection = assert.rejects(aborting, error => error.name === 'AbortError')
vm.runInContext('controller.abort()', context)
await rejection
assert.equal(aborted, 1)
await new Promise(setImmediate)

const timed = vm.runInContext('fetch("https://a.test/timeout", { signal: AbortSignal.timeout(5) })', context)
let timeoutWatchdog
try {
  await Promise.race([
    assert.rejects(timed, error => error.name === 'TimeoutError'),
    new Promise((_, reject) => { timeoutWatchdog = setTimeout(() => reject(new Error('signal timeout did not run')), 1000) }),
  ])
} finally {
  clearTimeout(timeoutWatchdog)
}
assert.equal(aborted, 2)
const before = started.length
vm.runInContext('globalThis.pre = new AbortController(); pre.abort()', context)
await assert.rejects(vm.runInContext('fetch("https://a.test", { signal: pre.signal })', context), error => error.name === 'AbortError')
assert.equal(started.length, before, 'pre-aborted signal never starts native fetch')
rejectStart = true
await assert.rejects(vm.runInContext('fetch("https://denied.test")', context), error => error.code === 'not-granted')
rejectStart = false
const failure = vm.runInContext('fetch("https://a.test/error")', context)
complete(started.at(-1).callback, { ok: false, code: 'too-big', error: 'body too large' })
await assert.rejects(failure, error => error.code === 'too-big')
console.log('PASS: actual bootstrap async Promise/completion, stale callback, script timers, actual web fetch abort wrapper, manual abort, timeout and pre-aborted signal')
