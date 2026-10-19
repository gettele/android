# Пачка 11: инструкция реализации для Android

## Назначение документа

1. Этот документ — рабочее руководство для реализации пачки 11 в ветке `tele`.
2. Изменять нужно только checkout Android `../Telegram`, затем экспортировать коммиты в очередь.
3. Этот файл не является патчем и не заменяет `docs/PATCHLIST.md`.
4. Пачка объединяет пять follow-up к уже перенесённым фичам и семь новых мелких тумблеров.
5. Всего в таблице ниже двенадцать строк.
6. Desktop-номера указаны по текущей очереди `origin/main`, а не по старой нумерации.
7. Бывший desktop 0043 входит в текущий 0017.
8. Бывшие desktop 0078 и 0079 входят в текущий 0077.
9. Текущая строка 0253 является follow-up к Android 0025.
10. `[INFERENCE]` означает место, которое следует подтвердить чтением текущего Android-кода или ручным тестом.
11. Нельзя выдавать inference за проверенный hook.
12. Объём пачки по плану: `S×10, M×2`.
13. Реализация должна оставаться минимальным gated-hunk в stock-файлах.
14. Fork-код обязан жить в новых файлах пакета `tele`.
15. `TLRPC.java` и stock-схему базы менять запрещено.
16. Все новые пользовательские строки идут в `strings_tele.xml`.
17. Все переключатели входят в `TeleConfig` и имеют default `false`.
18. Исключения составляют уже существующие переключатели, которые остаются с прежним согласованным default.
19. Follow-up не должен менять поведение, если родительский переключатель выключен.
20. Отключённая пачка должна быть неотличима от stock.

## Источники и зафиксированные решения

21. Прочитаны `AGENTS.md`, `PATCHLIST.md`, `decisions.md`, `portability.md`, `desktop-numbers.md`, `architecture.md` и `development.md`.
22. Прочитаны рабочие срезы `local://desk-0125-0164.md` и `local://desk-delta.md`.
23. Desktop-патчи прочитаны из `origin/main:patches/tdesktop/*` через `git show`.
24. Android anchors проверены на ветке `tele` через `git show`.
25. Desktop 0017 теперь включает текст времени у service messages.
26. Формат строки: исходный action-текст, затем ` · HH:mm:ss`.
27. Формат зависит от 12/24-часового `formatterDay`.
28. Desktop 0077 включает редактор правил и presets.
29. Устаревшая цель `vxtiktok.com` должна мигрировать в `tnktok.com`.
30. Preset TikTok оставляет только `tnktok.com`.
31. Preset X добавляет `samekosabax.com`.
32. Regex очистки tracking для X/Twitter также знает `samekosabax.com`.
33. Desktop 0095 требует повторов для `FLOOD_WAIT` и `SLOWMODE_WAIT`.
34. Сетевые и timeout-ошибки получают лестницу `5 s / 15 s / 1 min / 5 min / 15 min`.
35. Максимум попыток одного scheduled message — пять.
36. По окончании попыток появляется уведомление и toast.
37. Desktop 0006 требует resume загрузки через `.part` и HTTP `Range`.
38. Ответ `206` обязан подтвердить ожидаемый `Content-Range`.
39. Ответ `200` при resume означает truncation и повтор с нуля.
40. Ответ `416` при ненулевом локальном размере допускает немедленную проверку SHA-256.
41. Сетевые ошибки updater повторяются через `1 / 5 / 15 / 60 min`.
42. Desktop 0253 копирует plain digits в Bot API-виде независимо от визуального формата строки.
43. Решение мейнтейнера: тумблеры Android по умолчанию выключены.
44. Решение мейнтейнера: 0172 скрывает только phone row профиля.
45. Решение мейнтейнера: 0154 использует сохранение и восстановление Lite Mode.
46. Для новых строк features.md нужен английский текст и ссылка на desktop номер.
47. Для текущей пачки не следует добавлять в Android работу desktop-only 0135 и 0136.
48. В пачке 11 нет сетевого tele-сервера для новых функций.
49. Telegram API остаётся единственным сетевым каналом scheduled-отправки.
50. Updater использует только разрешённый GitHub releases URL.

## Состав пачки и commits

51. В таблице `commit` указано имя desktop commit, а рядом — ожидаемое имя Android commit.
52. Экспортированный Android patch получает номер очереди только после фактического коммита.
53. Не редактировать `.patch` вручную.
54. Каждая строка должна стать отдельным commit в Telegram checkout.
55. Следовать формату commit subject из `AGENTS.md`: lowercase, imperative, одна строка.

