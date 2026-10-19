# Пачка 16 — внешний вид списка, профиля и пузырей

## Назначение и границы

1. Этот документ — пошаговый план реализации строк пачки 16 из `docs/PATCHLIST.md`.
2. В пачке находятся desktop-патчи 0129, 0133, 0300, 0279, 0299, 0304, 0267, 0276, 0022/0035, 0010/0041 и 0068.
3. Номер означает текущую нумерацию очереди desktop, а номер Android-патча появится только после экспорта очереди.
4. Нельзя заранее называть номер файла `patches/android/`: он зависит от позиции commit в ветке `tele`.
5. Цель пачки — локальные изменения отображения; Telegram-сеть, серверные сущности и stock DB не меняются.
6. Любой новый fork-код должен находиться в `TMessagesProj/src/main/java/tele/`.
7. В Java-файле stock разрешены только короткий gated call, ранний return или вызов `TeleHooks`.
8. Сгенерированный `TLRPC.java` не редактировать.
9. Stock-схему SQLite и `LAST_DB_VERSION` не редактировать.
10. Малые настройки и кэш изображения хранить в `tele_kv` или собственных `tele_*` таблицах.
11. Каждая пользовательская функция получает отдельный commit в Android checkout.
12. Каждая такая функция получает строку `strings_tele.xml`, settings row, search entry и export/import spec.
13. Все переключатели Android имеют default `false`.
14. Выключенный переключатель обязан оставлять поведение Android ровно stock.
15. [INFERENCE] Часть текущих desktop-путей не имеет Android-аналога один к одному; ниже такие места помечены явно.
16. Источники проверки: `AGENTS.md`, `PATCHLIST.md`, `decisions.md`, `portability.md`, `desktop-numbers.md`, `architecture.md`, `development.md`.
17. Также прочитаны `local://desk-0125-0164.md` и `local://desk-4.md`.
18. В Android ветке `tele` через `git show` прочитаны `TeleConfig.kt` и `TeleSearch.kt`.
19. В desktop `origin/main` через `git show` прочитаны патчи 0133, 0180, 0208, 0267, 0276, 0299, 0304, 0160 и связанные старые патчи.
20. Desktop 0299 и 0304 подтверждают отдельные parent/child настройки фона профиля.
21. Desktop 0133 подтверждает четыре видимых дочерних направления счётчиков и отдельный список исключённых аккаунтов.
22. Desktop 0208 подтверждает режим невидимых имён, fallback без username и настройку текста-пометки.
23. Desktop 0160 подтверждает самостоятельные настройки streamer mode и его menu entry.
24. Desktop 0180 — desktop-only fix кэша userpic; Android требует отдельной проверки bind/recycle.
25. Desktop 0322 не входит в пачку; упоминание форматов стикеров ниже не означает добавление этой функции.

## Состав и порядок

26. Порядок commit должен минимизировать регрессии горячих файлов.
27. Первым сделать 0129, потому что он меняет высоту и layout `DialogCell`.
28. Вторым сделать 0133, используя уже подтверждённые состояния строк списка.
29. Третьим сделать 0300, после того как вкладки и пересчёт высоты стабилизированы.
30. Четвёртым сделать 0279; его UI-гейты должны использовать общий `onConfigChanged`.
31. Пятым сделать 0299, только после измерения текущей `ProfileActivity.TopView`.
32. Шестым сделать 0304 поверх готового фонового источника 0299.
33. Седьмым сделать 0267, отдельно от изменения размеров и отступов пузыря.
34. Восьмым сделать 0276 поверх уже существующих `TeleNameBadges` и `BUBBLE_BADGES`.
35. Девятым сделать 0022/0035; сначала доказать безопасную точку перехвата локалей.
36. Десятым сделать 0010/0041 как ограниченный Android-эквивалент без window title.
37. Одиннадцатым сделать 0068, поскольку он касается network gate и локального wallpaper state.
38. [INFERENCE] Если maintainer объединит 0299 и 0304 в один Android commit, это нужно сначала отразить в PATCHLIST; по умолчанию commits раздельны.
39. [INFERENCE] 0022 и 0035 могут быть одним или двумя toggles; точный desktop control надо сверить перед кодом.
40. Строки 0208 и 0160 ниже описаны как связанный QoL и dependency, но не поглощаются в batch 16 без изменения PATCHLIST.

## План commits, effort и зависимости

