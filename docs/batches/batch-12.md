# Пачка 12: база приватности — руководство реализации для Android

## Назначение и границы

1. Документ описывает реализацию именно строк пачки 12 в `docs/PATCHLIST.md`.
2. Целевая очередь Android — ветка `tele`; fork-код — Kotlin в `tele/`.
3. Изменять stock-код только небольшими вызовами `TeleHooks` за ранним гейтом.
4. Этот документ — план, не утверждение, что перечисленные hooks уже проверены в checkout.
5. Android checkout нельзя было прочитать через `git show`: ожидаемый `../Telegram` отсутствует в текущем рабочем окружении.
6. Поэтому точные Java anchor-snippets ниже — ориентиры по именам, зафиксированным PATCHLIST и рабочим заметкам, а не буквальные цитаты исходника.
7. Каждый такой anchor считать `[INFERENCE]` и сверить `git show tele:<path>` перед редактированием.
8. Desktop-поведение изучено в локальных оценках `desk-0125-0164`, `desk-2`, `desk-3`, `desk-delta`; изменения применять по Android-плану и решениям.
9. Номера в этом документе — текущие номера патчей `origin/main` desktop; не путать их с Android patch position.
10. Batch 12 содержит девять строк: 0016/0073, 0032/0073, 0032/0064, 0166, 0228, 0227, 0229, 0282, 0160.
11. Оценка из PATCHLIST: `M×7, L×2`.
12. Цель — сначала локальная база приватности, затем её потребители.
13. Нельзя менять `TLRPC.java`, stock DB schema или `LAST_DB_VERSION`.
14. Каждая новая опция — item `TeleConfig`, default `false`, UI row и export/import spec.
15. Переключатель OFF обязан оставить поведение stock Android неизменным.
16. Fork-данные — `tele_kv` или таблицы `tele_*` через `TeleDatabaseHelper`.
17. Account-dependent state всегда включает account id в ключ или запрос.
18. Никаких account ids, username, contacts, message text на tele-сервер не отправлять.
19. Сетевые действия должны идти только через Telegram API там, где этого требует feature; приватные фильтры локальны.
20. Не добавлять комментарии к коду; краткие имена и небольшие функции предпочтительнее.
21. Каждая пользовательская строка — `strings_tele.xml`, префикс `Tele`.
22. Поиск настроек получает стабильные уникальные IDs 1120–1139.
23. Любое упоминание конкретного места реализации, отсутствующее в исходниках/доках, помечать `[INFERENCE]`.

## Прочитанные источники и ограничения

24. Прочитан `AGENTS.md`: fork-код новый, hooks минимальны, off=stock, приватность и мног аккаунтность обязательны.
25. Прочитан `docs/PATCHLIST.md`: состав, зависимости, порядок и batch gate.
26. Прочитан `docs/decisions.md`: приватность базой, 0166 Java-regex, 0282 off и обязательное восстановление при старте, 0160 независимо от 0113/0172.
27. Прочитан `docs/portability.md`: desktop-функции и заявленные Android call sites.
28. Прочитан `docs/desktop-numbers.md`: desktop номера использовать по текущей очереди.
29. Прочитан `docs/architecture.md`: TeleConfig/settings/db/export/import conventions.
30. Прочитан `docs/development.md`: commit/export/build/manual gate workflow.
31. Прочитан `local://desk-0125-0164.md`: ghost, privacy, last-seen механика и Android ограничения.
32. Прочитан `local://desk-2.md`: ignored words, Java Regex, фильтрация сообщений.
33. Прочитан `local://desk-3.md`: уведомления, stories и ghost schedule follow-ups.
34. Прочитан `local://desk-delta.md`: новые desktop номера и изменение поведения старых патчей.
35. Попытка `git show tele:...` и `git show origin/main:...` была остановлена отсутствием `../Telegram` в окружении.
36. Следовательно, никаких утверждений о точных строках Android или проверенном поведении здесь нет.
37. Локальные источники описывают Android 12.10.x, но текущая ветка может дрейфовать.
38. Перед первым кодовым патчем сверить API и состояние уже перенесённого ghost/story кода непосредственно в `tele`.
39. PATCHLIST говорит, что глобальный ghost/receipts уже есть из batch 2; остаток — schedule/offline-after-send и исключения чатов.
40. Невидимые stories 0021 уже перенесены Android patch 0021; не дублировать их глобальный тумблер.

## Полный состав, commits, усилия и порядок

41. Одна строка таблицы соответствует одному отдельному commit на Android.
42. Subject lowercase imperative, формат `feat: …`; не включать desktop номер в commit subject.
43. Export через `git format-patch`; номер Android-патча присваивается позицией очереди, не придумывать его заранее.
44. Effort и зависимости — как в PATCHLIST; внутренний порядок ниже — обязательный для реализации.

| Порядок | Desktop № | Commit subject draft | Effort | Зависимости / назначение |
|---:|---|---|---|---|
| 1 | 0016, 0073 | `feat: add ignored peers` | M | Базовые списки peer и общий peer picker |
| 2 | 0032, 0073 | `feat: add per-chat ghost mode` | M | Игнор-пикер/хранилище и уже существующие глобальные ghost hooks |
| 3 | 0032, 0064 | `feat: add ghost scheduled sending` | M | Ghost base; scheduleDate hook и offline-after-send |
| 4 | 0166 | `feat: hide messages by words` | M | Игнор-база; глобальные и per-chat Java-regex rules |
| 5 | 0228 | `feat: mute ignored and hidden messages` | M | Ignore + 0166; NotificationsController фильтр, локальные unread presentation |
| 6 | 0227 | `feat: show ghost scheduled messages` | L | Ghost schedule + per-chat ghost + ignore behavior |
| 7 | 0229 | `feat: keep invisible story reads local` | M | Per-chat ghost + Android 0021 invisible stories |
| 8 | 0282 | `feat: restore last seen after inspection` | L | Прямой тумблер last-seen swap, запусковая очистка/restore |
| 9 | 0160 | `feat: add streamer mode` | M | Независим от 0113/0172; privacy surface, secure window and previews |

