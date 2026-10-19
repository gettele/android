# Пачка 22: центр уведомлений

## 1. Назначение документа

1. Этот файл — пошаговый план переноса пачки 22 из `docs/PATCHLIST.md`.
2. Пачка называется «центр уведомлений».
3. Номера ниже — текущие номера очереди desktop.
4. Старые номера не использовать; карту даёт `docs/desktop-numbers.md`.
5. Источник поведения desktop — `origin/main` репозитория `tele`.
6. Источник Android — ветка `tele` в соседнем checkout `Telegram`.
7. Ветка Android сейчас заканчивается экспортом `feat: attach media above the field`.
8. Это не готовая реализация и не обещание, что серверная часть уже существует.
9. Все новые переключатели обязаны быть выключены по умолчанию.
10. Выключенный переключатель обязан оставлять поведение tgnet и UI стока.
11. Код форка должен жить в `tele/`.
12. В stock-файлах допустимы только маленькие гейтированные хуки.
13. `TLRPC.java` изменять нельзя.
14. Схему stock-БД и `LAST_DB_VERSION` изменять нельзя.
15. Состояние центра хранится только в таблицах `tele_*`.
16. Значения, относящиеся к аккаунту, нельзя хранить одной глобальной переменной.
17. Данные с сервера tele должны быть публичными и сопоставляться на устройстве.
18. Клиент не отправляет серверу id, username, контакты или сообщения пользователя.
19. Любой новый HTTP-запрос обязан иметь нижнеуровневый offline/server gate.
20. Цель пачки — debug APK и ручная проверка на устройстве.
21. Успешная компиляция без ручной проверки не переводит пачку в `done`.
22. Маркер `[INFERENCE]` означает предложение, которое нужно подтвердить кодом или решением.
23. Маркер `[OPEN]` означает вопрос, блокирующий серверный или продуктовый контракт.
24. Маркер `[SOURCE]` означает факт, проверенный в указанном исходнике.

## 2. Состав пачки и критерий готовности

25. Патч 0205 строит базовый центр, хранилище и первый JNI-хук.
26. Патч 0212 добавляет flood/slowmode/download-throttling обработку.
27. Патч 0232 добавляет упоминания и ответы в центр.
28. Патч 0239 добавляет полные записи и раскрытие `Show more`.
29. Патч 0240 добавляет журнал скопированных значений.
30. Патч 0246 добавляет косметические reply/@ badges.
31. Патч 0206 добавляет notices из общего tele-server feed.
32. Патч 0206 не должен блокировать базовый центр при недоступном сервере.
33. Сначала должен работать локальный центр без server notices.
34. Ворота пачки требуют искусственный `FLOOD_WAIT`.
35. Ворота требуют проверку `SLOWMODE_WAIT`.
36. Ворота требуют проверку ограничения загрузки.
37. Ворота требуют проверку упоминания из muted-группы.
38. Ворота требуют проверку ответа мне в группе.
39. Ворота требуют длинную запись, `Show more` и `Show less`.
40. Ворота требуют повторное копирование сохранённого значения.
41. Ворота требуют server notice при разрешённом `platforms: ["android"]`.
42. Ворота требуют server notice, отфильтрованный по build range.
43. Ворота требуют запуск с двумя аккаунтами.
44. Ворота требуют остановку сети и отсутствие tele HTTP-запроса при отключённом gate.
45. Ворота требуют native rebuild для всех ABI.
46. Ворота требуют лог подтверждения callback в logcat.
47. На каждом сценарии нужно повторить вариант «все переключатели выключены».
48. На выключенном варианте центр не должен добавлять observer, map запросов или записи.
49. На выключенном варианте tgnet должен повторять запросы ровно как stock.
50. На выключенном варианте штатные toast и clipboard не должны превращаться в tele-записи.

## 3. Что проверено в Android tree

