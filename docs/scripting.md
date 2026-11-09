# scripting

settings → tele → scripts: javascript and typescript files that run inside tele, one QuickJS runtime per script and account on their own thread. a script is off until you switch it on, and it only gets the permissions you approve.

this page is the android reference for the API of this build. it is not the full desktop reference: the desktop runtime has settings pages, commands, interceptors, calls, the music player and the widget layer. [what is not here yet](#what-is-not-here-yet) lists the differences.

## your first script

```js
export default defineScript({
  name: 'echo',
  grants: ['onUpdate(new_message)', 'call(messages.sendMessage)'],
  setup(tg) {
    tg.onNewMessage((message) => {
      if (message.out) return
      return tg.sendMessage(message.chat?.input ?? message.chatId, message.text)
    })
  },
})
```

`defineScript` is a global on android. don't `import` it from `tele`: this runtime has no module resolver yet, so a script must be a single file (or a folder with `index.js` / `index.ts`) and use the globals.

## where scripts live

the default folder is `tele/scripts` in the app's external files folder:

```
Android/data/org.telegram.messenger.tele.dev/files/tele/scripts/
  tele.d.ts          written by tele, don't edit
  tsconfig.json      written once, yours to change
  calculator.js
  quick-translate.js
  away-auto-reply.js
  _lib/              skipped: shared helpers
```

- a top-level `.js`, `.mjs`, `.ts` or `.mts` file is a script.
- a top-level folder is a script when it has `index.js`, `index.mjs`, `index.ts` or `index.mts`. everything else inside is that script's private code.
- skipped: names starting with `_` or `.`, `node_modules`, `*.d.ts`, `tsconfig.json` and other extensions.
- the file or folder name is the script id. the switch, the approved grants and `tg.storage` are kept under that id; renaming the file makes a new script.
- settings → tele → scripts opens the folder, rescans it, changes it with the system picker or returns to the app folder. import a script from a file or a direct link; imported scripts stay off until you enable them.
- typescript is stripped by the runtime. the generated `tele.d.ts` describes this build.

## defineScript

```ts
interface ScriptConfig {
  name: string
  grants?: string[]
  setup?(tg: Tele): void | Promise<void>
}
```

- `name` is shown in the scripts manager.
- `grants` is the list of permissions the user approves before the script starts. declaring an unknown grant asks for it and shows it as unknown; don't rely on that.
- `setup` runs once when the script starts. async setup is allowed, but everything runs on the script's thread; a blocking script blocks only that thread.

## grants

a grant is `name` or `name(scope)`. scopes are matched exactly or with a trailing `*`. the current APIs use these:

| grant | what it allows |
|---|---|
| `onUpdate(new_message)` | `tg.onNewMessage`, `tg.onMessageEdited`, `tg.onMessageDeleted` and the message updates behind them |
| `call(messages.sendMessage)` | `tg.sendMessage` and `Message.reply`; use the exact TL method the script calls |
| `call(<method>)` | any other `tg.call` request, for example `call(messages.getHistory)` |
| `fetch(<host>)` | `fetch` to that exact host; redirects are checked again on every hop |
| `display(messages)` | `tg.decorateMessages` and `tg.decorateMessage`; changes are local to this device |
| `app` | `tg.openChat` |

the other grants from the desktop runtime are recognized in the consent dialog but their APIs are not available on android yet. a script that needs one of them does not start.

## api

### identity and storage

```ts
tg.selfId        // bigint
tg.scriptName    // string
tg.randomId()    // bigint, never zero
tg.log(...args)
tg.onUnload(callback)
```

```ts
tg.storage.get(key)          // unknown | null
tg.storage.set(key, value)   // boolean
tg.storage.delete(key)       // boolean
tg.storage.keys()            // string[]
tg.storage.clear()           // boolean
```

storage is per script and per account, 16 MB, and survives restarts. values are JSON values; bigints are revived as bigints.

### telegram methods

```ts
const result = await tg.call({ _: 'users.getFullUser', id: { _: 'inputUserSelf' } })
```

`tg.call` sends any method the app knows as the current account. the method needs a `call(<method>)` grant. requests and answers use the TL field names of this build: `_` for the constructor, camelCase fields, `bigint` for 64-bit ids and `{$b: "…"}` on the wire. `null` is returned when the answer has no value. a forbidden call throws `TeleError` with `code: 'not-granted'` and the missing grant.

```ts
const peer = await tg.peers.resolve('@username')
const me = await tg.call({ _: 'users.getFullUser', id: { _: 'inputUserSelf' } })
```

`tg.peers.resolve` accepts a username, a `t.me` link or a numeric id known to the app and returns `{ id, kind, name, username?, input }` or `null`.

### messages

```ts
tg.onNewMessage((message) => {})
tg.onMessageEdited((message, previous) => {})
tg.onMessageDeleted(({ chatId, ids, messages }) => {})
tg.onUpdate((update) => {})
```

`onNewMessage` gets every new message the app sees, including your own (`out` is true). `message.chat` is the peer when the update carries its users and chats; `message.chatId` is always there.

a message exposes `id`, `chatId`, `senderId`, `chat`, `sender`, `text`, `entities`, `textWithEntities`, `date`, `editDate`, `out`, `mentioned`, `media`, `mediaType`, `document`, `photo`, `duration`, `replyToMessageId`, `topicId`, `raw` and the actions:

```ts
message.reply('answer')
message.edit('new text')
message.delete()
message.react('👍')
message.forward(peer)
message.read()
```

the same operations without a message:

```ts
await tg.sendMessage(peer, 'text')
await tg.sendMessage(peer, { text: 'text', entities: [] })
await tg.getHistory(peer, { limit: 50 })
await tg.getMessages(peer, [id1, id2])
await tg.getDialogs({ limit: 100 })
```

`peer` can be a message, a `PeerInfo`, a username, a numeric id, an input peer or `'me'`. sending needs `call(messages.sendMessage)`; history and edits need the matching `call(...)` grants.

### message actions

```ts
tg.registerMessageAction({
  id: 'translate',
  text: 'translate',
  icon: 'message',
  onClick: async (context) => {
    // context: { chatId, messageId, text, date, out }
  },
})
```

the action appears in the long-press menu of a message. `tg.messageAction` is the same function. icons are app icon names: `copy`, `delete`, `edit`, `info`, `link`, `message`, `search`, `settings`, `star`, `stats`, `forward`; an unknown name leaves the item without an icon. the returned disposer removes the action.

### decorating messages

```ts
tg.decorateMessages((message) => ({ footer: 'translated …' }))
await tg.decorateMessage(peer, id, { footer: 'translated …' })
```

a decoration is local to this device. fields are `text`, `footer`, `badge`, `opacity` and `hidden`. `display(messages)` is the grant. `decorateMessage` returns a disposer that removes the decoration.

### network

```ts
const response = await fetch('https://example.com/api', {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ hello: 'world' }),
  timeout: 10_000,
})
const data = await response.json()
```

`fetch` follows at most five redirects, checks the `fetch(<host>)` grant on every hop, has 20/30 second connect/read timeouts, and refuses bodies over 16 MB. it never sends telegram credentials and respects the app's network switches.

### app

```ts
tg.openChat(peer, messageId?)  // needs app
tg.accounts.list()
tg.connection()
```

`tg.openChat` opens a chat or a message. `accounts.list` returns the activated accounts. `tg.connection()` is `1` when the app is connected.

`tg.app.theme.setDark(true)` is the same switch as the day and night toggle in the chat list, with the theme names the user picked; `tg.app.theme.isDark()` reads it (both need `app`).

### intercepting links

```ts
const dispose = tg.interceptLink(({ url }) => 'open')                     // needs interceptLink
const onlyYouTube = tg.interceptLink(/^https:\/\/(www\.)?youtube\.com/, ({ url }) => url.replace('youtube.com', 'yewtu.be'))
```

The interceptor gets the url as it would open now and returns `'open'`, `'drop'` or a new url; anything else (or no answer within half a second) opens the original link. A rewritten url goes on to the next interceptor, and the final one opens. Android runs the interceptors on the script thread, so an answer must be synchronous.

### intercepting notifications

```ts
const dispose = tg.interceptNotification(({ kind, message }) => 'show')       // needs interceptNotification
```

Called before a new message notification is shown: `kind` is `"message"`, `message.mentioned` says whether it mentions you, and returning `'drop'` keeps the notification away while the message stays unread. The message itself is not passed in full yet, and an answer has to be synchronous.

### calls

```ts
const call = tg.calls.current()                          // free
const dispose = tg.calls.onChange((call) => {})          // free
tg.calls.answer(); tg.calls.hangup(); tg.calls.setMuted(true)   // needs calls
```

The call that is going on now, or `null`: `{ state, muted, video, outgoing, user: { id, name } }`, where the state is `incoming`, `ringing`, `waiting` or `established`. `onChange` fires when the call appears, changes state or ends. Starting a call from a script is not available on android yet.

### the player

```ts
const track = tg.app.player.current()                    // free
const dispose = tg.app.player.onChange((track) => {})    // free
tg.app.player.pause()                                    // needs app
```

The app's media player: music files, voice and round video messages, whatever account plays them. `current()` returns `{ type, title, performer, duration, position, playing, chatId, messageId, documentId }` or `null`; `play`, `pause`, `toggle`, `stop`, `next` and `previous` control it. `onChange` fires when the track or its play state changes, and its disposer removes the listener.

### the message field

```ts
tg.compose.onInput(({ chatId, text }) => {})          // needs account.read(draft, peers)
tg.compose.set('replacement')                         // needs account.write(draft)
tg.compose.get()
```

`onInput` runs on every change of the open chat's field, with the chat id and the text as it is now. `set` rewrites the field of the chat that is open (and is not fed back to `onInput`), `get` reads it. The field of another chat is never touched.

### message actions

```ts
const dispose = tg.registerMessageAction({
  id: 'translate',
  text: 'translate',
  icon: 'message',
  chats: 'all',
  onClick: ({ chatId, messageId, text }) => {},
})
```

Adds an item to the long press menu of a message; the context carries `chatId`, `messageId`, `text`, `date` and `out`. `chats` narrows it to `user`, `group`, `channel` or `all`; the disposer takes the item away. No grant is needed: nothing runs until the item is picked.

### showing text

```ts
tg.ui.text({ title: 'translate', text: longText })
```

A dialog with the whole text: scrollable, selectable, with copy. Use it when a toast is too small.

### asking the user

```ts
const code = await tg.ui.prompt({ title: 'code', placeholder: ':code:', maxLength: 32 })
```

A line of text in a dialog; resolves to the value or `null` when the dialog is cancelled. `multiline: true` allows a longer box.

### intercepting shared files

```ts
const dispose = tg.interceptDrop(({ files }) => 'accept')   // needs interceptDrop
```

Called when files are shared into tele from another app, before they reach a chat: `files` are `{ name, size }` (size in bytes, `-1` when unknown). Return `'drop'` to keep them away. Not every way files enter the app goes through it yet; the attach panel is not covered, and an answer has to be synchronous.

### timers

`setTimeout`, `clearTimeout`, `setInterval` and `clearInterval` work, with a minimum interval of 1 ms and a maximum delay of one hour. timers run on the script thread.

### schedule

```ts
const stop = tg.schedule({ daily: '21:00' }, () => tg.app.theme.setDark(true))
const tick = tg.schedule({ every: 60_000 }, () => tg.refresh())
```

`daily` is a local `HH:MM` that fires once a day; `every` is a delay in milliseconds. The disposer cancels it, and a stopped script cancels all of its schedules. Unlike timers, a schedule may wait longer than an hour.

### toast

```ts
tg.toast('saved')
```

Shows for a moment and goes to the notification center with the other tele toasts.

### settings page

```ts
tg.registerSettings(tg.ui.settingsPage({
  title: 'theme scheduler',
  items: () => [
    tg.ui.input({ text: 'night mode from', value: night, placeholder: 'HH:MM', maxLength: 5, onChange: (value) => { night = value; tg.storage.set('night', value) } }),
  ],
}))

tg.ui.check({ text: 'enabled', value, onChange })
tg.ui.slider({ text: 'days', value, min: 0, max: 30, step: 1, onChange })
tg.ui.button({ text: 'reset', onClick })
tg.ui.header('rules'), tg.ui.separator(), tg.ui.item({ text, detail, onClick }), tg.ui.notice('...')
```

The page is built when the app opens it, so the rows always show the current values. A script's page opens from its row in `settings → tele → scripts` (long press): the rows are drawn as a simple list, and every change goes back to the script's `onChange` or `onClick`, which decides what to keep and re-registers the page.

## scripts in this repository

[scripts](scripts/index.json) holds the android ports that run on the current runtime:

- [calculator](scripts/calculator.js): `calculate` in a message menu.
- [away-auto-reply](scripts/away-auto-reply.js): answers a private chat once while away; the `away` message action toggles it.
- [quick-translate](scripts/quick-translate.js): `translate` in a message menu, with the result in the message footer.
- [theme-scheduler](scripts/theme-scheduler/script.js): night mode by the clock; `tg.schedule` switches the theme at two times of the day.
- [link-cleaner](scripts/link-cleaner/script.js): strips `utm_` and the usual click ids from the links you open, plus the parameters you add.
- [quiet-hours](scripts/quiet-hours/script.js): drops message notifications between two hours, mentions still come through.
- [drop-guard](scripts/drop-guard/script.js): keeps programs, scripts and files over a limit out of the chats they are shared into.
- [compose-snippets](scripts/compose-snippets/script.js): expands short codes into text while you type in the message field.
- [music-status](scripts/music-status/script.js): puts the song you listen to into your bio, and gives the normal bio back when the player stops.
- [call-assistant](scripts/call-assistant/script.js): pauses the music when a call connects, mutes you on request and logs the length of the call.
- [quick translate](scripts/quick-translate.js): adds a translate item to the message menu and shows the translation in a dialog.

the other desktop scripts need APIs this build does not have yet:

| desktop script | why it is not here |
|---|---|
| call assistant | there is no calls API |
| music status | there is no music player API |

## what is not here yet

- settings entries, commands, keyboard shortcuts, message-field buttons and profile rows;
- the outgoing-message interceptor, the full message in the notification hook, the attach panel for shared files, and the field of a chat that is not open; keyboard shortcuts are desktop-only.
- calls, the music player, file pickers and file access, and the theme beyond day and night;
- local messages, the widget layer and module imports from `tele`.

## errors and limits

- a script source is at most 2 MB; the runtime has 64 MB of memory and a 1 MB stack.
- the log opens as a screen of monospace lines with their times, like the mtproto log, from the script's menu.
- one runtime per script and account, on its own thread. stopping a script stops its timers, menus, decorations and network requests.
- storage is 16 MB per script and account; the log keeps the last 200 lines.
- setup errors and runtime errors are shown in the script's page and its log; the script stays off after a crash.