45. SUBJECTS — предложения по плану, не утверждение о фактических именах desktop commits.
46. Сначала 0016/0073 строит фундамент; последующие строки используют общий filter contract.
47. Порядок 0032 ghost базой перед hidden words и stories следует решению мейнтейнера.
48. 0228 не меняет серверные unread значения: это локальный визуальный/notification слой.
49. 0227 после scheduling base, поскольку только так можно отобразить локальное призрачное сообщение и передать его отправке.
50. 0282 не зависит от 0160; разместить в конце по объёму/restore-регрессиям.
51. 0160 также не блокировать 0113 «never block screenshots» или 0172 «hide phone» зависимостью.
52. Не объединять эти функции одним супер-тумблером: каждый patch — отдельная фича и экспортируемая настройка.

## Конфигурация, страницы и поиск

53. Использовать уже имеющиеся `TeleConfig`, settings rows, `TeleSearch` и export/import registry.
54. Не добавлять второй ключ, если соответствующая строка уже существует; сверить TeleConfig в ветке.
55. Все новые пользовательские toggles — false, включая streamer mode и last-seen swap.
56. Родительские тумблеры могут иметь скрытые дочерние настройки; дочерний row показывать только при включённом родителе.
57. Страницы берём из текущей Android структуры: privacy для ignore/ghost/words/stories/last seen/streamer.
58. Picker доступен из privacy и из chat context; reusable экран должен сообщать режим, а не иметь неразличимые списки.
59. Per-chat правила скрытых слов доступны через пункт чата, глобальные — в privacy.
60. Ghost schedule option — privacy, с кратким описанием ограничения: только локальный контроль очереди, не отменяет серверную отправку по расписанию.
61. Silent ignored/hidden — дочерняя privacy опция; может называться «Не уведомлять об игнорируемых и скрытых».
62. Last-seen описание обязательно предупреждает, что временное изменение правила видимости может раскрыть активность и автоматически восстанавливается после убийства процесса.
63. Streamer описывает захват экрана, превью уведомлений и скрытие номеров; оконный заголовок на Android отсутствует.
64. Экспортировать bool items, global words config, privacy modes только если они оформлены как config; большие изменяемые peer sets export spec — отдельное решение ниже.
65. Search IDs стабильны; ID не равен dialog id, не пересылается по сети и не переиспользуется.

| Search ID | TeleConfig / запись поиска | Настройки | Default | Keywords |
|---:|---|---|---|---|
| 1120 | `IGNORE_PEERS` / ignored list | privacy | false | ignore, ignored, user, hide, fade, исключение |
| 1121 | `IGNORE_FADE` | privacy / child | false | fade, dim, opacity, затухание |
| 1122 | `GHOST_MODE` (reuse current key if present) | privacy | existing setting; do not duplicate | ghost, invisible, privacy, online |
| 1123 | `GHOST_PER_CHAT` | privacy | false | chat ghost, exception, per chat |
| 1124 | `GHOST_SCHEDULE` | privacy | false | scheduled, ghost, scheduleDate |
| 1125 | `HIDDEN_WORDS` | privacy | false | keyword, regex, hidden words |
| 1126 | `HIDDEN_WORDS_PER_CHAT` | privacy / child | false | chat rule, local rule, regex |
| 1127 | `MUTE_IGNORED` | privacy | false | silent, ignored, notification, mute |
| 1128 | `INVISIBLE_STORIES_PER_CHAT` | privacy | false | stories, invisible, read, ghost |
| 1129 | `LAST_SEEN_SWAP` | privacy | false | last seen, online, restore, status |
| 1130 | `STREAMER_MODE` | privacy | false | streamer, screenshot, screen capture |
| 1131 | `STREAMER_HIDE_NOTIFICATIONS` | privacy / child | false | notification preview, content, lock screen |
| 1132 | `STREAMER_HIDE_PHONE` | privacy / child | false | phone number, profile, account |
| 1133 | `GHOST_SCHEDULE_SHOW_LOCAL` | privacy / child | false | local scheduled message, ghost send |
| 1134 | ignore picker help/detail | privacy detail page | — | privacy picker, ignored peers |
| 1135 | ghost-chat picker help/detail | privacy detail page | — | ghost exceptions, selected chats |
| 1136 | hidden words editor help/detail | privacy detail page | — | regex syntax, Java regex |
| 1137 | story read-state help/detail | privacy detail page | — | max_read_id, stories read |
| 1138 | last-seen restore help/detail | privacy detail page | — | restore startup, process death |
| 1139 | streamer limitations help/detail | privacy detail page | — | FLAG_SECURE, screenshots, Recents |

