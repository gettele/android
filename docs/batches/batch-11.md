# Пачка 11 — база приватности

## Назначение и границы

1. Это рабочее руководство для **текущей пачки 11**, а не старый quick-wins-план.
2. Порядок и состав ниже повторяют `docs/PATCHLIST.md` после перестановки: приватность реализуется первой.
3. В пачке ровно десять строк: `0016/0073`, `0032/0073`, `0032/0064`, `0166`, `0228`, `0227`, `0229`, `0282`, `0160`.
4. Порядок строк — порядок зависимостей, его нельзя менять без изменения PATCHLIST.
5. Сначала общий слой правил и picker, затем per-chat ghost, затем ghost-schedule; только после этого слова, уведомления, scheduled, stories, last-seen и streamer.
6. Старые быстрые фичи этой пачки сюда не возвращать.
7. Не включать в эту пачку desktop-only `0135`, `0136`, `0150`, `0152`, `0159`, `0163` и любые строки следующих пачек.
8. `0016`, `0073`, `0032`, `0064`, `0166`, `0228`, `0227`, `0229`, `0282`, `0160` — номера текущей очереди desktop.
9. Старые номера ghost и picker сверены с `desktop-numbers.md`: старый 0073 соответствует текущему 0073; старый ghost 0032 остаётся 0032.
10. `desk-0125-0164`, `desk-2`, `desk-3` и `desk-delta` использованы как assessment, но проверенный Android hook имеет приоритет.
11. Desktop-патчи читать только `git show origin/main:patches/tdesktop/...`; код Android — только `git show tele:...`.
12. Не копировать C++/Qt; переносится поведение через минимальные stock-хуки.
13. `[INFERENCE]` означает, что точка не подтверждена чтением ветки `tele` или требует ручного теста.
14. Нельзя выдавать `[INFERENCE]` за существующий hook.
15. В этом документе «локально» означает устройство и конкретный аккаунт, не tele-server.
16. Все сетевые действия остаются Telegram API; новый tele-server endpoint не добавляется.
17. Выключенный тумблер обязан быть неотличим от stock.
18. Любой новый тумблер `TeleConfig` имеет default `false`.
19. Исключение: существующие согласованные тумблеры не переопределять.
20. Ветка реализации — checkout Android `../Telegram`, branch `tele`; этот файл не патчируется в Android checkout.

## Нормативные правила реализации

21. Fork-код помещать в новые файлы `TMessagesProj/src/main/java/tele/`.
22. В stock-файле оставить import и минимальный gated call.
23. Не менять `TLRPC.java`, stock schema и `LAST_DB_VERSION`.
24. Не редактировать stock `strings.xml`; строки — `strings_tele.xml`, ключи с `Tele`.
25. Каждый пользовательский тумблер добавить в TeleConfig, settings row и export/import spec.
26. Из Java получать значение как `TeleConfig.ITEM.getValue()`, не обращаться к `.value`.
27. `TeleHooks.onConfigChanged` применяет изменения без перезапуска.
28. UI-пересчёт выполняется на main thread.
29. Ответы storage и ConnectionsManager переходят через `AndroidUtilities.runOnUIThread` перед UI.
30. Account передавать явно: `currentAccount`, `account`, `MessagesController.getInstance(account)`.
31. Никогда не использовать молча account 0 или `UserConfig.selectedAccount`.
32. Состояние Recycler/ListView выставлять в bind, не только в holder creation.
33. При переключении обновлять уже созданные cells, headers и notification rows.
34. Учитывать recycling: скрытая ячейка должна полностью сбрасываться при bind.
35. Не запускать анимации поверх `LiteMode` и performance-class ограничений.
36. Проверять nullable TL-поля до dereference.
37. Не логировать текст сообщений, usernames, номера и URL целиком.
38. Для нового notification channel использовать собственный `tele_*` id.
39. Не подменять серверные unread counters: корректировать локальные уведомления, badge и preview.
40. Не отправлять фильтры, ghost-исключения, слова или last-seen правила на tele-server.

