# Пачка 20 — имена, id и история версий

## 1. Назначение, источники и границы

1. Этот документ описывает только пачку 20 из `docs/PATCHLIST.md`.
2. Название пачки: «имена, id и история версий».
3. В пачку входят ровно десять строк: 0208, 0209, 0189, 0196, 0265, 0173, 0237, 0241, 0244 и 0253 (копирование peer id голыми цифрами, влить в android 0024).
4. Номера — текущая нумерация desktop queue; старые номера не подставлять.
5. Соответствие старой и текущей нумерации сверяется по `docs/desktop-numbers.md`.
6. PATCHLIST остаётся источником статусов, состава и ворот, а этот файл — рабочим планом.
7. Desktop-диффы проверены через `git show origin/main:<patch>` в checkout `/Users/tangenx/Code/tele_android/tele`.
8. Android anchors проверены через `git show tele:<path>` в checkout `/Users/tangenx/Code/tele_android/Telegram`.
9. Desktop C++/Qt-код не копировать: переносится наблюдаемое поведение через Android API.
10. Коммиты делаются в ветке `tele` checkout `Telegram`, затем экспортируются в `patches/android/`.
11. `.patch` в этом репозитории вручную не редактировать.
12. Каждая строка, требующая кода, получает отдельный Android-коммит.
13. Не создавать искусственный коммит для уже существующего поведения.
14. Итоговая оценка пачки: `S×3, M×5, L×1`, как в PATCHLIST.
15. Критерий OFF: helper, UI, фоновые задачи и сетевой запрос фичи не запускаются.
16. Новые переключатели по умолчанию выключены.
17. История версий и live previews не должны требовать сети или отправлять данные аккаунта.
18. Не менять `TLRPC.java`, stock DB schema или `LAST_DB_VERSION`.
19. Fork-состояние хранить в `tele_kv` или существующих `tele_*` таблицах.
20. UI всегда обновлять на main thread; callbacks сети/storage считать фоновыми.
21. Состояние всегда связывать с `currentAccount`; singleton account 0 запрещён.
22. В recycler-ячейке вычислять и задавать состояние при каждом bind.
23. Уважать `LiteMode` и performance class; для этой пачки анимация не обязательна.
24. [INFERENCE] Точные номера строк не фиксируются: перед каждым хуком искать символ в актуальной ветке.
25. [INFERENCE] Точный состав таблицы Unicode берётся из текущего desktop-патча 0208/0209, а не восстанавливается по памяти.
26. Вне пачки остаются desktop-окна, rich-редактор и все функции, которых нет в десяти строках (девять отдельных коммитов; 0253 вливается в `0024`).
27. 0237 не заменяет уже работающий `TeleChangelog`: он добавляет офлайн-историю всех версий.
28. 0241 не создаёт вторую модель настроек: строки должны переиспользовать `TeleSettingsActivity`.
29. 0244 не встраивает `ChatMessageCell` в settings: нужен лёгкий самостоятельный preview View.
30. Вопросы, требующие решения, явно помечены `[ВОПРОС]`, а не замаскированы предположением.

## 2. Состав и порядок

31. 0208 — имена пользователей и чатов, состоящие только из невидимых символов.
32. 0209 — видимые именованные плашки для скрытых символов.
33. 0189 — DC чата по самому первому фото, с асинхронным результатом и `uncertain`.
34. 0196 — DC медиа в `PhotoViewer` и `StoryViewer`, используя общий DC helper.
35. 0265 — дата загрузки медиа в viewer, рядом с DC при его включении.
36. 0173 — стиль имени автора в цитате удалённого сообщения.
37. 0237 — офлайн-история изменений всех Android-релизов в APK.
38. 0241 — страница «new in tele» с версиями, поиском и живыми тумблерами.
39. 0244 — живые previews имени, скрытых символов, ghost и peer id; последняя строка.
40. Рекомендуемый порядок: 0208 → 0209 → 0189 → 0196 → 0265.
41. После ID-зависимостей выполнить 0173, не смешивая его с визуальными именами.
42. Затем 0237, затем 0241, затем 0244.
43. 0208 должен закончить общий invisible-name helper для 0209 и 0244.
44. 0189 должен расширить `PeerId`, а 0196 и 0265 используют его публичные media helpers.
45. 0237 должен подготовить модель версий до добавления live controls в 0241.
46. 0244 должен быть последним из-за сложности кастомных View и зависимости от ghost.
47. Никакой параллельной записи в общие горячие Java-файлы без согласованного порядка.
48. После всех девяти коммитов — один batch gate, не отдельная «проверочная» сборка посреди пачки.

## 3. TeleConfig, настройки и поиск