66. IDs 1122 reuse an existing ghost item or point to its existing search entry; never create duplicate config.
67. 1131/1132 are optional children only if separate control is required by actual UX; otherwise point to STREAMER_MODE help.
68. Search entries 1134–1139 may link to setting/help rows; they must not create additional toggles.
69. One search result per actual item; aliases reference the item and must not double-register key.
70. Check current allocated IDs before using 1120–1139; if collision exists, select a contiguous free range and update this guide in same change.

## Shared privacy contract

71. Implement a central helper such as `PrivacyFilter` / `TeleHooks` entry points; no independent policy logic in each cell.
72. A decision function takes `account`, `dialogId`, optional `topicId`, message owner/object, and purpose enum.
73. Purpose distinguishes render-in-chat, dialog preview, notification, unread presentation, story read, and send behavior.
74. Do not treat “hidden” as “deleted”: preserve underlying Telegram data and server updates.
75. Filter only incoming messages from ignored users; own messages and service/sponsored messages are excluded from word hiding per desktop notes.
76. [INFERENCE] Whether ignore-list hides both participants and chats is ambiguous in PATCHLIST (“user id”, peer picker); support user and channel/group peer ids only after checking desktop patch semantics.
77. A hidden message must not collapse list indices inconsistently or make recycler animation corrupt; choose stable adapter filtering or explicit zero-height binding after inspecting stock list model.
78. The same predicate must govern chat rows, chat preview, message list, notifications, and mention/reaction navigation where listed.
79. Never mutate `TLRPC.Message` text or server-side unread state to implement local hiding.
80. For asynchronously loaded rules, default to showing stock content only when feature is off; when enabled, avoid transient exposure if policy data is not yet loaded.
81. [INFERENCE] Startup-safe cache/placeholder behavior needs maintainer choice; do not silently hide everything while DB is loading.
82. All UI updates and dialogs execute on main thread; storage and matching data may run off-main as permitted by stock pipeline.
83. `ConnectionsManager` callbacks and `MessagesStorage` callbacks must hop to UI before view access.
84. Bind recycled holders from current account + current message every time; clear stale alpha/visibility/text when no rule applies.
85. Account switching must clear/rebind visible rows and list screens; never use `getInstance(0)` implicitly.
86. Do not log words, regex source, message body, username, phone, or peer identity.
87. Diagnostics may log feature state, result category, and anonymized operation count only, and should be debug-only.
88. Respect stock `LiteMode` and performance gates; this batch has no required animation.

## Storage and migrations

89. Peer sets are per account and stored in `tele_kv`; a table is unnecessary for compact list state, as PATCHLIST specifies.
90. PATCHLIST legacy suggestion: comma-separated IDs; prefer a versioned JSON list if existing helper conventions support it, to avoid delimiter ambiguity; `[INFERENCE]` format must be chosen after reviewing `TeleDatabaseHelper`.
91. Separate keys for ignored peers and ghosted dialogs, with account scoping matching current TeleDatabaseHelper rules.
92. Store peer IDs as signed 64-bit decimal values; preserve Telegram dialogId sign conventions.
93. Do not use usernames as identifiers: they change and can disclose data.
94. The picker resolves names/photos from the local account cache; no new network fetch is necessary just to pick known peers.
95. If peer object is not cached, picker may use stock local contacts/dialog list; network resolution is an unresolved UX choice, not permission for tele server upload.
96. Hidden words global rules: persist a versioned list in `tele_kv`, or use TeleConfig StringItem only if size and export handling are safe.
97. Per-chat words: per-account JSON map `dialogId -> list<Rule>` in `tele_kv`; PATCHLIST expressly suggests key-value storage.
98. Rule fields should preserve literal-vs-regex and case mode; avoid inferring slash syntax beyond desktop notes.
99. Parse/compile patterns once on write, cache compiled patterns by account and rule revision, invalidate on edit.
100. Invalid Java regex must be surfaced inline in editor; keep previous valid rules active until save succeeds.
101. Java `Pattern` semantics are accepted by decisions; do not claim PCRE parity.
102. Ghost schedule persistence belongs in fork storage only if queued local messages must survive process restart; PATCHLIST requires locally visible pending message and successful handover.
103. [INFERENCE] Exact durable queue fields are not defined in the plan; first inspect stock scheduled message and existing `SendMessagesHelper` queue persistence.
104. Prefer existing local scheduled-message representation if it supports unsent ghost messages without altering stock schema.
105. If extra records needed, use `tele_ghost_scheduled` table through TeleDatabaseHelper; fields likely account/dialog/topic/local id/date/state, but exact key/serialization is unresolved.
106. Never add a stock column or change `LAST_DB_VERSION`.
107. For story read memory: desktop notes call for remembering max read id for 48 hours; persist per account/peer/story id + expiry in tele table/KV.
108. [INFERENCE] PATCHLIST does not specify retention duration; 48h is from `desk-3` analysis and must be confirmed against exact desktop patch before implementation.
109. Story read storage must be monotonic within expiry and must not overwrite server read state.
110. Last-seen swap: store original account privacy rule and restoration intent in `tele_kv` before any request changing it.
111. Store enough to restore after forced process death; recovery runs before ordinary online-status request at application startup.
112. [INFERENCE] Exact privacy API fields/request names require inspecting current TL classes; do not invent request structure or edit TLRPC.java.
113. One-time migration: absent keys mean empty sets/off; malformed data is ignored safely and preserved for possible recovery, not blindly overwritten.
114. Migration must be idempotent and scoped by account.
115. Export/import should include user-configurable toggles and rule lists only after explicit spec; peer IDs and patterns are private data, and default export may omit them.
116. Ask maintainer / resolve in implementation: whether privacy lists/rules are included in settings export; current docs do not decide.

