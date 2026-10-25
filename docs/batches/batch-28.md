# Пачка 28 — скриптинг

## Назначение и границы

1. Этот документ — план реализации Android-переноса строк пачки 28 из `docs/PATCHLIST.md`.
2. В объём входят текущие номера desktop-очереди 0302 (в него влиты grant `display` и веб-платформа) и 0329 (иконки пунктов меню скриптов).
3. Номера 0302/0329 — номера desktop, а не будущих Android-файлов `patches/android/`.
4. Android-патчи должны быть отдельными коммитами в Telegram checkout на ветке `tele`.
5. Экспортированные `.patch` нельзя редактировать вручную.
6. Целевой язык fork-кода — Kotlin/Java под `tele/`, native-часть — C++/QuickJS в `TMessagesProj/jni/`.
7. Desktop C++/Qt-код не копировать: переносится поведение и контракт API, не реализация виджетов.
8. По решению мейнтейнера портируется вся подсистема скриптинга, включая веб-платформу (влита в 0302).
9. Это не означает перенос Qt-окон, Monaco, Qt widget API или desktop tray.
10. В Android-версии UI-поверхности должны быть нативными Android, WebView и системными picker-диалогами.
11. QuickJS-ng — исполняемый движок, а не средство дать скрипту доступ к Android VM.
12. Скрипт не должен получать произвольный Java reflection, class-loader или JNI pointer.
13. Сетевой Telegram API доступен через контролируемый TL bridge, а не через прямой native socket из скрипта.
14. Все функции, изменяющие сервер, локальный интерфейс или чувствительные данные, требуют grant.
15. Новые настройки по умолчанию выключены, кроме строк, для которых отдельно принято иное решение.
16. При выключенной настройке код скриптинга не должен менять stock-поток, сеть, UI или хранилище.
17. Не обещать пользователю абсолютную sandbox-безопасность: это сложная native/JS граница, её нужно проверять тестами и аудитом.
18. В документации и UI честно указывать, какие данные grants разрешают читать или менять.
19. Не использовать third-party network без явного пользовательского действия и grant на host.
20. Для web API применять существующий fork-правилом offline/network switch на самом низком слое.
21. Не отправлять аккаунтные данные на tele-server или каталог скриптов.
22. Каталог/обновление скриптов может отдавать только публичный файл, но не должен получать сессию Telegram.
23. Скрипты привязаны к аккаунту; глобальные настройки папки не должны смешивать per-account grants и state.
24. Переключение аккаунта не должно переиспользовать `tg` или permission set другого аккаунта.
25. Один script id и один аккаунт получают отдельный QuickJS runtime и отдельное состояние.
26. Скрипт, выключенный в UI, не запускается от появления файла в папке.
27. В пачке нет виджет-слоя Qt и нет Monaco editor.
28. Текстовый редактор скрипта — внешний редактор пользователя либо системный SAF picker.
29. В пачке нет HTML-пузырей `.tgw`; это зависимая последующая пачка 29.
30. В пачке нет litehtml; 0312–0313 реализуются отдельно после 0302.
31. В пачке нет расширения stock TL schema; схема берётся из сгенерированного Android `TLRPC`/TL-классов.
32. `TLRPC.java` не редактировать.
33. Stock database schema и `LAST_DB_VERSION` не редактировать.
34. Fork preferences хранить через существующий `TeleConfig`/`tele` storage.
35. Fork persistent tables, если понадобятся, создавать только через `TeleDatabaseHelper` с префиксом `tele_`.
36. Кэш, script grants и script logs не помещать в stock таблицы сообщений.
37. Любая новая stock-точка должна быть минимальным gated call в `TeleHooks` или новый `tele_` API.
38. Комментарии в коде не использовать, кроме короткой заметки о реально невыразимом native trap.
39. Статусы PATCHLIST не менять этим документом: статус меняется после commit, export, build и human gate.
40. Этот документ — implementation guide, а не доказательство работоспособности.

## Источники и зафиксированные решения

41. `PATCHLIST.md` описывает batch 28 как QuickJS-ng через NDK, grants, web-платформу, SAF import и отдельный script thread.
42. Ворота PATCHLIST: debug APK, запуск скрипта из папки, consent для `display`, рабочие TL-вызовы и остановка скрипта.
43. `PATCHLIST.md` оценивает пачку как `L×1, S×1` (0302 — L, 0329 — S).
44. 0302 отмечен как прототип scripting с QuickJS, grants, TL и interception hooks; effort L.
45. Grant `display` с consent (прежняя отдельная строка 0303) влит в 0302 на десктопе; в плане — шаг внутри 0302.
46. Web platform и script APIs через `tele_script_*` JNI/Kotlin и OkHttp (прежняя отдельная строка 0320) влиты в 0302 на десктопе; в плане — шаг внутри 0302. Десктопный фикс 0320 (падение при listing accounts из скрипта) учесть в `tg`-мосте.
47. Decisions фиксирует: 0302 портируется полностью, включая grant `display` и веб-платформу; 0329 — отдельная небольшая строка (S).
48. Decisions отдельно фиксирует папку скриптов в app external files dir и импорт через SAF.
49. Decisions отдельно фиксирует отдельный поток скриптов.
50. Portability описывает 0302 как `ConnectionsManager.sendRequest`, `MessagesController.processUpdates` и новый engine.
51. Portability описывает grant `display` как `tele/scripting` permissions/consent внутри 0302.
52. Portability описывает веб-платформу внутри 0302 как fetch, WebSocket, URL, AbortController, crypto.subtle, Intl, Workers, compression и fs.
53. Portability предупреждает, что panels, webview panels, media viewer, group calls и chat UI требуют Android UI решения.
54. `local://desk-5.md` повторяет эти оценки и перечисляет API веб-платформы: stories, gifts, inline, dialogs, files, search, compose, panels и media.
55. `local://desk-5.md` предлагает переиспользовать runtime JS files почти как есть, но `tele_script_*.cpp` переносить через JNI/Kotlin.
56. Desktop `origin/main:docs/scripting.md` описывает QuickJS-ng 0.17 и отдельный engine per script/per account.
57. Desktop documentation описывает ES modules, TypeScript stripping, `defineScript`, generated `tele.d.ts` и off-until-enabled lifecycle.
58. Desktop documentation описывает grants как declared strings, approval per account и runtime `not-granted` checks.
59. Desktop documentation описывает raw `tg.call`, `onUpdate`, `interceptRpc` и `interceptUpdate`.
60. Desktop documentation описывает sensitive-data filtering и takeover filter; Android обязан иметь эквивалент, но не заявлять эквивалентность до аудита.
61. Desktop documentation задаёт ориентиры 16 MB `tg.storage`, 16 MB fetch response, 256 MB script file area и 8 workers.
62. Desktop limits — ориентиры для проектирования, не готовые Android commitments: лимиты надо согласовать с RAM/ABI/device profile.
63. `desktop-numbers.md` подтверждает, что номера PATCHLIST — текущие номера desktop queue.
64. `architecture.md` требует fork-code в новых `tele/` файлах и минимальные stock hooks.
65. `development.md` фиксирует Android SDK 36, NDK `27.2.12479018` и CMake `3.22.1`.
66. `AGENTS.md` требует default-off для новых settings, `TeleConfig`, settings row, search keywords и export/import spec.
67. `AGENTS.md` требует `currentAccount` во всех account-sensitive вызовах.
68. `AGENTS.md` требует UI только на main thread, network hooks на data layer и null-check TL responses.
69. `AGENTS.md` запрещает менять `TLRPC.java` и stock DB schema.
70. [INFERENCE] Desktop grant names должны быть сохранены настолько, насколько Android API может честно обеспечить; неподдержанный scope нельзя silently grant-ить.