49. Каждый фактический switch объявить отдельным item в `tele/TeleConfig.kt`.
50. Boolean keys используют snake_case и default `false`.
51. 0208 master: `INVISIBLE_NAMES = BoolItem("invisible_names", false)`.
52. 0208 fallback — строковый выбор `phrase`/`id`, дочерний к master и не показываемый при OFF.
53. 0208 phrase — локальная строка, ограниченная лимитом desktop; точный лимит сверить с патчем.
54. 0209: `SHOW_HIDDEN_CHARS = BoolItem("show_hidden_chars", false)`.
55. 0189: `SHOW_FIRST_PHOTO_DC = BoolItem("show_first_photo_dc", false)`.
56. 0196: переиспользовать существующий `SHOW_DC`, если его смысл подтверждён на текущей ветке; не создавать дубль.
57. `SHOW_DC` уже default-off в Android `TeleConfig`; включение media DC должно быть таким же gated behavior.
58. 0265: `MEDIA_UPLOAD_DATE = BoolItem("media_upload_date", false)`.
59. 0173: master `DELETED_REPLY_AUTHOR = BoolItem("deleted_reply_author", false)`.
60. 0173 style — дочерний `DELETED_REPLY_AUTHOR_STYLE`, default `bold` только в выключенной группе.
61. [INFERENCE] Если maintainer предпочитает один существующий `DELETED_REPLY` value, мигрировать без второго master и сохранить OFF=stock.
62. 0237 не нужен toggle: история доступна офлайн всегда после установки версии с asset.
63. 0241 не нужен toggle: `MODE_NEW` всегда открывается из существующей settings page.
64. 0244 не нужен toggle: previews появляются в settings только у соответствующих групп.
65. Все новые items вне 0237/0241/0244 включить в export/import spec.
66. Fallback и phrase экспортируются только вместе с `INVISIBLE_NAMES` либо как обычные значения с безопасным пропуском.
67. `SHOW_FIRST_PHOTO_DC`, `MEDIA_UPLOAD_DATE`, `DELETED_REPLY_AUTHOR` экспортируются явно.
68. Не экспортировать search aliases, заголовки групп, версии или сгенерированный JSON.
69. Строки добавлять только в `strings_tele.xml`, с ключами `Tele...`.
70. Описания должны назвать область действия, локальность, лимиты и OFF=stock.
71. Для 0189 показывать «uncertain», когда история фото неполная или DC различаются.
72. Для 0208 не обещать замену названия там, где chat object ещё не загружен.
73. Для 0209 не обещать отображение каждого Unicode-кодпоинта вне таблицы.
74. Для 0237 явно сказать «в APK, доступно без сети».
75. Для 0244 явно сказать «пример, не реальные сообщения и не сетевой preview».
76. Страницу 0208/0209/0189/0196/0265/0173 поместить в существующую `MODE_IDS`/`MODE_DATA` по текущей структуре.
77. [ВОПРОС] Если после 0169 структура settings изменит modes, выбрать фактическую группу, но не добавлять новый корневой экран.
78. Зарезервировать постоянный диапазон Search IDs 1280..1299.
79. 1280 — invisible names master.
80. 1281 — fallback phrase or id.
81. 1282 — custom fallback phrase.
82. 1283 — show hidden characters.
83. 1284 — first photo DC.
84. 1285 — media viewer DC.
85. 1286 — media upload date.
86. 1287 — deleted reply author name.
87. 1288 — deleted reply author link.
88. 1289 — deleted reply author mention.
89. 1290 — all tele version history.
90. 1291 — offline changelog in APK.
91. 1292 — new in tele by version.
92. 1293 — live settings toggles.
93. 1294 — settings preview.
94. 1295 — hidden character names.
95. 1296 — invisible username fallback.
96. 1297 — uncertain data center.
97. 1298 — uploaded media timestamp.
98. 1299 — deleted message quote author.
99. IDs 1280, 1283, 1284, 1285, 1286 and 1287 point at real setting rows.
100. IDs 1288, 1289, 1299 point at child choice rows or the existing deleted-reply group.
101. IDs 1290..1294 point at history/new/preview rows or their groups.
102. IDs 1291, 1295, 1296, 1297, 1298 are search aliases where no independent setting exists.
103. [INFERENCE] Final title wording is localized later; numeric IDs must not change after release.
104. Add Russian and English terms: «невидимое имя», «скрытые символы», «username», «имя», «DC», «дата загрузки», «удалённый ответ», «история», «версия», «new», «preview».
105. Register IDs once in `TeleSearch`, with the correct settings mode/deeplink.
106. Search must not expose child controls as active when their parent is OFF.
107. Search result click must open the existing mode, not a placeholder.
108. Reusing `SHOW_DC` requires one row, one export value and one search target, not two controls.

## 4. Общий invisible-name helper (0208 и 0209)

