# Пачка 21 — уведомления, загрузки и система

## 1. Назначение и границы

1. Этот документ описывает ровно состав пачки 21 из `docs/PATCHLIST.md`.
2. Состав: 0155, 0158, 0138, 0137, 0262, 0222 и 0070.
3. Номера — текущие номера очереди desktop, не старые номера v7.2.9.
4. Проверять соответствие номеров по `docs/desktop-numbers.md` перед экспортом.
5. Desktop-источник читается через `git show origin/main:patches/tdesktop/<patch>`.
6. Android-якоря читаются через `git show tele:<path>` в checkout `Telegram`.
7. Desktop C++/Qt не копировать: переносится наблюдаемое поведение через Android API.
8. Статус строк и ворота остаются в `docs/PATCHLIST.md`.
9. Этот файл является планом реализации, а не доказательством готовности.
10. Все новые пользовательские переключатели имеют default OFF.
11. OFF обязан давать ровно поведение stock Android.
12. При OFF не создаются сервис, канал, файл, запрос, chooser или фоновая задача фичи.
13. Fork-код размещать в новых файлах под `tele/`.
14. В stock-файлах добавлять только минимальный gated-call или ранний return.
15. `TLRPC.java`, stock schema и `LAST_DB_VERSION` не менять.
16. Fork-состояние хранить в `tele_kv` или таблицах `tele_*`.
17. Сетевые запросы фичи должны уважать offline-переключатели.
18. Внешние сайты карт не являются tele-server и не получают аккаунтные данные.
19. Основные callbacks Telegram, storage и service приходят не на UI thread.
20. UI обновлять через `AndroidUtilities.runOnUIThread`.
21. Любой state ключевать `(account, peerId)`, а не singleton account 0.
22. Recycler-ячейки заново применяют состояние в каждом bind.
23. Анимации не должны игнорировать `LiteMode` и performance class.
24. [INFERENCE] Точные номера строк не фиксируются: искать символы в актуальной ветке.
25. [INFERENCE] Android-вариант FGS-политики требует проверки target SDK перед кодом.
26. Не включать в пачку новые функции, которых нет в семи строках ниже.
27. 0153 MKV отмечен отдельно как cross-batch контроль, а не новая строка пачки 21.
28. 0153 остаётся частичным и не меняет состав PATCHLIST пачки 21.

## 2. Состав, усилие и порядок

29. 0155 — online notifications, усилие M.
30. 0158 — per-chat download folders, усилие M и частичное поведение.
31. 0138 — выбор веб-карт, усилие S.
32. 0137 — выключить AI, усилие M.
33. 0262 — тонкая кисть, усилие S.
34. 0222 — retry call-log loading, усилие S.
35. 0070 — test-server account, усилие M и частичное поведение.
36. Сводная оценка PATCHLIST: `S×3, M×4`.
37. Фактически S: 0138, 0262, 0222.
38. Фактически M: 0155, 0158, 0137, 0070.
39. Первый коммит — инфраструктура конфигов и строк settings только если она нужна.
40. Второй коммит — 0155: service, channel, online state и выбор людей.
41. Третий коммит — 0158: путь сохранения и все download entry points.
42. Четвёртый коммит — 0138: карта и web URL chooser.
43. Пятый коммит — 0137: единый AI gate, транскрипция не закрывается.
44. Шестой коммит — 0262: минимальное значение кисти.
45. Седьмой коммит — 0222: page-size correction и bounded retry.
46. Восьмой коммит — 0070: per-account test backend и long-press UI.
47. Каждый коммит содержит одну feature, один imperative subject и экспортированный patch.
48. [INFERENCE] 0155 и 0158 нельзя безопасно делать параллельно: оба затрагивают lifecycle/storage.
49. 0138, 0262 и 0222 независимы от 0155, если общие settings строки уже готовы.
50. 0070 требует native setter, поэтому его делать после проверки JNI ABI и всех split.
51. 0158 делать после определения доступного public-storage API для minSdk ветки.
52. 0137 делать после аудита всех Android AI entry points, чтобы не оставить обход.
53. 0155 делать до ручной проверки ворот, потому что service влияет на процесс и батарею.
54. MKV проверить в отдельном тестовом наборе перед закрытием всей пачки.
55. Плановая трудоёмкость: S — до 0,5 дня, M — 1–2 дня, без обещания фактического времени.
56. [INFERENCE] Реальная трудоёмкость 0155 может вырасти из-за Android background restrictions.

## 3. TeleConfig, settings, export/import и поиск