| Desktop № | Desktop commit | Android commit / область | Effort | Зависимость |
|---|---|---|---|---|
| 0017 (follow-up) | `feat: show seconds in message times` | `fix: show times on service messages`; `MessageObject`/`TeleHooks` | S | Android 0008 |
| 0077 (follow-up) | `feat: rewrite pasted links with your own rules` | `fix: refresh link rewrite presets`; `LinkRewrites`/`Tracking` | S | Android 0051/0052 |
| 0095 (follow-up) | `feat: send scheduled messages on time` | `fix: retry punctual scheduled messages`; `PunctualScheduled` | M | Android 0064 |
| 0006 (follow-up) | `feat: update from the tele github releases` | `fix: resume tele updates`; `TeleUpdater` | M | Android 0086 |
| 0253 (follow-up) | `fix: copy peer ids as plain digits` | `fix: copy peer ids as plain digits`; `PeerId`/ProfileActivity | S | Android 0025 |
| 0125 | `feat: hide the gift button in the message field` | `feat: hide the gift button`; input and channel buttons | S | — |
| 0132 | `feat: hide similar channels` | `feat: hide similar channels`; recommendations/profile | S | — |
| 0143 | `feat: hide the collectible status tooltip in profiles` | `feat: hide collectible status tooltip`; ProfileActivity | S | — |
| 0154 | `feat: reduce motion` | `feat: reduce motion`; LiteMode bridge | S | LiteMode |
| 0172 | `feat: hide phone numbers in profiles` | `feat: hide phone numbers in profiles`; ProfileActivity | S | Android 0075 optional |
| 0233 | `feat: no edited mark on bot messages` | `feat: hide edited mark on bot messages`; ChatMessageCell | S | — |
| 0231 | `feat: show the start parameter on the start button` | `feat: show bot start parameter`; ChatActivity | S | bot info |

## Карта TeleConfig и search IDs 1100–1119

56. Search IDs ниже являются стабильными идентификаторами записей поиска пачки.
57. Они не являются Telegram dialog id и не должны попадать в сеть.
58. При реализации использовать существующий тип registry в `TeleSearch`.
59. В каждой записи хранить ключ настройки, заголовок, описание, страницу и keywords.
60. Для follow-up использовать существующий item, а не второй item с тем же pref key.
61. Если текущий item отсутствует, добавить его в `TeleConfig` с default `false`.
62. `Item.getValue()` использовать из Java; не обращаться к внутреннему `.value` из новых Java hooks.
63. IDs 1100–1119 должны покрыть и основной тумблер, и доступные под-тумблеры.

| Search ID | TeleConfig item / запись | Страница | Default | Keywords |
|---:|---|---|---|---|
| 1100 | `SHOW_SECONDS` (service-message extension) | interface | false | seconds, service messages, joins, pins |
| 1101 | `REWRITE_PASTED_LINKS` | links | false | rewrite, pasted links, URL, TikTok |
| 1102 | `PUNCTUAL_SCHEDULED` | sending | false | scheduled, punctual, retry, flood wait |
| 1103 | `AUTO_UPDATE` (resume/retry extension) | updates | existing approved default | update, GitHub, download, resume |
| 1104 | `BOT_API_PEER_IDS` / copy plain digits | ids | false | peer id, bot API, digits, copy |
| 1105 | `HIDE_GIFT_BUTTON` | sending | false | gift, premium, message field |
| 1106 | `HIDE_SIMILAR` | chats | false | similar, recommended, channels |
| 1107 | `HIDE_SIMILAR_JOIN` | chats | false | after joining, recommendations |
| 1108 | `HIDE_SIMILAR_PROFILE` | chats | false | profile, recommended channels |
| 1109 | `NO_COLLECTIBLE_TOOLTIP` | ids | false | collectible, status, tooltip, gift |
| 1110 | `REDUCE_MOTION` | interface | false | animations, Lite Mode, battery |
| 1111 | `HIDE_PHONE_IN_PROFILE` | profiles and ids | false | phone, number, profile, privacy |
| 1112 | `HIDE_BOT_EDITED` | interface | false | edited, bot, modified |
| 1113 | `SHOW_START_PARAM` | bots | false | start, parameter, bot, deep link |
| 1114 | service time search alias | interface | false | service, time, action message |
| 1115 | updater resume search alias | updates | existing approved default | partial, Range, `.part` |
| 1116 | scheduled retry search alias | sending | false | timeout, retry, flood, slowmode |
| 1117 | link migration search alias | links | false | vxtiktok, tnktok, samekosabax |
| 1118 | peer copy search alias | ids | false | plain, unformatted, clipboard |
| 1119 | bot message display search alias | interface | false | bot messages, no edited badge |

64. Alias records 1114–1119 must point at an existing item or detail page.
65. Они не должны создавать дублирующий переключатель.
66. Если текущая реализация поиска не поддерживает aliases, добавить только записи в существующий массив поиска.
67. Не менять формат IDs, уже занятых чужими страницами.
68. Все новые названия и описания должны быть в `strings_tele.xml` с префиксом `Tele`.
69. Не менять stock `strings.xml`.
70. Английский базовый текст нужен для features.md; UI locale может перевести его позднее.

## Общий порядок реализации

71. Сначала обновить/добавить `TeleConfig` items и экспортный spec.
72. Затем добавить helper в `tele/helpers/`, если логика больше одного stock call site.
73. В stock-файле оставить только импорт `tele` и маленький gated call.
74. Применять настройку через `TeleHooks.onConfigChanged` без рестарта.
75. Пересчитывать UI на main thread.
76. Для фоновых ответов использовать `AndroidUtilities.runOnUIThread`.
77. Для аккаунтных данных передавать `currentAccount` или `account` явно.
78. Не брать молча `MessagesController.getInstance(0)`.
79. Уведомления пачки не переиспользуют stock notification channel, если создаётся новый вид уведомления.
80. Для обновлений и scheduled errors использовать отдельный `tele` channel id.
81. Все RecyclerView/ListView состояния применять в bind, а не только в holder creation.
82. При изменении настройки обновлять уже созданные cells и rows.
83. В `LiteMode` не запускать новую анимацию поверх ограничений.
84. Проверять nullable TL-поля перед доступом.
85. Не дублировать stock алгоритм, если достаточно public extension point.