## Общая модель хранения

41. Небольшие списки и настройки хранить через `TeleDatabaseHelper` в `tele_kv`.
42. Ключи должны быть account-scoped, как существующие `Aliases` и `LocalNames`.
43. Формат ключа должен содержать account в принятом helper-механизме; не делать глобальный singleton.
44. Для peer-specific значений использовать `account + dialogId`, а не только dialogId.
45. Значения игнора и ghost хранить раздельно, даже если picker общий.
46. Рекомендуемые ключи: `privacy_ignore`, `privacy_ghost`, `privacy_ghost_schedule`, `privacy_hidden_words`.
47. Для каждого ключа описать JSON/CSV формат и миграцию пустого/старого значения.
48. Набор peer id должен переживать cold start и смену аккаунта.
49. Удаление аккаунта удаляет только его fork-значения.
50. Не создавать stock-table и не писать в Telegram database rows.
51. Для per-chat words хранить `dialogId -> rules`; глобальные rules хранить отдельно.
52. Для last-seen хранить snapshot исходного правила и timestamp восстановления.
53. Для invisible stories хранить локальный `max_read_id` с TTL 48 часов, если это потребуется после проверки stock.
54. Удалять просроченные ghost/story записи на DB queue.
55. JSON read/write выполнять на database queue; UI picker получает immutable snapshot.
56. Изменение picker атомарно заменяет набор, не оставляет частично записанный JSON.
57. Не держать mutable rule list между аккаунтами.
58. Экспорт настроек не должен экспортировать приватные peer IDs в общий файл без явного решения.
59. Если export/import уже имеет account-scoped entries, добавить privacy keys туда явно.
60. В unresolved notes зафиксировать формат миграции до commit.

## TeleConfig и поиск

61. Основные privacy items: `IGNORE_USERS`, `GHOST_PER_CHAT`, `GHOST_SCHEDULE`, `HIDDEN_WORDS`, `MUTE_IGNORED`, `GHOST_SCHEDULED_MESSAGES`, `INVISIBLE_STORIES`, `LAST_SEEN_RESTORE`, `STREAMER_MODE`.
62. Все новые items default `false`.
63. Подтумблеры могут быть BoolItem/StringItem, но дочерний row скрывать при выключенном parent.
64. `GHOST_SCHEDULED_MESSAGES` не включать без `GHOST_SCHEDULE`.
65. `MUTE_IGNORED` не включать без ignore/hidden rules.
66. `INVISIBLE_STORIES` может использовать уже перенесённый master, но per-chat ghost обязателен для новой ветки.
67. `LAST_SEEN_RESTORE` default off и содержит предупреждение о возможном раскрытии факта просмотра.
68. `STREAMER_MODE` независим от 0113 never-block-screenshots и 0172 hide-phone.
69. Зарезервировать search IDs **1100–1119** включительно.
70. Эти IDs — локальные registry IDs, не Telegram dialog IDs и не сеть.
71. Не занимать IDs чужих страниц и не создавать второй item с тем же pref key.
72. Использовать существующий тип registry `TeleSearch`.
73. Каждая запись содержит key, title, description, page и keywords.
74. Рекомендуемая карта: 1100 `IGNORE_USERS`, 1101 `GHOST_PER_CHAT`, 1102 `GHOST_SCHEDULE`.
75. 1103 `HIDDEN_WORDS`, 1104 `MUTE_IGNORED`, 1105 `GHOST_SCHEDULED_MESSAGES`.
76. 1106 `INVISIBLE_STORIES`, 1107 `LAST_SEEN_RESTORE`, 1108 `STREAMER_MODE`.
77. 1109–1119 — aliases/details, указывающие на существующие rows или detail pages.
78. Keywords: ignore, muted, ghost, online, typing, read, schedule, hidden words, stories, last seen, streamer.
79. Alias не создаёт duplicate toggle.
80. Названия и описания UI — в `strings_tele.xml`; английский текст нужен также для `features.md`.
81. Search result должен открывать правильную privacy страницу, а не stock PrivacyUsersActivity.
82. Search rows account-independent; значения account-dependent.
83. Проверить deeplink и возврат назад после открытия search result.
84. Если текущий registry не поддерживает aliases, добавить записи в существующий массив без нового формата.
85. После добавления registry проверить отсутствие коллизий 1100–1119.