51. `ConnectionsManager.sendRequest` выдаёт `requestToken` до постановки работы на `Utilities.stageQueue`.
52. `[SOURCE]` `ConnectionsManager.java:380–395` показывает создание токена и `sendRequestInternal`.
53. `[SOURCE]` `sendRequestInternal` сериализует объект и вызывает native send.
54. `[SOURCE]` callback ответа разбирает `TL_error` внутри `ConnectionsManager.java`.
55. `[SOURCE]` текущий JNI callback — `onPremiumFloodWait`.
56. `[SOURCE]` его Java signature: `(int currentAccount, int requestToken, boolean isUpload)`.
57. `[SOURCE]` `onPremiumFloodWait` сначала переходит через `AndroidUtilities.runOnUIThread`.
58. `[SOURCE]` он отбрасывает callback невыбранного аккаунта.
59. Для центра этот отбрасывающий selected-account guard нельзя копировать.
60. Центр должен записать событие для любого активного аккаунта.
61. `[SOURCE]` `TgNetWrapper.cpp:397–399` вызывает Java static method напрямую из native delegate.
62. `[SOURCE]` delegate получает `instanceNum` и `requestToken`.
63. `[SOURCE]` `Defines.h:142–159` содержит pure-virtual `ConnectiosManagerDelegate`.
64. Новый метод обязан быть добавлен в этот интерфейс и в единственный `Delegate`.
65. `[SOURCE]` `Request.h` хранит `failedByFloodWait`, `premiumFloodWait` и `requestToken`.
66. `[SOURCE]` `ConnectionsManager.cpp:1389–1427` распознаёт `FLOOD_WAIT_`, `FLOOD_PREMIUM_WAIT_`, `SLOWMODE_WAIT_`.
67. `[SOURCE]` при обычном flood response native выставляет `discardResponse = true`.
68. `[SOURCE]` при slowmode native оставляет `discardResponse = false`.
69. Поэтому Java callback должен произойти до решения `discardResponse`.
70. `[SOURCE]` `minStartTime` рассчитывается из `waitTime`.
71. `[SOURCE]` retry loop находится около `ConnectionsManager.cpp:2610–2714`.
72. `[SOURCE]` текущий retry loop переотправляет запрос после `failedByFloodWait`.
73. [INFERENCE] отдельный одноразовый native resend callback нужен для события «снова отправлено».
74. `[SOURCE]` `DialogsHintCell` уже умеет title, subtitle, image, avatars и click listener.
75. `[SOURCE]` `DialogsHintCell` ограничивает title и message пятью строками.
76. Центр не должен встраивать записи в этот stock cell.
77. Плашка лимита может переиспользовать `DialogsHintCell` через маленький gated hook.
78. `[SOURCE]` `TeleConfig` загружается из `tele_config` при `TeleHooks.init`.
79. `[SOURCE]` `TeleDatabaseHelper` использует отдельный `tele.db`.
80. `[SOURCE]` `TeleDatabaseHelper` уже создаёт `tele_kv` и `tele_*` таблицы.
81. `[SOURCE]` текущая версия helper — 7, но stock database version не затрагивается.
82. `[SOURCE]` `TeleServer` скачивает `/v1/badges`, кеширует ETag и ограничивает feed четырьмя MiB.
83. `[SOURCE]` `TeleServer` выполняет HTTP на `DispatchQueue("teleServer")`.
84. `[SOURCE]` `TeleBadges` вычисляет Argon2 ключи на отдельной queue.
85. `[SOURCE]` `TeleBadges` кеширует данные через `AtomicReference`.
86. `[SOURCE]` существующий feed уже требует salt, argon2 и peers.
87. Не создавать второй HTTP-клиент для server notices.
88. Не передавать серверу raw account id только ради фильтра notice.
89. [INFERENCE] для `users` нужен тот же Argon2 key format, что и для `peers`.
90. Это требует подтверждения tele-server maintainer.

## 4. Таблица работ, коммитов и зависимостей

91. Коммит A: `feat: add notification notices storage`.
92. Коммит A покрывает модель, таблицу, сериализацию и prune.
93. Коммит A — effort M.
94. Коммит A зависит от существующего `TeleDatabaseHelper`.
95. Коммит B: `feat: hook tgnet flood waits`.
96. Коммит B покрывает C++ delegate, JNI wrapper и Java entry.
97. Коммит B — effort L из-за NDK и ABI.
98. Коммит B должен идти первым по порядку runtime-инфраструктуры.
99. Коммит C: `feat: add notification centre`.
100. Коммит C покрывает экран, settings row, unread badge и limit banner.
101. Коммит C — effort L.
102. Коммит C зависит от A и B.
103. Коммит D: `feat: show rate limit notices`.
104. Коммит D покрывает flood, slowmode, upload/download классификацию.
105. Коммит D — effort S после B и C.
106. Коммит E: `feat: log mentions and replies`.
107. Коммит E покрывает observer `didReceiveNewMessages` и deeplink.
108. Коммит E — effort M.
109. Коммит E зависит от C.
110. Коммит F: `feat: expand notification entries`.
111. Коммит F покрывает `Show more`/`Show less` в cell.
112. Коммит F — effort S.
113. Коммит F зависит от C.
114. Коммит G: `feat: log copied tele values`.
115. Коммит G покрывает fork clipboard callsites и `Copy` kind.
116. Коммит G — effort S.
117. Коммит G зависит от C.
118. Коммит H: `feat: badge notification mentions`.
119. Коммит H покрывает @/reply badge painting.
120. Коммит H — effort S.
121. Коммит H зависит от E и C.
122. Коммит I: `feat: add server notices`.
123. Коммит I покрывает feed parser, filters, photo cache и server gate.
124. Коммит I — effort M.
125. Коммит I зависит от C и готовых Android 0073/0074.
126. Рекомендуемый порядок: A, B, C, D, E, F, G, H, I.
127. Ручной native build нужен после B.
128. Полный batch build нужен после I.
129. Не объединять B с UI в один огромный commit.
130. Не добавлять unrelated clipboard callsites stock Telegram.
131. Не менять существующие Android patches задним числом без fixup в их commit.
132. Экспортировать каждый коммит отдельным Android patch.
133. Обновить PATCHLIST status только после реального export.
134. `features.md` обновлять в том же commit, что и export соответствующей фичи.

## 5. TeleConfig и настройки