## Порядок патчей, subjects, effort и зависимости

71. Внутри 0302 шаги делать в порядке: runtime → grants/display → web platform; 0329 — после 0302.
72. 0302 сначала создаёт runtime, storage, TL bridge, lifecycle и минимальный script manager.
73. Шаг grants/display добавляет consent/grant engine поверх реального 0302 registry, не создаёт второй permission system.
74. Шаг web platform добавляет web platform и API surfaces поверх стабильных bridge/thread/security interfaces.
75. 0302 subject: `feat: add android scripting runtime`.
76. Шаг grants/display, subject: `feat: ask script display grants`.
77. Шаг web platform, subject: `feat: add script web platform`.
78. Subjects — lowercase imperative, максимум пять слов и 50 символов по правилам репозитория.
79. 0302 effort L: native vendor, JNI, runtime lifecycle, TL serialization и update interception.
80. Шаг grants/display, effort M: grant parser, consent UI, per-account persistence и display gate.
81. Шаг web platform, effort L: web globals, OkHttp bridge, worker scheduling, file APIs, WebView bridge и Android API adapters.
82. 0302 зависит от готовых TeleConfig, TeleHooks, settings section, TeleSearch и export/import infrastructure.
83. 0302 зависит от Android stock `ConnectionsManager`, `MessagesController`, `Utilities.stageQueue`, `NativeByteBuffer` и `FileLog`.
84. Шаг grants/display зависит строго от API runtime 0302; нельзя сначала добавлять UI-mock grants.
85. Шаг web platform зависит от QuickJS isolate/thread runtime и от grant checks.
86. Batch 29 depends on script runtime and must not leak `.tgw` rendering into this batch.
87. Runtime 0302 may expose a small API needed by the web platform step, but no speculative UI API without a caller.
88. Each commit must build independently on top of preceding queue commits.
89. Export each commit after its code is committed; Android patch numbering is determined by queue position.
90. `features.md` update is required for user-facing rows in the same repository commit as exported feature patch.

## Опорные точки Android и поток данных

91. `ConnectionsManager.sendRequest` serializes a `TLObject` into `NativeByteBuffer` and dispatches through `Utilities.stageQueue`.
92. `ConnectionsManager.sendRequestTyped` adds typed callback and optional executor but does not expose a generic script API.
93. `sendRequestInternal` deserializes response using the request object's `deserializeResponse` and returns `TL_error` on failure.
94. Native `TgNetWrapper.cpp` allocates `TL_api_request`, invokes native ConnectionsManager and calls Java static completion methods.
95. Native `TgNetWrapper.cpp` registers JNI methods using `RegisterNatives` during `registerNativeTgNetFunctions`.
96. `ConnectionsManager` has per-account instances and native methods all carry `currentAccount`.
97. `MessagesController.processUpdates` is required to run from `Utilities.stageQueue`.
98. `processUpdates` handles short updates, combined updates, seq/pts/qts queues, channel differences and `processUpdateArray`.
99. `processUpdateArray` updates storage/cache and posts UI work through `AndroidUtilities.runOnUIThread`.
100. [INFERENCE] Script update callbacks should observe updates before stock mutation, but must not block the stock stage queue indefinitely.
101. [INFERENCE] A native/JNI hook should copy immutable serialized bytes or a validated TL object before entering QuickJS; never retain a borrowed `NativeByteBuffer`.
102. [INFERENCE] Script requests should use a dedicated request broker that serializes/validates on the script thread and posts actual send to stage queue.
103. Input flow: file scanner → metadata parser → consent check → per-account runtime → script callback.
104. TL call flow: JS plain object → schema lookup → TL object/bytes → account ConnectionsManager → callback → decode/filter → JS promise.
105. Update flow: native/Java receive → update snapshot → interceptors in order → stock `processUpdates` → listeners according to grant.
106. Stop flow: mark runtime stopping → cancel callbacks and timers → detach hooks → finish/cancel pending bridge operations → destroy isolate.
107. UI flow: script callback posts intent/event to main thread → Android presenter validates account and lifecycle → renders settings/menu/command.
108. Storage flow: app external files dir metadata and script files; per-account JSON/SQLite fork state for enabled/grants/storage.
109. SAF flow: ACTION_OPEN_DOCUMENT with MIME filters → persist URI permission only when needed → bounded copy into script directory → keep file off until consent.
110. No script callback may directly touch an Android View or `MessagesController` mutable collection.
111. No TL object received from network may be handed to JS as a mutable alias of stock state.
112. Copy user/chat/message values or create read-only wrappers; mutation must go through explicit API.
113. Every callback carries account id and script id in its dispatch context.
114. Reject stale callbacks after runtime stop, account logout or script replacement.
115. [INFERENCE] A monotonically increasing runtime generation is the simplest stale-callback guard.
116. Use `currentAccount` for every `MessagesController`, `ConnectionsManager`, `MessagesStorage`, `NotificationCenter` and UI navigation call.
117. Long IDs must preserve 64-bit values; expose Kotlin/Java `long` through JS BigInt or documented safe representation.
118. Do not use `Number` for Telegram IDs in serialization or map keys.
119. Null optional TL fields must remain absent/null according to generated schema semantics.
120. Unknown constructors must produce a controlled `TeleError`, not crash native code.