41. `feat: add compact chat rows` — desktop 0129, effort L.
42. Зависимости 0129: текущий `TeleConfig`, `TeleHooks`, settings infrastructure и список `DialogCell`/`DialogsAdapter`.
43. 0129 не должен зависеть от локальных папок batch 15; tabs должны передавать уже рассчитанные данные.
44. `feat: hide unread counters` — desktop 0133, effort M.
45. Зависимости 0133: `FilterTabsView`, notification badge API, drawer cells и account-aware config.
46. `feat: show folder icons only` — desktop 0300, effort L.
47. Зависимости 0300: `FilterTabsView`, `DialogsActivity`, существующие folder icons и accessibility semantics.
48. `feat: hide birthday decorations` — desktop 0279, effort S.
49. Зависимость 0279: Android 0125 gift-button surface и birthday controller callbacks.
50. `feat: blur profile photo background` — desktop 0299, effort M.
51. Зависимость 0299: точная текущая `ProfileActivity.TopView` и account-scoped avatar receiver.
52. `feat: color profile from photo` — desktop 0304, effort L.
53. Зависимость 0304: 0299, `Theme.ResourcesProvider`, `ProfileActivity` and profile media layers.
54. `feat: hide bubble tails` — desktop 0267, effort M.
55. Зависимость 0267: `ChatMessageCell`, `Theme.MessageDrawable`, media/background grouping.
56. `feat: add forwarded and reply badges` — desktop 0276, effort M.
57. Зависимость 0276: Android 0077/0083 and existing `TeleNameBadges`.
58. `feat: lowercase interface text` — desktop 0022/0035, effort M.
59. Зависимость lowercase: a tested LocaleController hook and format-string policy.
60. `feat: format dialogs title` — desktop 0010/0041, effort M.
61. Зависимость title format: current `TeleBuild.label()` and a documented Android-only screen-title scope.
62. `feat: keep chat backgrounds local` — desktop 0068, effort M.
63. Зависимость backgrounds: stock `ChatThemeController`, `setWallpaperToPeer`, `clearWallpaper` and local wallpaper cache.
64. Android commit subject must be lowercase imperative and contain no desktop number.
65. Export each commit with `git format-patch` only after its manual test is complete.

## TeleConfig и настройки

66. Existing `TeleConfig.kt` registers `Item` instances in `configItems` and persists to `tele_config` preferences.
67. Java callers must use `TeleConfig.ITEM.getValue()` after the accessor exists; never use Kotlin internal `.value` from Java.
68. Add `COMPACT_CHAT_ROWS = BoolItem("compact_chat_rows", false)`.
69. Add `HIDE_UNREAD_COUNTERS = BoolItem("hide_unread_counters", false)`.
70. Add `HIDE_FOLDER_COUNTERS = BoolItem("hide_folder_counters", false)`.
71. Add `HIDE_APP_COUNTER = BoolItem("hide_app_counter", false)`.
72. Add `SKIP_ARCHIVE_COUNTER = BoolItem("skip_archive_counter", false)`.
73. [INFERENCE] Desktop `uncounted_accounts` is a peer/account set, not a boolean; do not invent its Android storage until its UX is approved.
74. Add `FOLDERS_ICONS_ONLY = BoolItem("folders_icons_only", false)`.
75. Add `HIDE_BIRTHDAYS = BoolItem("hide_birthdays", false)`.
76. Add `PROFILE_PHOTO_BACKGROUND = BoolItem("profile_photo_background", false)`.
77. Add `PROFILE_PHOTO_BACKGROUND_COLOR = BoolItem("profile_photo_background_color", false)`.
78. Add `HIDE_BUBBLE_TAILS = BoolItem("hide_bubble_tails", false)`.
79. Do not add a duplicate badge master: 0276 follows existing `BUBBLE_BADGES`.
80. Add `LOWERCASE_INTERFACE = BoolItem("lowercase_interface", false)` only after the desktop control is confirmed.
81. [INFERENCE] Add `LOWERCASE_TELE_TEXTS` only if desktop 0035 has an independent persisted control; otherwise it is an internal branch of 0022.
82. Add `DIALOGS_TITLE_FORMAT_ENABLED = BoolItem("dialogs_title_format_enabled", false)`.
83. Add `DIALOGS_TITLE_FORMAT = StringItem("dialogs_title_format", "")`, with empty value meaning stock title.
84. Add `LOCAL_CHAT_BACKGROUNDS = BoolItem("local_chat_backgrounds", false)`.
85. Do not add `STREAMER_MODE` to this batch; batch 12 owns it and decisions require independence.
86. Do not add `INVISIBLE_NAMES` here unless maintainer explicitly moves desktop 0208 into this batch.
87. Settings rows belong to the current structure, even if the old checkout still uses `MODE_INTERFACE`.
88. Proposed destinations: 0129, 0133, 0300 and 0279 in interface/chats appearance.
89. Proposed destinations: 0299 and 0304 in profiles.
90. Proposed destinations: 0267 and 0276 in messages/chats appearance.
91. Proposed destinations: 0022/0035 and 0010/0041 in interface.
92. Proposed destination: 0068 in interface/privacy only if its description clearly says local-only.
93. Parent rows must hide or disable child rows according to existing settings UI convention.
94. Turning a parent off must not delete child values.
95. Config changes must refresh an open screen without restart through `TeleHooks.onConfigChanged`.
96. Settings descriptions must state whether data is local, whether a network call is suppressed and whether a restart is unnecessary.

## Search registry IDs 1200–1219

