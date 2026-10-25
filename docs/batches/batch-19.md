# Пачка 19 — поиск и чат

## 1. Назначение, источники и границы

1. Этот план описывает только пачку 19 из `docs/PATCHLIST.md`.
2. Название пачки: «поиск и чат».
3. В пачку входят ровно десять строк таблицы PATCHLIST: 0168, 0281, 0280, 0268, 0134, 0235, 0127, 0317, 0328, 0249.
4. Очерёдность номеров — текущая нумерация desktop queue, а не старые номера.
5. `docs/desktop-numbers.md` — источник отображения старой и новой нумерации.
6. Изучены правила `AGENTS.md`, PATCHLIST, решения, portability, desktop-numbers, architecture и development.
7. Также учтены исследования `desk-2.md`, `desk-3.md`, `desk-4.md` и `desk-delta.md`.
8. Desktop patch content сверялся командой `git show origin/main:<patch>` в checkout `tele` для всех десяти desktop rows.
9. Android anchors и API сверялись по `git show tele:<path>` в checkout `Telegram`.
10. Desktop C++/Qt реализацию не копировать: переносится видимое поведение через Android APIs.
11. Android изменения идут коммитами на ветке `tele` соседнего checkout `Telegram`.
12. `patches/android/*.patch` не редактировать вручную.
13. Экспортировать очередь обычным `git format-patch` по правилам `docs/development.md`.
14. Статусы PATCHLIST не менять этой инструкцией.
15. Каждый desktop row, требующий работы, — отдельный Android commit.
16. Исключение — уже существующая stock функциональность: не создавать искусственный коммит.
17. В PATCHLIST у пачки effort `S×4, M×6`; сохранить это агрегатное обозначение.
18. В каждой заметке PATCHLIST есть оценки отдельных задач, ниже дана практическая последовательность.
19. Критерий off: ни helper, ни UI-вмешательство не исполняются при выключенной фиче.
20. Все новые пользовательские switches по умолчанию выключены.
21. Никакой stock DB schema, `LAST_DB_VERSION` или `TLRPC.java` не менять.
22. Fork состояние хранить в `tele_kv` или новых `tele_*` таблицах.
23. UI менять только на главном потоке.
24. Сетевые/storage callbacks считать фоновыми до явного перехода на UI.
25. Любое состояние привязывать к `currentAccount`; поиск — также к dialog/topic/query.
26. В recycler/cached row каждое визуальное состояние задавать при bind, не только при создании.
27. Соблюдать `LiteMode` и performance class; для этих функций анимация не обязательна.
28. `[INFERENCE]` Конкретные номера строк Android-кода не фиксировать: anchors находить по именам символов на актуальном `tele`.
29. Перед хунком искать точную сигнатуру в целевом upstream; не переносить численные line anchors из исследований.
30. Любое поведение, которое источники не подтверждают, ниже явно помечено `[INFERENCE]` или вынесено в вопрос.

## 2. Состав и исключённые соседние задачи

31. 0168 — regex поиск в уже загруженной истории; решение по умолчанию включает поиск в чате и в поиске списка чатов.
32. 0281 — поиск в чате с рядом type chips, включая GIF и кружки.
33. Поиск по автору вместе с типом сообщения (прежняя отдельная строка 0306, на десктопе влита в 0281) входит в 0281.
34. 0280 — последовательное упоминание нескольких людей долгим нажатием; не для inline-ботов.
35. 0268 — показать онлайн участников большой группы, включая край скрытого списка участников при числе не более 200.
36. 0134 — показать/скрыть панель закрепа из меню чата; default off, пункт при `!allowPin` согласно PATCHLIST.
37. 0235 — собственная полоса реакций, локальный порядок и drag-reorder.
38. 0127 — локально закреплённые sticker/emoji наборы в панели.
39. 0317 — фильтр sticker/emoji по формату через mime документа.
40. 0249 — запрет мини-аппам переходить в fullscreen; при запросе вернуть `UNSUPPORTED`.
41. В строках пачки нет call log, VoIP-звонков или voice-chat функций.
42. Поэтому calls не добавлять и не расширять call UI в этой пачке.
43. В строках нет удаления сообщений/чатов, отката удаления, Retry all, upload retry или queued send.
44. Эти задачи находятся в соседних строках/пачках и не должны попасть в коммиты пачки 19.
45. В частности 0220 Retry all и 0226 «видно и отпустить сообщения за upload» относятся к пачке 17.
46. Keep-deleted / recovery находятся в пачке 14 и базе приватности в пачке 12; не смешивать.
47. В batch 19 нет изменения истории редактирования/удаления.
48. «Поиск истории» 0168 означает локальный проход загруженных объектов, не архивирование и не обход всей SQLite.
49. Android уже имеет глобальные search filters; 0281 касается именно поиска внутри чата.
50. Calendar 0225 в PATCHLIST отмечен уже имеющимся в stock; отдельная календарная работа в 19 отсутствует.
51. `[INFERENCE]` «Детали чата», history screen и календарь нельзя трактовать как дополнительные deliverables этой пачки без изменения PATCHLIST.
52. Ворота — ровно критерии PATCHLIST, дополненные regression-проверками из этого guide.