135. Добавить `NOTICES = BoolItem("notices", false)`.
136. Добавить `NOTICES_LIMITS = BoolItem("notices_limits", false)`.
137. Добавить `NOTICES_LOG_LIMITS = BoolItem("notices_log_limits", false)`.
138. Добавить `NOTICES_TELE_TOASTS = BoolItem("notices_tele_toasts", false)`.
139. Добавить `NOTICES_MENTIONS = BoolItem("notices_mentions", false)`.
140. Добавить `NOTICES_COPIES = BoolItem("notices_copies", false)`.
141. Добавить `NOTICES_SERVER = BoolItem("notices_server", false)`.
142. Все семь новых default должны быть `false`.
143. `NOTICES` — родительский gate для локального центра.
144. Дочерние rows скрывать, пока `NOTICES` выключен.
145. `NOTICES_LIMITS` управляет toast и верхней limit-плашкой.
146. `NOTICES_LOG_LIMITS` управляет записью лимита в историю.
147. Это разделение следует desktop 0212.
148. `NOTICES_TELE_TOASTS` управляет записью fork toast.
149. `NOTICES_MENTIONS` управляет записью mention/reply.
150. `NOTICES_COPIES` управляет записью fork copy.
151. `NOTICES_SERVER` управляет применением notices из общего feed.
152. `NOTICES_SERVER` не должен включать обычные server badges.
153. URL server остаётся существующим `TELE_SERVER_URL`.
154. Пустой/invalid URL по-прежнему выключает tele server.
155. В settings section добавить страницу `notifications`.
156. Root row назвать `notifications`.
157. Root row содержит unread badge рядом с названием.
158. Внутри страницы показать `notification centre`.
159. Внутри страницы показать `rate limit notices`.
160. Внутри страницы показать `log rate limits`.
161. Внутри страницы показать `log tele toasts`.
162. Внутри страницы показать `log mentions and replies`.
163. Внутри страницы показать `log copied values`.
164. В server section показать `notifications from the server`.
165. Вариант `notifications from the server` скрывать, если root notices off.
166. Существующий settings builder использует RecyclerListView.
167. Каждый toggle обязан применять `TeleHooks.onConfigChanged`.
168. При выключении root нужно закрыть/сбросить текущие callbacks.
169. При выключении server нужно удалить pending photo/download jobs.
170. Добавить все семь ключей в export/import spec.
171. Не экспортировать записи центра вместе с настройками.
172. Записи центра являются локальной историей аккаунта.

## 6. Поиск настроек: IDs 1320..1339

173. Не переиспользовать существующие GUID 950..1109.
174. Зарезервировать диапазон 1320..1339 только для пачки 22.
175. `1320` — `tele notifications` → `notifications` page.
176. `1321` — `notification centre` → center page.
177. `1322` — `rate limit notices` → notifications page.
178. `1323` — `log rate limits` → notifications page.
179. `1324` — `log tele toasts` → notifications page.
180. `1325` — `log mentions and replies` → notifications page.
181. `1326` — `log copied values` → notifications page.
182. `1327` — `notifications from the server` → server page.
183. `1328` — `flood wait` keyword entry → notifications page.
184. `1329` — `slow mode` keyword entry → notifications page.
185. `1330` — `download throttling` keyword entry → notifications page.
186. `1331` — `upload throttling` keyword entry → notifications page.
187. `1332` — `mentions` keyword entry → notifications page.
188. `1333` — `replies` keyword entry → notifications page.
189. `1334` — `copied values` keyword entry → notifications page.
190. `1335` — `show more` keyword entry → center page.
191. `1336` — `server notices` keyword entry → server page.
192. `1337` — `notification history` keyword entry → center page.
193. `1338` — `tele toasts` keyword entry → notifications page.
194. `1339` — `unread notifications` keyword entry → center page.
195. [INFERENCE] SearchResult callback can point several keyword entries to one screen.
196. [INFERENCE] If the existing search adapter requires unique row semantics, use 1328..1339 as aliases with same destination.
197. Search titles must be lowercase to match existing TeleSearch style.
198. Search keywords must include both `slow mode` and `slowmode`.
199. Search keywords must include both `flood wait` and `flood_wait`.
200. Search keywords must include `copy`, `clipboard`, `history`.
201. Search IDs must be stable across subsequent patches.

## 7. Native tgnet hook: exact recommendation

202. Add `teleFloodWait` to `ConnectiosManagerDelegate`.
203. Recommended C++ declaration is:
204. `virtual void onTeleFloodWait(int32_t instanceNum, int32_t requestToken, int32_t seconds, bool resent, std::string error) = 0;`
205. The `error` argument is required to distinguish FLOOD, PREMIUM and SLOWMODE.
206. This signature is [INFERENCE] but follows existing delegate argument style.
207. Existing `onPremiumFloodWait` proves Java callback shape can carry account and token.
208. Add `jmethodID jclass_ConnectionsManager_onTeleFloodWait` beside existing method IDs.
209. In `TgNetWrapper.cpp`, implement the Delegate method beside `onPremiumFloodWait`.
210. Create `jstring errorString = NewStringUTF(error.c_str())`.
211. Call Java with `CallStaticVoidMethod`.
212. Release `errorString` with `DeleteLocalRef`.
213. Recommended Java signature is:
214. `@Keep public static void onTeleFloodWait(int currentAccount, int requestToken, int seconds, boolean resent, String error)`.
215. JNI descriptor is `(IIIZLjava/lang/String;)V`.
216. Java callback must not check `UserConfig.selectedAccount`.
217. Java callback must first check the native/root gate.
218. Java callback must post UI-visible work with `AndroidUtilities.runOnUIThread`.
219. Java callback must preserve `currentAccount` in every call to `TeleNotices`.
220. At native error parsing line 1393, parse wait text already present in `error->error_message`.
221. Call the new delegate after `waitTime` is validated.
222. Call it before `discardResponse` is used for completion.
223. Include `seconds = waitTime` for all three wait families.
224. Include the original error text, not a localized string.
225. Keep `FLOOD_PREMIUM_WAIT` separate from ordinary flood in `error`.
226. Keep `SLOWMODE_WAIT` separate from ordinary flood in `error`.
227. Add a native per-instance `teleNoticesEnabled` bit.
228. The bit must default false before Java config initialization.
229. Add a small native setter called from `TeleHooks` after config load.
230. The native branch must not call the delegate while that bit is false.
231. This is the lowest-level off gate required for stock-equivalent behavior.
232. [INFERENCE] setter can be posted to `Utilities.stageQueue` like existing native controls.
233. Add `bool teleFloodResentReported` to `Request` only if one-shot state is needed.
234. Reset that bit whenever a new wait is parsed.
235. In retry loop, detect a request whose wait deadline is ready.
236. Before enqueueing its retry, send one callback with `resent=true`.
237. A resend callback uses `seconds=0` and empty `error`.
238. Mark it reported before enqueueing to prevent duplicate callbacks.
239. Do not change `failedByFloodWait` or `minStartTime` to implement the notification.
240. Do not call Java from a UI method in native code.
241. Do not allocate a Java object for every normal request.
242. Keep the new request metadata only when native/root gate is enabled.
243. Add log lines only under `BuildVars.LOGS_ENABLED` / native `LOGS_ENABLED`.
244. Native log should include account, token, seconds, resent and error kind.
245. Avoid logging message text, peer IDs or clipboard values.