57. Добавить в `tele/TeleConfig.kt` только новые items, default у каждого `false`.
58. `ONLINE_NOTIFY` key: `online_notify`, default OFF.
59. `DOWNLOADS_PER_CHAT` key: `downloads_per_chat`, default OFF.
60. `MAP_SERVICE` key: `map_service`, default значение не должно включать новую фичу.
61. Для `MAP_SERVICE` безопаснее использовать enum/string `system`, но selector скрыт при OFF.
62. `NO_AI` key: `no_ai`, default OFF.
63. `THIN_BRUSH` key: `thin_brush`, default OFF.
64. `CALL_LOG_RETRY` key: `call_log_retry`, default OFF.
65. `TEST_BACKEND_ACCOUNTS` key: `test_backend_accounts`, default OFF.
66. `MKV_AS_VIDEO` key: `mkv_as_video`, default OFF для partial device gate.
67. [INFERENCE] Если maintainer считает 0153 always-on fix, оставить отдельный item не нужно.
68. Такое решение обязательно зафиксировать до коммита 0153, не угадывать в коде.
69. `ONLINE_NOTIFY` row находится в группе Notifications.
70. `DOWNLOADS_PER_CHAT` row находится в группе Chats/Downloads.
71. `MAP_SERVICE` row находится в группе Interface/External apps.
72. `NO_AI` row находится в группе Interface/Privacy или Sending по фактической структуре.
73. `THIN_BRUSH` row находится в группе Sending/Editor.
74. `CALL_LOG_RETRY` row находится в группе Interface/Calls.
75. `TEST_BACKEND_ACCOUNTS` row находится у account list, не в сетевых общих настройках.
76. `MKV_AS_VIDEO` row находится у Sending/Files и видна только при поддержанном пути.
77. Ряды добавлять в `TeleSettingsActivity.buildRows` существующего mode.
78. Не создавать отдельный root mode для одной строки.
79. Дочерние selector rows скрывать, пока master OFF.
80. `map_service=system` означает Android `ACTION_VIEW` с `geo:`.
81. Allowed map values: `system`, `google`, `osm`, `yandex`, `2gis`.
82. `apple` из desktop не обещать на Android без проверки доступности URL/chooser.
83. [INFERENCE] Поддержка `apple` может быть добавлена только после ручной проверки Android intent.
84. Export/import spec должен включать все новые фактические TeleConfig items.
85. Экспортировать per-chat directory mapping только если mapping действительно хранится.
86. Не экспортировать runtime notification id, service state, channel id или cached test token.
87. Не экспортировать разрешения Android и user-granted SAF URI, поскольку SAF запрещён этим патчем.
88. Не экспортировать системный выбор приложения-карты, если его хранит ОС.
89. Не экспортировать секреты test backend или MTProto auth data.
90. Unknown import keys пропускать с одной диагностической строкой.
91. Использовать существующий `TeleSearch` и его deeplink/mode mapping.
92. Зарезервировать постоянный диапазон Search IDs `1300..1319`.
93. 1300 — `online_notify` master.
94. 1301 — online notification people/watched list.
95. 1302 — online presence/status keyword alias.
96. 1303 — `downloads_per_chat` master.
97. 1304 — download folder per chat/path keyword alias.
98. 1305 — public Telegram downloads keyword alias.
99. 1306 — `map_service` master.
100. 1307 — Google Maps choice.
101. 1308 — OpenStreetMap choice.
102. 1309 — Yandex Maps choice.
103. 1310 — 2GIS choice.
104. 1311 — `no_ai` master.
105. 1312 — AI writing/compose keyword alias.
106. 1313 — translation and summary keyword alias.
107. 1314 — `thin_brush` master.
108. 1315 — photo editor/paint/pen keyword alias.
109. 1316 — `call_log_retry` master.
110. 1317 — `test_backend_accounts` master.
111. 1318 — `mkv_as_video` master or device-gated row.
112. 1319 — system/downloads/settings batch alias.
113. [INFERENCE] 1319 has no independent toggle; it is an alias for the batch settings group.
114. If the search implementation disallows group targets, point 1319 to downloads group.
115. IDs must be registered once, not duplicated by mode or locale.
116. Search clicks must open the real existing mode and scroll to the real row.
117. Search must not expose child row as enabled while master is OFF.
118. Search terms include Russian and English: «онлайн», `online`, `presence`, «загрузка», `downloads`.
119. Search terms include `maps`, «карты», `Google`, `OSM`, `Яндекс`, `2GIS`.
120. Search terms include `AI`, «искусственный интеллект», `summary`, `translate`.
121. Search terms include «кисть», `brush`, `paint`, «звонки», `call log`, `test server`, `MKV`.
122. Add localized strings only to `strings_tele.xml`, with `Tele` keys.
123. Descriptions state scope, default OFF, privacy and limitations.
124. Existing `SHOW_DC` and unrelated config rows must not be duplicated.
125. Existing stock account rows must be reused instead of making a second account screen.
126. `onConfigChanged` refreshes visible rows and affected runtime objects.