## 3. Правила TeleConfig, настроек и Search IDs

53. Каждый реальный switch объявить в `tele/TeleConfig.kt` отдельным config item.
54. Config key — snake_case; Kotlin property — стабильное имя в стиле текущего файла.
55. Defaults всех новых функций — `false`, кроме подфункций, которые не являются независимыми переключателями.
56. Предлагаемый `REGEX_SEARCH` — master для regex режима 0168, default `false`.
57. Предлагаемый `CHAT_SEARCH_TYPES` — gate чипов 0281, default `false`.
58. Предлагаемый `CHAIN_MENTIONS` — 0280, default `false`.
59. Предлагаемый `SHOW_GROUP_ONLINE_MEMBERS` — 0268, default `false` для недостающего края; не переписывать stock поведение остальных групп.
60. Предлагаемый `PINNED_BAR_MENU` — 0134, default `false`.
61. Предлагаемый `REACTION_STRIP` — 0235, default `false`.
62. Предлагаемый `PIN_STICKER_SETS` — 0127, default `false`.
63. Предлагаемый `STICKER_FORMAT_FILTER` — 0317, default `false`.
64. Предлагаемый `WEBAPPS_NO_FULLSCREEN` — 0249, default `false`.
65. Property/key names здесь — планируемые, сверить совпадения в `TeleConfig` перед добавлением.
66. Сочетание «автор + тип» — дополнительное измерение поиска внутри 0281, а не самостоятельный дополнительный switch.
67. Не создавать switch для функции, уже работающей в stock и не изменяемой форком.
68. В частности поиск-пользователь внутри 0281 зависит от search chips и текущего Android API, а не обязательно config item отдельного типа.
69. Настройки размещать в существующей подходящей группе/странице `TeleSettingsActivity`; не строить новый корневой экран.
70. Chat-search и sticker-panel опции — группа chats/interface в текущей структуре; соблюдать действующие `MODE_*`.
71. Реакции — существующая группа chats/interface, по фактической структуре настроек.
72. Web apps — bots/interface согласно текущей странице и search scope.
73. Menu toggle 0134 — chats/menu по структуре текущего settings mode.
74. Search IDs для этой пачки зарезервировать диапазоном 1260–1279.
75. Номера ID — постоянные идентификаторы, не выводить их из порядка строк.
76. 1260 — regex search in chat.
77. 1261 — regex search in dialogs list.
78. 1262 — search loaded chat history.
79. 1263 — chat search filters.
80. 1264 — search GIF messages.
81. 1265 — search round video messages / кружки.
82. 1266 — search by sender and type / конкретный человек.
83. 1267 — chain mentions / mention several people.
84. 1268 — show online members in large groups.
85. 1269 — show or hide pinned bar from chat menu.
86. 1270 — custom reaction strip.
87. 1271 — reorder reactions / drag.
88. 1272 — pin sticker and emoji sets.
89. 1273 — filter stickers by format.
90. 1274 — filter emoji/stickers by format / mime.
91. 1275 — keep mini apps out of fullscreen.
92. 1276 — web app fullscreen request.
93. 1277 — regex errors and invalid patterns.
94. 1278 — search person plus media type.
95. 1279 — aliases in Russian/English for all above.
96. IDs should point to actual setting/group rows where possible; aliases can point to the same row.
97. Alias rows are search metadata only, not config items and not export/import values.
98. Do not expose child controls as independent active settings while parent is off.
99. Register IDs once in `TeleSearch`; add relevant Russian and English terms.
100. Search coverage: «regex», «регулярное выражение», «поиск», «GIF», «кружок», «автор», «человек», «упоминание», «онлайн», «закреп», «реакции», «стикер», «формат», «мини-апп», «fullscreen».
101. Search must scope each result to the page where its setting lives.
102. Every actual `TeleConfig` item must be in export/import spec table.
103. Search aliases and group-only rows must not be exported as config values.
104. Resource keys begin `Tele` in `strings_tele.xml`.
105. Never edit stock `strings.xml`.
106. Description should explain local-only behavior, scope, and data limits where appropriate.
107. Descriptions must not claim regex searches server history or SQLite.
108. Descriptions must not promise that unavailable member lists can be enumerated.
109. After adding settings, ensure `TeleNewSettings`/search registration uses current conventions.
110. Deeplink target should open the correct existing settings mode, not a new placeholder page.

## 4. Dependencies, commits and ordering