## 0016 + 0073: ignored peer list and picker

117. Behavior: selected users/peers are either hidden or faded; PATCHLIST names both modes.
118. UI is a fork picker that feels like Telegram Privacy exceptions, but must not reuse `PrivacyUsersActivity` because stock is hardwired to `TYPE_BLOCKED` and `ContactsController` block list.
119. Provide separate modes (hide / fade) using one peer set plus a per-feature display mode, unless desktop source proves separate sets.
120. [INFERENCE] Whether hide/fade are one mutually exclusive setting or independent state must be read from desktop 0016 before choosing.
121. Picker rows should show locally cached avatar/name, selected state, and an accessible removal action.
122. Add peers by selecting users/dialog participants; provide clear removal and empty-state UX.
123. Avoid exposing block-list controls; ignore is local and must not call `contacts.block` / unblock.
124. Storage is local `tele_kv`, per-account; no network mutation.
125. Data-layer filter contract includes ignored sender ids and peer scope.
126. For group messages, compare message sender id; do not hide every message in a group merely because the group itself is selected unless the documented mode defines peer-level hiding.
127. PATCHLIST explicitly requires `DialogCell` list filtering and `ChatMessageCell` in-chat filtering.
128. `[INFERENCE]` exact adapter entry point in current source must be located with `git show` + symbol search; do not edit hot file broadly.
129. Potential anchor (verify): `ChatMessageCell` bind/setup path receives `MessageObject`; gated call should set display style only after stock bind.
130. Potential anchor (verify): `DialogCell` layout/message preview setup receives last message; gated call should suppress/replace preview and clear all cached state on bind.
131. Prefer central helper `TeleHooks.ignoredMessage(account, messageObject)` returning a small enum such as NORMAL/HIDE/FADE.
132. A fade must affect message text/media consistently and not intercept taps in a misleading way.
133. A hide must preserve spacing semantics where possible; avoid deleting the underlying `MessageObject` from stock lists.
134. Changing rules refreshes visible cells and dialog list on UI thread without process restart.
135. Ensure mode selection does not collide with stock “blocked” or muted state.
136. Search IDs 1120–1121 should lead to list and mode controls.
137. User-facing feature rows draft appears later in this document.

## 0032 + 0073: per-chat ghost

138. Existing global ghost behavior in Android 0023 network-layer receipts and earlier ghost toggles is foundation; do not fork a second implementation.
139. Store a set of dialog ids whose ghost policy is enabled; account key required.
140. Reuse the same privacy peer picker component, but present a “Ghost chats” title and per-chat state.
141. Define effective ghost as global ghost enabled AND (`per_chat` list empty/all, according to desktop semantics); do not guess whether empty means all or none.
142. [INFERENCE] PATCHLIST says “exceptions and ghost per chats” but not whether list records exceptions to global mode or target chats for override; inspect desktop 0032/0073 before final data contract.
143. Required message domains: online status, typing, read receipts, content-read receipts; global 0023 network hooks should call one `ghostFor(account, dialogId, action)` predicate.
144. Each stock hook receives actual dialog/account context; no lookup through selected account.
145. `MessagesController` / `SendMessagesHelper` are preferred data-layer extension points per AGENTS.
146. Existing contents-read network suppression is Android 0023 in four `readMessageContents` paths per PATCHLIST; extend predicate, not duplicate request suppression.
147. Typing state may be represented in a separate path; verify all current calls before claiming complete coverage.
148. On setting change, cancel/refresh local typing or status state only if existing stock API supports it; do not issue extra privacy-changing network requests without explicit semantics.
149. UI should show per-chat ghost state in picker and an entry point from chat privacy menu if desktop provides it.
150. [INFERENCE] No exact Android menu anchor was accessible; locate `ChatActivity` header/options actions by symbols, avoid editing the giant file in broad context.
151. Every activity/menu row bind checks current account/chat and reflects current value after recycling.
152. Keep ghost chat state separate from ignore state even though they share picker UI.
153. Search IDs 1122–1123 find global/per-chat configuration; reuse global current setting if present.

## 0032 + 0064: ghost schedule and offline-after-send

154. Ghost-schedule toggles special handling when calling `SendMessagesHelper.sendMessage(..., scheduleDate)`; this signature is stated in PATCHLIST, verify current overload.
155. Desktop intent includes schedule trick and restoring offline status after send; batch gate explicitly requires locally visible ghost-scheduled message that later goes out.
156. Sequence: user composes with schedule intent; fork creates local pending state/message representation; no premature server read/typing/status disclosure; at due time hand over to normal Telegram scheduled send path.
157. Exact send mechanism is unresolved until inspect Android queue: determine whether stock scheduled send immediately submits `scheduleDate` or maintains a local schedule queue.
158. [INFERENCE] Never implement “ghost schedule” by simply suppressing `scheduleDate`; that can send immediately and violate user expectation.
159. Preserve the user-visible scheduled date and local pending status; message should appear in the conversation as scheduled/ghost according to 0227 feature layer.
160. Sending/handover uses Telegram API only; no tele-server request.
161. Per-chat ghost applies to its chat; global toggle and per-chat settings combine per desktop behavior.
162. On successful handover, clear local ghost pending state idempotently; on process restart, recover without duplicate send.
163. Failure paths must not silently lose or duplicate a locally queued message; expose retry/error using stock scheduled-message state where possible.
164. Offline-after-send should restore the previous desired online status only after send succeeds, not on enqueue or failure.
165. Use `try/finally`/completion semantics only after proving callbacks reflect actual send result; do not restore status before asynchronous network completion.
166. [INFERENCE] The phrase “offline-after-send” and exact status semantics depend on desktop patch; current Android may not expose a true offline flag.
167. In Android, “offline” may mean restoring `account.updateStatus(offline=true)` behavior; verify current `MessagesController` and ghost implementation, do not invent a toggle that promises OS offline mode.
168. Respect account-specific `ConnectionsManager` and `UserConfig` for all operations.
169. Check background/foreground behavior and process death; do not start a persistent service just to imitate desktop.
170. Search ID 1124 reveals the control and limitations in its description.