109. Создать новый `tele/helpers/InvisibleNames.kt`.
110. Helper принимает `account` явно, даже если сейчас часть данных доступна через current account.
111. Внутри хранить только вычисленные display values и не сохранять Telegram names.
112. Не писать заменённые имена в `tele_kv`, stock DB или cloud drafts.
113. Детектор должен различать пустую строку и строку, состоящую только из таблицы невидимых символов.
114. Проверять Unicode code points, а не только UTF-16 code units.
115. Не считать обычный пробел достаточным доказательством невидимого имени без подтверждения desktop-таблицей.
116. Использовать точную таблицу `NamedChar` из `git show origin/main` патчей 0208/0209.
117. В таблице desktop подтверждены как минимум `U+0009`, `U+000A`, `U+000B`, `U+000C`, `U+000D`, `U+0020`, `U+0085`.
118. В таблице также учитывать zero-width characters, если они присутствуют в исходном патче.
119. [INFERENCE] Не расширять таблицу всеми Unicode `Cf` без решения: это может неверно переименовать легитимные имена.
120. Публичные функции должны возвращать исходную строку при OFF или неизвестном code point.
121. `fallback(user)` сначала использует username, затем выбранную фразу или Bot API id.
122. Username форматировать как `@username`, без сетевого resolve.
123. Для чата fallback username применять только если chat реально имеет username.
124. Для user без username не выдумывать `@` и не обращаться к tele-server.
125. Fallback id — локальный peer id в согласованном display формате, не копируемая строка DC.
126. Длина пользовательской phrase ограничивается desktop-лимитом; длинный ввод отклонять, не обрезать молча.
127. Phrase очищать от line breaks, если это подтверждено desktop; иначе сохранить вопрос.
128. Все публичные методы должны быть pure по отношению к `TLRPC.User` и `TLRPC.Chat`.
129. Вызовы из Java должны быть маленькими `tele_`-hooks, без переформатирования stock-кода.
130. Применение к users — на слое `UserObject.getUserName/getFirstName`, совместно с `LocalNames`.
131. Порядок names: LocalNames, затем invisible fallback, затем stock name; точный порядок сверить с существующим helper.
132. Не позволять invisible fallback перетирать явно заданное локальное имя.
133. Применение к chat — через gated call из `MessagesController.putChat`.
134. `putChat` должен обновлять in-memory display cache, keyed by `(account, chatId)`.
135. Stock persistence должен получить оригинальный `chat.title`, а не заменённый fallback.
136. Если exact save order не позволяет разделить object и display cache, добавить только публичный hook, не мутировать `TLRPC.Chat`.
137. [INFERENCE] Точное место до/после stock DB save в `putChat` требует повторного чтения функции перед кодом.
138. Invalidate cache when real chat title, username or config changes.
139. On `INVISIBLE_NAMES` change post `NotificationCenter.updateInterfaces` for each affected account.
140. On `INVISIBLE_NAMES` change refresh dialogs, avatar header and visible message cells.
141. Do not broadcast only to `UserConfig.selectedAccount`.
142. `DialogCell` must apply display title in `onBind`/layout rebuild, not only constructor.
143. `ChatAvatarContainer` must use helper for chat header title and subtitle.
144. `ChatMessageCell` sender name must use helper without changing message owner.
145. `ProfileActivity` must use helper for profile display while retaining real username links.
146. `ContactsController.formatName` hook is acceptable only if it preserves LocalNames and account context.
147. [INFERENCE] If a central user getter cannot safely carry account, use minimal call sites rather than global process state.
148. Never substitute fallback in text sent to Telegram, entities, mentions or search queries.
149. Never replace a real username with a local fallback when resolving links.
150. Never send fallback names to tele-server, crash reports or analytics.

## 5. 0208 — @username вместо невидимых имён

151. Desktop 0208 changes user/chat display names, chat list title, top bar and bubble sender names.
152. Android target is users plus chats, per maintainer decision.
153. Android dependency is Android 0028 LocalNames.
154. Add `INVISIBLE_NAMES` and child fallback controls before touching UI cells.
155. Add a short `TeleInvisibleName` display helper in the new file.
156. Hook `UserObject` at the narrowest getter already used by Android.
157. If getter lacks account, pass account through the existing caller hook rather than global state.
158. Hook `MessagesController.putChat` for chat title cache only.
159. The hook must be invoked for cache and network loads, because both call `putChat`.
160. It must not alter server responses, `TLRPC.Chat`, or DB serialization.
161. On a chat title update, replace only the in-memory display value.
162. A later `putChat` with a visible title must remove the cached fallback.
163. A later username update must recompute `@username` immediately.
164. A deleted username must fall back to phrase/id without a stale @ value.
165. `DialogCell` title and preview sender names must bind the current account value.
166. `ChatAvatarContainer` title must be invalidated after config or chat update.
167. `ChatMessageCell` sender names must work for messages loaded before toggle activation.
168. `ProfileActivity` should show the same fallback and preserve profile controls.
169. A LocalNames value wins over invisible detection because it is an explicit local choice.
170. [INFERENCE] The stock getter call graph may have account-less paths; audit each before broadening a hook.
171. Recycler recycling test: bind invisible user, visible user, invisible user again and check no stale text.
172. Multi-account test: same peer id in accounts A/B must not share display cache.
173. Rotation test: recreate profile/list and verify only display cache is rebuilt.
174. Cold start test: no fallback phrase is persisted as Telegram chat title.
175. OFF test: all cells and profiles render exactly stock names and no helper log appears.
176. Privacy test: inspect HTTP/logcat and ensure no new tele-server request.
177. Do not add a username resolve request for a missing username.
178. If no username and phrase is empty, show configured id only when fallback=id.
179. If both phrase and id are unavailable, preserve stock invisible text rather than inventing copy.
180. [ВОПРОС] Should fallback phrase be a visible independent row or a child under the master; default is child.
181. [ВОПРОС] Confirm whether chat display cache may be rebuilt from stock DB on every account start; no DB write is allowed.

## 6. 0209 — показ скрытых символов

182. 0209 shares the exact codepoint/name table with 0208.
183. Create `HiddenCharSpan` or an equivalent `ReplacementSpan` in `InvisibleNames.kt`.
184. Spans are presentation-only and never modify `messageOwner.message`.
185. A string is replaced only when its visible text is empty and the gate is ON.
186. For mixed visible and invisible text, preserve stock text unless desktop patch explicitly marks each character.
187. Profile bio/about and intro are the first target in `ProfileActivity`.
188. Message body and media caption are targets through `MessageObject` presentation.
189. Service-message text must not be changed unless exact desktop coverage is confirmed.
190. Use `SpannableStringBuilder` with named labels such as `ZERO WIDTH SPACE` from the shared table.
191. Preserve selection, copy and link spans where possible; do not create fake clickable entities.
192. Clicking a hidden-character chip may show a small explanation dialog, not a network action.
193. Accessibility text should include the Unicode name and `U+XXXX` code point.
194. [INFERENCE] Exact span drawing metrics should follow Telegram text spans, not desktop opacity constants.
195. Use a muted color that remains readable in light and dark themes.
196. Do not show raw invisible glyphs as the only indication; the label is the feature.
197. Keep labels short enough for bubbles and profile rows.
198. [INFERENCE] Define a per-field display limit after measuring Android layout; do not silently truncate without an indicator.
199. If a message contains only zero-width characters, show one chip per code point up to the agreed limit.
200. If the limit is exceeded, show a final `…` chip and expose the count only after maintainer approval.
201. Do not alter message search text, server entities or draft contents.
202. Apply spans on UI thread after background message data has arrived.
203. Cache no spans in stock objects if toggling can invalidate them; rebuild presentation instead.
204. On `SHOW_HIDDEN_CHARS` change, invalidate visible `ChatMessageCell` and profile rows.
205. Recycler test: hidden-only, visible text, mixed text and empty value in one recycled holder.
206. Theme test: light, dark, large font and RTL locale.
207. OFF test: no replacement spans and normal copy behavior.
208. Privacy test: hidden content remains local and does not leave the device.
209. [ВОПРОС] Confirm whether `ProfileActivity` should mark hidden phone/username fields or only bio/name/intro.
210. [ВОПРОС] Confirm whether tapping the chip copies the code point or only opens explanation; default is explanation only.