111. Implement 0168 before 0281 because 0281 explicitly depends on it in PATCHLIST.
112. Implement search chips of 0281 first, then the sender + type combination inside the same row, on the filter contract of the chips.
113. Implement 0280 independently after checking existing mention adapter behavior.
114. Implement 0268 independently; preserve stock online count logic and add only the missing edge.
115. Implement 0134 independently; panel visibility must follow chat-specific permissions and preferences.
116. Implement 0235 after inspecting `MediaDataController` reaction source and custom emoji resolution.
117. Implement 0127 independently; local ordering state is per account.
118. Implement 0317 after inspecting sticker/emoji list filtering and document MIME metadata.
119. Implement 0249 independently, but test both initial fullscreen and later WebApp request paths.
120. Suggested commit 1: `feat: add regex history search` (0168).
121. Suggested commit 2: `feat: filter chat search` (0281).
122. Suggested commit 3: `feat: restrict from menus` (0328).
123. Suggested commit 4: `feat: chain user mentions` (0280).
124. Suggested commit 5: `feat: show group online members` (0268).
125. Suggested commit 6: `feat: toggle pinned bar` (0134).
126. Suggested commit 7: `feat: customize reaction strip` (0235).
127. Suggested commit 8: `feat: pin sticker sets` (0127).
128. Suggested commit 9: `feat: filter stickers by format` (0317).
129. Suggested commit 10: `feat: disable web app fullscreen` (0249).
130. Subjects are suggestions; retain imperative, lowercase commit style and <=5 words per AGENTS commit rule.
131. Keep exactly one feature per commit, never combine all search changes into one commit.
132. In 0281 the type chips and the sender filter share one filter state; the sender part may be a separate step inside the commit.
133. If 0168 integration requires reusable scanner, create it in 0168 so later rows can depend on its stable API.
134. Avoid a speculative generalized search framework.
135. `TeleConfig`, hook, strings, UI, export spec, and feature row belong in the corresponding feature commit.
136. After each feature commit export queue and update only its relevant PATCHLIST status/notes when work is actually queued.
137. Do not edit this guide as part of Android implementation unless plan genuinely changes.
138. Do not do build/test/format jobs until all batch work lands; final verification is the batch gate.
139. Existing dependencies: `ChatActivity`, `MediaDataController.searchMessagesInChat`, `DialogCell` and search adapters are stock anchors.
140. Sender filtering in 0281 must preserve the type chips and vice versa.
141. 0127’s persisted set order is in fork state (`tele_kv`), never in stock database schema.
142. 0235 should resolve custom reactions through the current account’s `MediaDataController`.
143. 0249 has two distinct entry surfaces: URL/initial properties and WebApp fullscreen request callback.
144. No dependency on network services is intended by these features.
145. Do not let a fork setting alter Telegram network requests while off.

## 5. 0168 — regex по загруженной истории

146. Desktop behavior scans loaded history, searches `originalText`, and fetches older pages as needed.
147. Android default server-search path is in `ChatActivity` and `MediaDataController.searchMessagesInChat`.
148. Decision: regex in chat and dialog-list search, but only over already loaded in-memory messages; do not scan SQLite.
149. Regex must be compiled once per query change, not once per message.
150. Catch `PatternSyntaxException`; render invalid query state without crashing or sending a malformed server query.
151. Provide a clear error state near the search input and keep typed query intact.
152. Regex mode must not send raw regex pattern to server search.
153. For chat, scan the actual loaded `MessageObject` collection and use the display/source text chosen by the desktop behavior (`originalText` equivalent).
154. `[INFERENCE]` Confirm whether caption text and service-action text are included before promising them; prefer searchable textual message content only.
155. Keep message identity as account + dialogId + topic/thread + message id.
156. Do not reuse a stale result list after dialog, account, topic, or pattern changes.
157. Result UI should reuse normal search navigation, selected result, up/down, counter, and `scrollToMessageId` paths.
158. Do not create a second message list view solely for regex results unless stock UI cannot represent a result.
159. Scanning must execute away from UI for large loaded histories; return immutable result IDs to UI thread.
160. UI updates must verify the query generation token to discard late worker results.
161. Avoid quadratic work: compile pattern once and iterate message text linearly.
162. `[INFERENCE]` Any maximum scan size/page count is a product limit not specified in decisions; propose a visible bounded cap only after maintainer agreement.
163. No silently truncated results: if bounded, display that only loaded/recent portion was searched.
164. Keep the distinction between “loaded history” and “all server history” explicit in UI copy.
165. New pages arriving while scan is active must trigger a controlled rescan/debounce, not concurrent accumulation of duplicates.
166. Deduplicate by stable message identity; same result appearing in two loaded pages appears once.
167. Preserve current filter/scope, including topic, pinned/from-user context, where stock exposes it.
168. Search list regex can inspect cached dialog preview text only; it cannot imply searching every message in each dialog.
169. `[INFERENCE]` Global list search may be only loaded/local records; confirm exact list data source before naming scope in UI.
170. Do not cause a storage query or network call when regex mode is active unless a separate explicit action requests loading more history.
171. `TeleConfig.REGEX_SEARCH` gates entry point, execution, and visual affordance.
172. Off mode must leave original stock search request and results untouched.
173. Query toggle off mid-search cancels/discards fork scan and returns to stock search semantics.
174. Use current account’s controller and account-bound UI fragment; no singleton account zero.
175. Worker must not retain `ChatActivity` or View beyond operation; pass immutable query/context and post result.
176. Search errors from pattern syntax are user input, not crash reports.
177. If a message is deleted while scanning, validate it is still present before navigating.
178. Do not mutate `MessageObject` or persist regex matches in stock storage.
179. Potential performance test: long query on large in-memory history, rapid typing, account switch, topic switch, rotation.
180. Manual test should distinguish no match, invalid regex, matching result, and ordinary literal search.