97. Reserve the contiguous block 1200–1219 for batch 16 before adding entries.
98. Check the actual registry in the current branch first; a collision moves the whole block, never one ID.
99. Search IDs are UI IDs, not dialog IDs, and must never go to Telegram or tele-server.
100. Each entry needs English and Russian keywords where the current search API accepts them.
101. 1200 — canonical `COMPACT_CHAT_ROWS`, title “compact chat rows”.
102. Keywords: `compact`, `chat list`, `one line`, `preview`, `компактный`, `список чатов`.
103. 1201 — alias for 1200, “hide chat previews”.
104. 1202 — canonical `HIDE_UNREAD_COUNTERS`, “hide unread counters”.
105. Keywords: `unread`, `counters`, `badge`, `прочитанные`, `счётчики`, `бейдж`.
106. 1203 — child `HIDE_FOLDER_COUNTERS`, “hide folder counters”.
107. 1204 — child `HIDE_APP_COUNTER`, “hide app badge”.
108. 1205 — child `SKIP_ARCHIVE_COUNTER`, “skip archive counter”.
109. 1206 — help/alias for account-scope counters, “hide account counters”.
110. 1207 — canonical `FOLDERS_ICONS_ONLY`, “folder icons only”.
111. Keywords: `folders`, `icons`, `tabs`, `папки`, `иконки`, `вкладки`.
112. 1208 — canonical `HIDE_BIRTHDAYS`, “hide birthdays”.
113. Keywords: `birthday`, `cake`, `effects`, `день рождения`, `торт`, `эффект`.
114. 1209 — canonical `PROFILE_PHOTO_BACKGROUND`, “blurred profile photo background”.
115. Keywords: `profile`, `blur`, `avatar`, `background`, `профиль`, `размытие`, `аватар`, `фон`.
116. 1210 — child `PROFILE_PHOTO_BACKGROUND_COLOR`, “fill profile with photo colour”.
117. 1211 — canonical `HIDE_BUBBLE_TAILS`, “hide bubble tails”.
118. Keywords: `bubble`, `tail`, `message`, `пузырь`, `хвостик`, `сообщение`.
119. 1212 — alias/help for existing `BUBBLE_BADGES`, “badges in forwarded and reply headers”.
120. 1213 — canonical `LOWERCASE_INTERFACE`, “lowercase interface”.
121. Keywords: `lowercase`, `case`, `локализ`, `строчные`, `регистр`.
122. 1214 — alias for the tele-text branch if 0035 is not independent, “lowercase tele texts”.
123. 1215 — canonical `DIALOGS_TITLE_FORMAT_ENABLED`, “format dialogs title”.
124. Keywords: `title`, `header`, `format`, `template`, `заголовок`, `шаблон`, `формат`.
125. 1216 — canonical `LOCAL_CHAT_BACKGROUNDS`, “local chat backgrounds”.
126. Keywords: `wallpaper`, `background`, `local`, `обои`, `фон`, `локально`.
127. 1217 — help/alias for adjacent desktop 0208, “usernames for invisible names”; no config in batch 16.
128. 1218 — help/alias for batch 12 0160, “streamer mode”; no duplicate config.
129. 1219 — help row for hidden-member online edge case; no toggle until scope is approved.
130. [INFERENCE] IDs 1206, 1212, 1214, 1217–1219 are intentionally aliases/help, not extra TeleConfig items.
131. Search callback must open the canonical settings page and read current config on the main thread.
132. Search results must not expose chat names, account IDs or message text.

## 0129 — компактные строки чатов

133. Desktop semantics: one compact row, small userpic, name/date/counter, no message preview or topic block.
134. Android anchor: `DialogCell.buildLayout()`; do not rewrite stock text measurement when OFF.
135. Android height anchor: `DialogCell.onMeasure()` and the existing two-line/three-line height decision.
136. Android positioning anchors: `DialogCell.onLayout()`, `avatarImage`, name/date and counter draw paths.
137. `DialogsAdapter` must request a rebind/re-measure after config change; do not mutate only visible cells.
138. Compact target: avatar 28dp, one line for name/date and the existing unread/draft indicator.
139. Preserve draft indication without displaying the draft body.
140. Preserve mention/reaction behavior; 0129 must not silently reimplement 0016.
141. Do not show topic title, message name or message preview in compact mode.
142. [INFERENCE] Exact dp values beyond the documented 28dp avatar must be measured against current density and font scale.
143. Keep RTL alignment and ellipsize behavior identical to stock.
144. Large font scale must reduce available name width, never clip date or unread marker.
145. If a name is too long, ellipsize the name before the date, as stock layout does.
146. If a dialog has no avatar, the placeholder must occupy the same 28dp slot.
147. For Saved Messages, Replies and deleted peers use existing avatar types, not a null avatar fallback.
148. For forum dialogs, compact height must not leave a topic-only orphan row.
149. `DialogCell` is recycled; bind must clear message layout, topic layout, badge, alpha and compact-only flags first.
150. Every bind must set compact state from current config, never from holder history.
151. When switching account, discard cached dimensions and badge keys before binding the new account.
152. `currentAccount` must be passed through `MessagesController`/adapter; no account 0 singleton.
153. Background calculation may run off main only for immutable data; all view mutation runs on main.
154. Use `AndroidUtilities.runOnUIThread` from config/database callbacks.
155. Do not animate height changes when LiteMode disables transitions.
156. A visible recycler update may use `notifyDataSetChanged`; avoid repeated per-cell reload storms.
157. [INFERENCE] Prefer one adapter refresh after `onConfigChanged`; no current diff contract was verified.
158. Compact mode must not alter sorting, unread count, mute state, pin state or network requests.
159. OFF test must match stock `useThreeLinesLayout`, preview, topic and avatar dimensions byte-for-byte where practical.
160. Recycle test: bind compact, bind normal, bind compact again; no stale message text may remain.
161. Font test: system sizes small/default/large and display density changes.
162. Content test: private user, group, channel, forum topic, archive, folder, Saved Messages, Replies.
163. Log only state transitions and account number; never log peer title or message text.