## 0302 — QuickJS-ng через NDK

121. Vendor a pinned QuickJS-ng revision under a dedicated `TMessagesProj/jni/third_party/quickjs-ng/` subtree.
122. Record upstream revision, license and local Android adaptations in the commit message or source manifest.
123. Do not download source during Gradle configuration or an ordinary offline build.
124. Do not use system `libquickjs` or an ABI-specific prebuilt of unknown provenance.
125. Compile QuickJS-ng as a static library for every supported Android ABI.
126. Keep QuickJS compiler flags separate from legacy `tmessages.49` flags where possible.
127. Enable only needed QuickJS-ng features; explicitly decide BigInt, modules, workers, Intl and regexp support.
128. [INFERENCE] QuickJS-ng 0.17 desktop behavior is the compatibility target, but Android vendor revision may differ.
129. Add a `quickjs` CMake target with include dirs scoped to scripting targets.
130. Add a `tele_scripting_jni` object/static target for JNI bridge sources.
131. Link scripting objects into existing `${NATIVE_LIB}` only if symbol visibility and lifecycle are controlled.
132. Prefer an object library to avoid archive extraction dropping JNI exports, as current wallet bridge does.
133. Do not add a second shared native library unless Java loader and ABI packaging justify it.
134. Add `-fvisibility=hidden` by default and export only explicit JNI registration symbols.
135. Build with C++17 unless a QuickJS API requires a narrower standard; do not alter all legacy JNI sources.
136. Avoid exceptions crossing JNI; translate native errors to Java `TeleError`/status objects.
137. Check `JNIEnv*` belongs to the calling thread; attach the dedicated script thread once and detach at shutdown.
138. Never call Java UI methods from the QuickJS thread directly.
139. Use global references only with explicit ownership and release on runtime destruction.
140. Bound JS string/array/object conversion sizes before allocating native buffers.
141. Bound recursion depth when converting TL objects into JS and JS objects into TL.
142. Detect cycles in JS values where JSON/TL conversion cannot represent them.
143. Use arena or per-call temporary allocations and free them after one bridge call.
144. Do not retain `JSValue` handles after a runtime is destroyed.
145. Store per-isolate opaque context with script id, account id and generation.
146. Set interrupt handler for instruction/time budget and runtime stop.
147. Interrupt handler must be cheap, thread-safe and free of JNI calls.
148. Set memory limit per isolate and expose a controlled out-of-memory error.
149. Set stack size/recursion limit suitable for low-memory Android devices.
150. Disable eval only if compatibility analysis proves it is safe; do not claim that disabling eval is a complete sandbox.
151. Disable shared mutable globals between isolates.
152. Give each worker a separate isolate and explicit message channel; no pointer sharing.
153. Workers must be joined or cancelled before parent runtime destruction.
154. Worker count and total memory require hard per-script/account caps.
155. Promise jobs must be drained on the script thread, never on the stage queue.
156. Timer callbacks run only through script scheduler and are removed at stop.
157. Native callback queues must drop events after generation mismatch.
158. Log every runtime creation/destruction with account/script id but never source, tokens or message contents.
159. [INFERENCE] Runtime thread priority should be background/default, never UI priority.
160. [INFERENCE] Android process death may interrupt cleanup; startup must detect stale runtime metadata and recover without replaying grants.

## 0302 — module loading, scripts folder and lifecycle

161. Default root is `context.getExternalFilesDir(null)/scripts`.
162. This is app-private external storage, not a public shared `Telegram/` folder.
163. Do not request MANAGE_EXTERNAL_STORAGE for the default root.
164. Do not expose the app external files path as a public share URL.
165. Create the folder lazily from Scripts manager or explicit Open folder action.
166. Scan only top-level `.js`, `.mjs`, `.ts`, `.mts` and folders with `index.js`/`index.ts`.
167. Ignore dot/underscore entries, `node_modules` scanning as scripts, generated typings and unknown extensions.
168. Resolve relative imports only inside the script root or permitted script `node_modules`.
169. Refuse `..` traversal after canonical path resolution.
170. Treat symlink/path escape as an import error; Android external files behavior must be tested.
171. Generate `tele.d.ts` from the exact Android API schema and write it atomically.
172. Generate `tsconfig.json` only when absent; never overwrite user edits.
173. Implement type stripping only if an existing embeddable stripper is vendored and audited.
174. [INFERENCE] A small Android-first JS subset may ship before full desktop TypeScript parity, but this must be an explicit unresolved decision, not a hidden fallback.
175. A script entry must export `defineScript({ name, grants, setup })` as default.
176. Parse static metadata without executing code while a script is off.
177. Metadata parsing must have a bounded byte limit and reject dynamic code as metadata.
178. New script starts disabled for every account.
179. `enabled`, grants and script storage keys are per account.
180. A script folder change stops all account runtimes before rescanning.
181. Hot reload stops old generation then starts a fresh isolate after debounce.
182. Reload must not preserve JS object identity or native handles.
183. Preserve explicit storage across reload, but not transient callbacks or timers.
184. A failed start remains off/running-error and may retry after file change.
185. Five consecutive handler faults should turn a script off, matching desktop guidance where feasible.
186. [INFERENCE] Exact timeout and five-failure thresholds need Android device testing and must be constants in one runtime policy.
187. Logout stops only that account's runtime and revokes its in-memory handles.
188. Removing a script removes/archives files only after explicit confirmation.
189. Script manager must show path/id, status, last error and last start time.
190. Script log retains bounded lines and redacts sensitive bridge payloads.

## TL bridge и сгенерированная schema