## 6. 0281 — фильтры поиска в чате

181. Add type chips to chat search, not merely duplicate global dialogs search chips.
182. Required formats include GIF and round video, in addition to standard media types.
183. Android search data path is `MediaDataController.searchMessagesInChat`; verify its current method signature before patching.
184. Map each UI filter to a supported `TL_inputMessagesFilter*` type where Telegram schema already provides one.
185. Never edit generated `TLRPC.java`; reference existing generated filter classes.
186. For any type without a distinct server filter, document the exact local post-filter or surface a maintainer question.
187. Preserve empty-text search when a type chip is selected, as required to list all messages of that type.
188. Current `ChatActivity.searchItem` may reject empty query; narrowly gate that condition for a selected type filter.
189. Do not make empty query start an unfiltered full-history search.
190. Encode query, sender, type, dialog, topic, and account in request/cache identity.
191. A change to any chip cancels or invalidates the previous request and result cursor.
192. Chip row uses Android-native horizontally scrollable controls matching existing Telegram search style.
193. Selected state and available filter state must be reset/rebound correctly when recycler rows recycle or chat changes.
194. Keep chip semantics apparent to TalkBack; selected state is not only a color change.
195. No custom animation is needed; honor `LiteMode` if animated chip transitions are introduced.
196. `[INFERENCE]` PATCHLIST asks row of chips, so do not replace with an overflow menu without maintainer approval.
197. Support combined filters only when API can represent them; do not silently pretend a combination works when server filter is singular.
198. Person + type search is part of 0281 and must be designed into filter state composition.
199. Sender chip must coexist with search type without clearing query or losing scroll position unnecessarily.
200. Preserve pagination offsets and server cursor for each filter tuple.
201. Avoid showing stale page contents while a new filter request is in flight; use standard loading/empty state.
202. Server errors should go through stock handling; no swallowing failures to show an empty list.
203. Test permissions/secret chats separately; do not assert filters unsupported by underlying API work.
204. Display no-results distinctly from no-text/no-filter idle state.
205. Filters should cover photo, video, file/document, music, voice, GIF, round video, links as supported by Android API.
206. PATCHLIST explicitly requires at least GIF and кружки; both must be directly testable.
207. Filter addition is a fork feature and remains off by default.
208. Off path must call original stock request unchanged.
209. Search state is fragment/account/dialog scoped; restoring it must not restore another account’s query.
210. Do not add a filter to ProfileActivity media tabs as a substitute for chat search.

## 7. 0281 (продолжение) — человек плюс тип

211. Прежняя отдельная строка 0306 влита в 0281 на десктопе; реализуется после chips, на их контракте.
212. Provide a sender/person selector in chat search and combine it with currently selected type.
213. Preserve selected sender ID as a peer identity, not display name (names can change or collide).
214. Sender resolution and labels use current account’s cached users/chats; avoid network resolution unless stock explicitly requires it.
215. If sender list comes from search results/history, scope it to the current dialog/thread.
216. Do not include hidden/blocked members beyond what stock permits to resolve.
217. The request must carry both sender filter and type filter when supported by Telegram search API.
218. If stock API only supports one filter plus sender argument, use that existing API shape rather than synthesizing a new TL field.
219. No `TLRPC.java` edit or handcrafted request type.
220. When sender changes, reset pagination and invalidate results from previous sender.
221. When type changes, retain sender selection and query.
222. When sender is cleared, retain type and query.
223. Test a user’s photos, messages, and GIFs with both sender and type selected.
224. `[INFERENCE]` Server filtering semantics for sender + media type should be confirmed against current method implementation and desktop patch; do not claim local-only combination is equivalent until verified.
225. Sender selection is part of the 0281 commit, no separate commit.