## 4. 0155 — «пришёл в онлайн»

127. Desktop source adds a watch list, a master toggle and peer context action.
128. Desktop constants are max 65,536 users and ten-minute per-user cooldown.
129. Desktop ignores self, bots, service users and inaccessible users.
130. Android behavior: when watched user changes to online, emit local notification.
131. Do not notify on offline, recently, last-week or last-month status placeholders.
132. Do not notify the account owner itself.
133. Do not notify bots or service accounts unless explicit future decision changes scope.
134. Add long-press menu action «Notify when online» to a user profile/message avatar path.
135. Add a settings picker with search and multi-select of eligible users.
136. Picker stores peer ids per account in `tele_kv`, not stock DB.
137. Suggested key: `online_notify_users:<account>`.
138. Store a bounded JSON array or comma-separated signed ids; validate every id on load.
139. Limit watched users to desktop limit 65,536 unless Android storage requires lower limit.
140. [INFERENCE] A lower Android limit must be agreed, not silently introduced.
141. Store last-notified timestamps per `(account,userId)` in `tele_kv`.
142. Enforce ten-minute cooldown from desktop unless maintainer changes UX.
143. Cooldown prevents repeated status flaps from notification spam.
144. Do not store Telegram password, phone, contact list or profile text in the watcher state.
145. Android source status enters `MessagesController.processUpdateArray`.
146. Current branch routes `TL_updateUserStatus` to `updatesOnMainThread` around that switch.
147. The later status branch updates `currentUser.status` and `dbUsersStatus`.
148. Add a small `TeleHooks.onUserStatus(account, update)` at that data-layer point.
149. Hook must run only when `TeleConfig.ONLINE_NOTIFY.getValue()` is true.
150. Hook must check watched membership before reading/displaying user details.
151. Do not add a network request to resolve watched users during status update.
152. If the user object is absent, defer display to a local id-only fallback or skip.
153. Notification text should be localized «<name> пришёл(а) в сеть».
154. Name/photo disclosure must respect stock notification privacy settings.
155. If stock notification settings hide name/photo, use generic text and no avatar.
156. Tap notification opens the corresponding profile/chat with explicit account id.
157. Use a stable content intent with `account` and `userId`, never selected account only.
158. Use one notification id per account/user or a deterministic update id.
159. Notification channel is a new immutable channel, e.g. `tele_online_presence`.
160. Never reuse a stock message channel because channels are immutable after creation.
161. Channel name and description are fork strings.
162. Channel importance should be user-configurable; initial importance must not be guessed.
163. [ВОПРОС] Choose default channel importance: low silent or default audible.
164. [ВОПРОС] Should notification be persistent only while service is alive, or normal dismissible event.
165. The keep-alive requirement means a foreground service must own the live connection.
166. Add `TeleOnlineService` as a non-exported Android `Service` in fork manifest overlay.
167. Use `startForegroundService` only after explicit user ON and eligible account exists.
168. Call `startForeground` promptly with a separate ongoing channel.
169. Foreground service notification must say the feature is active, not pretend it is a chat.
170. The ongoing channel id must differ from event channel id.
171. [INFERENCE] Exact `foregroundServiceType` depends on target SDK and platform policy.
172. Do not claim `dataSync` or `remoteMessaging` until manifest/build accepts it.
173. Service owns no UI and only coordinates existing account connections.
174. On service start, enumerate activated accounts from `UserConfig`, not account 0.
175. On account logout/deactivation, remove its watcher and stop that account loop.
176. On app/process shutdown, stop service and release callbacks.
177. On setting OFF, stop service, cancel ongoing notification and clear only runtime handles.
178. Turning OFF does not delete user-selected watched ids unless product decision says so.
179. On setting ON, service must rehydrate watchers and attach status listeners.
180. Service must not force battery-unrestricted mode or request unrelated permissions.
181. [INFERENCE] Android may kill the service; restart policy must be chosen explicitly.
182. Use `START_STICKY` only if maintainer accepts battery implications.
183. Do not schedule a hidden polling loop as fallback.
184. Keep-alive must use stock Telegram connection lifecycle, not a second MTProto client.
185. Do not send presence updates or change account status to implement this feature.
186. No FCM is assumed: PATCHLIST explicitly requires service without FCM.
187. [INFERENCE] Exact method to keep a connection awake is not identified in current docs.
188. Before coding, identify stock keep-alive entry point in `ConnectionsManager`/application lifecycle.
189. If no safe entry point exists, stop and ask maintainer instead of polling.
190. Service callbacks and status events hop to main thread before NotificationManager calls.
191. Storage reads/writes use TeleDatabase helper queue and never block main thread.
192. Use generation token when account set changes while service starts.
193. Ignore late status callbacks after account generation or watcher list changes.
194. `onDestroy` unregisters every observer and cancels every runnable.
195. Log tag: `TeleOnline`.
196. Log only account number, user id and transition class; never names or message text.
197. OFF log expectation: no `TeleOnline` service start and no status callback.
198. A notification must be de-duplicated across cold start and reconnect.
199. Reconnect alone is not an online transition for a watched user.
200. Compare previous local status to new status before emitting.
201. Persist last known status only in fork storage if restart de-duplication needs it.
202. [INFERENCE] Whether stock status cache survives process death must be verified on device.
203. Use user id, not access hash, as local key.
204. Long-press menu must show selected state when row is rebound.
205. Recycler and profile rotation must preserve selected state from `tele_kv`.
206. `LiteMode` affects no required notification semantics; avoid animated service UI.
207. Privacy test must inspect logcat and confirm no server request for watcher list.