## 7. 0189 — DC чата по первому фото

211. Desktop 0189 scans chat photo history, takes the oldest available photo DC and marks uncertainty.
212. Android `PeerId.dc()` currently reads the current profile photo (`dc_id`, then small/big locations).
213. Add a separate async helper, not a blocking call inside `ProfileActivity` rendering.
214. Candidate anchor: `MessagesController.getDialogPhotos(dialogId)` and its `load`/merged history path.
215. Load at most the desktop-equivalent bounded photo history; exact limit is 500 in the desktop patch.
216. [INFERENCE] Confirm Android pagination API and whether 500 photos are feasible before choosing requests.
217. For each photo, read the photo location DC, preferring the same fields as `PeerId.photoDc`.
218. Select the oldest photo encountered, not the current avatar, for the display DC.
219. Track all DCs, completeness and whether the first photo was actually loaded.
220. If no photo or no DC exists, render no DC or `uncertain` only according to desktop semantics.
221. If current and first-photo DC differ, keep first-photo DC and mark `uncertain`.
222. If multiple historical DCs exist, mark `uncertain`.
223. If pagination is incomplete, mark `uncertain`.
224. Keep current `PeerId.dc()` behavior for users and self account unless row explicitly asks chat history.
225. Add a callback/result data class keyed by `(account, peerId, generation)`.
226. Start loading only when `SHOW_FIRST_PHOTO_DC` or required DC row is visible and ON.
227. Cancel or ignore late results when account, profile or peer changes.
228. Network requests must use Telegram APIs only and must not use tele-server.
229. Storage callbacks are background; post `runOnUIThread` before changing a profile row.
230. Cache result in memory per account/peer with invalidation on new/deleted chat photo.
231. Do not persist photo history or DC cache in stock DB.
232. [INFERENCE] A bounded `tele_kv` cache is optional; default is memory-only until restart semantics are decided.
233. Profile row initially says loading/uncertain only if UI copy is approved; do not block the profile.
234. Keep asynchronous refresh from jumping the row or losing scroll position.
235. Copy action copies numeric DC only, consistent with existing profile row behavior.
236. `PeerId.rowText` should append `uncertain` without changing the bare ID copy path.
237. Test no photo, one photo, multiple same DC, multiple DC and incomplete pagination.
238. Test chat vs user and account switch while request is in flight.
239. OFF test: no `getDialogPhotos` request is started and current profile output is unchanged.
240. Logcat should show one tagged request/result pair, never a per-scroll request storm.
241. [ВОПРОС] Confirm whether showing `uncertain` belongs in the row or only in a tooltip; desktop uses row text.

## 8. 0196 — DC медиа в просмотрщике

242. Desktop 0196 adds media DC to media viewer and stories, controlled by SHOW_DC.
243. Reuse the common `PeerId` media DC helper where possible.
244. For photos, read the relevant `PhotoSize`/`FileLocation.dc_id`.
245. For documents/video, read the document location DC used by the viewer.
246. For stories, use the story photo/document object available in `StoryViewer`.
247. Candidate anchors are `PhotoViewer` title/date control updates and `StoryViewer` header data updates.
248. Add a small `TeleHooks.mediaDc(...)` call rather than duplicating formatting in both viewers.
249. Gate at the final text assembly and at any async data load.
250. OFF must not compute DC, append labels or change viewer layout.
251. Keep existing `SHOW_DC` settings row and default-off behavior.
252. If media has no DC, omit the suffix; do not show DC 0.
253. If a media DC differs from peer DC, display the media value, not the profile value.
254. Separator should match PATCHLIST: use ` · ` with the date/upload suffix where both exist.
255. Rebind/recompute when the viewer switches album item; do not retain previous media label.
256. Story viewer may use a different header lifecycle; cover open and next/previous transitions.
257. `PhotoViewer` and `StoryViewer` UI mutations run on main thread.
258. Media metadata arriving from loader is nullable; check every location before dereferencing.
259. No new network request solely for a DC label; use metadata already loaded by viewer.
260. Do not change download routing or file references.
261. Honor `LiteMode`: no animated label transition is needed.
262. Test photo, document, video, story photo, missing location and album navigation.
263. Test `SHOW_DC` OFF and ON without activity restart if `onConfigChanged` supports it.
264. Recycled/retained viewer test: open media A, B, A and verify exact labels.
265. [INFERENCE] Confirm the exact Android document location field at implementation time; never edit generated TL classes.

## 9. 0265 — дата загрузки медиа