## Точный порядок работ

86. Шаг 1: общий `PrivacyRules`/`PrivacyPeers` helper и account-scoped tele_kv.
87. Шаг 2: privacy picker и первый патч 0016/0073.
88. Шаг 3: data-layer gates для DialogCell и ChatMessageCell.
89. Шаг 4: per-chat ghost, используя тот же picker и helper.
90. Шаг 5: ghost-schedule и возврат offline-after-send.
91. Шаг 6: hidden words поверх общей классификации видимости.
92. Шаг 7: notification suppression и локальные preview/unread corrections.
93. Шаг 8: ghost-scheduled local message handover.
94. Шаг 9: invisible stories и rollback/read persistence.
95. Шаг 10: last-seen snapshot/restore.
96. Шаг 11: streamer mode, включая все windows и notifications.
97. Не начинать следующий шаг, пока API предыдущего не зафиксирован.
98. Каждый desktop row остаётся отдельным Android commit.
99. Если строку приходится делить, указать это в PATCHLIST до реализации.
100. После каждого commit экспортировать обычным `git format-patch`, не редактируя `.patch` вручную.

## 0016, 0073 — игнор-лист

101. Поведение: выбранный пользователь/чат скрывается или затухает в списке и сообщениях.
102. Picker должен выглядеть как privacy exceptions, но stock `PrivacyUsersActivity` не переиспользовать.
103. Причина: stock activity зашита на `TYPE_BLOCKED` и `ContactsController` block-list.
104. Сделать fork picker в `tele/ui/settings/` с выбором users/chats и поиском.
105. Picker возвращает account-scoped peer IDs и режим `hide` или `fade`.
106. Точный текущий Android anchor picker не подтверждён в доступном stock window: `[INFERENCE]`.
107. Перед реализацией найти существующие `PrivacyUsersActivity`, `ContactsController` и launch picker через `git show tele`.
108. Не перехватывать server block/unblock и не вызывать `contacts.block`.
109. Хранить список в `tele_kv`, без новой таблицы.
110. Фильтр сообщений должен быть единым helper, чтобы 0166 и 0228 использовали тот же результат.
111. Для ChatMessageCell: hide означает не строить видимый текст/контент, fade означает стабильную alpha.
112. Для DialogCell: hide исключает preview, fade применяет alpha только к содержимому игнорируемого peer.
113. При recycling всегда восстанавливать alpha и visibility для обычного peer.
114. Не скрывать собственные исходящие сообщения, если desktop semantics не требуют иного; решение уточнить.
115. Не применять к service messages без явного решения.
116. Не удалять MessageObject и не менять серверную историю.
117. Не менять `TL_dialog.unread_count` в базе.
118. Кэш результата допустим только на bind и должен инвалидироваться при изменении списка.
119. Вызов должен быть data-layer-first; UI hook — последний фильтр для render.
120. [INFERENCE] Точная точка загрузки новых сообщений зависит от текущего `ChatActivity` notification path.
121. Проверить `MessagesController`, `ChatActivity` и `DialogCell` локальными окнами вокруг символов.
122. При смене ignore settings послать существующий UI update на main thread.
123. Не делать отдельный network request.
124. Добавить privacy row, picker entry, search ID и export spec.
125. On: выбрать пользователя, проверить скрытие в чате и list preview.
126. On: выбрать fade и проверить alpha после scroll/rebind.
127. On: cold start, второй аккаунт, переключение аккаунтов.
128. Off: сравнить с stock и убедиться, что текст/preview/alpha не меняются.
129. Logcat tag `TelePrivacy`; debug-only account/dialog IDs, без текста.
130. Ошибка picker не должна включать фильтр по умолчанию.

## 0032, 0073 — per-chat ghost