## 5. 0158 — per-chat download folders

208. Desktop applies chat path to automatic downloads, explicit save, viewer download and upload auto-save.
209. Android target is a subdirectory under standard public `Telegram` folders.
210. Required visible shape: `Telegram/<chat>` inside the standard media/download base.
211. Do not use SAF for this feature, per maintainer decision.
212. Do not write to app-private files when user requested public Telegram storage.
213. Resolve a peer display directory name from local chat data only.
214. Sanitize `/`, `\\`, NUL, dot segments and platform separators.
215. Preserve a non-empty fallback such as `chat_<peerId>` when title is empty.
216. Never use user-entered title as a path without sanitization.
217. Bound path/name lengths before creating directories.
218. Desktop source limits path length 4096 and chat name length 64.
219. [INFERENCE] Android should adopt 64-byte-or-character name bound after filesystem test.
220. Do not silently merge two chats that sanitize to the same name.
221. [INFERENCE] Collision suffix format must be chosen: peer id suffix is safest.
222. Recommended collision form: `<sanitized title>_<peerId>`.
223. Resolve paths per account and peer, but public folder names may be shared intentionally.
224. [ВОПРОС] Should same-title chats across accounts share folder or always include account id.
225. Default recommendation is include peer id, not account id, to match `Telegram/<chat>` UX.
226. Directory mapping is local; never send it to Telegram or tele-server.
227. Add `TeleDownloadFolders.resolve(account, dialogId, baseType)` helper.
228. Helper returns original stock path when toggle OFF.
229. `MediaController.saveFile` is the central explicit save anchor in current Android branch.
230. It has overloads at `saveFile(fullPath, context, type, name, mime, ...)`.
231. Its API 29 branch calls `saveFileInternal(type, sourceFile, null)`.
232. Its pre-29 branch creates public `Environment` directories.
233. Add a gated destination resolver immediately before destination creation.
234. Resolver must preserve `type` semantics: pictures, videos, audio and documents.
235. For API 29+, pass `ContentValues.DISPLAY_NAME` and `RELATIVE_PATH` with subfolder.
236. For pre-29, append subfolder to the corresponding public Telegram directory.
237. [INFERENCE] Exact `saveFileInternal` ContentValues signature must be re-read before edit.
238. Do not alter MediaStore ownership, MIME, pending flag or scan behavior.
239. Automatic downloads use `FileLoader`/`MediaController` save paths, not only manual `saveFile`.
240. Search `MediaController.saveFilesFromMessages` and `MediaLoader` before coding.
241. Add resolver to all paths that expose a user-visible save destination.
242. Explicit «Save to…» path chosen by user must win over per-chat default.
243. SAF path, if supplied by an existing stock flow, must not be rewritten.
244. Temporary path and cache path must not be rewritten.
245. Protected media and secret chat files must obey existing restrictions.
246. Do not move a downloaded source file after completion if it changes stock semantics.
247. Prefer selecting destination before download to avoid duplicate copies.
248. For albums, all files belong to the peer of the selected messages.
249. If an album mixes peers, keep stock explicit path or reject per-chat routing.
250. [INFERENCE] Mixed-peer album behavior needs a manual decision; do not guess.
251. A folder must be created off the main thread.
252. UI may show a Bulletin after success or failure on main thread.
253. Failed mkdir must leave stock error behavior and must not fall back silently to another chat.
254. Log tag: `TeleDownloads`, path class only, no full user title if privacy policy forbids it.
255. Avoid logging absolute public paths by default.
256. Directory picker/reset UX is out of scope because PATCHLIST says no SAF.
257. Add long-press/context action only if desktop row requires path open/reset and Android has anchor.
258. [INFERENCE] No Android reset UI anchor is verified; initially settings toggle may be sufficient.
259. Do not delete existing files when turning toggle OFF.
260. Turning OFF affects new saves only; existing folders remain user-owned.
261. Changing chat title must not move old files automatically.
262. New title path behavior needs explicit decision to avoid orphan confusion.
263. [ВОПРОС] Freeze folder name at first save or recompute from current chat title.
264. Recommendation: use stable peer id suffix and current sanitized title for new saves.
265. Test titles with slash, emoji, RTL, empty title, 64+ characters and collision.
266. Test API 28 and API 29+ separately.
267. Test photo, video, audio, document, album and viewer download.
268. Test OFF: exact stock `Telegram` destination with no `TeleDownloads` log.
269. Test multi-account same dialog id and account switching.
270. Ensure Recycler state is irrelevant to path but settings row binds each time.
271. Respect storage permission behavior already used by stock branch.
272. Do not add broad storage permissions without maintainer approval.