266. Desktop 0265 appends `uploaded <date>` when media upload date differs from message date by at least five minutes.
267. Add `MEDIA_UPLOAD_DATE` default-off in the IDs/settings group.
268. Candidate anchor is `PhotoViewer` date/subtitle assembly, adjacent to 0196.
269. For photos use photo date; for documents use document date, if available.
270. Compare media date and message date in seconds; use absolute difference.
271. [INFERENCE] Verify Android field units and whether `document.date` is upload date in this branch.
272. Suppress the suffix when either date is zero or the difference is below five minutes.
273. Use locale-aware Android date/time formatting, not a hard-coded English timestamp.
274. Keep the label semantically equivalent to «uploaded» in strings, with localizable arguments.
275. If 0196 is ON, compose `DC … · uploaded …` in deterministic order.
276. If 0196 is OFF, upload date still works independently when its own toggle is ON.
277. If media date is unavailable, leave the stock viewer subtitle unchanged.
278. Do not show upload dates in chat bubbles or the chat list; PATCHLIST says viewer.
279. Do not persist computed dates.
280. On viewer item changes, clear old date text before setting new text.
281. On toggle change, refresh current viewer if an explicit hook exists; otherwise apply on next open.
282. OFF test: no date formatting work and no changed subtitle.
283. ON test: equal dates, under-five-minute difference, over-five-minute difference and absent date.
284. Test timezone/locale and 12/24-hour settings.
285. [ВОПРОС] Confirm whether «five minutes» is a strict `< 300` or `<= 300` boundary; desktop uses a skip threshold.

## 10. 0173 — подпись имени в цитате удалённого

286. Desktop 0173 chooses bold, link or mention for the quoted author of a deleted message.
287. Android dependency is existing deleted-reply behavior from Android 0063.
288. Candidate implementation anchor is `tele/helpers/DeletedReply.kt`, especially `composeQuote`.
289. Add only the style/entity choice; do not rewrite deleted-message storage.
290. Master `DELETED_REPLY_AUTHOR` default-off preserves current quote output.
291. Child style choices: bold, link and mention; hidden until master is ON.
292. For link, use the real username and a `t.me` URL only when username exists.
293. For mention, use a supported `MentionName` entity with current account/user id.
294. For users without username, link mode falls back to bold or plain according to explicit choice.
295. Never create a mention for a chat/channel without a valid user entity.
296. Keep quote text and entity offsets valid after truncation.
297. Keep the deleted-reply privacy rule: kept deleted messages cannot be replied to or forwarded as live server messages.
298. Build quote entities before sending, not by mutating archived bytes.
299. Account and author IDs must be explicit; no account-0 lookup.
300. UI choice is local and belongs in `MODE_DATA`/deleted reply settings.
301. Recycled rows are irrelevant to the persisted quote, but preview of the selected style must bind correctly.
302. Test deleted user with username, without username, deleted author and chat author.
303. Test each style with short and truncated quote text.
304. OFF test: exact Android 0063 output and no additional entity.
305. [ВОПРОС] Decide whether author style should be a separate master or a child of existing `DELETED_REPLY=quote`; default plan uses separate OFF master for safe rollout.

## 11. 0237 — история всех версий в APK

306. Desktop 0237 adds a large `changelog_history.json` asset and a versioned/searchable changelog page.
307. Maintainer decision: Android history is bundled in APK and generated by CI.
308. The asset must be `res/raw/changelog_history.json` in the applied Telegram checkout.
309. Add a new `TeleChangelogHistory.kt` parser or extend `TeleChangelog.kt` without duplicating request code.
310. Parser accepts the generated Android schema and validates version/tag/item bounds.
311. Keep release identity: tag, title, URL, Android patch number, text, where, category and options when available.
312. Do not claim desktop patch numbers as Android patch numbers; preserve both fields if source provides both.
313. Prefer Android `patches/android`/release changelog data for user-facing history.
314. Public desktop data may be included only where the generated source explicitly maps it.
315. No account data, usernames, contacts, message text or access tokens in the asset.
316. Opening history reads raw resource only and must work with airplane mode.
317. If the asset is absent in a developer build, show a clear missing-data state and keep current changelog.
318. Do not silently fall back to a network request for the full history.
319. Current-release `TeleChangelog` may continue its existing release download for local chat notes.
320. History parser work should run on a `DispatchQueue`, then post immutable model to UI.
321. Use generation tokens when changing version/query so late parses cannot replace a newer selection.
322. Version tabs/list are main-thread UI and must not parse JSON in `onCreateView`.
323. Bound item/category/version counts to safe values matching existing changelog limits.
324. Preserve long-text limits and avoid allocating a second giant copy per row.
325. [INFERENCE] Exact history schema must be finalized from the Android release asset; do not copy desktop-only fields blindly.
326. [INFERENCE] If old Android releases lack structured options, show text/where only and label missing fields honestly.
327. Search must be local over parsed versions and entries, with no network side effect.
328. Search result navigation should select the version and scroll to the matching row.
329. Accessibility must expose version title and entry text, not only colored tabs.
330. A missing or malformed asset must log one concise error and show an explanatory empty state.
331. Do not log the full asset or user input.
332. Add an asset checksum or deterministic ordering only if the CI generator needs reproducibility; do not add runtime trust assumptions.
333. History test: old version, current version, missing asset, malformed JSON and empty search.
334. OFF is not applicable: this is a bundled always-available page, not a network feature.

### CI генерация asset