## Follow-up 0017: время service messages

86. Существующий `SHOW_SECONDS` уже меняет formatter в `TeleHooks.secondsFormatterFormat`.
87. Текущая реализация Android 0008 сама по себе не меняет action-текст service message.
88. Добавить helper `TeleHooks.withServiceTime` или отдельный `ServiceTime.kt` в `tele/helpers`.
89. Вход helper: `MessageObject`, исходный action-текст и account-independent formatter.
90. Гейт должен быть первым: `if (!TeleConfig.SHOW_SECONDS.getValue()) return original`.
91. Гейт также должен исключать не-service messages.
92. Время брать из `messageOwner.date`.
93. Форматировать тем же `formatterDay`/formatter, который использует SHOW_SECONDS.
94. Результат должен быть `text + " · " + HH:mm:ss`.
95. Не добавлять суффикс дважды при повторной генерации layout.
96. Лучше держать исходный текст отдельно и формировать display text заново.
97. Не менять серверное поле `messageOwner.message`.
98. Не отправлять суффикс обратно в Telegram.
99. Учитывать центрированные service cells и строки в chat list.
100. Desktop anchor: `Tele::WithServiceTime` вызывается при `setTextWithLinks`.
101. Android anchor: `MessageObject.messageText`/`generateLayout` и `ChatActionCell`.
102. `[INFERENCE]` Точная Android точка зависит от текущей генерации action текста.
103. Найти `TL_messageService`, `isService`, `messageText`, `generateLayout` через `rg`.
104. Не читать `ChatMessageCell.java` целиком; открыть локальные окна вокруг символов.
105. При смене toggle вызвать существующий `LocaleController.recreateFormatters()`.
106. Затем послать `messagesDidLoad` для всех account instances, как делает текущий hook.
107. На main thread обновить видимые ChatActionCell.
108. UX title: `Show seconds in message times`.
109. UX description: `Service messages like joins and pins also show their time.`
110. Строка должна совпадать по смыслу с desktop commit.
111. Лимит service text не менять.
112. Privacy: время локально вычисляется, сетевых запросов нет.
113. Per-account: formatter — глобальный locale, сообщение — account-specific.
114. Recycling: action cell bind обязан получать исходный текст заново.
115. On test: включить seconds и открыть join, pin, title-change, photo-service messages.
116. Off test: сравнить текст с stock и проверить отсутствие ` · `.
117. Logcat tag: `TeleServiceTime` только на debug-level при необходимости.
118. Не оставлять постоянный verbose logging.

## Follow-up 0077: миграция link rewrite presets

119. Текущий Android anchor — `tele/helpers/LinkRewrites.kt`.
120. `rules()` читает JSON из `TeleDatabaseHelper` key `link_rewrite_rules`.
121. `presets()` сейчас содержит X, Instagram, TikTok, Reddit, Bluesky и Pixiv.
122. В `presets()` заменить TikTok targets на ровно `listOf("tnktok.com")`.
123. В X targets добавить `samekosabax.com` после существующих targets.
124. Порядок targets сохранять стабильным для random selection.
125. В `rules()` нормализовать `to` при чтении persisted JSON.
126. Замена должна быть case-insensitive по domain, но не менять произвольный путь.
127. `vxtiktok.com` заменить на `tnktok.com`.
128. После замены удалить дублирующиеся targets, сохранив первое вхождение.
129. Не перезаписывать JSON, пока пользователь не сохранит правила, если текущий storage read-only.
130. Либо выполнить однократную idempotent migration при чтении и сохранить через `TeleDatabaseHelper`.
131. Выбранный способ записать в implementation notes commit.
132. `[INFERENCE]` Точка сохранения миграции не зафиксирована текущим кодом.
133. `applyToText` уже гейтирует `REWRITE_PASTED_LINKS`.
134. Не запускать rewrite для feature-off.
135. Existing toast listing changes должен остаться и показывать фактическую замену.
136. `Tracking.kt` добавить `samekosabax\.com` в X/Twitter tracking regex.
137. Не отправлять ссылку на сторонний tele-server.
138. User UX: `Rewrite pasted links by rules` и editor `Rewrite rules`.
139. Preset labels: `X/Twitter`, `TikTok`, `Instagram`, `Reddit`, `Bluesky`, `Pixiv`.
140. Текст миграции пользователю не показывать как network warning.
141. Limits: текущий toast ограничен максимумом трёх change notes; сохранить этот предел.
142. Per-account: `TeleDatabaseHelper` должен выбирать текущий account так же, как существующие rules.
143. Не держать глобальный mutable rule list между аккаунтами.
144. Threading: JSON read/write на db queue; UI preset menu на main.
145. Recycler: editor rows bind enabled state и targets после миграции.
146. On test: вставить URL с `vxtiktok.com`, проверить `tnktok.com`.
147. On test: загрузить старый JSON с двумя одинаковыми targets и проверить dedupe.
148. On test: preset X содержит `samekosabax.com`.
149. On test: pasted X tracking parameter очищается по regex.
150. Off test: вставка URL остаётся неизменной.
151. Logcat tag: `TeleLinkRewrites`; не логировать приватные URL целиком.

## Follow-up 0095: scheduled retries