131. Per-chat ghost — исключение/включение ghost для конкретного dialog.
132. Существующий global ghost layer уже подавляет online, typing, read и contents-read; не дублировать его.
133. Добавить `PrivacyRules.isGhosted(account, dialogId)` в самый нижний общий gate.
134. Для ghosted chat подавлять `account.updateStatus`, typing updates, read receipts и contents receipts.
135. Android 0023 network contents-read gate должен учитывать peer, а не только global switch.
136. `MessagesController` и `ConnectionsManager` call sites должны получать account явно.
137. Не отправлять исключения на сервер и не менять Telegram privacy settings.
138. Picker тот же, что в 0016, но отдельный storage key.
139. Разрешить глобальный ghost плюс per-chat allowlist/denylist, не смешивать семантики.
140. Зафиксировать UI label: `Ghost mode exceptions`.
141. [INFERENCE] Точные Java anchors для online/typing/read не перечислять до чтения `git show tele`.
142. Использовать уже проверенный network-layer hook 0023 только если его сигнатура совпадает.
143. Не считать отсутствие callback доказательством offline.
144. On: включить ghost globally, добавить обычный чат в исключение, проверить online/typing/read.
145. On: проверить contents-read на медиа и text.
146. On: проверить другой аккаунт не наследует список.
147. Off: global ghost off — per-chat storage не меняет stock.
148. Off: remove exception — поведение совпадает с global ghost.
149. Kill/restart: исключения переживают cold start.
150. Logcat `TeleGhost`, только event type/account/dialog, без peer name.

## 0032, 0064 — ghost-schedule и offline-after-send

151. Цель: schedule-трюк отправляет ghost message с `scheduleDate`, затем возвращает клиент в offline state.
152. Это база для 0227; 0227 нельзя начинать раньше этого row.
153. Desktop source read via `git show origin/main`; Android behavior assessment says current scheduled path is in `SendMessagesHelper`.
154. [INFERENCE] Точная Android signature `SendMessagesHelper.sendMessage(... scheduleDate)` требует повторной проверки ветки `tele`.
155. Не изменять server scheduled date semantics для обычных scheduled messages.
156. Ghost schedule должен быть gated одновременно `GHOST_SCHEDULE` и per-chat ghost.
157. В момент отправки использовать Telegram API, не tele-server.
158. После send не оставлять пользователя online дольше stock-required request window.
159. Не глушить unrelated chats и active user actions.
160. Состояние retry/ghost handover account + dialog + mid.
161. Сохранять только минимальную локальную metadata, не message body.
162. Schedule date и privacy state должны быть nullable-safe.
163. Не отправлять typing/read receipt после handover.
164. [INFERENCE] «offline-after-send» требует ручного теста сетевых updates и может нуждаться в отдельном hook.
165. Если Telegram API не позволяет точный трюк на Android, эскалировать как unresolved, не имитировать успех.
166. On: schedule ghost message, закрыть чат, убедиться, что локальный ghost marker виден.
167. On: online/typing/read не появляются для peer.
168. On: после due message уходит через Telegram API.
169. On: process kill до due и cold start восстанавливают локальный state.
170. Off: ordinary schedule path byte/behavior-equivalent to stock.
171. Logcat `TeleGhostSchedule`, account/dialog/mid/status only.

## 0166 — скрытие по слову и Java-regex