## 8. 0280 — последовательные упоминания

226. Existing Android mention UI is the `ChatActivity` `mentionContainer` / mentions adapter path.
227. Desktop right-click/Tab is not a suitable mobile gesture; maintainer decision is long-press on a user row.
228. On long-press, insert the selected participant and prepare the next `@` mention query.
229. Do not chain for inline bot suggestions; this is an explicit decision.
230. Respect existing mention replacement range and `replaceWithText`/entity logic.
231. Insert using the actual peer entity/user ID, not rendered `@name` plain text alone.
232. Preserve cursor placement, draft text and composing state after insertion.
233. Avoid duplicate `@` if user typed a delimiter or selection range already includes one.
234. Do not auto-chain on ordinary taps; long-press is the explicit opt-in action.
235. Long-press must not conflict with stock context menus or selection actions on other suggestion row types.
236. Ensure the row binds its long-click behavior for recycled holders and removes listeners when not a user suggestion.
237. Respect inline bot, hashtag, command, and emoji suggestion categories as stock.
238. Account/user data passed to insertion must be from active account.
239. A change in `ChatActivity` / composer runs only on main thread.
240. OFF should preserve stock mention selection behavior exactly.
241. Accessibility: provide equivalent long-press action description, not a hidden visual-only action.
242. Test first mention, second chained mention, cancel/dismiss, backspace, cursor moved, inline bot, account switch.

## 9. 0268 — онлайн участников больших групп

243. Stock already shows online counts for large groups in many cases; this row is only the remaining edge.
244. `MessagesController` and `ChatAvatarContainer` are the planned Android anchors.
245. Patch only the count path where participant list is hidden and group size is at most 200, per PATCHLIST.
246. Do not replace server-provided participant count with a guessed local count.
247. If `participants == null`, use a valid `info.online_count` only after confirming the object type and availability.
248. `[INFERENCE]` The exact nullable fields and threshold boundary must be verified in branch `tele` before implementation.
249. Preserve stock behavior for larger groups and groups with accessible participant lists.
250. Never fetch participants solely to populate a decorative online label.
251. Avoid introducing network traffic or presence updates.
252. Presence values are ephemeral; do not persist them in `tele_kv`.
253. Apply toggle in the smallest data/render path and rebuild affected UI on config change if current infrastructure supports it.
254. Offline/default path must render stock count exactly.
255. Verify hidden members, visible members, group sizes 199/200/201, user offline, user online.
256. If the server does not provide a reliable count for the edge, show stock result rather than an invented value.

## 10. 0134 — панель закрепа из меню чата

257. PATCHLIST says the toggle is default off and menu item appears when `!allowPin`.
258. Reuse the current pinned-message bar controls and per-dialog preference (`pin_<dialogId>`) if confirmed on Android branch.
259. This is not permission bypass: never show an action that lets a user pin/unpin without server rights.
260. Menu action controls visibility of the pinned bar, not server pin state.
261. Use the current chat dialog/topic identity in any per-chat preference key.
262. Do not use account-0 global preference for per-chat state.
263. The row/menu item must be gated with `TeleConfig`; OFF must leave stock menu and bar behavior unchanged.
264. Apply state on menu creation and on subsequent bar updates; do not only mutate the existing View once.
265. If the stock bar is absent because no pinned message exists, do not expose misleading show/hide action.
266. Hide/show behavior should remain stable across fragment recreation and app restart if the setting is persistent.
267. Preference namespace must not collide with stock pin state; verify whether stock already owns `pin_<dialogId>` before choosing reuse.
268. `[INFERENCE]` PATCHLIST’s note `pref pin_<dialogId>` is a candidate only; inspect actual storage ownership before writing it.
269. Respect chat permissions and forum topic context.
270. Test eligible admin, non-admin, no pinned item, pinned item visible, hidden bar, process restart, toggle off.

## 11. 0235 — собственная полоса реакций

271. Provide a local list/order setting for reactions offered in the reaction strip.
272. `ReactionsContainerLayout.setVisibleReactionsList` is the planned application point; verify exact current overload.
273. Use account-scoped local config/state and resolve reaction definitions through `MediaDataController`.
274. Custom reactions need stable IDs/document IDs, not emoji display text.
275. Missing/unavailable custom reaction IDs must not crash; omit unresolved entries and retain stored order for possible future resolution.
276. Preserve Telegram’s enabled-reaction/permission rules; do not offer reactions the chat disallows.
277. Apply ordering only to the set the server/chat currently allows.
278. Drag reorder UI should follow existing `ItemTouchHelper`/settings patterns, with persisted changes and stable IDs.
279. No network writes: this is the user’s local ordering preference.
280. Ensure changes refresh open reaction strip without rebuilding unrelated chat data.
281. Avoid repeatedly allocating/copying reaction lists on hot draw paths; compute on config/data change and reuse immutable result if current APIs allow.
282. Keep default behavior identical to stock list and ordering.
283. Test standard emoji, custom emoji reaction, disallowed reaction, missing pack, reorder, account switch.
284. If an animated preview is introduced, obey `LiteMode`; static list is sufficient.