152. Текущий Android anchor — `tele/helpers/PunctualScheduled.kt`.
153. Сейчас `INTERVAL_MS = 20_000L` и callback `sendRequest(request) { _, _ -> }` игнорирует ошибку.
154. Удалить silent callback semantics, сохранив Telegram request.
155. Состояние попытки ключевать `(account, dialogId, mid)`.
156. Для каждой записи хранить `failures`, `retryAt`, `terminal`.
157. Не использовать один глобальный counter для всех аккаунтов.
158. Групповой request может содержать несколько ids, но ошибка должна быть сопоставлена группе.
159. `[INFERENCE]` Декомпозиция ответа по id зависит от TL API; не дробить пачку при неповторяемой ошибке.
160. Для `FLOOD_WAIT_N` ждать `N + 1` секунд.
161. Для `SLOWMODE_WAIT_N` ждать `N + 1` секунд.
162. Для code `<= 0`, code `>= 500` или text `TIMEOUT` применить ladder.
163. Ladder: `5 s`, `15 s`, `60 s`, `300 s`, `900 s`.
164. После пяти попыток считать message terminal.
165. Не возвращать terminal message в каждые 20 секунд.
166. При успехе удалить attempt state.
167. При terminal failure сохранить suppressed state до следующего scheduled date cycle.
168. Текст уведомления: `Couldn't send a scheduled message on time: <reason>`.
169. Toast должен показываться на UI thread.
170. Notification channel: собственный `tele_scheduled`.
171. Notification intent должен открыть нужный account/chat/message.
172. Не включать сообщение Telegram в tele-server запрос.
173. Пункт `send scheduled messages on time` default off.
174. Description уточняет: работает пока tele online/open, как desktop UX.
175. Архивные чаты нужно сканировать при sweep.
176. `[INFERENCE]` Текущая `due` выборка может не загружать archive автоматически.
177. Проверить `MessagesController`/`MessagesStorage` query для archive before changing it.
178. Не менять stock scheduled date.
179. Threading: storage scan background, `sendRequest` Telegram queue, state lock один.
180. UI toast только через `AndroidUtilities.runOnUIThread`.
181. Per-account request через `ConnectionsManager.getInstance(account)`.
182. Не использовать `UserConfig.selectedAccount` для отправки.
183. On test: force due message, fake `FLOOD_WAIT_2`, убедиться в retry не раньше 3 s.
184. On test: пять retry failures дают один toast и одно notification.
185. On test: timeout после 5 retries не повторяется каждые 20 s.
186. Off test: stock scheduled message path unchanged.
187. Logcat: `TelePunctual` fields account/dialog/mid, но не message body.

## Follow-up 0006: updater resume

188. Текущий Android anchor — `tele/helpers/TeleUpdater.kt`.
189. Feed URL: `https://github.com/gettele/android/releases/latest/download/tele-update-android.json`.
190. Download prefix: `https://github.com/gettele/android/releases/download/`.
191. Feed fields: `tag`, `base`, `counter`, `url`, `apk_sha256`.
192. Проверять URL prefix и `.apk` suffix до начала загрузки.
193. Temporary path: `files/cache/tele_update/tele-<tag>.apk.part`.
194. При network IOException оставить `.part` на диске.
195. Перед повтором получить `offset = part.length()`.
196. Если offset > 0, отправить `Range: bytes=<offset>-`.
197. При `206` принять только `Content-Range` с тем же start offset.
198. При некорректном `Content-Range` удалить или truncate `.part` и повторить с нуля.
199. При `200` на resume открыть output с truncate.
200. При `416` и offset > 0 вычислить SHA-256 текущего `.part`.
201. При совпадении переименовать `.part` в final APK.
202. При несовпадении удалить `.part` и выполнить чистую загрузку.
203. SHA-256 вычислять на готовом файле, не по status-ready bytes.
204. При mismatch feed hash удалить temp и показывать failure.
205. Не устанавливать APK до hash match.
206. Прогресс: `offset + ready` из текущего HTTP body.
207. Total для 206: `offset + Content-Range total`, если известен.
208. Limit сохранить `MAX_APK_SIZE = 512 MiB` из текущего helper.
209. Feed size limit сохранить `64 KiB`.
210. Timeout оставить 60 s на запрос, если нет причины изменить.
211. Retry counter отдельно для сетевых failures.
212. Сетевой failure schedule: 1, 5, 15, 60 минут.
213. Успех и non-network error сбрасывают network retry counter.
214. Проверка по умолчанию после старта 15 s, обычный interval 3 h.
215. Local build без `TELE_BUILD` не обновлять.
216. `AUTO_UPDATE` остаётся текущим approved default, не превращать его в false.
217. Threading: весь file IO и HTTP на `DispatchQueue("teleUpdater")`.
218. UI status и progress публиковать через текущий listener mechanism.
219. Не читать и не писать `.part` на main thread.
220. При уничтожении процесса `.part` должен быть валиден для следующего запуска.
221. Пересечение account не применяется: updater общий для APK, не per-account.
222. Privacy: URL, hash и progress не содержат id аккаунта, username или сообщений.
223. On test: оборвать скачивание после известного offset и повторить с сохранённым `.part`.
224. On test: серверный `200` при Range даёт чистый restart.
225. On test: корректный `206` продолжает и итоговый SHA совпадает.
226. On test: искусственный `416` с полным part принимает файл только после SHA.
227. On test: повреждённый part удаляется, а не устанавливается.
228. Off test: `AUTO_UPDATE` false не делает feed request.
229. Logcat: `TeleUpdater` state/offset/status code, без URL query и пользовательских данных.
230. Не использовать endpoint кроме feed и URL, разрешённых текущим helper.