## 8. Java request metadata and TeleNotices entry

246. `ConnectionsManager` needs a token metadata map only while notices are enabled.
247. Store request class/category, connection type and account implicitly by manager instance.
248. Do not retain the entire `TLObject` after serialization.
249. Remove metadata on normal completion.
250. Remove metadata on cancel and failed terminal request.
251. Remove metadata after resend classification is consumed.
252. Map upload/download requests by connection type first.
253. Map generic request by `object.getClass().getSimpleName()` or stable TL constructor.
254. [INFERENCE] constructor-name mapping is less brittle than reflection over generated TLRPC.
255. Centralize mapping in `TeleNotices.classifyRequest`.
256. Categories must be `send`, `react`, `join`, `search`, `contacts`, `payment`, `transfer`, `other`.
257. Desktop send list includes sendMessage, sendMedia, sendMultiMedia, forwardMessages and sendInlineBotResult.
258. Desktop react list includes sendReaction, sendPaidReaction and stories sendReaction.
259. Desktop join list includes joinChannel and importChatInvite.
260. Desktop search list includes contacts search, messages search/global and resolve username.
261. Desktop contacts list includes importContacts and addContact.
262. Desktop payment list includes getPaymentForm, sendPaymentForm and sendStarsForm.
263. Desktop transfer list includes upload get/save/reupload operations.
264. Android generated constructor names must be checked in `TLRPC.java`, not edited.
265. If a constructor is unavailable, classify as `other` and record the gap.
266. `onTeleFloodWait` resolves request metadata before handing to TeleNotices.
267. `TeleNotices.onFloodWait(account, category, token, seconds, resent, error)` is the Java entry.
268. `TeleNotices` must own episode merging and countdown state.
269. `TeleNotices` must not call UI views from tgnet/native thread.
270. `TeleNotices` writes a database row from its account-specific state.
271. The `resent` event removes token from an active episode.
272. An episode is keyed by account and category.
273. A newer deadline extends the same episode rather than adding duplicate rows.
274. Use monotonic time for countdowns.
275. Store wall-clock creation date only for persistence and display.
276. `TeleNotices` must provide unread count as an account-scoped observable.
277. Root settings badge must use selected account only for display.
278. The center screen must accept explicit `currentAccount`.
279. Opening center marks only that account's visible entries read.
280. A copy action must not accidentally mark unrelated rows read.

## 9. Storage model and limits

281. Create `tele_notices` in `TeleDatabaseHelper.createArchiveTables`.
282. Use `account INTEGER NOT NULL` in every notice row.
283. Use composite primary key `(account, id)`.
284. Store desktop-like `id`, `kind`, `tone`, `date`, `key`, `rev`.
285. Store `title`, `text`, `entities` as UTF-8-safe strings/JSON.
286. Store `value` and `value_entities` for `Copy` notices.
287. Store buttons as bounded JSON array.
288. Store photo filename and width/height, not arbitrary remote bytes in SQLite.
289. Store peer, from, message, topic, source and source message when present.
290. Store nullable reply flag for mention/reply badge.
291. Store unread and an `extra` JSON object for forward compatibility.
292. Add indexes `(account, date DESC)` and `(account, unread)`.
293. Add an index `(account, kind, key)` for deduplication.
294. Store server seen state separately or in `tele_kv` with account prefix.
295. Server seen state needs id, revision and toasted flag.
296. The desktop current queue keeps notices for 30 days.
297. The desktop base cap is 300 non-mention notices.
298. Desktop 0232 adds a separate cap of 300 mention notices.
299. [INFERENCE] Android should preserve both caps for parity.
300. Prune old rows on helper initialization and after every insert batch.
301. Prune server seen entries to 500 ids, matching desktop behavior.
302. Server feed parser accepts at most 64 notices per response.
303. Server notice id maximum is 64 characters.
304. Server notice text maximum is 4096 characters.
305. Server notice entities maximum is 256.
306. Server notice photo maximum is 1 MiB.
307. Server notice buttons maximum is 2.
308. Server notice user key list maximum is 100000 parsed keys.
309. Existing feed maximum remains 4 MiB in `TeleServer`.
310. Do not load a full unbounded photo into memory.
311. Stream photo bytes and stop at 1 MiB plus one byte.
312. Use atomic temp-file rename for photo cache.
313. On revision update, replace the same `(account,id)` notice.
314. A revision update may toast once for the new revision.
315. A same-revision feed refresh must not duplicate a row or toast.
316. Merge equal tele toasts inside a 10-second window.
317. For copies, merge equal values only when the desktop behavior calls for it.
318. Store entities rather than flattening text; `Show more` must preserve links.
319. Sanitize offsets and lengths before saving or rendering.
320. Never deserialize untrusted JSON directly into a view object.

## 10. Rate-limit UX and exact strings