## 12. 0127 — закреплённые sticker/emoji sets

285. Stock `EmojiView` is the relevant sticker/emoji panel; inspect current panel sections and `frozenStickerSets` / `frozenEmojiPacks` equivalents.
286. Store pinned pack IDs and order locally in account-scoped `tele_kv`.
287. Do not modify stock sticker-set ordering server-side or sync this local list to Telegram.
288. Use stable pack set IDs and distinguish sticker set from emoji pack where the source model does.
289. Pinned ordering applies only to locally available/loaded sets; missing or removed packs must not crash panel construction.
290. Avoid making a network fetch solely to render pins; use stock loader/cache lifecycle.
291. The pinned collection should integrate into the existing panel, not duplicate the whole emoji picker.
292. Apply pinned state whenever recycled set cells bind, not only on initial creation.
293. Keep drag ordering consistent with other local lists, if desktop behavior requires order.
294. `[INFERENCE]` Whether pins are a separate strip or simply promoted packs needs current desktop patch and existing Android UX inspection; preserve platform-native UI and ask maintainer if materially ambiguous.
295. Default off means stock pack order and stock picker layout remain unchanged.
296. Tests: pin/unpin, reordered pins, pack removed, cache reload, multiple accounts, restart, switch off.

## 13. 0317 — фильтр sticker/emoji по формату

297. `StickersActivity` and `EmojiView` are the planned Android surfaces.
298. Decide actual format categories from document MIME/type metadata present in the current object; do not infer format from file name alone.
299. Keep generated TLRPC structures read-only and null-check all network-derived fields.
300. Filtering is a presentation/query operation; do not rewrite sticker-set metadata or server data.
301. Use the same format classifier in the relevant picker surfaces to avoid inconsistent filtering.
302. Filter state is local to current account and picker surface; do not leak between accounts.
303. Empty filter means stock behavior.
304. Missing MIME/document metadata should classify as unknown and remain accessible through an all/unknown path.
305. Do not accidentally hide static stickers or custom emoji because their renderer differs from the file MIME.
306. Ensure selection still sends original document and attributes unchanged.
307. Filter row controls require clear selected states and accessible descriptions.
308. No extra file downloads to determine format.
309. Default off has zero effect on stock panel ordering or visibility.
310. Test static, animated TGS, video sticker, custom emoji, unknown metadata, empty pack, removed pack.
311. `[INFERENCE]` Exact format taxonomy (static/animated/video/vector/emoji) should follow the desktop patch and Android data model; do not add categories not evidenced by them.

## 14. 0249 — запрет fullscreen mini apps

312. `BotWebViewContainer` receives `web_app_request_fullscreen`; corresponding sheet/attached-sheet delegates implement the request.
313. Initial fullscreen may also be represented by URL/result properties and `BotWebViewSheet.setFullscreen`.
314. Gate both initial fullscreen and later API request; implementing only one leaves a bypass.
315. With setting on, reject request using protocol response `UNSUPPORTED` as specified by desktop behavior.
316. Strip or ignore incoming fullscreen URL state only if the current Android parser supports that exact field; do not mutate unrelated parameters.
317. Preserve normal mini-app launch, orientation, viewport, and close behavior when fullscreen is rejected.
318. Keep off path byte-for-byte/behaviorally stock wherever feasible.
319. Do not intercept other web app permission requests.
320. This is client-side UX; no external network request or tele server is introduced.
321. Menu/config item belongs in bots/interface settings and has a useful search alias.
322. Test normal embedded app, initial fullscreen URL, later request, attached sheet, toggle off, orientation and return.

## 15. Features, localization and data

323. Every user-facing patch updates `main/features.md` in English in the same export commit.
324. One feature row per feature, placed under the section that owns its switch.
325. Each row states one plain sentence, settings location, default, Android patch filename, and current desktop patch number.
326. Sender-plus-type search is described inside the 0281 row of PATCHLIST; no separate row.
327. Stock-only parts do not receive a fake feature row.
328. Current Android patch filenames are assigned by queue position at export; do not guess them in advance.
329. Desktop source number in feature rows is current number (0168 etc.), not historical number.
330. New strings go only in `strings_tele.xml`, prefix `Tele`, with positional arguments for locale safety.
331. Export/import spec includes each real preference; pin IDs/state may be included only if this spec supports the relevant data type.
332. Local operational state (such as per-account ordered pack IDs) must be evaluated separately from settings export; do not serialize private account data inadvertently.
333. No usernames, contacts, message text, query text, or account IDs leave the client for tele services.
334. No third-party network integration is part of batch 19.
335. The only network calls should be existing Telegram stock search/presence behavior, with normal account/offline controls.
336. Regex must remain local and never upload query/history.
337. Keep sensitive search results in memory only; do not add a fork history database.
338. Do not introduce persistent logs of user queries or mentions.