## 0133 — счётчики непрочитанного

164. Desktop options confirmed: parent hide counters, folder counters, app badge and archive skipping.
165. Android anchors: `FilterTabsView`, `NotificationsController.setBadge/updateBadge`, `DrawerUserCell` and `DrawerProfileCell`.
166. Parent OFF must leave all counter surfaces stock, regardless of stale child values.
167. Parent ON plus child OFF must hide nothing from that child surface.
168. Parent ON plus folder child hides folder/tab unread counters but not message unread state.
169. App badge child gates only `NotificationBadge.applyCount`; it must not reset Telegram read state.
170. Archive child skips archive contribution, not unread state inside the archive.
171. Account counter semantics need separate review because desktop has `uncounted_accounts` data.
172. [INFERENCE] Do not implement account exclusion as a comma-separated account list until export/import and UI are approved.
173. `NotificationsController` callbacks run on its queue; post visual changes to main thread.
174. Never call `setBadge` from a background callback with a stale account.
175. Recompute counters on config change and account switch.
176. Drawer cells are recycled; reset badge visibility, count text and content description in every bind.
177. Filter tabs must reset selected/unselected alpha and accessibility text in every bind.
178. If a counter is hidden, keep the tab clickable and keep unread sorting unchanged.
179. Hidden counter does not imply notification suppression; 0133 is appearance only.
180. Hidden counter does not imply streamer mode or privacy mode.
181. Exact limit: no new unread limit; all stock counts remain available to internal logic.
182. Test zero, one, 99 and 100+ unread values, archived-only unread and multiple accounts.
183. Test parent OFF, parent ON/each child OFF, and parent ON/each child ON.
184. Test cold start and switching accounts while drawer is open.
185. Log only which surface is gated and current config booleans; no peer identifiers.

## 0300 — папки только с иконками

186. Desktop decision says this is a new feature; stock Android has no equivalent mode.
187. Android anchors: `FilterTabsView` tab construction/bind and `DialogsActivity` folder strip measurement.
188. Keep the selected folder and tab order unchanged.
189. Replace visible title with the existing folder icon only; do not synthesize an icon when the folder has none.
190. [INFERENCE] Fallback for a folder without an icon must be decided from current Android folder model before coding.
191. Preserve a content description containing the folder title for TalkBack.
192. Preserve long-press/menu access; icons-only is not a hit-target reduction.
193. Preserve All Chats behavior and existing 0009 hide-all gate.
194. Do not add a server filter or modify `dialogFilter` objects.
195. Do not make local folder state or unsorted state part of this feature.
196. On font scale changes, tab width should remain icon-size based and not collapse below touch target.
197. On RTL, icon placement and selected indicator must remain correct.
198. Recycler/reused tab views must clear text, icon, counter, alpha and content description before bind.
199. LiteMode does not require an animation; avoid adding one.
200. Config change must rebuild tabs once on main thread.
201. Test one folder, many folders, missing icon, selected folder, hidden All Chats and local folder.
202. Test narrow and wide screens and font scale small/default/large.
203. [INFERENCE] Exact minimum tab width and icon fallback remain open until current `FilterTabsView` implementation is inspected.

## 0279 — скрытие дней рождения

204. Central data gate: `BirthdayController.isToday` and its account-aware instance method.
205. UI anchors: `DialogsActivity` birthday suggestions, `ChatActivityEnterView` birthday gift path and `ProfileBirthdayEffect`.
206. `HIDE_BIRTHDAYS` ON must hide banners, cake/effects and birthday-only gift affordances.
207. It must not hide ordinary gifts or ordinary profile gift tabs.
208. It must not alter birthday data received from Telegram.
209. The 0125 gift-button hook and birthday hook must compose: hidden birthdays must not re-show a gift button.
210. `BirthdayController.isToday` should be gated at the lowest display decision only if doing so does not affect server requests.
211. [INFERENCE] Do not return false globally from data methods if that changes non-UI gift eligibility; inspect callers and use a display helper where needed.
212. `ProfileBirthdayEffect` subscribes to LiteMode; the fork must cancel/detach existing effect on toggle.
213. Config changes must remove an already-visible suggestion/effect without restarting the activity.
214. Account must be explicit in birthday controller and profile callbacks.
215. Test a birthday today, non-birthday, gifts disabled and birthday with ordinary gifts.
216. Test ON/OFF after profile creation and after cold start.
217. Log only feature state and event type, never birth date or peer name.