## Follow-up 0253: plain peer ID

231. Текущий Android anchor — `tele/helpers/PeerId.kt` и copy action в `ProfileActivity.java`.
232. `rowText(account, userId, chatId)` предназначен для отображения.
233. `rowText` может содержать разделители разрядов и suffix `(DC…)`.
234. Copy action не должен использовать `rowText`.
235. Добавить публичный helper `copyText(account, userId, chatId)`.
236. `copyText` возвращает `botApiAdjusted(...).toString()` без пробелов.
237. Для user возвращается user id.
238. Для basic group возвращается chat id по существующей формуле.
239. Для channel/supergroup при включённом Bot API mode сохраняется `-100…` форма.
240. `[INFERENCE]` Называние `copyText` и точная сигнатура — предложение guide; сохранить существующий naming convention.
241. Не изменять отображение строки профиля.
242. Не зависеть от `PEER_IDS_WITHOUT_SPACES` при копировании.
243. Не зависеть от `SHOW_DC` или `MERGE_ID_DC` при копировании.
244. Clipboard payload — только цифры с возможным ведущим минусом.
245. UX copy label остаётся существующим `Copy`.
246. Search keywords: `peer id`, `copy`, `plain digits`, `bot api`.
247. Per-account: `botApiAdjusted` получает account явным аргументом.
248. Threading: copy callback main thread; lookup chat nullable.
249. If chat missing, fallback должен быть текущим `chatId`, без crash.
250. On test: выключить ids-without-spaces и merge-id-dc, скопировать channel.
251. Ожидается plain `-100…` без `(DC…)` и без separators.
252. On test: user/group/channel and account 1.
253. Off test: visual row и прежние profile controls unchanged.
254. Logcat не нужен; не логировать peer IDs.

## 0125: скрыть gift button

255. Настройка: `HIDE_GIFT_BUTTON`, default false, sending page.
256. Personal chat anchor: `ChatActivityEnterView.createGiftButton()`.
257. Второй anchor: `ChatActivityEnterView.updateGiftButton()`.
258. Включённый toggle должен сделать `giftButton` `GONE` или не создать его.
259. Channel anchor: `ChatActivity` calculates `showGiftButton`.
260. Перед `bottomChannelButtonsLayout.showButton(BUTTON_GIFT, …)` проверить toggle.
261. Не скрывать другие channel buttons.
262. Do not touch gift payload or Telegram request.
263. UX title: `Hide the gift button in the message field`.
264. Keywords: `gift`, `premium`, `message field`.
265. `TeleHooks.onConfigChanged` обновляет personal и channel layout.
266. Recycler recycling: если layout reusable, bind обязан повторно применить visibility.
267. Main thread: all View visibility changes only on UI thread.
268. Per-account: use activity currentAccount, not selectedAccount.
269. Privacy: no network and no account data.
270. On test: private chat, channel, bot chat and Saved Messages.
271. On test: toggle on/off while chat remains open.
272. Off test: gift button and its existing click action are stock.
273. Logcat tag optional `TeleGiftButton`.

## 0132: скрыть похожие каналы

274. Parent item `HIDE_SIMILAR`, default false, chats page.
275. Child items `HIDE_SIMILAR_JOIN` and `HIDE_SIMILAR_PROFILE`, default false.
276. Child rows hidden until parent is enabled.
277. Join anchor: `MessageObject` branch creating `TYPE_JOINED_CHANNEL`.
278. If hide-after-join is enabled, do not create/show that recommendation service message.
279. Data anchor: `MessagesController.getChannelRecommendations`.
280. If hide-after-join is enabled, avoid `TL_channels_getChannelRecommendations`.
281. Profile anchor: recommendation block in `ProfileActivity`.
282. Gate both button creation and `hasRecommendations`/visibility result.
283. No empty placeholder should remain in profile.
284. UX parent: `Hide similar channels`.
285. UX child: `After joining` and `In profiles`.
286. Keywords: `similar`, `recommended`, `channels`, `join`, `profile`.
287. Network privacy: disabled query is a Telegram request suppression, not tele-server traffic.
288. Per-account: recommendations use current account controller.
289. Threading: network callback can be background; UI block change on main.
290. Recycler: recommendation cells must reset visibility in bind.
291. On test: join a channel with recommendations available.
292. On test: open channel profile with recommendations.
293. On test: parent on, each child independently on/off.
294. Off test: stock recommendation request and block remain.
295. `[INFERENCE]` Exact Android recommendation message branch must be confirmed against current `tele` checkout.

## 0143: скрыть collectible tooltip

296. Item `NO_COLLECTIBLE_TOOLTIP`, default false, ids page.
297. Anchor: `ProfileActivity.collectibleHint` creation.
298. Secondary anchors: `updateCollectibleHint()` callers.
299. Add early return before creating `HintView2`.
300. Do not hide collectible status row itself.
301. Do not hide regular gift or emoji status data.
302. UX title: `No tooltip for collectible statuses`.
303. Keywords: `collectible`, `status`, `tooltip`, `gift`.
304. On config change remove an already visible hint.
305. Main thread: hint creation/removal only on UI thread.
306. Per-account: profile activity account owns the hint.
307. Recycling: profile header recreation must recheck toggle.
308. On test: collectible username, collectible number and ordinary profile.
309. Off test: existing tooltip appears with stock timing.
310. Logcat not required.