## 0166: hidden words and regex

171. Global and per-chat rules; per-chat rules append to global rules as PATCHLIST indicates.
172. Include both literal word and Java-regex semantics; desktop assessment describes `/regex/` and `/regex/i` syntax but exact parsing needs source confirmation.
173. Decision accepts Java regex; document that PCRE-only constructs may not work.
174. Apply to other people’s messages, excluding own, service, and sponsored messages per desktop analysis.
175. Hide matching messages in chat using same visual behavior as ignored peers; replace chat-list preview with empty text.
176. Add “hidden words” editor to privacy settings and per-chat editor item in chat menu.
177. Use shared `TeleHooks.hiddenByWords(MessageObject)`-style predicate, extended with explicit account/dialog parameters to avoid current-account ambiguity.
178. Compile patterns on save; invalid regex display error at exact rule and preserve last valid rules.
179. Cache matching result by stable message/account/rule revision if profiling justifies it; avoid repeated regex compilation in hot rendering path.
180. Avoid unbounded regex catastrophic backtracking if untrusted rules are allowed; rule text is user-authored, still cap input length and report slow matches in debug without content.
181. [INFERENCE] Rule length and count caps are not specified; define modest documented caps only after inspecting desktop implementation, do not silently truncate.
182. Text source should include message text and caption if desktop behavior covers both; verify against desktop patch; do not match hidden fields/media metadata by assumption.
183. `DialogCell` must not leak matched text via name/snippet fallback or reused layout.
184. `ChatMessageCell` uses central filter before display and resets fade/visibility on every bind.
185. A rule update invalidates compiled cache and refreshes loaded cells/dialog list.
186. Search IDs 1125–1126; descriptions explain literal and Java regex.

## 0228: ignored/hidden messages stay silent

187. This feature depends on ignore list and 0166; it must not be implemented earlier as a second filter.
188. Filter `NotificationsController` at new-message notification processing using shared privacy predicate.
189. Also prevent matching items from local notification preview and notification grouping; do not alter server-owned unread count.
190. PATCHLIST says server unread cannot be changed; locally adjust only notification/UI badge presentation where safe.
191. Do not decrement Telegram `TL_dialog.unread_count` or mutate unread updates; doing so risks read-state desynchronization.
192. Mention/reaction buttons should skip ignored/hidden messages where they enumerate candidate messages, not alter server data.
193. Chat preview (`DialogCell`) should show the prior eligible message, up to 512 messages per desktop analysis; limit should be explicit and tested.
194. [INFERENCE] Android stock history loading may not retain 512 candidates in memory; implement a bounded storage query only if current APIs permit and performance is measured.
195. If eligible predecessor is unavailable, show no content rather than leaking hidden text.
196. Keep message count semantics honest: local badge suppression is presentation only, server unread remains unchanged.
197. A visible app may still show unread marker from server count; product text must clarify if that is not fully suppressed.
198. Batch gate requires ignored and hidden words do not send notifications; assert this against notifications and lockscreen previews.
199. Test both global and per-chat rules, users/groups, muted chats, mentions/replies, notification disabled, and account switching.
200. Avoid shared mutable notification list across accounts.
201. Search ID 1127 points to mute option and limitation description.

## 0227: show ghost-scheduled messages

202. Depends on ghost-schedule, per-chat ghost, and ignore list according to PATCHLIST.
203. Render pending ghost-scheduled message locally in chat before handover, with scheduled marker/time and no server id until server assigns one.
204. Use existing local sending-message conventions rather than forge a server `TLRPC.Message` that might be serialized or read as server state.
205. [INFERENCE] Exact local message insertion/removal anchor and temp-id rules require current source inspection.
206. `SendMessagesHelper` is listed as send hook; `ChatActivity` is display hook.
207. Matching ghost/ignore policy should not hide the user's own queued message from themselves; self-message is excluded from hidden words.
208. On handover, map local object to server response once; remove duplicate local row without jumping scroll position.
209. Keep draft and scheduled media attachments intact; avoid copying file payload or reupload unless stock path requires it.
210. On schedule cancel/edit, update local representation and storage; use Telegram-native scheduled UI where available.
211. If app restarts, rehydrate rows from local store in correct account/chat/topic and sort by schedule time.
212. [INFERENCE] PATCHLIST does not define topic support; preserve `topicRootId` when stock API provides it, otherwise document limitation.
213. Scheduled send must use Telegram API and never upload message content to tele infrastructure.
214. Error UI must permit user recovery and avoid indefinite invisible queue.
215. Validate no duplicate sends on retry/process restart.
216. Search ID 1133 should route to the local scheduled message visibility description.

## 0229: invisible stories follow per-chat ghost