191. The bridge must not hand `TLRPC.java` generated classes directly to arbitrary JS.
192. Build a schema descriptor from generated TL method/class metadata or a checked-in generated descriptor.
193. Descriptor includes methods, constructor names, fields, types, flags and result type.
194. [INFERENCE] If generator metadata is unavailable at runtime, generate a compact descriptor at build time from the same TL source.
195. Keep schema descriptor versioned with the Android `TLRPC` layer and `tele.d.ts`.
196. A method request is a JS object with `_` equal to a dotted method name.
197. Field names may use the documented camelCase mapping; reject unknown required fields rather than silently dropping them.
198. Encode TL on the script thread into an owned native buffer.
199. Validate method grant before sending bytes to `ConnectionsManager`.
200. Resolve default DC/current account from bridge context; allow explicit DC only under policy.
201. Use existing `ConnectionsManager.sendRequest`/typed path rather than duplicating MTProto transport.
202. Set request flags deliberately; do not inherit upload/download behavior accidentally.
203. Completion callback copies response bytes before crossing into script thread.
204. Decode according to method result descriptor and return plain JS objects with `_` tags.
205. Decode `TL_error` into a stable `RpcError` shape with code/type/message.
206. Handle constructor mismatch and truncated response as bridge errors with method/path context.
207. Limit nested TL depth and vector lengths before allocation.
208. Limit bytes/string sizes before constructing JS values.
209. For updates results, route through the same update pipeline contract as stock requests.
210. Explicitly decide whether a script `tg.call` result is delivered to that script's own update listeners.
211. Do not let a script's own request recursively enter its own interceptor chain without a guard.
212. Account protection must block auth/session/password/login-code methods by default.
213. Dangerous methods (delete, leave, payment, account destruction) require exact grants, not broad globs.
214. `unsafe.disableApiFiltering` must be explicit, conspicuous and never implied by `call`.
215. Sensitive-data filtering must cover login-code service messages and draft content as applicable.
216. Do not log raw TL request/response bytes in normal logcat.
217. Debug TL logging requires a separate developer switch and redaction.
218. Expose generated schema typings to scripts but never let typings bypass runtime validation.
219. `tele.d.ts` must describe Android-supported API, not desktop-only methods that throw at runtime.
220. Unsupported methods must return a stable `unsupported` error and explain the missing Android surface.
221. [INFERENCE] A schema hash in bridge handshake will detect stale `tele.d.ts` after app update.
222. Bridge tests must round-trip representative `messages.*`, `users.*`, `updates.*`, `upload.*` and a bytes field.
223. Include flags, optional fields, vectors, 64-bit ids, empty bytes and null response cases.
224. Test server errors, migration, flood wait and cancellation without requiring a user account in unit tests.
225. Test account 0 and a nonzero account to catch singleton leakage.

## Updates и interception hooks

226. Add one central `TeleHooks` entry around `ConnectionsManager` response/update delivery, not dozens of UI hooks.
227. Add a minimal hook before stock `MessagesController.processUpdates` receives a validated update batch.
228. Preserve stock seq/pts/qts/channel-difference ordering regardless of script latency.
229. [INFERENCE] A serial update broker should queue snapshots and resume stock processing after interception.
230. Never execute unbounded JS synchronously on `Utilities.stageQueue`.
231. If an interceptor times out, deliver the original update and continue stock processing.
232. If an interceptor crashes, log a redacted fault and deliver original data unless explicit drop policy is safe.
233. Dropping an update must preserve pts/qts sequence semantics or force correct difference recovery.
234. Do not invent empty delete updates without verifying Android's sequence bookkeeping.
235. Interceptor order should be deterministic: script folder order then registration order.
236. Registration/disposal must be generation-aware and idempotent.
237. `onUpdate` listeners receive snapshots after approved interceptor mutations and before/after stock according to documented contract.
238. Pick one contract and test it; do not expose both ambiguous pre/post states.
239. Short updates must be normalized consistently with full `TLRPC.Updates` containers.
240. Difference updates from `getDifference` and `getChannelDifference` must follow the same policy.
241. Updates emitted by local actions must be marked so scripts can avoid feedback loops.
242. Script-created TL calls should not deadlock against update interception.
243. Intercepted RPC requests need a hold/next/result contract with a hard deadline.
244. A stopped script releases held requests: continue original request, or fail safely according to operation type.
245. Never silently swallow a held send request because a script stopped.
246. Requests from one chat must preserve stock ordering if interception is enabled.
247. Unrelated accounts and unrelated methods should not be serialized behind one slow script.
248. `interceptSendMessage` must run before final serialization only if stock object ownership is safe.
249. [INFERENCE] First implementation may expose RPC interceptors only after immutable request-copy path is proven.
250. UI interceptors (link, notification, drop) must be downstream of Android native event and upstream of action, with explicit verdicts.
251. A verdict outside the enum is a fault and must fall back to stock action.
252. Update/interceptor budgets belong to runtime policy and must appear in diagnostics.
253. Log queue length, wait time, timeout and fallback category, not payloads.
254. Test rapid updates, update bursts, channel difference and process death while a hook is pending.
255. Test off state: no hook registration and identical stock output.

## 0302 (шаг) — grants, consent и display

256. Implement one canonical grant parser and matcher in `tele/scripting`.
257. Grant declarations are strings, normalized for whitespace and validated against known names/scopes.
258. Unknown grant names must not silently become powerful access.
259. Invalid known scope must fail start with a visible error.
260. Match host grants by exact host/subdomain boundary, not string suffix alone.
261. Match TL grants against schema methods and exact dangerous-method list.
262. Match update grants against constructor names and supported short event names.
263. Match file grants against canonical root paths after resolving `..`.
264. Store approved grants per script id and account id.
265. Store only the normalized grant set; never infer approval from enabled state.
266. Turning a script off forgets approved grants, while script storage may remain.
267. Editing a running script to add grants stops it and enters waiting-for-approval.
268. Removing a grant restarts the script only after revalidation.
269. Consent dialog lists every declared grant in plain Russian/locale text.
270. Dangerous grants appear in a separate warning section.
271. Consent text must say whether data leaves device, reaches Telegram, writes files or changes display.
272. `display(messages)` is the first mandatory gate in the batch gate.
273. Display consent must cover message decorations, local message insertion and peer appearance overrides.
274. Display grant does not permit server writes.
275. A script with display grant still cannot forge Telegram server data in TL responses.
276. `display` denial leaves script stopped/off with no partial registration.
277. Add Review permissions action in script page for missing grants.
278. Add revoke action that removes approval and stops script.
279. Consent UI runs on main thread and is account-scoped.
280. Consent callback returns to script thread only if runtime generation is still current.
281. Do not show secrets or raw URLs beyond necessary host/scope in consent text.
282. [INFERENCE] Grant names should start with desktop-compatible `display`, `call`, `onUpdate`, `interceptRpc`, `interceptUpdate`, `fetch`, `fs.read`, `fs.write` and `unsafe.*`.
283. [INFERENCE] Android-only grants may be needed for SAF import, notifications and WebView; document them as Android extensions.
284. No grant should mean unrestricted Java/Android filesystem access.
285. Test consent Cancel, back, outside tap, rotation, process background and account switch.
286. Test declared grant narrowing/widening and an unknown grant after app update.
287. Test dangerous method exact grant versus wildcard grant.
288. Test display grant off/on with a message decorator and verify no server mutation.