## 6. 0138 — выбор веб-карт

273. Desktop provides Google, OSM, Yandex, 2GIS and Apple site templates.
274. PATCHLIST explicitly requires Yandex, 2GIS, OSM and Google on Android.
275. Android current anchor is `LocationActivity` menu id `open_in`.
276. Current stock path builds `geo:<lat>,<lon>?q=<lat>,<lon>` and starts `ACTION_VIEW`.
277. Preserve `geo:` as the `system` choice.
278. Add a map chooser only when `MAP_SERVICE` is ON.
279. Google endpoint: `https://maps.google.com/maps?q={lat},{lon}&ll={lat},{lon}&z=16`.
280. OSM endpoint: `https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}`.
281. Yandex endpoint: `https://yandex.ru/maps/?ll={lon},{lat}&z=16&pt={lon},{lat}`.
282. 2GIS endpoint: `https://2gis.ru/geo/{lon},{lat}?m={lon},{lat}/16`.
283. Apple endpoint from desktop is `https://maps.apple.com/?ll={lat},{lon}&q={title}&z=16`.
284. URL encode title and all query components; do not concatenate raw user text.
285. Lat/lon must come from `messageObject.messageOwner.media.geo`.
286. Do not resolve an address or call a third-party geocoder.
287. For live location, preserve existing live-location/directions menu semantics.
288. [INFERENCE] Whether chooser appears as submenu or direct selected URL needs UX decision.
289. Recommendation: one «Open in» submenu with System, Google, OSM, Yandex, 2GIS.
290. If selected site fails to open, show stock-style failure Bulletin and no network retry.
291. Do not silently fall back to a different site after an explicit choice.
292. Keep `ACTION_VIEW` and let browser handle HTTPS endpoint.
293. No account data, peer id or message id belongs in the URL.
294. The title is optional and must be omitted when empty.
295. Update selected choice without restart through `onConfigChanged` if supported.
296. OFF must execute the current stock `geo:` intent and no URL-template code.
297. Test each URL with positive, negative and decimal coordinates.
298. Test RTL title, Unicode title, no title and location from chat versus attachment.
299. Test missing browser and no handler.
300. Log tag `TeleMaps` should record site id only, not coordinates or title.

## 7. 0137 — выключить AI, оставить транскрипцию

301. Desktop gate covers compose AI, summaries, translation helpers, AI tone refresh and AI pills.
302. Maintainer decision explicitly keeps voice transcription.
303. Android targets are `AIEditorAlert`, `TranslateController` and `AiTonesController`.
304. Add `TeleHooks.noAi()` or a small `TeleNoAi` helper with an early gated check.
305. Hook `AIEditorAlert` before AI compose/apply network work.
306. Hook translation and summary UI creation before AI-only actions.
307. Hook `AiTonesController` refresh/request entry point.
308. Do not hook voice transcription loading or display.
309. Do not block `MediaController` voice recording or `api_transcribes` transcription.
310. No-AI OFF must not change stock AI buttons, summaries, translation or tone refresh.
311. No-AI ON hides or disables AI affordances consistently, rather than leaving dead buttons.
312. Existing translation that is not AI must remain available if current implementation proves it.
313. [INFERENCE] Android `AIEditorAlert` may combine translation and AI tabs; audit tab IDs before hiding.
314. [ИНFERENCE] Do not infer that all `TranslateController` calls are AI until call sites are classified.
315. Network gate belongs below UI so deep links cannot bypass the option.
316. If a request is already in flight when OFF changes, cancel or ignore its result.
317. If ON changes, invalidate visible AI rows on main thread.
318. Do not erase cached Telegram text or transcription when toggle changes.
319. Log tag `TeleAI` records blocked feature kind, not message text.
320. Privacy test confirms no AI request starts while ON.
321. Positive test confirms voice transcription still loads while ON.
322. Test compose, summarize, translate, tones and deep-link entry.
323. Test account switching and process restart.
324. [ВОПРОС] Confirm whether translation tab is classified as AI in this Android release.
325. Until answered, preserve non-AI translation and gate only confirmed AI paths.