217. Reuse Android 0021 invisible-story gate; do not duplicate `INVISIBLE_STORIES` behavior.
218. Effective invisibility is global watch-invisibly setting OR ghost-stories for a ghosted peer, according to desktop summary; confirm exact boolean semantics from patch.
219. `StoriesController.markStoryAsRead` anchor is specified by `desk-3` as line vicinity 1287; verify current path and all overloads.
220. Prevent `TL_stories_readStories` when effective invisibility applies.
221. Preserve local “seen through id” state so story ring does not reappear after restart; analysis describes 48-hour memory.
222. Storage key includes account, peer, max story id, expiry.
223. Confirm story storage reload does not roll back local `max_read_id`; local notes flag this as unverified.
224. Do not modify remote max-read state while invisible; avoid later automatic read request due to cache reconciliation.
225. Before visible reaction or reply that would reveal viewing, show confirmation; user may cancel with no action.
226. User confirmation to proceed must explain the server can reveal the view, then invoke normal action exactly once.
227. For live stories, desktop notes replace hard block with confirmation; do not keep current hard block if the agreed patch behavior says confirm.
228. [INFERENCE] Exact `StoryViewer`/`PeerStoriesView` controls need branch source search before hook.
229. Handle story navigation and recycled story cells with account/peer-specific state.
230. Search ID 1128; help ID 1137 covers local read memory and reveal confirmation.
231. Batch gate: verify invisible story is not marked read and remains so after process kill/cold start.

## 0282: peek at hidden last seen

232. Decision: default OFF; setting description contains a warning; mandatory restore at app startup.
233. This is sensitive and can reveal status contrary to another user’s privacy choice; make the warning explicit and require deliberate opt-in.
234. PATCHLIST points to `ContactsController`, `ProfileActivity`, `TeleDatabaseHelper`.
235. Do not guess or fabricate a Telegram endpoint; inspect desktop patch and current TL definitions, never edit generated TLRPC.
236. The intended “swap” behavior should be understood from desktop patch: potentially temporarily alter own privacy rule to inspect status, then restore. Confirm exact mechanism before implementation.
237. [INFERENCE] The feature name “peek at hidden last seen” does not itself establish safe/allowed server semantics; implementation could expose the user’s own last seen and must document that risk.
238. Before sending any request, durably store original privacy rule and pending-restore marker for that account.
239. If storage write fails, do not change privacy rule.
240. On completion, error, cancellation, network loss, or process restart, attempt restoration and keep marker until server confirms restore.
241. Startup restore runs before normal status/privacy updates can supersede the saved rule.
242. Serialize per-account swaps; prevent concurrent attempts from overwriting original state.
243. Handle account logout/removal without restoring another account’s rule; retain or clear orphaned state through explicit safe policy.
244. Expose progress/failure state and never claim restored until acknowledged.
245. Consider server flood wait; do not bypass stock rate limits or retry aggressively.
246. Do not log privacy rule contents, peer ids, or last-seen values.
247. Test kill process between save/change/restore phases and reboot/force-stop cold start.
248. Search ID 1129 and help 1138; warning visible in setting description and confirmation.
249. `[INFERENCE]` Exact UX confirmation modality, API calls, restore acknowledgement, and conflict policy are unresolved in docs; ask maintainer or derive only from desktop patch/code.

## 0160: streamer mode

250. Decision: independent of 0113 never-block-screenshots and 0172 hide-phone patch; do not add dependency rows.
251. Android scope: secure screen capture, notification previews, phone numbers; desktop window title/tray have no Android equivalent.
252. `FLAG_SECURE` is per-window; AGENTS warns to audit PhotoViewer, secret chats, stories and any window setting it.
253. Potential anchors from desktop analysis: `FlagSecureReason`, `NotificationsController`, `DrawerProfileCell`, `ProfileActivity`; verify actual current source before edit.
254. Streamer ON should add secure reason, not overwrite stock secure reasons.
255. Existing “never block screenshots” interaction is unresolved in portability analysis; decision says independent, so do not assume precedence. Ask maintainer or retain composable independent reasons and make behavior explicit.
256. If 0113 globally removes `FLAG_SECURE`, whether streamer may re-add it is a product decision; never silently defeat either option.
257. Notification content suppression should apply to all new notifications and already posted notifications when mode toggles on.
258. Do not mutate stock notification preferences; derive effective preview policy at build/update time.
259. Phone hiding covers profile phone row and account/drawer display only where currently rendered; no window title exists.
260. Do not conflate hide phone with hiding account identity in unrelated screens unless explicitly specified.
261. Toggling off must restore prior stock behavior and flags for every active window.
262. Window lifecycle must recalculate on resume/recreate; secure state cannot be cached only at application launch.
263. Do not leak preview in notification shade, lockscreen, wear/connected device if stock API allows suppression; verify platform behavior.
264. Recycled drawer/profile cells must clear placeholder and show stock phone when disabled.
265. Search ID 1130 and help ID 1139; optional child toggles only if maintainer accepts independent controls.
266. No network usage.

## UX strings and endpoints/limits