335. Add a deterministic generator under `ci/`, for example `ci/changelog_history.py`.
336. The generator reads public release changelog assets/tags and the Android queue metadata.
337. It must be runnable from repository root in CI without Android SDK.
338. Fetch release list in stable order, oldest-to-newest or newest-to-oldest consistently.
339. Download only public `tele-changelog.json` assets; reject unexpected hosts/paths.
340. Validate JSON before merging; skip a missing historical asset with a recorded warning.
341. Normalize tag, title, URL, categories and items to the Android schema.
342. Include Android patch number/file and desktop current number only when explicitly known.
343. Escape text as JSON with UTF-8 and deterministic separators/order.
344. Enforce bounded item/category lengths before writing the resource.
345. Write `Telegram/TMessagesProj/src/main/res/raw/changelog_history.json` after Telegram checkout and patch application.
346. Create `res/raw` if the applied checkout does not already contain it.
347. Run the generator before `assembleAfatRelease`; the generated file must be inside the APK.
348. Do not commit generated CI output to this docs-only change.
349. Add a CI assertion that the raw file exists and is valid JSON before Gradle.
350. Add a CI assertion that the APK contains `res/raw/changelog_history.json` or equivalent packaged resource.
351. The current workflow already checks `ci/changelog.json` before the long build; keep that validation.
352. Add history generation after tag selection, so the current release tag can be represented.
353. Do not require release signing secrets to generate/test the JSON locally.
354. On a push build, a temporary generated asset is fine; on publish, the same generator must run.
355. On failure to fetch one old release, decide whether warning or hard failure; default is hard failure for malformed current data, warning for missing old release.
356. [ВОПРОС] Confirm whether GitHub API pagination or a checked public manifest is the source of release history.
357. [ВОПРОС] Confirm retention policy for releases removed from GitHub; bundled history cannot reconstruct deleted assets.
358. Add a small CI fixture test for duplicate tags, invalid item lengths and missing categories.
359. Keep generator network use limited to public GitHub release metadata; no Telegram account requests.
360. Document the generator command in the implementation commit or CI comments, not in this docs-only file only.

## 12. 0241 — what's new с живыми тумблерами

361. 0241 depends on 0237, Android 0078 and the 0169 settings structure.
362. Existing Android anchors are `TeleSettingsActivity(MODE_NEW)` and `TeleNewSettings`.
363. Replace the flat «new setting ids» presentation only after the history model exists.
364. Group rows by release/version from the local history asset.
365. For each entry with a known setting id, reuse the same row builder as the normal settings page.
366. A live toggle writes through `TeleConfig.set` and calls `TeleHooks.onConfigChanged`.
367. A live value selector uses the same dialog as the canonical settings page.
368. Never create a second preference key for the new page.
369. If an entry has no Android setting id, render explanatory text and its release link only.
370. Do not render desktop-only settings as clickable Android toggles.
371. Version tab selection and query are UI state, not TeleConfig.
372. `TeleNewSettings.KNOWN_SETTINGS` remains the seen/new marker and stays per device.
373. Mark seen on `onResume` as existing `MODE_NEW` behavior, not on background parse completion.
374. Search uses local history and settings metadata; it must not request GitHub.
375. Search result should open the canonical settings mode and preserve the selected version when returning.
376. Toggle rows must bind checked/value state on every recycler bind.
377. A parent OFF hides child rows exactly as canonical settings do.
378. A parent ON immediately reveals child rows and updates the current list.
379. On config change, refresh the visible new-page adapter without recreating the activity unnecessarily.
380. Main-thread guard applies to every row mutation and dialog callback.
381. Account-independent settings remain global; never key them to selected account accidentally.
382. Do not show account-specific data in history entries.
383. `MODE_NEW` should remain reachable from current root/new links and TeleChangelog buttons.
384. [INFERENCE] If a version entry points to a setting removed from current build, render disabled historical text instead of a dead link.
385. Test live toggle from new page, navigate to canonical page, toggle back, rotate and return.
386. Test old release with unknown option, empty search and mixed version categories.
387. OFF test for every represented feature still means stock behavior; the new-page shell itself is always available.

## 13. 0244 — живые previews в настройках

388. 0244 is the only L row and is last in the batch.
389. Dependencies are 0208, 0209, ghost settings, Android 0024 peer IDs and 0169 settings structure.
390. Do not reuse real `ChatMessageCell`, `ProfileActivity` or `PhotoViewer` inside settings.
391. Add a new `TYPE_PREVIEW` row/view to `TeleSettingsActivity` and its adapter.
392. Preview view draws simple Android-native Canvas/TextView mock surfaces.
393. Preview must accept a snapshot of relevant current config values, not a live Activity reference.
394. Rebuild snapshot on every config change and invalidate on main thread.
395. Invisible-name preview shows a user/chat with an invisible source and the resulting `@username`/phrase.
396. Hidden-char preview shows named chips for representative table entries.
397. Ghost preview shows online, typing, read and stories states with hidden markers.
398. Peer-id preview shows formatted id, optional DC and the uncertain state.
399. [INFERENCE] Exact preview copy and dimensions are UX choices; preserve desktop concepts, not desktop pixels.
400. Preview must work without an account, network, loaded chat or real message.
401. Do not put real usernames, ids, profile photos or message text into the preview.
402. Do not send preview events to Telegram or tele-server.
403. Use theme colors from the current `Theme.ResourcesProvider`.
404. Support light/dark themes, font scale and RTL layout.
405. Keep preview height bounded so settings scrolling remains predictable.
406. Avoid expensive blur, particle effects and image decoding; LiteMode must not be bypassed.
407. If animation is later added, use `LiteMode` and a static fallback.
408. Preview clicks must not mutate settings unless the enclosing setting row explicitly does so.
409. Recycler bind must remove old preview listeners and set the new snapshot.
410. Parent-gated preview rows hide with their group, preventing stale child previews.
411. Refresh after each relevant toggle without losing scroll position.
412. Test multiple previews on one page and repeated bind/recycle.
413. Test rotation, process recreation, font scale, RTL and dark theme.
414. Test with no Telegram account loaded and with all ghost options OFF.
415. OFF for each underlying feature means preview reflects stock state, not that the preview page disappears.
416. [ВОПРОС] Decide whether previews are shown by default in settings or behind an optional «show examples» row; PATCHLIST implies shown.
417. [ВОПРОС] Decide whether 0244 includes a preview for media upload date; PATCHLIST names ghost, invisible names and ids, so default excludes it.