## 0302 (шаг) — web platform и API скриптов

289. Implement URL/URLSearchParams with a standards-tested JavaScript/native implementation.
290. Implement AbortController and cancellation propagation to OkHttp calls.
291. Implement `fetch` through OkHttp or existing fork HTTP stack, never raw unrestricted `HttpURLConnection` per script.
292. Require `fetch(host)` grant before DNS/connect and again for each redirect host.
293. Permit only http/https URLs; reject file/content/data URLs unless an API explicitly needs them.
294. Bound timeout, response bytes, headers, redirects and concurrent requests.
295. Do not provide streaming response until backpressure and cancellation are designed.
296. Expose response status, headers, text, JSON and bytes with copies.
297. Redact Authorization, cookies and Telegram session headers from logs.
298. Do not attach Telegram auth headers/cookies to script fetch.
299. Use proxy/offline policy consistently with other tele network requests.
300. Implement WebSocket only if OkHttp WebSocket lifecycle can be cancelled on stop.
301. Bound message size, connection count and idle lifetime.
302. Implement `crypto.subtle` only with platform primitives whose key export/import semantics are explicit.
303. Never expose Telegram auth keys, SRP secrets or Android keystore handles to JS.
304. Implement random bytes with secure platform RNG and per-call output limit.
305. Implement `Intl` via ICU bridge or a vetted JS implementation; locale data size needs a cap.
306. Implement compression with bounded output and no unbounded decompression bomb.
307. Implement `TextEncoder`, `TextDecoder`, URL, EventTarget, AbortSignal and structured clone as required globals.
308. Do not claim browser DOM globals; no `window`, `document`, `navigator` or unrestricted `localStorage` in QuickJS.
309. Workers use dedicated isolate/thread plus message ports; no imports unless bundled policy supports them.
310. Worker stop must resolve/reject pending messages deterministically before isolate destruction.
311. Worker cannot call Android UI or `ConnectionsManager` directly.
312. `tg.storage` is serialized per script/account and bounded; no arbitrary Java serialization.
313. `tg.fs` is script-private file area under external files dir, with canonical path checks.
314. `fs.read`/`fs.write` grants are required outside the private area or for sensitive paths.
315. `tg.fs` must refuse `../`, symlink escapes and paths resolving into app databases.
316. Add file count, total bytes and per-file size limits.
317. Add atomic write/rename and recovery from interrupted writes.
318. `tg.ui.webview` may load inline HTML or approved HTTPS URL only.
319. WebView must use a separate profile/storage namespace per script/account.
320. WebView bridge exposes JSON messages only; no `tg` object or Java object injection.
321. Disable file access, universal access, intent interception and arbitrary downloads by default.
322. Apply CSP and navigation host policy derived from fetch grants.
323. WebView `postMessage` must reject BigInt, cycles and oversized payloads.
324. Stop closes WebView panels and removes message callbacks.
325. [INFERENCE] WebView panels may be delivered as modal `BottomSheet`/fragment rather than desktop window; choose one Android pattern before implementation.
326. Web platform API surfaces for stories/gifts/inline/search/compose must call existing Android controllers.
327. Unsupported desktop surfaces (Qt widgets, tray, desktop media window) return `unsupported` rather than fake success.
328. Commands, menus, shortcuts and settings pages use native `tele/ui` registrations.
329. Every registration returns a disposer and is removed at stop/reload.
330. Commands must run on script thread, then post send/UI work through validated bridge.
331. Menu visibility callbacks have bounded synchronous budget and safe stock fallback.
332. Settings pages are generated from native row builders, not arbitrary View pointers.
333. Script-added rows cannot inject arbitrary resource ids, fragments or intents.
334. File import from SAF is user-selected and must not require broad filesystem permission.
335. URI copy must be bounded, MIME-checked and atomic; reject executable/native libraries by default.
336. Imported script remains off until user explicitly enables it and consents.
337. [INFERENCE] Link-installed update support should be postponed until signature/version policy is decided; do not download-and-run as part of the web platform core.
338. If link updates are included, verify HTTPS, size, redirect grants, version and digest before replacing file.

## Хранилище, SAF и external files dir

339. Resolve root with `ApplicationLoader.applicationContext.getExternalFilesDir(null)` and null-check it.
340. Use a stable child directory, for example `tele/scripts`, not a public Telegram media directory.
341. Per-account data should be under `tele/script_state/account_<id>/` or `tele_*` database records.
342. Script source itself is global folder content; enabled/grants/storage are account-specific.
343. Prevent account id path injection by encoding numeric account index only.
344. Keep `tele.d.ts`, `tsconfig.json`, script source and generated metadata separate.
345. Scanner must ignore temporary files and partial SAF copy names.
346. Copy to `<name>.part`, fsync/close, validate, then atomic rename.
347. Validate UTF-8, extension, maximum source size and module metadata before indexing.
348. Do not execute a source file while it is being copied.
349. SAF import uses `Intent.ACTION_OPEN_DOCUMENT`, `CATEGORY_OPENABLE`, and `text/*`/`application/javascript` filters with All files fallback.
350. Read through `ContentResolver.openInputStream`, not a path assumption.
351. Verify returned display name and extension independently; URI name is untrusted.
352. Do not persist URI permission unless a later feature needs a source URI; copied scripts do not need it.
353. Show replace confirmation if target script id already exists.
354. Keep old source until new source validates and atomic replacement succeeds.
355. If import fails, leave current script and grants untouched.
356. A script's private file area must not be the source root unless explicitly designed that way.
357. Clear storage action must report bytes/keys and require confirmation.
358. Storage quota failure must be recoverable without corrupting prior values.
359. Do not include source contents or storage values in crash reports by default.
360. [INFERENCE] External-files storage can be removed by Android when app is uninstalled; UI should describe this and offer user export through SAF.
361. Exporting a script source is user initiated; export grants no account data unless the user selects it.
362. Export/import of Tele settings must include script settings only if the existing spec explicitly supports script grants safely.
363. Never import approved grants silently from another device/account.