## 8. 0262 — тонкая кисть

326. Desktop changes the minimum brush ratio from about 3.4 px to 1 px.
327. Desktop implementation uses minimum ratio `1.5 / 100000` because zero is dropped.
328. Android current editor is `LPhotoPaintView` with `RenderView` and `PaintWeightChooserView`.
329. Current min/max is selected around `0.05f..1f` for normal brush.
330. Add `TeleBrush.minWeight(current, brush)` returning stock value OFF.
331. ON lowers only normal brush minimum; do not alter eraser, blurer or shape ranges.
332. Apply helper at `PaintWeightChooserView.setMinMax`/weight initialization anchor.
333. Preserve persisted per-account brush weight through `PersistColorPalette`.
334. Clamp persisted old values to new range when ON, without rewriting on OFF.
335. Do not change canvas stroke width directly after render begins.
336. Do not add animation; LiteMode therefore needs no special branch.
337. Log tag `TeleBrush` only on settings change, not every stroke.
338. Test minimum slider, drawing, undo, redo and export.
339. Test normal brush, eraser, blurer, shape and text tool.
340. Test light/dark theme, rotation and account switch.
341. OFF test confirms stock minimum and no helper path.
342. [INFERENCE] Exact Java class containing min/max setter must be found before edit; grep showed calls in `LPhotoPaintView`.
343. Do not edit generated or unrelated paint classes if a public hook suffices.

## 9. 0222 — retry журнала звонков

344. Desktop first page is 20, subsequent pages are 100, and failed requests retry with 1s then doubling to 30s.
345. Android anchor is `CallLogActivity.getCalls(max_id, count)`.
346. Current `loading` guard prevents duplicate calls.
347. Add `CALL_LOG_RETRY` gate around retry timer only.
348. Keep stock page sizes unless current Android request proves wrong; inspect request fields before edit.
349. On failure clear `loading`, schedule retry with bounded delay and leave existing rows visible.
350. On success reset retry delay and continue normal pagination.
351. Cancel timer in `onFragmentDestroy`/equivalent lifecycle hook.
352. Do not retry permanent auth or permission failures indefinitely.
353. [INFERENCE] Error classification fields in current callback must be read before selecting retry policy.
354. Use account-local timer; do not share account 0 state.
355. UI progress and adapter updates run on main thread.
356. Log tag `TeleCalls`, attempt and delay only, no phone numbers.
357. Test first page failure, later page failure, success after failure and repeated failure.
358. Test rotation/background and account switching while timer is active.
359. OFF test: stock single request behavior and no timer.

## 10. 0070 — accounts test-server

360. Desktop replaces an Alt+Shift+right-click requirement with plain right-click in account list.
361. Android has no right-click; use long-press on an existing account row.
362. Anchor account rows are `SettingsActivity` account list and `AccountCell` binding.
363. Long-press must target the selected account, not `UserConfig.selectedAccount`.
364. Show explicit «Production server» / «Test server» choice with current checkmark.
365. Apply setting only to the chosen account after confirmation.
366. Existing Android native getter is `ConnectionsManager.isTestBackend()`.
367. Existing native symbol is `native_isTestBackend(currentAccount)`.
368. Add a per-account native setter beside the existing getter only if ABI supports it.
369. Do not write test backend into stock SharedPreferences as the source of truth.
370. [INFERENCE] Exact tgnet setter/native configuration function is not identified by current branch.
371. Surface this as a blocker/question before changing JNI rather than guessing a symbol.
372. Native config must be applied before account connection starts.
373. Switching backend likely requires reconnect/restart of that account.
374. Do not silently migrate production auth to test server or vice versa.
375. Warn that test and production sessions/data are different.
376. Long-press menu state must bind after account list recycling.
377. Test two accounts with opposite backend choices.
378. Test cold start, account switch and logout.
379. Test OFF: no long-press option and no native setter call.
380. Native logs must include account index and backend boolean only.
381. [ВОПРОС] Is test-server selection allowed in release builds or debug only.
382. [ВОПРОС] Does backend switching require logout, reconnect, or process restart.
383. Until answers, implement no destructive switch and keep row disabled if unsafe.