321. The desktop timing constants are 5 seconds for a toast threshold.
322. The desktop banner threshold is 60 seconds.
323. The desktop expiry toast threshold is 30 seconds.
324. The desktop toast duration is 10 seconds.
325. The desktop episode gap is 60 seconds.
326. The desktop countdown tick is 250 ms.
327. Use Android monotonic clock for those calculations.
328. Recommended exact labels are `Sending is limited`.
329. Recommended exact labels are `Reacting is limited`.
330. Recommended exact labels are `Joining chats is limited`.
331. Recommended exact labels are `Search is limited`.
332. Recommended exact labels are `Importing contacts is limited`.
333. Recommended exact labels are `Payments are limited`.
334. Recommended exact labels are `You can send again`.
335. Recommended exact labels are `You can react again`.
336. Recommended exact labels are `You can join chats again`.
337. Recommended exact labels are `You can search again`.
338. Recommended exact labels are `You can import contacts again`.
339. Recommended exact labels are `You can pay again`.
340. Countdown format is `%1 for %2`.
341. Banner subtitle format is `%1 left`.
342. Duration format is `%1 s` below one minute.
343. Duration format is `%1 m` or `%1 m %2 s` below one hour.
344. Duration format is `%1 h` or `%1 h %2 m` at one hour and above.
345. Completion title is the matching `You can … again` string.
346. Completion text is `After %1`.
347. All user-visible strings go to `strings_tele.xml`.
348. Do not edit stock `strings.xml`.
349. Use positional format arguments for translation safety.
350. [INFERENCE] Russian translations should be supplied with the normal Android resource workflow.
351. A limit row icon should be timer-shaped, matching desktop semantic icon.
352. A limit row should display the largest active deadline.
353. Tap on the limit banner opens the notification center.
354. Dismiss on the banner hides only the banner, not the history row.
355. `NOTICES_LIMITS` off hides toast/banner but does not imply `NOTICES_LOG_LIMITS` off.
356. `NOTICES_LOG_LIMITS` off keeps native detection only if needed for stock retry.
357. Native detection itself must remain invisible to the user when all gates are off.
358. Desktop 0212 excludes `SLOWMODE_WAIT` from `Tracked`.
359. Desktop 0212 excludes premium flood for transfer operations from `Tracked`.
360. The PATCHLIST gate explicitly asks Android to show flood wait/slowmode.
361. [OPEN] Decide whether Android follows desktop exclusion or the PATCHLIST gate.
362. Until resolved, detect and log the raw kind without silently dropping it.
363. Do not claim parity while that policy differs.

## 11. Mentions and replies

364. Subscribe to `NotificationCenter.didReceiveNewMessages`.
365. Do not use `NotificationsController.processNewMessages`.
366. `processNewMessages` does not include muted chat cases required here.
367. Event args are dialog id, message list, scheduled flag and mode.
368. Ignore scheduled messages.
369. Ignore outgoing messages.
370. Ignore service messages.
371. Require a group or megagroup target.
372. Detect `messageOwner.mentioned`.
373. Detect text entities addressing the current user.
374. Detect `MentionName` entities addressing the current account.
375. Detect replies whose resolved message belongs to the current account.
376. Do not treat a generic mention and a reply as the same badge.
377. Keep `reply` nullable when classification cannot be proven.
378. Exclude forum topic-root false positives as desktop does.
379. Use key `mention:<peer>:<message>`.
380. Keep up to 300 mention records for 30 days.
381. On click, open `LaunchActivity` deeplink to peer/message/topic.
382. Preserve explicit account in the deeplink intent.
383. If message no longer exists locally, request normal Telegram history.
384. Do not fetch message content from tele-server.
385. Edited message support uses `NotificationCenter.messageEdited` path.
386. Update text only inside the desktop 120-second edit window.
387. Keep the original notice if edit arrives after that window.
388. Mark the notice read when its row is opened or explicitly marked.
389. Add a mentions filter tab to center.
390. Add a replies distinction in icon and badge.
391. Reply badge uses reply icon.
392. Mention badge uses @/mention icon.
393. Avatar badge is drawn over sender avatar, not over recycled title text.
394. [INFERENCE] if sender avatar is unavailable, use semantic mention icon.

## 12. Full entries and copied values

395. The center list uses a dedicated RecyclerView adapter/cell in `tele/ui`.
396. Long text initially shows six lines, matching desktop 0239.
397. Add exact link text `Show more` after the clamped preview.
398. Expanded state changes to exact link text `Show less`.
399. Expand state belongs to notice id/revision, not only adapter position.
400. Recycled holder must restore collapsed/expanded state in every bind.
401. Width changes must recalculate StaticLayout and line count.
402. Entity spans must remain clickable after expansion.
403. Do not mutate stored notice text when expanding.
404. Do not use stock `DialogsHintCell` as the long-form notice cell.
405. The notice context menu includes `Copy` for text/value.
406. Copy notice activation copies its stored `value` again.
407. Copy notice title is the original toast title when present.
408. Copy notice body is the original toast text when present.
409. Copy notice value is never rendered as a title-only substitute unless body is empty.
410. Add `Copy` filter tab.
411. Exact copy toast is `Copied to clipboard.`.
412. Existing fork copy callsites must pass the copied value to `TeleNotices.copied`.
413. Start with fork callsites: peer id, message id, emoji id, aliases, bot payloads, link rewrites and tele settings export.
414. Do not wrap every stock `AndroidUtilities.addToClipboard` call.
415. A common fork helper should call `AndroidUtilities.addToClipboard` and then log.
416. Preserve plain text and HTML/entity clipboard variants where already supported.
417. Do not persist secrets, passwords, auth tokens or raw private keys.
418. [INFERENCE] add an explicit sensitive-value parameter to refuse logging.
419. Deduplicate equal values within the intended toast merge window.
420. Value rows must not leak values into logcat.