267. Settings and picker UX should use native Android navigation and stock dialogs/RecyclerListView patterns.
268. Ignore list: “Ignored peers”; item action adds/removes locally; modes explicitly labeled “Hide” and “Dim” if both are supported.
269. Ghost list: “Ghost chats”; selection indicates where existing global ghost rules apply.
270. Hidden words editor: global multiline editor with rule rows and syntax errors; per-chat editor opened from chat menu.
271. Silent ignored: one explanatory toggle; it affects notification presentation, not server unread state.
272. Ghost-scheduled row is visibly local/pending and shows scheduled time; cancellation/error should use a recoverable UI.
273. Invisible stories: explain no read receipt; warn before reaction/reply/live action reveals viewing.
274. Last-seen swap: warning in description and deliberate confirmation; restore state on every exit and app cold start.
275. Streamer: setting toggle and, if requested, convenient quick toggle in existing settings; no Android window-title behavior.
276. Do not invent a tele-server endpoint for any batch feature.
277. Telegram API endpoints are whatever stock current code already uses; verify request types from branch source.
278. Story `readStories` suppression is the explicit endpoint behavior in existing analysis; no extra tele network.
279. Last-seen update endpoint is unresolved until inspection; no guessed method names in implementation.
280. Limits explicitly evidenced: 0228 predecessor scan up to 512 messages; 0229 remembered reads 48 hours in desktop assessment; other caps require desktop source confirmation.
281. No silent hard-coded cap on users/rules unless required by source and shown in UX.
282. All local data and matching remain on-device.

## Threading, per-account, recycling, performance

283. Settings clicks and visible view updates run on main thread.
284. Storage reads/writes use TeleDatabaseHelper queue; callbacks hop with `AndroidUtilities.runOnUIThread` before updating UI.
285. Regex compilation and bulk filtering must not run on main for long histories; cache immutable compiled rule snapshots.
286. Keep account id in every helper signature; avoid static state that can bleed between accounts.
287. In-flight callbacks validate account and fragment lifecycle before touching UI.
288. On account switch, clear old rules from view cache before rebinding the new account.
289. Adapter/cell bind always recomputes hide/fade/preview state and resets recycled properties.
290. Changing a setting invalidates only affected account/chat caches, then notifies visible UI.
291. No new animation needed; if any transition added, obey `LiteMode`/performance class.
292. Large peer lists use stable ids/diff updates rather than full repeated network loading.
293. Never do synchronous DB access in `DialogCell`/`ChatMessageCell` hot path.
294. Privacy decision helper should be O(1) membership for peer ids and bounded pattern count.
295. If patterns are expensive, evaluate in message processing and cache result; never hold a lock during regex match.
296. Storage corruption must fail closed only for explicit enabled feature without hiding unrelated stock content; notify user and preserve backup.

## `features.md` draft rows

297. These are English draft descriptions; add only after corresponding user-visible patch is implemented/exported.
298. Place each row under the privacy section that owns the actual toggle.
299. Patch file must be the real generated Android filename after export; placeholders are intentionally not asserted as final numbers.
300. Desktop source numbers in parentheses use current desktop numbering.

| Feature | Draft user sentence | Where | Default | Android patch | Desktop |
|---|---|---|---|---|---|
| Ignored peers | Hide or dim messages from peers you choose, only on this device. | Privacy → Ignored peers | Off | generated after export | 0016, 0073 |
| Per-chat ghost | Apply ghost-mode privacy rules only to selected chats. | Privacy → Ghost mode | Off | generated after export | 0032, 0073 |
| Ghost schedule | Keep scheduled-message privacy handling local until the message is handed to Telegram. | Privacy → Ghost mode | Off | generated after export | 0032, 0064 |
| Hidden words | Hide messages matching your global or chat-specific words and Java regular expressions. | Privacy → Hidden words | Off | generated after export | 0166 |
| Mute ignored/hidden | Do not notify about messages hidden by your ignore list or word rules; server unread counts are unchanged. | Privacy → Notifications | Off | generated after export | 0228 |
| Ghost scheduled display | Show your locally queued ghost-scheduled messages in the chat until they are sent. | Privacy → Ghost mode | Off | generated after export | 0227 |
| Invisible stories | Keep story reads local in ghost chats and ask before actions that reveal your view. | Privacy → Stories | Off | generated after export | 0229 |
| Last-seen swap | Temporarily inspect last-seen visibility and restore your privacy rule after use and on startup. | Privacy → Last seen | Off | generated after export | 0282 |
| Streamer mode | Hide screen contents from capture and notification previews, and hide phone numbers where shown. | Privacy → Streamer mode | Off | generated after export | 0160 |

301. If privacy page grouping differs after settings restructure, keep location consistent with current `TeleSettingsActivity`, do not create a new section casually.
302. Each feature row goes in same commit/export change as its patch per AGENTS.

## Pitfalls / explicit unresolved decisions

303. Do not reuse `PrivacyUsersActivity`: it edits Telegram block state, not local ignore state.
304. Do not alter stock DB schema or generated TLRPC.
305. Do not treat ignored/hidden message as read or deleted.
306. Do not claim unread counters are server-corrected; server unread is immutable here.
307. Do not send private configuration or message content to tele server.
308. Do not use `currentAccount` singleton implicitly from background work; pass account explicitly.
309. Do not use adapter position as durable message key; messages move and recycle.
310. Do not apply story `max_read_id` update remotely as a side effect of local visibility.
311. Do not let visible reaction/reply silently reveal an invisible story.
312. Do not let last-seen swap survive process death without a durable restoration marker.
313. Do not overwrite stock secure-window reasons when streamer toggles.
314. Do not silently choose precedence between streamer and never-block-screenshots; unresolved Q.
315. Do not assume ghost exception list semantics (allowlist vs blocklist); verify desktop source.
316. Do not assume ignored peer set includes groups/channels the same way as users; verify desktop source.
317. Do not assume `sendMessage(... scheduleDate)` is a local scheduler; inspect current stock implementation.
318. Do not assert all services / reactions / typing are ghosted until each actual network call site is audited.
319. Do not claim stories survive restart until `storiesStorage` interaction is manually tested.
320. Do not add behavior to global story toggle 0021 already covered by Android 0021.
321. Decisions to obtain or settle from desktop source/maintainer before coding: 0160 precedence, 0282 exact API and confirmation, 0016 hide-vs-fade state, 0032 list semantics, 0229 48h retention and live-story confirmation.
322. Unresolved export policy: whether peer lists and hidden-word text are included in settings backup.
323. Unresolved last-seen restore failure UX: persistent warning and retry strategy after network/auth failure.
324. Unresolved ignore of group peer: hide group messages versus individual sender; must match desktop semantics.
325. All of these are explicit blockers to final behavior where applicable; do not guess and label as done.