## 11. MKV cross-batch control (0153)

384. Desktop 0153 adds `.mkv` to the video extension set.
385. PATCHLIST marks it partial and requires an on-device check.
386. Android `SendMessagesHelper` already has an `.mkv` extension path around document preparation.
387. This does not prove Android sends every MKV as video.
388. Audit MIME, extension, codec and `MessageObject.isVideoDocument` together.
389. If Android accepts the path, add only a gated hook for `MKV_AS_VIDEO`.
390. If stock already handles it, do not add duplicate code.
391. If codec/container support fails, preserve file send and report partial behavior.
392. Device gate must test a real MKV with video-only, audio+video and unsupported codec.
393. Test gallery picker, file picker, attach menu and retry send.
394. Test OFF produces stock document/video classification exactly.
395. Test ON changes only extension classification, never transcodes silently.
396. Log tag `TeleSend` records extension and detected MIME, not file path.
397. [INFERENCE] No desktop-equivalent Android MIME gate is confirmed until device test.

## 12. Common pitfalls and dependencies

398. Never start `TeleOnlineService` from a static initializer.
399. Never hold an Activity reference in service, helper or timer.
400. Always unregister NotificationCenter observers on destroy.
401. Notification channels cannot be changed after creation; version channel ids if semantics change.
402. Android 13 notification permission may suppress event notifications; do not treat suppression as status failure.
403. Foreground-service restrictions can reject background starts; show an actionable settings explanation.
404. Do not request notification permission merely when feature is OFF.
405. Public storage paths differ on API 28 and API 29+; test both.
406. `RELATIVE_PATH` must be a relative MediaStore path, not an absolute path.
407. Do not double-prefix `Telegram` when stock caller already supplies it.
408. Do not use chat title as a SQL key or persist it in stock DB.
409. Null TL fields must be checked before reading status, geo or document metadata.
410. All account calls use `MessagesController.getInstance(account)`.
411. All settings changes use `TeleConfig.<ITEM>.getValue()` from Java.
412. Never read `.value` from Java call sites.
413. Do not call third-party map URLs with raw coordinates if URL encoding is required.
414. Do not block the UI while creating a directory or parsing a status list.
415. Do not use polling to imitate keep-alive.
416. Do not emit online notifications for every reconnect update.
417. Do not put watched users into tele-server requests.
418. Do not include account data in logs, features metadata or crash reports.
419. Do not make AI OFF erase existing translations or transcripts.
420. Do not make thin brush alter eraser or blur semantics.
421. Do not use unbounded retry timers for call log.
422. Do not let a recycled account row display another account's backend state.
423. Do not claim a row is complete until ON and OFF are exercised.

## 13. Planned features.md rows

424. Add one English row for 0155 under Notifications: watched users get local online alerts; default OFF; settings location; patch filename and desktop 0155.
425. Add one English row for 0158 under Chats/Downloads: saves into `Telegram/<chat>`; default OFF; no SAF; patch filename and desktop 0158.
426. Add one English row for 0138 under Interface: choose web map provider; default OFF/system stock; list providers and patch/desktop number.
427. Add one English row for 0137 under Interface: hide confirmed AI tools while retaining voice transcription; default OFF; patch/desktop number.
428. Add one English row for 0262 under Editor: lower normal brush minimum; default OFF; patch/desktop number.
429. Add one English row for 0222 under Calls: retry failed call-log pages; default OFF; bounded delay; patch/desktop number.
430. Add one English row for 0070 under Accounts: long-press to choose test backend; default OFF; partial/native caveat; patch/desktop number.
431. Add a row for 0153 only in its owning batch/section, not silently in batch 21.
432. Features rows are user-facing summaries, not implementation notes or unresolved guesses.
433. The `features.md` update belongs to the same commit as its exported patch.
434. If a row remains blocked by a question, do not mark it as implemented.

## 14. Manual tests and logcat