## Выделенный поток скриптов и границы песочницы

364. Создать один поток-планировщик процесса или ограниченный пул, с отдельной очередью исполнения isolate для каждого runtime.
365. Не выполнять JS в main thread, `Utilities.stageQueue`, storage queue или потоке callback нативной сети.
366. Использовать blocking queue/event loop для JS-задач, таймеров, promise jobs и completion bridge-вызовов.
367. UI-callback ставит задачу в main thread и возвращает результат в script thread через future, если это нужно API.
368. Callback stage queue копирует данные и ставит JS-задачу в очередь; он никогда синхронно не ждёт JS.
369. Для каждой JS-задачи действует CPU/time budget и interrupt handler.
370. Блокирующий скрипт не должен замораживать UI Telegram или обработку MTProto.
371. Для обновлений нужна backpressure: ограниченная очередь, допустимое coalescing только при сохранении семантики, иначе безопасный fallback с диагностикой.
372. Cancellation token проверяется на границах bridge и перед каждым callback.
373. При остановке runtime сначала выставляется cancellation, затем снимаются native hooks, чтобы новая работа не входила в runtime.
374. Worker threads присоединяются с timeout; аварийное завершение логируется без блокировки UI.
375. JSValue уничтожается только в потоке-владельце.
376. JNI local references освобождаются в циклах, особенно при TL-векторах и пакетах обновлений.
377. Каждый JNI-вход проверяет null, тип, длину и принадлежность аккаунту.
378. Native pointers непрозрачны и никогда не сериализуются в JS.
379. JS не может выбирать произвольные имена Java-методов или классов.
380. JS не запускает shell-команды; `unsafe.exec` не входит в Android-пачку без отдельного review.
381. Android sandbox действует на уровне процесса и не является границей безопасности против вредоносного native-кода внутри APK.
382. Изоляция памяти QuickJS не гарантирует защиты от native memory corruption.
383. WebView sandbox и QuickJS sandbox различны; обе границы нужно описать отдельно.
384. Grants ограничивают заявленный API-доступ, но не заменяют code review, hardening и OS permissions.
385. Импортированный скрипт считать непроверенным кодом и явно показывать это в consent UI.
386. Не называть функцию «безопасной» без evidence из threat model и fuzz-тестов.
387. Threat model включает вредоносный source, скомпрометированный update-host, malformed TL, вредоносные server data и hostile WebView content.
388. Threat model включает переключение аккаунта, logout, process death, low memory, rotation и удаление external storage.
389. Threat model включает native fuzz input, integer overflow, path traversal, symlink race и decompression bomb.
390. Использовать fuzz/property tests для TL conversion, grant matching, canonical paths и JSON bridge.
391. Использовать ASAN/UBSAN для native unit/fuzz targets, если это поддерживается NDK-сборкой.
392. В debug включить StrictMode и проверки неверного main-thread/JNI использования.
393. Не выпускать debug bypass для grants, path checks или account protection.
394. Диагностический switch может логировать имена методов и размеры, но обязан redacted-ить значения и secrets.
395. [INFERENCE] Изоляция каждого скрипта в отдельном процессе, вероятно, слишком дорога для этого fork; при отказе явно записать residual risk.
396. [INFERENCE] SELinux/Android app sandbox защищает процесс от других приложений, но не скрипт от native bugs.
397. Security review обязателен до link-installed updates или широких `fs` grants.
398. Security review нельзя заменять успешным unit-test suite.

## Настройки, OFF-поведение и search IDs

399. Добавить Scripts в существующую структуру Tele settings, не создавать новую верхнеуровневую Android settings section.
400. Добавить master `TeleConfig.SCRIPTING` со значением `false`, если нужна общая opt-in ограда.
401. Если master gate не нужен, каждый script всё равно должен быть индивидуально выключен по умолчанию; выбор описать в коде и UI.
402. Master OFF должен запрещать создание runtime, watcher папки и script network traffic.
403. Individual OFF останавливает runtime, снимает registrations и оставляет stock UI/network неизменными.
404. Добавить строки Scripts, Open scripts folder, Import script и clear script state, если они нужны выбранной UX-модели.
405. Описать per-account grants, расположение файлов, network access и риск непроверенного source.
406. В export/import включать только non-secret script preferences; approved grants не экспортировать автоматически.
407. Для entries и keywords этой пачки использовать только search IDs 1440–1459.
408. [INFERENCE] Зарезервировать 1440 под «Scripts», 1441 под «script manager», 1442 под «import script», 1443 под «open scripts folder».
409. [INFERENCE] Зарезервировать 1444 под «script permissions», 1445 под «grants», 1446 под «display», 1447 под «consent».
410. [INFERENCE] Зарезервировать 1448 под «QuickJS», 1449 под «JavaScript», 1450 под «TypeScript», 1451 под «TL API».
411. [INFERENCE] Зарезервировать 1452 под «web platform», 1453 под «fetch», 1454 под «WebSocket», 1455 под «workers».
412. [INFERENCE] Зарезервировать 1456 под «script files», 1457 под «SAF», 1458 под «external files», 1459 под «sandbox».
413. Перед изменением кода сверить каждый предложенный ID с реальным registry `TeleSearch`.
414. Не создавать duplicate search IDs, если текущий registry назначает один ID на keyword group.
415. Search result должен вести на Scripts page и сохранять account context.
416. Settings UI работает в main thread, а manager state использует `currentAccount`.
417. Child rows скрывать при OFF master/parent, если это поддерживает текущий settings framework.
418. «OFF» должен проверяться после cold start, а не только сразу после переключения.