## 0299 — размытый фон шапки профиля

218. Desktop 0299 uses the profile photo, blur and an edge colour; it excludes preview/topic/saved variants in its desktop top bar.
219. Android anchor is `ProfileActivity.TopView`, but exact class/member names must be checked in current stock before editing.
220. Create a `tele` helper that owns blur cache and invalidation; do not put image processing in the profile view.
221. Cache key must include account, peer identity, avatar location/version and target size.
222. Cache must not include message text, username or server response.
223. Decode and blur off the UI thread; publish only if account, fragment lifecycle and cache key still match.
224. UI assignment and invalidation run on main thread.
225. Use existing Android image receiver/blur utilities if available; do not add a native blur dependency without approval.
226. [INFERENCE] Exact blur radius, crop and darkening factor are not specified in PATCHLIST and must be measured against desktop source/device UX.
227. On missing avatar, deleted avatar, animated avatar or load failure, fall back to stock profile header.
228. Streamer mode and screenshot flags are not part of 0299.
229. LiteMode must disable any new crossfade/animation, not the static background.
230. Recreate cache after theme, orientation, density or profile width changes.
231. Avoid retaining `Activity`, `View` or `ImageReceiver` in a worker callback.
232. Test user, group, channel, self, Saved Messages and no-avatar profiles.
233. Test light/dark themes, portrait rotation, large image and slow network.
234. OFF test must show stock `TopView` with no blur allocation.
235. Log cache hit/miss and account only; no URI, peer ID or image content.

## 0304 — заливка профиля через ResourcesProvider

236. Maintainer decision requires a full `ResourcesProvider` override, not a local colour tweak.
237. Parent 0299 must be ON before exposing the child row.
238. `PROFILE_PHOTO_BACKGROUND_COLOR` OFF must leave all theme keys stock even when blur is ON.
239. Build a profile-scoped provider that delegates every unhandled key to the original provider.
240. Override only keys proven by `ProfileActivity`/profile child views to be part of this surface.
241. Never install the provider globally for settings, chat list or another account.
242. Provider must be passed to every child that accepts `Theme.ResourcesProvider`.
243. Provider must retain the original provider for fallback and release when the profile fragment dies.
244. [INFERENCE] Exact key set is not safely inferable from `ResourcesProvider` call sites; enumerate it by tracing profile inflation and theme descriptions.
245. Compute colour from the blurred image edge/bottom only after source and algorithm are confirmed.
246. Maintain readable foreground contrast in light and dark themes.
247. If colour computation fails, use original provider rather than transparent/black.
248. Theme changes, profile avatar changes and config changes must invalidate provider caches on main thread.
249. Do not write derived colours into global `Theme` or shared preferences unless a versioned cache is needed.
250. Test profile body, shared media, tabs, buttons, dividers, text, status bar and bottom sheets.
251. Test a bright photo, dark photo, transparent/gradient photo, no photo and animated photo.
252. Test parent OFF, parent ON child OFF and both ON.
253. Test opening two profiles on different accounts and rapidly switching between them.
254. Log only provider lifecycle and fallback reason; no colour source image or peer data.

## 0267 — хвостики пузырей и сервисные сообщения

255. Desktop 0267 rounds the sender corner and also covers sticker-caption/settings preview surfaces.
256. Android background selection anchor: `ChatMessageCell.getCurrentBackgroundDrawable()`.
257. Existing selection distinguishes `msgIn/msgOut` from `msgInMedia/msgOutMedia` using `drawPinnedBottom` and media grouping.
258. Preferred Android strategy is to force the no-tail/pinned-bottom drawable when the toggle is ON.
259. [INFERENCE] The exact field assignment point for `drawPinnedBottom` must be rechecked in current `ChatMessageCell`; do not set it in every draw call.
260. The hook must preserve incoming/outgoing colour, selected state, reaction state and media background.
261. Do not blindly alter `dp` padding, total height or avatar placement in the first implementation.
262. Existing `drawPinnedBottom` changes text padding and height; verify before accepting those side effects.
263. If a dedicated no-tail drawable can be selected without pinned-bottom geometry, prefer it.
264. Service messages use `ChatActionCell` and may not use `ChatMessageCell` background; inspect and gate separately.
265. [INFERENCE] No service-cell tail hook was confirmed in the read set; do not claim service messages are covered until device render proves it.
266. Sticker captions and bot keyboards must retain their existing rounded/media rules.
267. Replies, forwarded messages and albums must not gain a second tail or lose grouping separators.
268. Recycled cells must clear any forced-pinned flag before normal bind.
269. Respect LiteMode; no new bubble animation is allowed.
270. Test incoming/outgoing text, media, album, document, bot keyboard, sticker caption, reply, forwarded and service message.
271. Test first/middle/last messages in a grouped run and messages with `mediaBackground`.
272. Test ON/OFF, theme changes, font scales and RTL.
273. Log only drawable mode and message kind; never log text or IDs.