172. Зависит от ignore-list; rules engine не создавать заново.
173. Глобальные rules и per-chat rules объединяются перед match.
174. Семантика: plain string или Java regex; принять Java-regex, не обещать PCRE.
175. Поддержать case-sensitive и `/regex/i`, если формат согласован в settings UI.
176. Невалидный regex подсвечивать и не применять, сохраняя пользовательский текст.
177. `TeleHooks.hiddenByWords(MessageObject)` — рекомендуемый public extension point.
178. Не менять `messageOwner.message`; display text может быть заменён локально.
179. В чате скрывать чужие, не service и не sponsored сообщения согласно desktop semantics.
180. В DialogCell preview брать последнее подходящее видимое сообщение.
181. [INFERENCE] Точный load/new-message anchor `messagesDidLoad`/notification path не утверждать без `git show`.
182. Кэш match на HistoryItem допустим, но инвалидировать при изменении rules.
183. Unicode match не должен падать на surrogate pairs.
184. Не regex-сканировать всю SQLite без лимита: stock sqlite REGEXP отсутствует.
185. Per-chat editor открывается из chat header, global editor — privacy page.
186. On: слово скрывает сообщение в чате и preview.
187. On: regex, invalid regex, case-insensitive и per-chat rule.
188. Off: сообщение и preview полностью stock.
189. Logcat `TeleHiddenWords`, не логировать rule или message text.

## 0228 — ignored/hidden words молчат

190. Зависит от 0016/0073 и 0166.
191. `MUTE_IGNORED` не должен запрещать Telegram получать update.
192. В `NotificationsController.processNewMessages` пропускать notification side effects для classified hidden messages.
193. Не показывать notification, toast, mention/reaction badge для hidden item.
194. Локальный badge/preview можно скорректировать, серверный unread не менять.
195. Dialog preview берёт предыдущее подходящее сообщение, максимум 512 сообщений как assessment target.
196. Если подходящего нет, показывать стандартный empty/last-known state.
197. [INFERENCE] Точная точка выбора `dialog.top_message` требует проверки `MessagesController`/`MessagesStorage`.
198. Не удалять hidden message из history и не менять read state сервера без ghost semantics.
199. Mentions button должен исключать hidden IDs локально.
200. Reactions/mentions controls должны bind-reset при recycling.
201. On: ignored incoming message не создаёт notification.
202. On: hidden-word incoming message не создаёт notification.
203. On: ordinary incoming message всё ещё уведомляет.
204. On: server unread remains explainably unchanged while local UI is quiet.
205. Off: stock notifications and preview restored.
206. Logcat `TelePrivacyNotifications`, classification only.

## 0227 — показ ghost-scheduled сообщений

207. Зависит от ghost-schedule, per-chat ghost и ignore filter.
208. До server due ghost-scheduled message видно только локально автору.
209. Local row должен иметь distinct non-server marker, но не менять Telegram TL schema.
210. Handover после отправки заменяет local object server response, как stock send path.
211. Не дублировать сообщение при updates/reconnect.
212. Ignore/hidden words применяются к local display так же, как к server display.
213. Notifications не создаются до handover.
214. После handover обычные notification rules применяются по итоговому server message.
215. [INFERENCE] Точный local object insertion point в `ChatActivity`/`SendMessagesHelper` не подтверждён.
216. [INFERENCE] Принцип handover должен быть проверен на album, reply и media.
217. Не хранить message body в `tele_kv`; использовать существующий local message/draft mechanism.
218. On: local message visible only to author before due.
219. On: process restart restores or safely drops local marker according to chosen persistence.
220. On: successful send yields one server message and one row.
221. On: failed send shows local error without notification storm.
222. Off: stock scheduled message path unchanged.
223. Logcat `TeleGhostScheduled`, account/dialog/mid/status, no body.

## 0229 — невидимые сторис

224. Зависит от per-chat ghost и existing Android 0021 invisible stories.
225. Target behavior: `InvisibleStories(peer) = watch-invisibly || (ghost-stories && Ghosted(peer))`.
226. `StoriesController.markStoryAsRead` must suppress `TL_stories_readStories` for invisible peer.
227. Existing assessment anchor: `StoriesController.markStoryAsRead` around 1287–1322; verify exact branch via `git show tele`.
228. `StoryViewer` live-story behavior currently blocks in an assessed path; verify before changing.
229. Local read memory may use `dialogIdToMaxReadId` and `storiesStorage.updateMaxReadId`.
230. [INFERENCE] Проверить, что `getAllStories` не откатывает local max_read_id после restart.
231. Keep local read memory for 48h only if stock storage semantics permit.
232. Reaction/reply that would reveal viewer requires confirmation.
233. Live story: unresolved whether hard block or confirmation; do not silently choose.
234. No story endpoint besides Telegram `stories.*` calls.
235. On: view ordinary story without server read request.
236. On: ring does not reappear after local read TTL rules.
237. On: reaction/reply asks before revealing.
238. On: process kill/cold start preserves expected invisible state.
239. Off: existing 0021 behavior exactly unchanged.
240. Logcat `TeleInvisibleStories`, peer/story IDs only in debug.