## Native build, vendor и CMake

419. Добавить QuickJS sources в CMake ровно один раз и только для поддерживаемых ABI.
420. Проверить, что `ANDROID_ABI` согласован с существующей схемой `prebuild/lib/${ANDROID_ABI}`.
421. Добавлять include path до compile target, а не глобально ко всем legacy targets.
422. Добавить quickjs library перед scripting bridge в link order, если это требуется static symbols.
423. Сохранить совместимость `-Wl,--gc-sections` и hidden visibility с нужными JNI registration symbols.
424. Если LTO ломает QuickJS setjmp/longjmp или retention symbols, изолировать flags quickjs-target и документировать причину.
425. C++ source не должен зависеть от desktop Qt, glib или недоступных на Android filesystem APIs.
426. `AAssetManager` использовать только для bundled immutable runtime assets; source остаётся в external-files/SAF.
427. JS runtime files в `res/raw`/assets добавлять только с license, version и immutable policy.
428. `tele.d.ts` генерировать из той же schema revision, что использует native bridge.
429. Gradle packaging rules для native symbols добавлять только если они нужны debug crash diagnosis.
430. Release build не должен содержать unrestricted native debug entry points.
431. На batch gate собрать все ABI splits, не только arm64.
432. Как минимум проверить arm64-v8a и один 32-bit ABI, если он настроен проектом.
433. Проверить отсутствие duplicate `libc++_shared.so` и QuickJS symbol collision.
434. `nm`/link diagnostics применять только к build artifacts при расследовании exports; private symbols не открывать без причины.
435. Native methods регистрировать одним контролируемым initializer и ясно падать при ошибке регистрации.
436. Добавить в CMake compile definition scripting version/schema hash, а не вычислять guessed constant в runtime.
437. Положить vendor license/notice в место, требуемое policy проекта.
438. `assembleDebug` никогда не должен скачивать QuickJS source.
439. [INFERENCE] Маленький native unit target может запускать host-side helpers TL/grants, но QuickJS ABI всё равно проверяется Android instrumentation tests.
440. [INFERENCE] NDK 27.2 может требовать patch deprecated C APIs; такие patches держать минимальными и upstreamable.

## Нерешённые вопросы перед реализацией

441. [INFERENCE] Нужен ли в batch 28 полный desktop TypeScript stripping или допустим JavaScript-first до выбора проверенного stripper?
442. [INFERENCE] Какой QuickJS-ng commit точно соответствует desktop 0.17 и Android license/vendor policy?
443. [INFERENCE] Должен ли весь JS использовать один process thread или каждый worker получает отдельный thread с hard cap?
444. [INFERENCE] Какие CPU, memory, source-size, file-size и callback budgets допустимы на low-RAM devices?
445. [INFERENCE] Должен ли `tg.call` сразу принимать arbitrary TL methods или сначала работать через audited allowlist?
446. [INFERENCE] Какая update point authoritative для interception: до `processUpdates`, после sequence validation или обе точки разными API?
447. [INFERENCE] Как представлять dropped `pts`/`qts`, чтобы не запускать нежелательные `getDifference` loops?
448. [INFERENCE] Какую Android WebView presentation выбрать для веб-платформы: fragment, bottom sheet или full-screen activity?
449. [INFERENCE] Нужны ли WebSocket и crypto.subtle в первом commit веб-платформы или временно explicit `unsupported` errors?
450. [INFERENCE] Входят ли stories, gifts, calls, media viewer и inline results в первую Android API schema или требуют последующих UI patches?
451. [INFERENCE] Какое user-facing warning нужно для SAF scripts по сравнению с trusted source?
452. [INFERENCE] Для source updates нужны signature verification, pinned key, digest или только explicit file replacement?
453. [INFERENCE] Grants отзываются при каждом restart, только logout или сохраняются per script/account как на desktop?
454. [INFERENCE] Допустим ли public export script + settings без grants и какие значения исключаются?
455. [INFERENCE] Какие Android offline switches являются обязательным lowest-level gate для OkHttp fetch?
456. [INFERENCE] Каковы точные logcat tags и redaction policy для script faults и native crashes?
457. [INFERENCE] Перенесёт ли stock update processing asynchronous interception без изменения sequence queues?
458. [INFERENCE] Поддерживает ли текущий WebView CSP и JS bridge restrictions на всех minSdk devices?
459. [INFERENCE] Какие search IDs 1440–1459 свободны непосредственно перед реализацией?
460. Не решать вопросы скрытым уменьшением объёма; ответы занести в decisions/PATCHLIST после решения мейнтейнера.

## Тестовая стратегия и logcat evidence