## 0276 — бейджи в forwarded и reply headers

274. Existing Android `BUBBLE_BADGES`, `TeleNameBadges.withVerified` and Android 0077/0083 are prerequisites.
275. Forward anchor: `ChatMessageCell.getForwardedName()` and `forwardedNameLayout[0|1]`.
276. Reply anchor: `replyNameLayout` and its forwarded-name branch.
277. Wrap only the displayed sender name, not the quote text or destination chat title.
278. Resolve badge with the original sender peer from `messageOwner.fwd_from.from_id` or reply source.
279. If source peer is absent/hidden/deleted, render the existing plain stock name.
280. Width measurement must include left icon and checkmark before layout caching.
281. Rebuild layouts when badge data changes, using the existing `tele_bubbleKey` invalidation contract.
282. Badge loading and Argon/server cache work stays off the UI thread.
283. Layout updates and cell invalidation return to main thread after checking account and bound message.
284. Recycled cells must clear old badge spans/drawables before bind.
285. Do not show a badge for a different account after account switch.
286. OFF means no additional badge work and exactly the current Android 0083 behavior.
287. Test ordinary forward, anonymous forward, channel forward, reply to forward, reply to user and missing source peer.
288. Test long names, RTL, large font, narrow width and media caption reply.
289. Test badge cache refresh while a cell is visible.
290. Log badge cache state only; never log sender name, peer ID or message content.

## Невидимые имена и скрытые участники (смежный QoL)

291. Desktop 0208 is not a PATCHLIST batch-16 row, but it is relevant to compact rows and profile/bubble readability.
292. Its confirmed semantics: when a displayed name is empty or made of invisible Unicode characters, show a username.
293. It has a master option, a fallback when there is no username and a configurable marked phrase.
294. Maintainer decision says user names are transformed through `UserObject`, while chat titles are applied through `MessagesController.putChat` only in memory.
295. No transformed chat title may be written to Telegram or stock DB.
296. [INFERENCE] Android implementation must first enumerate all `UserObject.getFirstName/getUserName`, `DialogCell`, profile, header and bubble callers.
297. Do not substitute the username in a message entity or outgoing text; this is display-only.
298. Preserve `Saved Messages`, `Replies`, deleted users and anonymous senders as stock special cases.
299. Invisible-character detection must use the desktop-defined codepoint set; do not copy a guessed Unicode list.
300. If no username exists, use the maintainer-approved fallback only; do not expose phone or peer ID by default.
301. Search ID 1217 is help/alias until 0208 receives its own Android row and commit.
302. Hidden members: portability notes identify a stock edge where a group with hidden participants and at most 200 members may not show online count.
303. This edge is not a new batch-16 toggle; it is a possible small QoL fix to verify separately.
304. If fixed, use `MessagesController` online data and `ChatAvatarContainer`, account-aware.
305. Never infer member identities from hidden participant data.
306. Do not log participant lists, names or online member IDs.

## Streamer mode independence

307. Desktop 0160 and maintainer decision require streamer mode independent of never-block-screenshots 0113 and hide-phone 0172.
308. Batch 16 must not add a second `STREAMER_MODE` item or precedence rule.
309. Android implementation belongs to batch 12 and must gate each window that can set `FLAG_SECURE`.
310. Relevant windows include `LaunchActivity`, `BubbleActivity` and `ExternalActionActivity`, plus every already-identified secure viewer.
311. Notification preview hiding and phone masking must be independently gated by the same batch-12 setting.
312. A batch-16 profile theme or hidden-name helper must not bypass streamer masking.
313. [INFERENCE] Conflict behavior with 0113 is intentionally “no precedence rule” per decision; do not resolve it in this guide.
314. Search ID 1218 points to the future canonical privacy row and must not create duplicate settings.
315. Streamer tests belong to batch 12 gate, but batch-16 profile tests should ensure no regression when it is ON.

## Local chat backgrounds, privacy and network gate

316. Desktop 0068 extends stock per-chat wallpaper with force-local set/remove behavior.
317. Android already has per-chat wallpaper; do not reimplement the stock picker or colour editor.
318. Android stock anchor confirmed in `ChatThemeController.setWallpaperToPeer()` and `clearWallpaper()`.
319. Both paths construct `TL_messages_setChatWallPaper`; the fork must stop the request only when local mode is ON.
320. Local apply/remove must persist fork state by account and dialog ID, not by title.
321. [INFERENCE] Exact local serialization should reuse `ChatThemeController`’s existing wallpaper representation without changing stock DB schema.
322. A local wallpaper must render in the chat and survive process restart on that account/device.
323. A local wallpaper must not create a server action message or trigger server sync.
324. Removing a local wallpaper must restore the prior local/default wallpaper without touching server state.
325. Existing server wallpapers remain server-owned; OFF follows all stock request and update paths.
326. Network gate must be at the lowest request path, not only at the picker button.
327. Callback handling must distinguish local completion from server response and ignore stale account callbacks.
328. Never put wallpaper bytes, chat titles or message text in logcat.
329. Test ON/OFF, set/remove, restart, account switch, server wallpaper update and failed upload.
330. Test a local-only change while offline; it must not queue a Telegram request.
331. Confirm stock `setWallpaperToPeer` call signatures before adding any `tele_` member.