## 0154: reduce motion and LiteMode

311. Item `REDUCE_MOTION`, default false, interface page.
312. This is a bridge to Android `LiteMode`, not a second animation engine.
313. Before enabling, snapshot current LiteMode flags into `tele_kv`.
314. Save whether animated stickers were enabled separately if current LiteMode requires it.
315. Enable all relevant animation restrictions while preserving call animations as stock policy requires.
316. On disable restore saved state, not hard-coded defaults.
317. If user changed LiteMode while reduce motion was active, merge rather than overwrite blindly.
318. `[INFERENCE]` Exact bit mask names must be taken from current `LiteMode` constants.
319. Never start a tele animation that ignores `LiteMode`.
320. Do not persist the snapshot in stock preferences.
321. Use per-account only if current LiteMode storage is account-scoped; otherwise document global scope.
322. `TeleHooks.onConfigChanged` applies immediately.
323. UI setting description must warn that Lite Mode is temporarily changed.
324. UX title: `Reduce motion`.
325. Keywords: `animations`, `battery`, `Lite Mode`, `sticker loops`.
326. On test: animated sticker, animated emoji, reactions, particles and chat transitions.
327. On test: set a custom Lite Mode combination, enable, disable, verify restoration.
328. On test: kill/restart app while enabled; no corrupted snapshot.
329. Off test: all current stock LiteMode behavior remains.
330. Logcat tag `TeleReduceMotion` may report mask transitions, never message data.

## 0172: скрыть телефон в профиле

331. Item `HIDE_PHONE_IN_PROFILE`, default false, profiles and ids page.
332. Anchor: `ProfileActivity.phoneRow` creation.
333. Gate only the phone row, not username, peer id or bio.
334. Do not alter `User.phone` in TL object.
335. Do not replace phone in outgoing contact operations.
336. UX title: `Hide phone numbers in profiles`.
337. Description must say this changes local profile display only.
338. Search keywords: `phone`, `number`, `profile`, `privacy`.
339. On config change rebuild or hide visible row without restart.
340. Main thread: row mutation on UI thread.
341. Per-account: profile `currentAccount` controls visibility.
342. Recycler: if profile rows recycle, bind resets phone visibility.
343. Privacy: no new network request; this is display-only.
344. On test: own profile, contact profile, non-contact profile, bot profile.
345. On test: toggle in an already open profile.
346. Off test: stock phone row and click behavior.
347. `[INFERENCE]` If stock uses a shared phone-row builder, expose it rather than duplicate.

## 0233: убрать edited mark у bot messages

348. Item `HIDE_BOT_EDITED`, default false, interface page.
349. Anchor: `ChatMessageCell` edited-label drawing/measurement.
350. Gate if sender user is bot or message has `via_bot_id`.
351. The desktop predicate is `bot` or `via_bot`.
352. Do not hide edited mark for ordinary human messages.
353. Do not change edit history, message date or message entities.
354. Remove the label from measurement as well as drawing to avoid a blank gap.
355. UX title: `No edited mark on bot messages`.
356. Description: `Bots edit their messages to update them.`
357. Keywords: `edited`, `bot`, `modified`.
358. `ChatMessageCell` is a hot file; use one narrow gated call.
359. Per-account: resolve sender through current account controller.
360. Nullable sender/user must fall back to showing stock mark.
361. Threading: cell bind/draw main thread; never query controller from background draw.
362. Recycling: reset edited visibility for every bind.
363. On test: bot edits, via-bot edits, human edits, forwarded bot message.
364. On test: scroll away and back to exercise recycling.
365. Off test: all edited labels exactly stock.
366. `[INFERENCE]` `via_bot_id` field availability is known from TL objects but exact cell predicate needs verification.

## 0231: parameter on bot Start button

367. Item `SHOW_START_PARAM`, default false, bots page or interface group.
368. Read start token from the bot info already loaded for the current chat.
369. Do not make a new network request for the token.
370. Anchor: `ChatActivity` bot Start button creation/update.
371. Long-press should show the full start parameter in a tooltip.
372. If parameter is non-empty, button text may show an elided parameter.
373. Preserve base `Start` text when parameter is empty or toggle is off.
374. Add `Restart` equivalent only if the current screen has a restart button.
375. UX title: `Show the start parameter`.
376. Description: `On the start button of a bot opened by a link.`
377. Tooltip delay: 500 ms, matching desktop patch.
378. Do not expose token in logcat.
379. Do not send or modify token; the existing Start request remains authoritative.
380. Per-account: use current bot info and current account.
381. Threading: bot info callback may be background; update button on main.
382. Recycling: button bind resets from base text each time.
383. On test: deep link with `start`, empty start, long token, Cyrillic-looking invalid token.
384. On test: toggle while chat is open and after bot info refresh.
385. Off test: exact stock `Start` button and request.
386. `[INFERENCE]` Android button class and bot-info field differ from desktop; verify anchor before editing.

## Хранилище и экспорт/import

387. Boolean items belong in the existing tele config SharedPreferences through `TeleConfig`.
388. Link rewrite JSON remains in `tele_kv` key `link_rewrite_rules`.
389. Scheduled retry state may stay in memory; it must not grow forever.
390. Purge successful and terminal scheduled keys after their date window.
391. Updater `.part` is a cache file, not tele account data.
392. Reduce-motion snapshot belongs in `tele_kv`, not stock LiteMode prefs.
393. No new table is needed for this batch.
394. Export/import spec must include new Boolean settings.
395. Do not export transient retry counters, updater progress or `.part` files.
396. Do not export account identifiers with global settings.
397. Import unknown keys with the existing skip-and-log behavior.
398. Import must preserve default false when a key is absent.
399. Link rule migration must be idempotent across repeated imports.
400. Exported link rules should contain normalized current targets after save.