## 13. Android UI, threading and performance

421. `TeleNotices` receives native events off the main thread.
422. Native callback must hop to `AndroidUtilities.runOnUIThread` before view changes.
423. Database reads/writes must run on a dedicated tele queue, not UI.
424. Feed parsing and Argon2 matching must remain off UI.
425. Photo decoding must remain off UI; only bitmap assignment returns to UI.
426. Use account-specific `AccountInstance` and `MessagesController`.
427. Never use account 0 as a hidden default.
428. Center fragment stores account at construction.
429. Root settings badge uses `UserConfig.selectedAccount` only at display time.
430. On account switch, reload the selected account unread count.
431. Recycler holders must bind every visible property on every bind.
432. Clear image, spans, buttons, badge and expanded state before applying new notice.
433. Do not leave a previous account's notice in a recycled holder.
434. Use stable IDs composed from account and notice id.
435. Revision changes must invalidate the stable row content.
436. Avoid a bitmap allocation when a notice has no photo.
437. Bound photo dimensions before decoding.
438. Avoid a second full copy of the feed or large text on UI.
439. Respect `LiteMode` for row animations and toast transitions.
440. No custom animation may bypass LiteMode flags.
441. Use normal ripple for `Show more` and row clicks.
442. Center scrolling must be a standard RecyclerView operation.
443. Empty state string is `No notifications yet`.
444. Offline state should say `Server notices unavailable` only for server filter.
445. Local notices remain visible offline.
446. Opening the center must not mark Telegram chat history read.
447. Center rows are not Telegram messages and do not alter server unread counters.
448. `FLAG_SECURE` behavior follows existing privacy setting; center adds no override.
449. Do not show notice photos in notification previews outside the center.
450. Server notice buttons accept only allowed schemes.
451. Link clicks use normal Android intent/deeplink validation.
452. Avoid loading remote URL directly in a WebView.
453. Use `BulletinFactory`/stock toast primitives where applicable.
454. Create no notification channel for this in-app center.
455. The center is not an OS notification replacement.

## 14. Server notices protocol

456. Extend the existing `/v1/badges` JSON with optional top-level `notices`.
457. Existing clients must ignore unknown `notices` without failing badge parsing.
458. Each notice has `id`, `rev`, `type`, `title`, `text` and optional entities.
459. `type` maps to `info`, `success`, `warning` or `critical` tone.
460. Optional `photo` contains a relative URL and is fetched from the configured server.
461. Optional `buttons` contains no more than two `{text, link}` objects.
462. Allowed button links are `https://`, `http://` and `tg://`.
463. Optional `toast` requests one in-app toast.
464. Optional `builds` has `min` and/or `max` integer bounds.
465. Optional `platforms` is a list of platform strings.
466. Optional `users` is a list of Argon2-derived keys.
467. Optional `from` and `until` are time bounds.
468. The server parser must reject malformed id/rev/type combinations.
469. The parser must sanitize entity offsets and URL entities.
470. The parser must cap 64 notices per feed.
471. The parser must cap text at 4096 characters.
472. The parser must cap entities at 256.
473. The parser must cap photo response at 1 MiB.
474. The parser must cap buttons at 2.
475. The parser must cap user keys at 100000.
476. The Android feed should identify itself as `android` in User-Agent/build matching.
477. Build filtering must compare Android `TELE_BUILD` consistently.
478. [OPEN] Server maintainer must add `android` to accepted `platforms`.
479. [OPEN] Server maintainer must define Android build number semantics.
480. [OPEN] Server maintainer must publish whether `users` keys hash user id or account key.
481. [OPEN] Server maintainer must confirm `from`/`until` units are Unix seconds.
482. [OPEN] Server maintainer must confirm relative photo URL resolution.
483. [OPEN] Server maintainer must confirm notices in `/v1/badges` are public.
484. [OPEN] Server maintainer must confirm no per-account request is required.
485. Until those answers, 0206 remains locally testable with a fixture only.
486. Store `rev` per account and notice id.
487. Replace a row when a higher revision arrives.
488. Do not toast a revision twice.
489. Keep a 500-id seen/toasted memory per account.
490. Download a photo only when `NOTICES_SERVER` and root gate are on.
491. If root gate is off, do not parse notices into the local store.
492. If server gate is off, retain badges behavior but skip notices.
493. If URL is empty, skip notice feed and clear only server notice cache as appropriate.
494. Never send current-account id to the server as a filtering query.
495. Match user keys locally with existing Argon2 helper.
496. Use existing ETag/cache behavior for feed body.
497. Use a separate filename namespace for notice photos.
498. On malformed photo, keep text notice and omit image.
499. On server HTTP failure, retain last valid local notices.
500. Display server notice buttons only after normal URL validation.

## 15. Privacy, offline gates and failure behavior