## 14. Общие threading/account/recycling правила

418. `TeleConfig` loads once in `TeleHooks.init`; settings writes happen on UI callbacks.
419. `TeleHooks.onConfigChanged` is the central refresh bus for every live setting.
420. Background `MessagesController`, `MessagesStorage` and network callbacks must never touch Views.
421. Post immutable results with `AndroidUtilities.runOnUIThread` and check fragment/account generation.
422. Every worker captures `account` and immutable peer/media ids, never an Activity or View.
423. On account switch, cancel or discard pending 0189 result and rebuild visible rows.
424. On profile/chat switch, discard stale peer and topic-independent labels.
425. `DialogCell`, `ChatMessageCell` and settings rows must fully reset state during bind.
426. Never rely on view-holder creation for visibility, spans, labels or checked state.
427. Cache only public metadata and only when invalidation is specified.
428. No new background executor is needed for simple text spans or Canvas previews.
429. History parsing may use existing `DispatchQueue`; avoid one thread per version.
430. All UI strings go through resources where localization matters.
431. All network paths added by this batch are Telegram metadata only, gated by a user switch where applicable.
432. There is no tele-server call for names, IDs, DC, dates or previews.
433. Logcat tags must avoid names, ids, message text and raw hidden characters.
434. Log only state transitions, counts and error classes, never sensitive payloads.
435. `LiteMode` controls any future preview animation; static rendering is the acceptance path.

## 15. Коммиты, effort и export

436. Commit 1: `feat: show usernames for invisible names` — 0208, M.
437. Commit 2: `feat: show hidden characters` — 0209, M.
438. Commit 3: `feat: show first photo dc` — 0189, M.
439. Commit 4: `feat: show media dc` — 0196, S.
440. Commit 5: `feat: show media upload date` — 0265, S.
441. Commit 6: `feat: style deleted reply names` — 0173, S.
442. Commit 7: `feat: bundle changelog history` — 0237, M.
443. Commit 8: `feat: add live new settings` — 0241, M.
444. Commit 9: `feat: add settings previews` — 0244, L.
445. Subjects are suggestions; keep lowercase imperative and no more than five words.
446. Each commit includes its TeleConfig item, settings row, strings, search registration, export spec and `features.md` row when user-facing.
447. 0208/0209 may share `InvisibleNames.kt`, but 0209 remains a separate commit.
448. 0189/0196/0265 may share public formatting helpers only when the preceding commit provides them.
449. 0237 must not include 0241 UI or 0244 preview code.
450. 0241 must not duplicate canonical settings row definitions.
451. 0244 must not silently add unrelated settings previews.
452. After each commit, export with `git format-patch <UPSTREAM> -o ../main/patches/android/ --zero-commit --no-signature --no-numbered`.
453. Update only the corresponding PATCHLIST status once the commit is actually queued/exported.
454. Add one English `features.md` row per user-visible feature, with where/default/android patch/current desktop number.
455. For 0237, the features row says history is offline in the APK and links desktop 0237.
456. For 0241, the row says new-in-tele entries contain live controls and links desktop 0241.
457. For 0244, the row says settings previews are illustrative and links desktop 0244.
458. 0253 peer-id copying is not a new switch or a new features row if the existing feature row can describe the fix.
459. Do not edit feature rows before the corresponding Android patch exists, except in the same queue/export commit.
460. At batch end, the nine patches are all committed in Telegram and exported here.

## 16. UX, limits and privacy acceptance

461. Invisible fallback is display-only and never changes server-visible profile data.
462. Hidden-character labels are explanatory, not replacement message content.
463. Bare peer-id copy is digits only, independent of formatted display spaces and DC suffix.
464. For 0253, `PeerId.copyText(account, userId, chatId)` returns `botApiAdjusted(...).toString()`.
465. It must be used by the existing profile ID copy action, not by changing `rowText` display.
466. User id remains user id; channel/supergroup follows existing Bot API `-100…` setting.
467. [INFERENCE] Verify the exact `ProfileActivity` copy anchor and preserve menu label before editing.
468. DC labels never imply creation DC unless 0189 has completed its first-photo computation.
469. `uncertain` is required when first-photo history is incomplete or contradictory.
470. Upload date is hidden when equal/near message date and shown only in viewer.
471. History is offline, read-only and bundled; it does not auto-update without a new APK.
472. Live new-page toggles have exactly the same persistence and defaults as canonical settings.
473. Previews are synthetic examples and never expose account-specific values.
474. No feature in this batch changes Telegram network payloads when OFF.
475. No feature in this batch uploads names, IDs, chat titles, hidden code points or media metadata.
476. Limits must prevent unbounded JSON, span count, history rows, photo paging and preview height.
477. [INFERENCE] Agree exact UI truncation/count copy with maintainer before freezing strings.
478. Accessibility labels must distinguish visible fallback from the real Telegram name.
479. Clipboard values must not include DC, grouping spaces or explanatory suffixes for peer IDs.
480. All copy actions use the existing `AndroidUtilities.addToClipboard` path.

## 17. Manual tests: OFF, ON and logcat