## Lowercase and format options

332. Desktop 0022 lowercases interface text; 0035 also addresses tele’s own texts.
333. Port through the narrowest proven `LocaleController.getString` path, not a global `String.toLowerCase()` sweep.
334. Use `Locale.ROOT` only if desktop semantics explicitly require locale-independent casing.
335. Never lowercase URLs, usernames, IDs, placeholders, message text, server data or user-entered names.
336. Do not lowercase format specifiers such as `%1$s`, `%d`, braces or markup tokens.
337. Preserve locale-specific casing and Turkish dotted/dotless-I behavior according to the approved desktop rule.
338. Fork strings remain in `strings_tele.xml`; stock `strings.xml` is read-only.
339. A formatted string must be lowercased after formatting only when its arguments are not user data; otherwise use a segment-aware operation.
340. [INFERENCE] The exact Android interception point and segment policy are unresolved; code only after a focused experiment with plural/format strings.
341. `LOWERCASE_INTERFACE` OFF must avoid creating transformed strings or changing LocaleController caches.
342. Config changes must invalidate/rebuild relevant visible UI without corrupting spans.
343. Test English, Russian, German, Turkish, Arabic and a locale with plural forms.
344. Test dates, counts, usernames, URLs, bot buttons, tele strings and accessibility descriptions.
345. Format title option is separate from lowercase; lowercasing a title must not mutate `TeleBuild.label()` data.
346. No network or account data is involved in these options.

## Dialogs title template (Android partial)

347. Desktop 0010/0041 format a window title; Android has no equivalent OS window title.
348. PATCHLIST permits only a partial screen-header interpretation and keeps 0150 skipped.
349. Therefore default UI keeps the current `TeleBuild.label()` behavior and no template is active.
350. If enabled, scope the template to the dialogs screen header only, not Android task title or notification title.
351. [INFERENCE] Variable names and escaping must be copied from the exact desktop patch before adding an editor.
352. Reject unknown variables visibly and preserve the stock title on invalid template input.
353. Limit template length to a maintainer-approved value; no arbitrary limit may be invented here.
354. Do not include account phone, peer title or message text unless explicitly part of approved variables.
355. Export/import the template only when the settings IO spec supports string options.
356. Search ID 1215 opens this row; the row remains hidden or disabled when partial Android support is not shipped.

## Settings strings, export and import

357. Every canonical item gets a `Tele...` key in `strings_tele.xml` plus a short description.
358. Descriptions must state “только внешний вид” where no data/network behavior changes.
359. 0068 must explicitly state “локальные обои не отправляются на сервер при включённом переключателе”.
360. 0299/0304 descriptions must explain parent/child relationship and fallback to stock on missing photo.
361. 0133 child rows appear only while `HIDE_UNREAD_COUNTERS` is ON, without deleting saved values.
362. 0304 child row appears only while `PROFILE_PHOTO_BACKGROUND` is ON.
363. Export/import includes all canonical bools and the approved title string, never search aliases.
364. Import must ignore unknown keys, preserve defaults and log only the key name.
365. Local image caches are not exported.
366. No user names, phone numbers, peer IDs or wallpaper bytes enter settings export unless a separate decision approves it.
367. `features.md` is user-facing English documentation, not an implementation notebook.

## Потоки, аккаунты, recycling и LiteMode checklist

368. Main-thread-only: View changes, Recycler binds, theme providers, `ImageReceiver` updates and invalidation.
369. Background-allowed: image decode/blur, cache IO, badge hash calculation and wallpaper serialization.
370. Every async callback checks account, fragment/view lifecycle and the current feature state.
371. Every account-specific helper receives `account` explicitly.
372. Never call `MessagesController.getInstance(0)` from a feature helper.
373. Recycled list cells reset every feature field before setting the bound state.
374. Recycled tabs reset icon/text/counter/content description before setting folder state.
375. LiteMode must suppress optional animations and crossfades introduced by this batch.
376. Static compact rows, static themes and no-tail drawables remain available under LiteMode.
377. A stale callback must be dropped rather than applied to a newly bound cell.
378. Account switch must invalidate in-memory profile theme, blur and badge caches.
379. Process death must restore only persisted config/local wallpaper state; never reconstruct network data from logs.
380. Privacy: display-only transforms never leave the device; 0068 local mode suppresses the Telegram request at request layer.

## Тесты on/off и logcat