501. Root `NOTICES` is the first gate for native callback delivery.
502. `NOTICES_LIMITS` gates toast and banner presentation.
503. `NOTICES_LOG_LIMITS` gates persisted limit rows.
504. `NOTICES_TELE_TOASTS` gates persisted fork toast rows.
505. `NOTICES_MENTIONS` gates the new-message observer work.
506. `NOTICES_COPIES` gates copied-value persistence.
507. `NOTICES_SERVER` gates parsing/application/photo requests.
508. Existing `TELE_SERVER_URL` gate remains the lowest HTTP URL gate.
509. Offline mode must not erase local center rows.
510. Offline mode must not retry server photo downloads indefinitely.
511. Use bounded retry behavior from existing `TeleServer` queue.
512. No tele-server request may include message text.
513. No tele-server request may include clipboard values.
514. No tele-server request may include mention/reply metadata.
515. No tele-server request may include account list.
516. Native logs may include request class/category but never message payload.
517. Crash reports must not include notice text or copied values.
518. Clear center data must remove only fork rows for the selected account.
519. Clearing server cache must not clear local flood/mention/copy rows.
520. Logout must remove that account's local rows and server seen state.
521. Account 0 logout must not remove account 1 rows.
522. Handle database errors by preserving stock behavior and logging locally.
523. Do not show a fake empty center when a DB read is still pending.
524. Show a deterministic empty state after the read completes.
525. On native callback parse error, do not affect request retry.
526. On Java exception, catch/log and leave tgnet request state untouched.
527. Never suppress a stock callback exception to claim center success.

## 16. features.md rows

528. Every user-facing patch needs an English row in `features.md`.
529. Rows belong under a new `notifications` settings subsection or agreed section.
530. Row 0205 name: `notification centre`.
531. Row 0205 description: `keeps tele notices, updates, crashes and rate-limit history in an in-app centre`.
532. Row 0205 location: `tele → notifications`.
533. Row 0205 default: `off`.
534. Row 0212 name: `rate limit notices`.
535. Row 0212 description: `shows flood, slow-mode and transfer throttling countdowns and records their end`.
536. Row 0212 location: `tele → notifications`.
537. Row 0212 default: `off`.
538. Row 0232 name: `mentions and replies in the notification centre`.
539. Row 0232 description: `keeps group mentions and replies to you, including muted groups`.
540. Row 0232 location: `tele → notifications`.
541. Row 0232 default: `off`.
542. Row 0239 name: `whole notification entries`.
543. Row 0239 description: `shows long entries with Show more and Show less`.
544. Row 0239 location: `tele → notifications`.
545. Row 0239 default: `with notification centre`.
546. Row 0240 name: `copied values in the notification centre`.
547. Row 0240 description: `keeps selected tele copied values so tapping a row copies them again`.
548. Row 0240 location: `tele → notifications`.
549. Row 0240 default: `off`.
550. Row 0246 name: `mention and reply badges`.
551. Row 0246 description: `marks mention and reply entries with the matching icon and avatar badge`.
552. Row 0246 location: `tele → notifications`.
553. Row 0246 default: `with mentions and replies`.
554. Row 0206 name: `server notices`.
555. Row 0206 description: `shows targeted public notices from the tele server feed without sending account data`.
556. Row 0206 location: `tele → server`.
557. Row 0206 default: `off`.
558. Use the actual exported Android patch link after export.
559. Use desktop links numbered 205, 212, 232, 239, 240, 246 and 206.
560. Do not invent Android patch filenames before export.
561. Do not call a row `always on` while its TeleConfig item defaults false.
562. Keep feature descriptions user-facing, not implementation notes.

## 17. Manual and automated test matrix

563. Build a clean debug APK after all native changes.
564. Install the ABI matching the device, normally arm64.
565. On launch confirm all new toggles are false.
566. Confirm notifications page is searchable by IDs 1320..1339.
567. Confirm root row has no unread badge with an empty store.
568. Enable only root center; generate a local tele toast.
569. Confirm toast is visible and row appears in center.
570. Disable root; generate another toast.
571. Confirm no new center row and normal toast behavior remains.
572. Enable limits presentation but keep limit logging off.
573. Trigger artificial `FLOOD_WAIT_5` in a test fixture.
574. Confirm countdown toast starts only at the defined threshold.
575. Confirm banner appears only for the defined 60-second threshold.
576. Confirm no persisted limit row while log gate is off.
577. Enable log limits and repeat the flood scenario.
578. Confirm one episode row, not one row per retry.
579. Let the request resend and confirm one `resent=true` transition.
580. Let the deadline expire and confirm `You can … again` row.
581. Trigger `SLOWMODE_WAIT_5` and inspect explicit policy result.
582. Trigger upload/download throttling and confirm category.
583. Confirm premium transfer handling matches the chosen policy.
584. Enable mentions and receive a mention in a muted group.
585. Confirm one notice and no dependency on OS notification delivery.
586. Reply to one of your own group messages.
587. Confirm reply icon differs from mention icon.
588. Edit the source message within 120 seconds.
589. Confirm notice text updates without duplicate row.
590. Edit after 120 seconds and confirm old row remains.
591. Tap mention row and confirm account-specific peer/message/topic open.
592. Disable mentions and repeat; confirm no row.
593. Create a long fork notice over six rendered lines.
594. Confirm exactly `Show more` is shown initially.
595. Tap it and confirm `Show less` plus full text.
596. Scroll/recycle rows and confirm expansion stays with notice id.
597. Rotate or resize and confirm no text/entity loss.
598. Enable copies and copy a fork peer/message/emoji id.
599. Confirm `Copy` row stores value but logcat does not print value.
600. Tap Copy row and confirm clipboard gets same value again.
601. Disable copies and repeat; confirm no row.
602. Install a fixture feed with one valid Android server notice.
603. Enable root, server gate and valid server URL.
604. Confirm one row and one toast for `toast: true`.
605. Refresh same feed and confirm no duplicate toast.
606. Increase `rev` and confirm replacement plus one new toast.
607. Use invalid scheme button and confirm it is discarded.
608. Use >1 MiB photo and confirm text row remains without photo.
609. Use 65 notices and confirm parser stores no more than 64.
610. Use wrong platform and confirm no row.
611. Use out-of-range build and confirm no row.
612. Turn off server gate while badges remain on.
613. Confirm badges can continue while notices are not applied.
614. Stop network before refresh.
615. Confirm cached local center remains visible and no new request loop.
616. Switch to account 1 and confirm account 0 unread count is not shown.
617. Log out account 1 and confirm account 0 rows remain.
618. Use LiteMode and confirm no extra animations or frame churn.
619. Capture before/after screenshots for every UI gate.