## 16. UX, limits and operational pitfalls

339. Search result and filter controls must not block message list scrolling or touch gestures.
340. Search chip row should remain usable on narrow phones and large text settings.
341. Respect RTL layouts and locale-specific text expansion.
342. Invalid regex must be recoverable by editing the query without dismissing the search screen.
343. Debounce rapid regex edits and cancel older scans to avoid UI stalls.
344. Do not allocate a compiled regex per item or rerun full scans synchronously on each keystroke.
345. Do not lose chat search state due to recycled holders, fragment changes or rotation.
346. Keep all list and View mutations on main thread.
347. Every callback must check fragment validity and query generation before updating UI.
348. `currentAccount` is explicit in controllers/config helpers that support account scope.
349. Thread/topic identity belongs in search context wherever stock has thread-aware requests.
350. Do not expand user-facing scope to full server history; scope is already-loaded memory unless a user explicitly requests stock load-more.
351. A cap or performance degradation must be visible; never report full-history coverage when scanning only loaded messages.
352. Online-member count must not be guessed when server data is unavailable.
353. Mini-app fullscreen rejection must not break unrelated web app actions.
354. Stickers and reaction affordances must obey chat permissions and Telegram’s allowed feature set.
355. Never call feature helper when its parent toggle is off.
356. Verify OFF at every stock call site, not only setting UI visibility.
357. Don’t add comments explaining obvious code; if a real trap requires a note, keep it short.
358. Keep stock-file hunks minimal: gated call before/after stock block; no broad formatting or renaming.
359. If required private stock API is inaccessible, expose it with the smallest visibility-only hunk rather than duplicating logic.
360. New stock members, if truly necessary, use `tele_` prefix.
361. Never remove stock imports or unrelated code as cleanup.
362. Check stock already covers behavior before implementing; 0268 is explicitly only the uncovered edge.

## 17. Open decisions / questions

363. Search 0168 is decided to include chat and chat-list, only in-memory loaded text; no open scope question.
364. Regex dialect is Java `Pattern`, not PCRE/QRegularExpression; explain Android semantics if the desktop syntax differs.
365. `[INFERENCE]` Decide whether a hard maximum scan window/page count is needed; sources specify loaded history but no numeric cap.
366. `[INFERENCE]` Confirm regex matching source includes captions, translated text, or only original text before finalizing help text.
367. 0281 uses a chip row and explicitly includes GIF and round videos, per PATCHLIST decision.
368. Person + type search (inside 0281) adds the sender filter after the chips; confirm exact server API compatibility during implementation rather than silently weakening combination semantics.
369. 0280 long-press is decided; no desktop mouse gesture analogue should be added on Android.
370. 0268 only addresses hidden participants ≤200 where stock lacks count; no request to change other group sizes.
371. 0134 is default-off; confirm precise stock pref ownership before reusing `pin_<dialogId>`.
372. 0235 order is local; unresolved custom-reaction display policy should default to omit invalid entries, not corrupt state.
373. 0127 visual location (promoted section vs separate strip) should follow inspected desktop and existing Android picker UX; seek maintainer only if actual user-visible divergence cannot be resolved.
374. 0317 format taxonomy must be evidenced by desktop patch and Android metadata; no invented category promises.
375. 0249 must reject fullscreen initial and requested paths; no further product question.
376. No calls, deletion recovery, retry, queued-send, chat-history archival, chat-details, or calendar feature is included by PATCHLIST rows.
377. If any such scope is later requested, amend PATCHLIST and create an appropriately bounded batch rather than silently expanding batch 19.
378. Any unverified API behavior must be marked `[INFERENCE]` in implementation notes until source inspection/device test settles it.

## 18. Tests with options on and off