## 0282 — restore hidden last seen

241. Default off and warning in description are mandatory.
242. Behavior: temporarily apply a local last-seen rule, inspect profile, restore original rule on exit/start.
243. This is not a server-side permanent privacy change.
244. Store original rule, account, target peer and restore state in `tele_kv`.
245. Restore is REQUIRED after process death and cold start.
246. Restore before opening ordinary UI if pending state exists.
247. Use `ContactsController`/`ProfileActivity` only after exact `git show tele` anchor verification.
248. [INFERENCE] Exact API request and callback names are not asserted here.
249. Never assume success from local UI; wait for Telegram response/error.
250. On failure, preserve pending restore and show non-sensitive local error.
251. Do not log phone, username, or privacy rule contents.
252. On: enable, inspect, leave profile, verify original rule restored.
253. On: kill process during operation, cold start restores original rule.
254. On: network failure, retry restore without looping requests.
255. Off: no request and no local mutation.
256. Logcat `TeleLastSeen`, account/peer/status only.

## 0160 — streamer mode

257. Independent from 0113 never-block-screenshots and 0172 hide-phone.
258. Default off; window title/tray desktop parts are n/a on Android.
259. Screen capture: apply secure behavior in every window that can set `FLAG_SECURE`.
260. Assessment names `FlagSecureReason`, `AndroidUtilities.allowScreenCapture`, `LaunchActivity`, `BubbleActivity`, `ExternalActionActivity`.
261. Exact anchors must be re-read via `git show tele`; snippets here are verified assessment names, not invented line numbers.
262. Notification previews must be hidden through `NotificationsController` preview branches.
263. Profile/drawer phone display uses common privacy helper with 0172, but does not depend on 0172.
264. Do not change account or chat title if Android has no desktop window title equivalent.
265. Conflict with 0113 is unresolved: define precedence before code; streamer should protect unless explicit maintainer decision says otherwise.
266. Never reuse stock notification channel for changed preview policy.
267. On: screenshot and recents thumbnail are protected in every applicable window.
268. On: notification content is generic, no sender/text preview.
269. On: profile/drawer phone is hidden.
270. On: opening/recycling rows restores normal display when off.
271. Off: stock capture, previews and phone rows unchanged.
272. Logcat `TeleStreamer`, event names only, no content.

## Проверенные/непроверенные anchors

273. Verified by assessments: `DialogCell`, `ChatMessageCell`, `NotificationsController`, `StoriesController`, `StoryViewer`, `SendMessagesHelper`, `ContactsController`, `ProfileActivity`, `FlagSecureReason`.
274. Verified behavior names are not permission to copy line numbers from another Android version.
275. `StoriesController.markStoryAsRead` and `ChatMessageCell` are hot paths; read small windows only.
276. `[INFERENCE]` 0016 picker exact implementation path.
277. `[INFERENCE]` new-message classification callback.
278. `[INFERENCE]` offline-after-send endpoint/hook.
279. `[INFERENCE]` ghost local message handover.
280. `[INFERENCE]` story read rollback after cold start.
281. `[INFERENCE]` last-seen request method and restore callback.
282. `[INFERENCE]` precedence between streamer and never-block-screenshots.
283. Before implementation, record exact class/method snippets in commit notes.
284. Do not put guessed snippets into this guide.
285. If anchor moved, update only the implementation note, not behavior contract.

## Тестовая матрица