## 18. Logcat, native rebuild and proof

620. Add temporary debug logs only behind existing logging flags.
621. Java callback log format: `tele flood account=<n> token=<n> seconds=<n> resent=<bool> kind=<kind>`.
622. Native log format must omit raw error text if it can contain sensitive payload.
623. Log only normalized kind (`flood`, `premium`, `slowmode`, `unknown`).
624. Verify callback appears for the artificial flood fixture.
625. Verify callback does not appear when native/root gate is false.
626. Verify resend log appears once per request token.
627. Verify account number is correct with two accounts.
628. Verify Java UI updates appear on main thread assertions in debug.
629. Verify DB writes appear on the tele database queue, not main.
630. Run `./gradlew :TMessagesProj_App:assembleDebug` from `Telegram`.
631. The first build compiles tgnet and other natives and can be slow.
632. Confirm native objects are rebuilt after C++ timestamp/commit change.
633. Confirm APK outputs exist for every configured ABI split.
634. Install arm64 and, if available, test another ABI split.
635. Use `adb logcat` filtered to `tele`, `ConnectionsManager`, `tgnet`.
636. Record native callback proof with account/token/seconds, not message content.
637. Record JNI load proof after app restart, not only incremental install.
638. Confirm a clean rebuild does not remove the callback symbol.
639. Confirm toggling root off does not require app restart for Java UI.
640. If native gate setter requires restart, document it and do not claim live toggle.
641. A batch gate is not passed by a compiler result alone.
642. Human must exercise on and off paths on device/emulator.
643. Attach exact manual steps to the maintainer handoff.

## 19. Pitfalls and review checklist

644. Do not route all stock toasts through `TeleNotices`; only fork callsites are in 0205/0240.
645. Do not use selected account as native callback account.
646. Do not write mentions from `processNewMessages`.
647. Do not touch generated TLRPC.
648. Do not touch stock DB schema.
649. Do not put notice JSON into `tele_config` preferences.
650. Do not forget `account` in every query and primary key.
651. Do not retain Java TL objects in the request map.
652. Do not let map entries survive cancellation.
653. Do not count a resend as a new flood episode.
654. Do not turn `SLOWMODE_WAIT` into a generic `FLOOD_WAIT` label.
655. Do not treat download throttling as send limitation.
656. Do not log clipboard value.
657. Do not fetch server photos when server notices are off.
658. Do not make server notice feed mandatory for local center.
659. Do not assume server supports `android` before maintainer confirmation.
660. Do not assume build number units; use the agreed contract.
661. Do not use unbounded remote image size.
662. Do not show stale photo after revision replacement.
663. Do not leave old holder spans or buttons after recycling.
664. Do not animate against LiteMode.
665. Do not mark Telegram unread counters when center row is opened.
666. Do not use a reused stock notification channel.
667. Do not silently clear local history on network errors.
668. Do not claim exact desktop parity where Android lacks a policy answer.
669. Review C++ method signature in `Defines.h`, wrapper and Java together.
670. Review JNI descriptor `(IIIZLjava/lang/String;)V` against the Java method.
671. Review native gate default false before any account initialization.
672. Review TeleConfig export/import includes all seven keys.
673. Review TeleSearch IDs 1320..1339 have no collision.
674. Review features rows only after actual patch export.
675. Review PATCHLIST statuses only after build/manual evidence.
676. Final batch status sequence is `todo` → `wip` → `built` → `done`.

## 20. Решения и вопросы перед реализацией

677. Решение мейнтейнера уже принято: центр переносится целиком.
678. Решение мейнтейнера уже принято: первый fork native hunk будет в `jni/`.
679. Решение мейнтейнера уже принято: вход — строка с badge в tele settings.
680. Desktop origin/main подтверждает отдельные kind `Mention` и `Copy`.
681. Desktop origin/main подтверждает шесть строк `Show more`.
682. Desktop origin/main подтверждает photo/button/server notice limits.
683. [OPEN] Нужен ответ server maintainer по `platforms: ["android"]`.
684. [OPEN] Нужен ответ server maintainer по Android `builds.min/max`.
685. [OPEN] Нужен ответ server maintainer по Argon2 `users`.
686. [OPEN] Нужен ответ server maintainer по timestamp units.
687. [OPEN] Нужен ответ server maintainer по relative photo URLs.
688. [OPEN] Нужно решить desktop `Tracked(SLOWMODE_WAIT)` против PATCHLIST gate.
689. [OPEN] Нужно решить, считать ли transfer premium waits в Android журнале.
690. [OPEN] Нужно подтвердить, допустима ли дополнительная native enable setter.
691. [OPEN] Нужно подтвердить, нужен ли локальный tele-chat вход дополнительно к settings row.
692. До ответов 0206 можно реализовать с fixture, но не считать server contract закрытым.
693. До ответа 688 нельзя утверждать полную parity slowmode behavior.
694. После ответов обновить этот guide и только потом начинать I.
695. После каждого коммита собрать его patch и сверить соответствующий PATCHLIST row.
696. После всего порядка собрать all-ABI debug APK.
697. После human test перевести строки пачки в `done`.
698. Это завершает assignment для batch 22.
