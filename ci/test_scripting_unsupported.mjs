import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'

const assets = new URL('../../Telegram/TMessagesProj/src/main/assets/tele/scripting/', import.meta.url)
const calls = []
const context = vm.createContext({
  __teleHost(name, raw) {
    const args = raw == null ? null : JSON.parse(raw)
    calls.push({ name, args })
    const values = {
      selfId: { $b: '7' }, scriptName: 'regression', randomId: '19',
      'theme.get': false, 'player.current': { title: 'song' }, 'call.current': { state: 'active' },
      'options.list': ['known'], 'decorate.message': 71,
    }
    return JSON.stringify({ ok: true, value: values[name] ?? true })
  },
})
for (const file of ['bootstrap.js', 'runtime.js']) {
  vm.runInContext(fs.readFileSync(new URL(file, assets), 'utf8'), context, { filename: file })
}
vm.runInContext('__teleInit()', context)

const unsupported = [
  'tg.localMessages()', 'tg.local.unread()', 'tg.local.folders()', 'tg.local.loaded()',
  'tg.local.draft("me")', 'tg.local.dialogs()',
  'tg.tele.ignored.list()', 'tg.tele.ignored.set("me", true)',
  'tg.tele.ghost.get("me")', 'tg.tele.ghost.set("me", "always")', 'tg.tele.ghost.list()',
  'tg.tele.localNames.list()', 'tg.tele.localNames.set("me", "name")',
  'tg.app.theme.onChange(() => {})',
  'tg.app.window.setTitle("title")', 'tg.app.window.setBadge(1)', 'tg.app.window.flash()',
  'tg.onWake(() => {})', 'tg.onConnectionChange(() => {})', 'tg.ui.onChatOpened(() => {})',
  'tg.connection()', 'tg.ui.current()',
  'tg.options.get("known")', 'tg.options.set("known", true)', 'tg.options.onChange(() => {})',
  'tg.options.onChange("known", () => {})',
]
for (const expression of unsupported) {
  await assert.rejects(async () => vm.runInContext(expression, context), error => {
    assert.equal(error.name, 'TeleError', expression)
    assert.equal(error.code, 'unsupported', expression)
    return true
  })
}
assert.equal(calls.filter(call => ['current', 'connection', 'options.get', 'options.set', 'options.listen'].includes(call.name)).length, 0)

vm.runInContext(`
  tg.app.player.current();
  tg.app.player.pause();
  const stopPlayer = tg.app.player.onChange(() => {});
  stopPlayer();
  tg.calls.current();
  tg.calls.answer();
  const stopCalls = tg.calls.onChange(() => {});
  stopCalls();
  tg.app.theme.setDark(true);
  tg.app.theme.get();
  tg.options.list();
  const action = tg.registerMessageAction({ text: 'working action', onClick() {} });
  action();
  const page = tg.ui.settingsPage({ title: 'settings', items: () => [tg.ui.input({ text: 'value', value: 'test' })] });
  const remove = tg.registerSettings(page);
  page.invalidate();
  remove();
  tg.ui.show({ title: 'dialog', text: 'body' });
`, context)
for (const name of ['player.current', 'player.control', 'player.listen', 'player.unlisten', 'call.current', 'call.control', 'call.listen', 'call.unlisten', 'theme.set', 'theme.get', 'options.list', 'messageAction.register', 'messageAction.unregister', 'settings.register', 'settings.rows', 'settings.unregister', 'ui.text']) {
  assert.ok(calls.some(call => call.name === name), name)
}
assert.equal(vm.runInContext('given.decorateMessage({ _: "inputPeerSelf" }, 5, { text: "replacement" })', context), 71)
vm.runInContext('given.decorateMessage({ _: "inputPeerSelf" }, 5, null, 71)', context)
assert.deepEqual(calls.filter(call => call.name === 'decorate.message').map(call => call.args.token), [null, 71])
console.log(`PASS: ${unsupported.length} final public unsupported APIs fail explicitly; player/calls/theme/settings/message actions/dialogs preserved; decoration token forwarded`)