435. Build with `./gradlew :TMessagesProj_App:assembleDebug` after every patch is exported as a queue, not as a claim of correctness.
436. Install the ABI matching the device and use a secondary/test account.
437. Test all new toggles at default OFF after clean install.
438. Enable only one feature at a time, then restart and repeat.
439. Online ON: add one normal user, kill app, keep service allowed, wait for status transition.
440. Online ON: verify ongoing service notification and event notification with correct account.
441. Online OFF: verify service/channel event is not started by status updates.
442. Online: verify ten-minute cooldown with repeated online/offline transitions.
443. Online: verify bots, self and service users are excluded.
444. Downloads ON: save photo, video, audio and document from message menu.
445. Downloads ON: verify exact public path `Telegram/<chat>` and no duplicate Telegram segment.
446. Downloads ON: automatic download and viewer download use same peer folder.
447. Downloads OFF: verify stock path and no folder resolver log.
448. Downloads: API 28 permission and API 29+ MediaStore path are separate cases.
449. Maps ON: open each Google, OSM, Yandex and 2GIS URL and check lat/lon.
450. Maps OFF: verify stock `geo:` chooser and no `TeleMaps` URL log.
451. AI ON: verify AI compose, summary, translation and tones are hidden/blocked as decided.
452. AI ON: verify voice transcription still works and transcript remains visible.
453. AI OFF: verify stock AI controls and no `TeleAI` blocked log.
454. Brush ON: drag to minimum and draw a one-pixel-like stroke, then export.
455. Brush OFF: compare minimum and exported output with stock build.
456. Call log ON: fail network, observe retry delay and eventual recovery.
457. Call log OFF: fail network, verify no fork timer.
458. Test backend ON: long-press account row, choose test, restart/reconnect safely.
459. Test backend OFF: long-press has no fork action and native setter is not called.
460. MKV ON: test supported and unsupported containers on a real device.
461. MKV OFF: verify stock classification and no forced conversion.
462. Use `adb logcat -s TeleOnline TeleDownloads TeleMaps TeleAI TeleBrush TeleCalls TeleSend`.
463. Expected ON logs contain account/peer or feature kind but no names, text, paths or secrets.
464. Expected OFF logs contain no feature execution entries.
465. Check `dumpsys notification` for distinct event and foreground channel ids.
466. Check `dumpsys activity services` for service lifetime and account transitions.
467. Check MediaStore rows/`RELATIVE_PATH` on API 29+.
468. Check no HTTP request to tele-server is created by 0155, 0158, 0138 or 0262.
469. Check map HTTPS URL only after explicit user map selection.
470. Check no extra permissions are requested with all toggles OFF.
471. Check rotation, process death, account switch and Recycler rebinding.
472. Check LiteMode ON does not crash or add animation work.
473. Check privacy: notification preview follows stock hide-name/photo settings.
474. Check logout removes account-local watcher/service state without touching another account.

## 15. Decisions, open questions and batch gate

475. [ВОПРОС] Approve FGS type, restart policy and battery disclosure for 0155.
476. [ВОПРОС] Approve event channel importance and whether online alerts are dismissible.
477. [ВОПРОС] Confirm exact stock keep-alive hook; no polling fallback is allowed.
478. [ВОПРОС] Confirm folder collision and title-renaming policy for 0158.
479. [ВОПРОС] Confirm Apple Maps support; PATCHLIST minimum is Google/OSM/Yandex/2GIS.
480. [ВОПРОС] Classify Android translation tab as AI or non-AI for 0137.
481. [ВОПРОС] Confirm 0070 release/debug availability and safe backend switch lifecycle.
482. [ВОПРОС] Decide 0153 default and whether separate `mkv_as_video` is wanted.
483. [ВОПРОС] Confirm Android 13 notification permission handling for the service event.
484. Do not hide these questions inside implementation assumptions.
485. Do not mark rows done while a question changes observable behavior.
486. Before gate, every patch has a commit in `Telegram` branch `tele`.
487. Every commit is exported to `main/patches/android/` with `git format-patch`.
488. No `.patch` is hand-edited.
489. `PATCHLIST.md` status remains `todo` until export, build and human test.
490. Run the single batch build after all seven rows are committed and exported.
491. Batch gate command is `./gradlew :TMessagesProj_App:assembleDebug`.
492. Hand the correct ABI APK to a human tester.
493. Human tester must run the ON/OFF list in section 14.
494. Human tester must verify the seven PATCHLIST gate statements.
495. Gate statement: online notification and live keep-alive service work.
496. Gate statement: save destination is `Telegram/<chat>` without SAF.
497. Gate statement: selected web map opens with correct coordinates.
498. Gate statement: AI tools are disabled while voice transcription remains.
499. Gate statement: thin brush is usable in photo editor.
500. Gate statement: call-log retry recovers after a failed page.
501. Gate statement: test account is added through long-press, with safe backend state.
502. MKV is an additional device-gated check and remains partial if unsupported.
503. Only after human verification may each row become `done`.
504. If any ON/OFF test fails, keep the row `wip` and record the exact logcat failure.
505. No claim of completion may be based on compilation alone.
506. Batch 21 closes only when every row is exported and manually verified.