## On/off test plan and logcat

326. Use a secondary account/test chat; privacy and last-seen tests can affect real contacts.
327. Exercise every toggle both OFF and ON; default installation state is OFF.
328. For each feature, verify switching OFF restores stock behavior without process restart where practical.
329. Logcat must not contain message text, regex contents, usernames, phone numbers, peer ids, story ids, or last-seen data.
330. Suggested tags for temporary debug-only diagnostics: `TelePrivacyIgnore`, `TeleGhost`, `TeleHiddenWords`, `TeleGhostSchedule`, `TeleStories`, `TeleLastSeen`, `TeleStreamer`.
331. Remove verbose logs or keep only non-sensitive debug state before export.

332. Ignore list OFF: messages and previews match stock exactly; ON hide: selected sender’s messages disappear in chat/list; other senders unaffected.
333. Ignore list ON fade: all message content remains readable enough per design, visual opacity resets on recycling; stock block list is unchanged.
334. Ignore list add/remove persists after process kill and is isolated across accounts.
335. Picker does not issue block/unblock API calls; no tele network calls.
336. Ghost global OFF: receipt/typing/online behavior matches stock; ON with no per-chat selection matches existing batch-2 behavior.
337. Per-chat ghost ON for chat A: receipts/typing/online suppressed only for A; chat B retains normal behavior; switch account and verify isolation.
338. Ghost contents-read sends no `readMessageContents` from selected chat through any existing four paths; control chat still does.
339. Ghost schedule: queue message, verify it is not sent early, local pending state persists after restart, and due handover sends exactly once.
340. Ghost schedule failure: disconnect/network error does not lose message or duplicate it on retry; restore online state only after successful send if semantics require it.
341. Hidden words OFF: matching content is visible and notifications remain stock; ON: literal and regex samples hide globally and per-chat as configured.
342. Hidden words test invalid regex, case-sensitive/case-insensitive forms, Unicode, empty rule, malformed slash syntax, and editing while old messages are loaded.
343. Hidden words excludes own/service/sponsored messages; test text and caption only if source behavior includes caption.
344. Silent ignored/hidden: no notification tone/banner/content for matching incoming messages; nonmatching notification normal.
345. Silent ignored does not mutate server unread count; explicitly compare after reconnect and another device.
346. Preview fallback examines eligible earlier messages up to 512 candidates where available; unavailable older content does not expose hidden text.
347. Ghost-scheduled display shows local row and scheduled time, reconciles to server row once, no duplicates after process restart.
348. Invisible stories: watch without server `TL_stories_readStories`, ring/local seen state remains correct after restart, ordinary stories still mark read when OFF.
349. Invisible story reaction/reply and live story: cancel means no request; confirm means normal action and visible warning; ensure no double-send.
350. Last-seen swap OFF does nothing; ON displays warning and confirms; kill process at each step and confirm original privacy restored before normal app behavior.
351. Last-seen error/network loss: pending restore is retained and user sees truthful failure; no false “restored” indicator.
352. Streamer ON hides sensitive notification preview, protects applicable windows according to agreed precedence, hides phone row; OFF restores stock values.
353. Streamer test each window independently: chat, profile, photo viewer, secret chat, story, Recents; validate interaction with 0113.
354. Test app process killed/restarted and account switched during each persistent/privacy flow.
355. Build and human gate must happen only after all patches exported; this guide does not claim a build was run.

## Batch gate and handoff

356. `todo` → `wip` when implementation starts; do not mark queued before commit and export.
357. Each patch is one Telegram-tree commit, exported via documented `git format-patch` command; never edit `.patch` by hand.
358. Update PATCHLIST statuses and notes only when actual state changes.
359. Add features.md row with true Android patch filename in the same repository change as export.
360. Once all nine patches are committed and exported, run the batch debug build per `docs/development.md` and hand the APK to a human.
361. Batch gate acceptance checklist is the exact PATCHLIST wording: ignored list hides/dims in chat and list; picker resembles privacy; per-chat ghost; ghost-scheduled visible locally and sent; hidden words and ignore send no notifications; invisible stories not marked read; last seen restored after process kill/cold start; streamer does not expose content.
362. Add negative checks: global/off settings match stock; multiple accounts stay isolated; no network upload of private data; server unread remains unchanged.
363. Human must exercise the device flows; compilation alone does not close the batch.
364. Only after human verification mark batch status `done`; before then status is `built` at most.
365. Record unresolved questions and limitations in PATCHLIST/decision thread; do not hide them in a successful gate claim.
366. This guide is complete as a plan, but implementation must still verify all `[INFERENCE]` anchors against branch `tele` and exact desktop patch sources.