## Общие privacy, account, thread и recycling проверки

401. Every added network operation has a controlling toggle at the lowest layer.
402. This batch adds no third-party data upload.
403. Updater sends only HTTP request metadata to GitHub.
404. Scheduled request sends only the existing Telegram request.
405. Link rewrite and display features are local.
406. Never log message text, URLs with query parameters, bot tokens, phone numbers or peer IDs.
407. `currentAccount` is not a substitute for an explicit callback account.
408. Use `MessagesController.getInstance(account)` and `ConnectionsManager.getInstance(account)`.
409. Background callbacks must cross to main before touching a View.
410. Main-thread setting changes must notify visible fragments.
411. RecyclerView holders may outlive the feature state; always reset both true and false branches.
412. Chat cells may be rebound with a different message; no state may remain in a field without reset.
413. `LiteMode` and power-saving flags are part of the rendering contract.
414. Notification channels are immutable; create new tele channel IDs for new notification classes.
415. `FLAG_SECURE` is irrelevant to this batch except as a regression guard.
416. Nullable `TLRPC` fields require null checks before bot/profile access.
417. Avoid `TLRPC.java` edits even when a convenient field appears absent.
418. Avoid stock database version changes.
419. Keep stock hunk additions one early return or one post-stock call.
420. New Java-facing methods in stock classes use `tele_` prefix if a member is unavoidable.

## Concrete implementation snippets (anchors, not copy-paste)

421. Seconds display:

```kotlin
fun serviceText(message: MessageObject, original: CharSequence): CharSequence {
    if (!TeleConfig.SHOW_SECONDS.getValue()) return original
    if (!message.isService()) return original
    return "$original · ${TeleHooks.serviceTime(message.messageOwner.date)}"
}
```

422. Link migration:

```kotlin
private fun normalizeTarget(value: String): String =
    if (value.equals("vxtiktok.com", ignoreCase = true)) "tnktok.com" else value
```

423. Scheduled classification:

```kotlin
val delay = when {
    text.startsWith("FLOOD_WAIT_") || text.startsWith("SLOWMODE_WAIT_") -> seconds + 1
    code <= 0 || code >= 500 || text == "TIMEOUT" -> ladder[failure]
    else -> null
}
```

424. Resume request:

```kotlin
val offset = part.length()
request.setRequestProperty("Range", "bytes=$offset-")
```

425. Plain peer copy:

```kotlin
fun copyText(account: Int, userId: Long, chatId: Long): String =
    botApiAdjusted(account, userId, chatId).toString()
```

426. Visibility gate:

```java
if (TeleConfig.HIDE_GIFT_BUTTON.getValue()) {
    giftButton.setVisibility(View.GONE);
    return;
}
```

427. Bot edited predicate:

```kotlin
return TeleConfig.HIDE_BOT_EDITED.getValue() &&
    (sender?.bot == true || message.messageOwner.via_bot_id != 0L)
```

428. These snippets intentionally omit imports and exact current line numbers.
429. Before editing, locate the symbol in the current `tele` branch.
430. Do not introduce comments explaining obvious code.

## UX, strings and limits checklist

431. Every new switch has a title, short description and search keywords.
432. Titles use sentence case consistent with current tele settings.
433. Use positional format arguments for translated strings.
434. Service suffix is exactly ` · HH:mm:ss` in 24-hour examples.
435. Link rewrite toast keeps a maximum of three notes.
436. TikTok target is exactly `tnktok.com`, not a pair containing the dead host.
437. X preset contains `samekosabax.com` once.
438. Scheduled retry maximum is five attempts.
439. Flood and slowmode delays add one second to server-provided N.
440. Generic retry delays are exactly 5 s, 15 s, 1 min, 5 min, 15 min.
441. Updater retry delays are exactly 1, 5, 15, 60 min.
442. APK maximum remains 512 MiB.
443. Feed maximum remains 64 KiB.
444. Peer copy has no spaces, grouping separators, DC suffix or display label.
445. Start parameter tooltip delay is 500 ms.
446. Reduce Motion restores prior state rather than forcing a guessed state.
447. Phone hiding changes only profile presentation.
448. Bot edited hiding does not apply to human-authored edits.
449. Similar-channel hiding suppresses both request and visible block when enabled.
450. Gift hiding covers private message field and channel gift button.

## Logcat and manual on/off matrix