286. Каждый row тестировать on и off; off must equal stock.
287. Каждую privacy setting test on two accounts.
288. Каждый peer-specific setting test personal chat, group and channel where applicable.
289. Test cold start, process kill, rotation and Recycler rebind.
290. Test network loss during every Telegram request.
291. Test empty picker, duplicate peer, removed peer and account switch.
292. Ignore: hide and fade, chat list and message list.
293. Ghost: online, typing, read, contents-read and exception removal.
294. Ghost-schedule: local visibility, send, handover, restart and failure.
295. Hidden words: plain, valid regex, invalid regex, per-chat and global.
296. Quiet notifications: ignored, hidden words, ordinary message, mentions/reactions.
297. Ghost scheduled: one row before and after handover, no duplicate.
298. Invisible stories: view, ring, live, reaction confirmation, restart.
299. Last seen: restore after normal exit, kill, error and retry.
300. Streamer: screenshots, recents, notification preview, profile phone, off restore.
301. LiteMode: no privacy feature adds animation when LiteMode is active.
302. Threading: no view access from storage or ConnectionsManager callback.
303. Logcat must contain no message body, URL, phone, username or rule text.
304. Verify `TeleConfig` defaults by inspecting settings and fresh install.
305. Verify search IDs 1100–1119 with every result opening the intended row.
306. Verify export/import does not leak cross-account peer IDs.
307. Verify no tele-server request occurs for any row.
308. Verify Telegram endpoint calls only happen when relevant toggle is on.

## Нерешённые решения

309. Выбрать hide/fade default semantics и можно ли смешивать режимы по peer.
310. Решить, включать ли service messages в ignore/word filters.
311. Утвердить формат per-chat rules и Java-regex syntax in UI.
312. Утвердить предел 512 сообщений для previous visible preview.
313. Утвердить offline-after-send API behavior on Android.
314. Утвердить persistence model local ghost-scheduled message после kill.
315. Утвердить live-story hard block versus confirmation.
316. Утвердить 48-hour story read TTL и server/local precedence.
317. Утвердить last-seen temporary rule API и failure retry policy.
318. Утвердить streamer precedence over never-block-screenshots.
319. Утвердить whether streamer hides phone in all profile variants or only profile row.
320. Утвердить whether privacy peer IDs are included in export/import.
321. Открытые решения записать в `docs/decisions.md` before changing contract; не закрывать их тихой inference.

## Контрольные команды и gate

322. Проверить Android source: `git show tele:<path>` в checkout Telegram.
323. Проверить desktop source: `git show origin/main:patches/tdesktop/<patch>`.
324. Не использовать рабочие незакоммиченные файлы как доказательство anchor.
325. Не редактировать `.patch` вручную.
326. Сначала каждый commit в Telegram checkout, затем export patch.
327. Обновить `PATCHLIST.md` статусы и notes после фактического результата.
328. Обновить `features.md` английской строкой для каждого user-facing patch.
329. Build gate: `./gradlew :TMessagesProj_App:assembleDebug`.
330. Передать debug APK на ручную проверку.
331. Пачка не `done`, пока человек не проверил on/off matrix.
332. Статусы: `todo → wip → built → done`; failed manual test не скрывать.
333. Gate acceptance: ignore list works in chat/list and picker resembles privacy.
334. Gate acceptance: per-chat ghost suppresses all four ghost classes.
335. Gate acceptance: ghost schedule sends through Telegram and returns offline.
336. Gate acceptance: hidden words and ignored peers do not notify.
337. Gate acceptance: ghost-scheduled message is local then hands over exactly once.
338. Gate acceptance: invisible stories do not mark read and survive restart.
339. Gate acceptance: last seen restores after process kill and cold start.
340. Gate acceptance: streamer mode does not expose content in capture or notifications.
341. Gate acceptance: every new toggle off is stock and no unexpected request occurs.
342. Gate acceptance: logs are privacy-safe and settings/search IDs are stable.
343. Никаких новых endpoint, tele-server payloads или stock DB migrations.
344. Никаких обещаний о проверенном hook там, где указано `[INFERENCE]`.
345. Этот документ завершён только после выполнения строк 1–344 и ручного batch gate.