481. Install the batch APK with a secondary account and preserve a stock comparison build.
482. Start with every new Boolean OFF and verify no changed rows, labels, requests or logs.
483. 0208 OFF: invisible user, invisible chat and normal user/chat all match stock.
484. 0208 ON: user with username becomes `@username` in list, header, profile and bubble.
485. 0208 ON: user without username uses phrase, then id fallback as selected.
486. 0208 ON: chat title uses username/fallback in list/header/profile without DB mutation.
487. 0208 ON: toggle off, cold restart and inspect original title from Telegram data.
488. 0208 recycling: scroll mixed rows repeatedly and check no stale fallback.
489. 0208 accounts: same numeric id in two accounts stays isolated.
490. 0209 OFF: hidden-only bio/message/caption remains stock.
491. 0209 ON: verify each representative named code point and accessibility text.
492. 0209 ON: bio, message and caption labels survive rotation and scrolling.
493. 0209 mixed text: visible text stays unchanged unless approved table behavior says otherwise.
494. 0189 OFF: opening profile starts no photo-history request.
495. 0189 ON: no photo, one photo, same-DС history, mixed DC and incomplete history.
496. 0189 ON: verify asynchronous loading does not block profile and marks uncertain correctly.
497. 0189 account switch: old result cannot overwrite the new profile.
498. 0196 OFF: PhotoViewer and StoryViewer show stock subtitles.
499. 0196 ON: photo/document/video/story labels show correct media DC or omit absent DC.
500. 0196 album: navigate A→B→A and check labels are not retained from another item.
501. 0265 OFF: upload date never appears.
502. 0265 ON: equal date, four-minute, five-minute boundary and later date.
503. 0265 ON: locale/timezone and media types remain readable.
504. 0173 OFF: deleted reply exactly follows Android 0063.
505. 0173 ON: bold, link and mention styles with/without username and truncation.
506. 0237 airplane mode: open every bundled version, search, select and scroll entries.
507. 0237 malformed/missing fixture: explanatory state, no crash and no network fallback.
508. 0241: open a new entry, toggle it, navigate canonical page, rotate and return.
509. 0241: unknown/removed historical setting is disabled explanatory text.
510. 0244: invisible-name, hidden-char, ghost and peer-id previews reflect toggles instantly.
511. 0244: previews work with no account, no network and no real peer data.
512. 0244: recycle rows, switch theme, RTL, large font and LiteMode.
513. Logcat OFF: no `InvisibleNames`, `PeerIdHistory`, `TeleChangelogHistory` network or preview error spam.
514. Logcat ON: only bounded state/error lines; no names, IDs, text or raw code points.
515. Use network inspector to confirm 0208/0209/0196/0265/0244 add no third-party request.
516. Kill and restart during 0189 loading; app must recover with stock/uncertain state.
517. Kill and restart after 0237 parse; asset remains available offline.
518. Verify process recreation does not duplicate history observers or preview callbacks.
519. Verify no ANR while parsing the largest generated history asset.
520. Verify no dropped UI refresh when toggles change quickly twice.

## 18. Ворота пачки

521. All nine Android commits exist on `Telegram` branch `tele` in the declared order.
522. All nine commits are exported as queue patches; no patch was hand-edited.
523. `TeleConfig` defaults are OFF for every new switch and export/import includes every item.
524. Search IDs 1280..1299 are registered once and open valid existing settings modes.
525. `features.md` contains the user-facing rows in the same queue commits as their patches.
526. CI generates deterministic `changelog_history.json` before APK assembly.
527. The APK contains the history asset and the history page opens without network.
528. 0208 replaces invisible user/chat display names only in memory; no DB title write occurs.
529. 0209 labels hidden characters without mutating messages or sending data.
530. 0253 copies bare digits while display formatting remains independently configurable.
531. 0189 handles first-photo DC asynchronously and exposes uncertainty honestly.
532. 0196 and 0265 handle viewer lifecycle, null metadata and OFF paths.
533. 0173 preserves deleted-reply privacy and valid entity offsets.
534. 0241 uses canonical live rows; 0244 uses bounded synthetic previews.
535. Debug APK is assembled with `./gradlew :TMessagesProj_App:assembleDebug`.
536. APK is handed to a human for the complete ON/OFF manual matrix above.
537. Statuses change to `built` only after handoff and to `done` only after human verification.
538. Compilation alone never closes this batch.
539. Any unresolved `[ВОПРОС]` is answered or explicitly recorded before the relevant commit.
540. Any behavior marked `[INFERENCE]` is confirmed against the current branch or remains an explicit implementation constraint.

## 19. Зависимости и открытые решения

541. 0208 requires Android 0028 LocalNames and current account-aware name paths.
542. 0209 requires the shared 0208 codepoint table and display helper.
543. 0189 requires Android 0024 PeerId and a verified dialog-photo pagination API.
544. 0196 requires 0189/PeerId media formatting and Android 0024 SHOW_DC.
545. 0265 may share 0196 viewer subtitle assembly but remains a separate S commit.
546. 0173 requires Android 0063 DeletedReply and existing menu/send entities.
547. 0237 requires Android 0077/0078 current changelog/new-settings infrastructure.
548. 0241 requires 0237, 0088 and 0169 settings structure.
549. 0244 requires 0208, 0209, ghost settings, Android 0024 and 0169.
550. [ВОПРОС] Confirm whether first-photo history is allowed to page up to 500 photos on mobile data.
551. [ВОПРОС] Confirm the Android field that represents a document's upload date.
552. [ВОПРОС] Confirm deleted-author style default and whether a separate master is wanted.
553. [ВОПРОС] Confirm generated history source/retention and whether missing old releases are warning-only.
554. [ВОПРОС] Confirm preview list exactly: ghost, invisible names, hidden chars, peer IDs; no media-date preview by default.
555. Until answered, do not guess, broaden scope or silently change PATCHLIST acceptance.
