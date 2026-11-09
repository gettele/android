import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
const assets = new URL('../../Telegram/TMessagesProj/src/main/assets/tele/scripting/', import.meta.url)
const results = []
const ids = []
const context = vm.createContext({
  __teleHost(name, raw) {
    const value = raw == null ? null : JSON.parse(raw)
    if (name === 'decorate.register') ids.push(value)
    if (name === 'decorate.result') results.push(value)
    return JSON.stringify({ ok: true, value: name === 'selfId' ? { $b: '1' } : true })
  },
})
for (const file of ['bootstrap.js', 'runtime.js']) vm.runInContext(fs.readFileSync(new URL(file, assets), 'utf8'), context)
vm.runInContext(`__teleInit(); globalThis.finish = null;
tg.decorateMessages(message => new Promise(resolve => { finish = () => resolve({ text: message.text + ' translated' }); }));`, context)
const request = { token: 77, ids, raw: { _: 'message', id: 10, message: 'hello', peerId: { _: 'peerUser', userId: { $b: '2' } } } }
context.payload = JSON.stringify(request)
vm.runInContext('__teleDecorate(payload)', context)
await new Promise(setImmediate)
assert.equal(results.length, 0, 'pending Promise has no result and does not busy poll')
vm.runInContext('finish()', context)
await new Promise(setImmediate)
assert.equal(results.length, 1)
assert.equal(results[0].token, 77)
assert.equal(results[0].value.text, 'hello translated')
vm.runInContext('tg.decorateMessages(async () => null)', context)
context.payload = JSON.stringify({ ...request, token: 78, ids: [ids.at(-1)] })
vm.runInContext('__teleDecorate(payload)', context)
await new Promise(setImmediate)
assert.equal(results.at(-1).token, 78)
assert.equal(results.at(-1).value, null)
assert.equal(vm.runInContext('typeof __teleDecorateResult', context), 'undefined')
console.log('PASS: real bootstrap/runtime decorator Promise settlement pushes tokenized results without polling; null results settle')