451. Build a debug APK only after every commit of this batch is exported.
452. Use a secondary account or Telegram test account.
453. Run each feature with default state first.
454. Then run each feature explicitly on.
455. Then turn it off without restarting.
456. Compare off screenshots and actions with stock behavior.
457. Seconds: service join/pin text on/off.
458. Links: old preset migration and new preset targets on/off.
459. Scheduled: success, FLOOD_WAIT, SLOWMODE_WAIT, timeout and terminal failure.
460. Updater: clean download, interrupted download, 206, 200, 416 and hash mismatch.
461. Peer ID: user, group, channel, merged DC and account switch.
462. Gift: private chat and channel.
463. Similar: after join and profile child switches independently.
464. Tooltip: collectible and ordinary profile.
465. Reduce Motion: animation flags and restoration.
466. Phone: own/contact/non-contact profile.
467. Bot edited: bot, via bot and human edited messages.
468. Start parameter: deep-link parameter, empty parameter and long parameter.
469. Recommended log tags: `TeleServiceTime`, `TeleLinkRewrites`, `TelePunctual`, `TeleUpdater`.
470. Logs must be disabled or low-volume in release behavior.
471. Never claim manual success from compilation alone.
472. Record exact device/API level and account used in handoff, not in telemetry.
473. For failures, capture exception class, HTTP status and local state, excluding secrets.
474. Check process death for scheduled retry state and updater `.part`.
475. Check cold start for TeleConfig initialization before any stock hook.

## features.md rows

476. Add one English row for each user-facing new setting in the appropriate section.
477. Follow-up-only bug fixes may update the existing row instead of creating a duplicate.
478. Row 0017 should mention service messages and keep Android patch reference 0008 plus follow-up commit.
479. Row 0077 should mention presets, `tnktok.com`, `samekosabax.com` and migration.
480. Row 0095 should mention retries and the terminal notification.
481. Row 0006 should mention resume, SHA-256 and network retry ladder.
482. Row 0253 should say copy is plain Bot API digits independent of visual formatting.
483. Row 0125 belongs under sending.
484. Row 0132 belongs under interface/chats.
485. Row 0143 belongs under ids.
486. Row 0154 belongs under interface.
487. Row 0172 belongs under ids/profiles.
488. Row 0233 belongs under interface.
489. Row 0231 belongs under bots/interface after the bots page exists.
490. Every new row says `off` unless it follows an existing approved switch.
491. Every desktop link uses current number 0017, 0077, 0095, 0006, 0253, 0125, 0132, 0143, 0154, 0172, 0233 or 0231.
492. Do not link follow-ups to obsolete old numbers 0043 or 0079 as if they were separate current patches.
493. Do not list skipped desktop 0135/0136 as Android features.
494. The Android patch filename is filled only after export assigns the queue position.
495. Keep English user copy free of implementation names such as `TeleHooks`.

## Maintainer decisions and unresolved questions

496. Decision: all new Android switches default off.
497. Decision: updater's existing approved default is not reset by this follow-up.
498. Decision: scheduled feature remains Telegram-only and online/open dependent.
499. Decision: 0172 hides only phone row, not all profile data.
500. Decision: 0154 restores saved Lite Mode state.
501. Decision: 0253 copies Bot API adjusted plain digits.
502. Decision: 0077 migrates dead TikTok target to `tnktok.com`.
503. Unresolved: exact Android service-message display hook.
504. Unresolved: whether link migration writes immediately or on save.
505. Unresolved: exact TL error-to-id mapping for grouped scheduled requests.
506. Unresolved: availability of `Content-Range` through the current HTTP helper.
507. Unresolved: exact current LiteMode mask semantics.
508. Unresolved: exact Android bot start button class and field name.
509. Unresolved: exact `via_bot_id` predicate in the current message cell.
510. Resolve each unresolved item by reading the current branch before coding.
511. If a hook cannot satisfy off=stock, stop and report the missing extension point.
512. Do not solve unresolved questions by adding a silent fallback that changes behavior.

## Pitfalls

513. Do not use global account 0 in any helper.
514. Do not touch generated `TLRPC.java`.
515. Do not add a stock DB column or bump `LAST_DB_VERSION`.
516. Do not leave `.part` cleanup in a `finally` that runs on network failure.
517. Do not accept `206` without validating range start.
518. Do not treat all HTTP errors as updater network retryable.
519. Do not retry terminal scheduled errors forever.
520. Do not display a service suffix on every layout regeneration.
521. Do not persist old TikTok targets after migration.
522. Do not let hidden UI labels leave measured blank space.
523. Do not hide similar channels only visually while still making the request.
524. Do not persist reduce-motion state in stock preferences.
525. Do not expose phone numbers or bot tokens in debug logs.
526. Do not apply a cell-only state in `onCreateViewHolder`.
527. Do not forget channel gift button; personal field alone is incomplete.
528. Do not use a notification channel already owned by stock Telegram.
529. Do not add comments as design essays; record rationale here instead.
530. Do not claim the batch gate passed before human verification.

## Batch gate

531. Confirm all twelve rows have one commit each in branch `tele`.
532. Confirm every commit has a one-line lowercase imperative subject.
533. Export with `git format-patch <UPSTREAM> -o ../main/patches/android/ --zero-commit --no-signature --no-numbered`.
534. Update statuses in `PATCHLIST.md` only after export; this guide itself is not a status file.
535. Update features.md rows in the same repository commit as their patch export.
536. Assemble `./gradlew :TMessagesProj_App:assembleDebug`.
537. Exercise every batch toggle at default, on and off where applicable.
538. Exercise updater and scheduled failure paths, not only successful paths.
539. Install the correct ABI split, normally arm64.
540. Hand the APK to a human with the numbered test matrix above.
541. Human verifies off equals stock and on matches each UX requirement.
542. Only then mark the batch `built` and later `done` according to PATCHLIST workflow.
543. A compile-only result is not acceptance.
544. A screenshot of one screen is not acceptance for multi-surface features.
545. The final handoff must list unverified inference items explicitly.
546. This guide is complete only when all lines 1–545 are followed or an unresolved question is escalated.