379. Complete all batch commits and exports before running the final batch verification.
380. Build with `./gradlew :TMessagesProj_App:assembleDebug` in `Telegram` as the batch gate requires.
381. Use a secondary/test account where possible; test multi-account isolation explicitly.
382. Exercise every option in its default-off state and enabled state.
383. Confirm disabled features leave stock UI, requests, result ordering and menu entries unchanged.
384. Regex chat: valid matching regex, no match, invalid syntax, Unicode text, large loaded history.
385. Regex chat: topic/thread scope, rapid query replacement, pagination arrival, rotation, account switch.
386. Regex list: loaded preview match and no match; confirm UI does not claim all messages in all dialogs were searched.
387. Filter chips: each exposed type, including GIF and round video; empty text with selected type; no-result and loading states.
388. Combined sender/type: one sender and one type, clear sender, change type, change dialog; ensure stale results disappear.
389. Mention chaining: long-press user, insert entity, choose next user; confirm inline bot is unchanged.
390. Online member edge: hidden members around 200 threshold; ensure no fabricated online count when unavailable.
391. Pinned bar: no rights, has rights, pinned item absent/present, show/hide, persistence and OFF behavior.
392. Reactions: default order, custom reaction, disallowed reaction, reorder, missing document, different accounts.
393. Pinned sticker packs: pin/unpin, ordering, pack missing after restart, default stock order with toggle off.
394. Format filtering: static, animated, video, custom emoji, unknown MIME and no extra download.
395. Mini apps: launch normal app; initial fullscreen; request fullscreen after launch; toggle off; attached-sheet path.
396. Verify talkback labels and RTL/narrow screen behavior for chips and long-press actions.
397. Test process recreation for all persisted local settings and account-scoped states.
398. Test changes applied without restart if `TeleHooks.onConfigChanged` is the established behavior for these settings.
399. Do not claim success from compilation alone; manual interaction is required.

## 19. Logcat and diagnostics

400. Capture logcat filtered to the app package and relevant tags while exercising each case.
401. Search logs for crashes, `LOC_ERR`, `IndexOutOfBoundsException`, regex syntax exceptions escaping the UI handler, and worker-thread View access.
402. Invalid regex is expected user state and must not appear as an uncaught exception.
403. Ensure callbacks after activity destruction do not update a detached view or retain the activity.
404. Ensure changing account does not emit results belonging to the prior account.
405. Confirm no new tele-server or third-party request occurs for any feature.
406. For regex mode, confirm no raw regex string is sent as Telegram server query.
407. For type/sender search, inspect normal Telegram request behavior only; redact account/message content from shared logs.
408. Do not add user message text, regex strings, peer IDs, or usernames to persistent telemetry.
409. Record test build and device/API details in handoff, not in app logs.
410. Any observed result not tested is not a claim; mark it as unverified.

## 20. Features.md, export and batch gate

411. For each user-facing feature, add one English row to `main/features.md` in the same commit that exports the patch.
412. Feature row identifies settings page, default off, Android patch filename and desktop current patch number.
413. Do not add a row for behavior already supplied by stock and left unchanged.
414. Update PATCHLIST status only when the corresponding code is committed and patch exported: `todo` → `wip` → `queued`.
415. Once all ten rows are implemented or correctly classified as no-work, export the complete queue and verify the patch list.
416. This plan currently treats all ten rows as work items because PATCHLIST explicitly lists them; if branch inspection proves a row fully stock, report to maintainer and update plan/status rather than fabricate code.
417. Batch build gate begins only after all batch patches are committed and exported.
418. Assemble the debug APK with the documented Gradle task.
419. Hand APK to maintainer with numbered manual test steps covering each feature on and off.
420. Human verifies on device/emulator; only then mark batch `done`.
421. Compilation, static inspection, or a passing automated test does not close the batch.
422. The assistant must not claim device verification unless the human has actually exercised it.
423. No commit or Android implementation is part of this documentation task.
424. This file is the implementation guide only; authoritative statuses and row names stay in PATCHLIST.

## 21. 0328 — restrict из меню сообщения и поиск человека по числовому id

425. Desktop 0328: пункт restrict участника из меню сообщения и из меню юзерпика; пикеры участников находят человека по числовому id. Перед кодом открыть патч `tele/patches/tdesktop/0328-feat-restrict-members-from-message-menus-and-find-th.patch`.
426. PATCHLIST: строка 0328, M, зависит от android 0042 (настраиваемое меню сообщения).
427. Пункт меню сообщения — через `ChatActivity.fillMessageMenu` и `MessageMenu.kt`, код пункта в реестре меню (скрытие, порядок, группы — как у остальных пунктов).
428. Пункт показывается только там, где у текущего пользователя есть право ограничивать участников (admin с `ban_users`) и цель — не создатель и не сам пользователь; иначе пункта нет.
429. Restrict использует стоковый путь (`ChatRightsEditActivity` / banned rights), своих TL-запросов не добавлять; `TLRPC.java` не править.
430. Поиск по числовому id в пикерах участников: запрос из цифр сопоставляется с id уже загруженных участников чата; сетевое разрешение id — только если сток уже так делает.
431. Пользователь выбирается по id как peer identity, а не по имени.
432. Новый тумблер только если desktop-патч его вводит; по умолчанию выключен, при выключенном — стоковое меню и стоковый поиск без изменений.
433. Проверка на устройстве: в группе, где пользователь admin, restrict из меню сообщения и из меню юзерпика; поиск участника по id в пикере; off = сток.