461. Unit-test grant parser, scope matcher, host boundary, dangerous-method classification и canonical paths.
462. Unit-test schema lookup TL и encode/decode round trips с optional flags и vectors.
463. Unit-test account isolation для account 0 и account 1 с одинаковым script id.
464. Unit-test runtime-generation cancellation и отклонение stale callbacks.
465. Unit-test storage quota, atomic replacement и восстановление corrupted metadata.
466. Unit-test SAF name/extension validation и очистку partial copy.
467. Native-test QuickJS isolate create/evaluate/interrupt/destroy для каждого практически доступного ABI.
468. Native-test malformed UTF-8, deep objects, huge arrays и cyclic JS values.
469. Instrumentation-test scanner, default external-files root и отсутствие public-storage permission.
470. Instrumentation-test import `.js`, `.mjs`, `.ts` и folder script; неизвестное расширение отклонять.
471. Instrumentation-test: после import и process restart script остаётся OFF.
472. Instrumentation-test базовые `defineScript` start, log, timer, stop и reload.
473. Instrumentation-test один script на двух аккаунтах и отдельные `selfId`, storage и grants.
474. Instrumentation-test display consent Cancel/Allow и отсутствие decorator до Allow.
475. Instrumentation-test TL read call на test account, malformed method, server error, cancellation и timeout.
476. Instrumentation-test `onUpdate` для new message, edit, delete, short update и channel update.
477. Instrumentation-test interceptor fallback при exception или превышении budget.
478. Instrumentation-test update bursts/channel difference не замораживают UI и не теряют stock sequence.
479. Instrumentation-test `fetch` для allowed host, denied host, redirect к denied host и timeout.
480. Instrumentation-test отсутствия Telegram auth headers/cookies у script HTTP.
481. Instrumentation-test WebSocket stop/close и message-size limit, если API включён.
482. Instrumentation-test worker start, message, cancellation, limit и parent stop.
483. Instrumentation-test private fs root, traversal, symlink, quota и atomic write.
484. Instrumentation-test inline WebView, JSON bridge, blocked navigation и stop cleanup.
485. Instrumentation-test commands, message menu, settings page и disposer после reload.
486. Instrumentation-test master OFF и individual OFF относительно stock baseline.
487. Manual gate: создать `hello.js`, импортировать SAF, включить, Allow только нужные grants, получить log/TL read и остановить.
488. Manual gate display: запросить `display(messages)`, нажать Cancel, проверить отсутствие decoration, затем Allow и локальное отображение.
489. Manual gate network: fetch allowed endpoint и denied endpoint; проверить grant errors и redacted log.
490. Manual gate update: изменить file, проверить stop старого runtime, start нового, сохранение storage и ожидание нового grant.
491. Manual gate account: включить один script на двух аккаунтах и проверить независимое состояние.
492. Manual gate process: background/kill/restart; persisted state не создаёт duplicate hooks.
493. Manual gate storage removal: uninstall/reinstall или clear external files; missing scripts не должны ронять UI.
494. Использовать `adb logcat` с фильтрами `TeleScript`, `TeleQuickJs`, `TeleScriptJni`, `ConnectionsManager`, `MessagesController`, `TeleHooks`.
495. Добавить log lines для runtime generation, account, script id, event type, queue latency и fallback reason.
496. Никогда не логировать source, TL payload values, message bodies, auth codes, cookies, bearer tokens и secret/private-key paths.
497. Native errors должны содержать operation и ABI, но не raw pointers и full buffers.
498. В debug собирать symbolized QuickJS/JNI crash stacks; отсутствие crash в ручном прогоне не является security evidence.
499. Denied-grant log содержит только API category и normalized missing grant.
500. Timeout log содержит script id, callback category, elapsed budget и stock fallback.
501. Stop log содержит generation invalidation, pending count и continued/cancelled outcome.
502. Проверить отсутствие `NetworkOnMainThreadException`, `CalledFromWrongThreadException`, JNI local-ref overflow и ANR.
503. Проверить отсутствие `FATAL EXCEPTION` от malformed source или malformed TL.
504. Проверить отсутствие duplicate registrations после reload подсчётом command/menu/update callbacks.
505. Проверить отсутствие account-0 callbacks при работе с account 1.
506. Проверить живость stage queue, пока script sleep/loop до interrupt или await network.
507. Проверить отзывчивость UI при large TL decode, file import и WebView creation.
508. Зафиксировать device/API/ABI, build counter, source hash и settings state в результатах gate.

## Ворота пачки, документация и передача результата

509. До gate все commit скриптинга (runtime, grants/display, web platform) и 0329 должны быть применены к ветке `tele` checkout `Telegram` и экспортированы.
510. Запустить `./gradlew :TMessagesProj_App:assembleDebug` со всеми настроенными ABI splits.
511. Установить соответствующий debug APK на device или emulator; compilation сама по себе не доказывает успех.
512. Проверить scripting ON/OFF, account isolation, grant consent, TL call, update listener и stop.
513. На clean install проверить SAF import и default app external-files path.
514. В manual flow проверить redaction log и отсутствие ANR/native crash.
515. Передать мейнтейнеру нумерованный manual test list и точный APK ABI path.
516. Отметить PATCHLIST `built` только после assemble и передачи APK.
517. Отметить `done` только после human verification gate, не после agent inspection.
518. Добавить в `features.md` по одной English row для каждой user-facing scripting setting/API surface.
519. В каждой row указать location, default, Android patch file и desktop number 0302 (и 0329 для иконок меню).
520. Честно описать grants и риск imported code; не называть feature secure без evidence.
521. Обновить export/import spec для каждой persisted non-secret script setting.
522. Не экспортировать approved grants, tokens, source digests или account data без отдельного reviewed format.
523. В PATCHLIST записывать только наблюдаемый implementation/status и unresolved decisions.
524. Сохранять метки [INFERENCE] там, где design anchor остаётся предположением.
525. Native build failure на одном ABI блокирует batch gate; ABI set нельзя молча сужать.
526. Failed OFF test блокирует gate: default-off обязан быть точным stock behavior.
527. Failed consent test блокирует gate: grant UI — security control, а не cosmetic UI.
528. Failed TL/update sequence test блокирует gate: недопустимы data loss и stale state.
529. Failed redaction test блокирует gate: logs являются частью privacy surface.
530. Никаких fake security assurances: при APK hand-off сообщить остаточные threat-model gaps и unresolved questions.

## 0329 — иконки пунктов меню скриптов

531. Desktop 0329: скрипт задаёт иконку своему пункту меню. Перед кодом открыть `tele/patches/tdesktop/0329-feat-let-scripts-give-their-menu-items-icons.patch`.
532. PATCHLIST: строка 0329, S, зависит от 0302 (скриптинг); делается после 0302.
533. Иконка задаётся полем пункта в API меню скриптов; допустимые значения — имена из фиксированного набора stock-иконок Android (`R.drawable.msg_*`), произвольные ресурсы и URL запрещены.
534. Неизвестное имя иконки — пункт без иконки, без исключения в скрипт и без падения.
535. Показ иконки — только в нативных меню Android (`ActionBarMenuItem`), на main thread; данные иконки хранятся вместе с описанием пункта в registry скриптов.
536. Иконка не должна давать скрипту доступ к ресурсам вне набора и не меняет grants: отдельного grant для иконок нет, если desktop-патч его не вводит.
537. OFF-поведение: при выключенном скриптинге пунктов и иконок нет; stock-меню без изменений.
538. Проверка на устройстве: скрипт добавляет пункт с иконкой, иконка отображается, неизвестное имя даёт пункт без иконки.
