import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'

function load(path, globals = {}) {
  let script
  vm.runInNewContext(fs.readFileSync(new URL(path, import.meta.url), 'utf8').replace('export default defineScript(', 'defineScript('), {
    defineScript: value => { script = value }, ...globals,
  })
  return script
}

for (const header of ['120', new Date(180000).toUTCString(), null, 'invalid']) {
  let now = 0
  let calls = 0
  let action
  let error
  const script = load('../docs/scripts/quick-translate.js', {
    Date: class extends Date { static now() { return now } },
    fetch: async () => {
      calls++
      if (calls === 1) return { status: 429, ok: false, headers: { get: () => header } }
      return { status: 200, ok: true, json: async () => [[['hello']], null, 'ru'] }
    },
  })
  script.setup({
    storage: { get: () => null }, registerMessageAction: value => { action = value },
    log() {}, toast: value => { error = value },
    decorateMessage: async () => () => {}, ui: { show() {} },
  })
  const context = { chatId: 1n, messageId: 1, text: 'привет' }
  await action.onClick(context)
  assert.match(error, /temporarily rate-limited/)
  await action.onClick(context)
  assert.equal(calls, 1, 'cooldown must not send another request')
  const cooldown = header === '120' ? 120000 : header?.includes('GMT') ? 180000 : 60000
  now = cooldown - 1
  await action.onClick(context)
  assert.equal(calls, 1)
  now++
  await action.onClick(context)
  assert.equal(calls, 2)
  await action.onClick(context)
  await action.onClick(context)
  assert.equal(calls, 2, 'repeat translation must use cache')
}

let restores = 0
let decorated = 0
let dialogs = 0
const actions = []
load('../docs/scripts/display-test/script.js').setup({
  registerMessageAction: action => actions.push(action),
  decorateMessage: async (peer, id, value) => {
    assert.match(value.text, /Local display test/)
    decorated++
    return () => restores++
  },
  ui: { show: () => dialogs++ }, log() {}, toast: message => assert.fail(message),
})
const context = { chatId: -5n, messageId: 2, text: 'original' }
await actions[0].onClick(context)
await actions[0].onClick(context)
assert.equal(decorated, 1)
assert.equal(restores, 1)
await actions[0].onClick({ ...context, canReplaceText: false })
actions[1].onClick(context)
assert.equal(dialogs, 2)
await actions[0].onClick({ ...context, sourceText: 'original', editDate: 1 })
await actions[0].onClick({ ...context, text: 'edited', sourceText: 'edited', editDate: 2 })
assert.equal(decorated, 3, 'editing source must replace stale disposer on first tap')
await actions[0].onClick({ ...context, text: 'decorated', sourceText: 'edited', editDate: 2 })
assert.equal(restores, 2, 'second tap restores the current edited source')
const editor = fs.readFileSync(new URL('../../Telegram/TMessagesProj/src/main/java/org/telegram/ui/Components/ChatActivityEnterView.java', import.meta.url), 'utf8')
assert.ok(editor.includes('editingText = tele.TeleConfig.SCRIPTING.getValue() ? tele.scripting.ScriptDisplay.editingText(editingMessageObject)'))
assert.ok(editor.includes('TextUtils.equals(message[0], tele.TeleConfig.SCRIPTING.getValue() ? tele.scripting.ScriptDisplay.editingText(editingMessageObject)'))
console.log('PASS: 429 cooldown, numeric/date/missing/invalid Retry-After, cached translations, offline display and dialog')