381. Build test uses `./gradlew :TMessagesProj_App:assembleDebug` in the Android checkout after all commits land.
382. Manual tester records default, OFF and ON states; compiling is not evidence of working rendering.
383. 0129: compare normal/compact rows across private/group/channel/forum/archive/Saved/Replies.
384. 0129: rotate, change font scale, switch account and recycle holders in each mode.
385. 0133: exercise parent and every child independently for folder, archive, app badge and account surfaces.
386. 0300: exercise icon-only tabs with missing icon, RTL, accessibility and hidden All Chats.
387. 0279: exercise birthday banner, gift button, profile effect and ordinary gift behavior.
388. 0299: exercise blurred header with avatar/no avatar, light/dark theme, rotation and slow load.
389. 0304: exercise parent/child matrix and readable controls over bright/dark/gradient photos.
390. 0267: exercise incoming/outgoing/service/media/album/sticker-caption/bot-keyboard bubbles.
391. 0276: exercise forwarded/reply headers with badge, missing source, long names and large font.
392. 0022/0035: exercise English/Russian/Turkish/plural/format strings and OFF exactness.
393. 0010/0041: exercise empty/invalid/approved template and stock fallback; no OS title claim.
394. 0068: exercise local set/remove offline, restart, account switch and server update; inspect no request.
395. For each ON test capture a screenshot and a short expected-vs-actual note.
396. For each OFF test compare against stock screen and note any visual delta.
397. Logcat filters may include `TeleHooks`, feature-specific tag and `AndroidRuntime`.
398. Add temporary logs only behind existing debug logging and remove them before export.
399. Permanent logs may include feature name, account index and cache outcome only.
400. Permanent logs must not include names, usernames, peer/message IDs, message text, URLs containing account data or image bytes.
401. Watch for ANR, `CalledFromWrongThreadException`, stale provider colours, recycled badge leakage and account-0 reads.
402. Verify no `TL_messages_setChatWallPaper` request occurs for local 0068 changes.

## features.md rows

403. Add one English row per user-facing canonical feature in the same repository commit as each exported patch.
404. 0129 row: compact one-line chat rows with small avatars and no message preview; interface/chats; default off; desktop 0129.
405. 0133 row: hide unread counters by selected surfaces without changing unread state; interface/chats; default off; desktop 0133.
406. 0300 row: show folder tabs as icons while retaining accessible names; interface/chats; default off; desktop 0300.
407. 0279 row: hide birthday banners, effects and birthday-only affordances; interface/chats; default off; desktop 0279.
408. 0299 row: use a blurred profile photo as the profile header background; profiles; default off; desktop 0299.
409. 0304 row: fill supported profile surfaces with a readable colour derived from that photo; profiles; default off; desktop 0304.
410. 0267 row: remove sender tails from message bubbles; messages; default off; desktop 0267.
411. 0276 row: show existing tele badges in forwarded and reply headers; messages; with existing bubble badges; desktop 0276.
412. 0022/0035 row: lowercase interface and, if independently confirmed, tele strings; interface; default off; desktop 0022/0035.
413. 0010/0041 row: format the dialogs screen title only where Android has a supported equivalent; interface; default off; desktop 0010/0041.
414. 0068 row: keep selected chat wallpapers local and suppress their server update; interface; default off; desktop 0068.
415. Do not add rows for aliases/help IDs, streamer mode 0160, invisible names 0208 or hidden-member QoL until their own Android patches exist.
416. Android column must point to exported patch filename, never a planned filename.
417. Desktop column must link current desktop queue number, not old number from `desktop-numbers.md`.

## Открытые решения и вопросы

418. Confirm exact desktop 0022/0035 control relationship before deciding one versus two TeleConfig items.
419. Confirm Android fallback for a folder with no icon in 0300.
420. Confirm whether account counter exclusions are in batch 16 or deferred with a separate picker.
421. Confirm exact blur radius/crop/darkening and cache policy for 0299.
422. Confirm the complete profile `ResourcesProvider` key set for 0304.
423. Confirm whether service `ChatActionCell` participates in 0267 or remains stock.
424. Confirm 0010/0041 Android variable set and maximum format length.
425. Confirm local wallpaper serialization and the exact lowest request gate for 0068.
426. Confirm whether 0208 is scheduled for a later batch and which settings page owns it.
427. Confirm hidden-member online count fix as separate QoL, with no hidden identity exposure.
428. Do not silently answer any of these by copying desktop assumptions into Android.

## Batch gate

429. All eleven batch-16 rows must have one exported Android commit or an explicit documented skip.
430. Every new config item must be default OFF and present in settings, search, export/import and `strings_tele.xml`.
431. Every call site must be gated so OFF is stock.
432. Debug APK must be assembled only after all commits and exports land.
433. Human device/AVD testing must cover compact rows and icon-only folders at multiple font sizes.
434. Human testing must cover profile blur and full colour override with light/dark and missing-photo cases.
435. Human testing must cover no-tail bubbles, forwarded/reply badges and service-message behavior.
436. Human testing must cover lowercase locale/format cases and local wallpaper network suppression.
437. Human testing must include account switching, recycled cells, LiteMode and streamer mode regression.
438. Batch status becomes `built` only after APK handoff, then `done` only after human verification.
439. A passing compile without screenshots, on/off comparison and logcat review is not the batch gate.
440. PATCHLIST statuses and features.md rows are updated only after export, never while the guide is merely planned.
