# Пачка 25: MTProto-инспектор, консоль и диагностика

## 1. Назначение документа

1. Этот документ — пошаговый план реализации пачки 25 для Telegram Android.
2. Он покрывает строки `0088`, `0195`, `0218`, `0298`, `0202` и `0203` из `docs/PATCHLIST.md`.
3. Название пачки в PATCHLIST: «MTProto: инспектор, консоль, диагностика».
4. Порядок ниже является порядком разработки, а не утверждением, что код уже существует.
5. Текущий статус всех строк пачки в PATCHLIST — `todo`.
6. Решение мейнтейнера обязательно: инспектор, консоль и TL-схема портируются комплектом.
7. Решение мейнтейнера также включает отчёты о крашах без дампа и о зависаниях.
8. Отчёты 0202 и 0203 должны быть закрыты серверным тумблером.
9. Для 0202 и 0203 требуется отдельная поддержка tele-server.
10. Основа плана — `AGENTS.md`, `PATCHLIST.md`, `decisions.md`, `portability.md`, `desktop-numbers.md` и `architecture.md`.
11. Дополнительные сверки сделаны по `local://desk-3.md` и `local://desk-5.md`.
12. Сверка Android выполнена по содержимому ветки `tele` через `git show`.
13. Сверка desktop выполнена по `origin/main` через `git show`.
14. Непроверенное проектное предложение помечено `[INFERENCE]`.
15. Нельзя превращать `[INFERENCE]` в факт без проверки в checkout или с maintainer.

## 2. Что именно видно в исходниках

16. Desktop `0088` добавляет HTML/CSS/JS просмотрщик MTProto-логов.
17. Desktop `0088` добавляет `tele_mtp_dump`, `tele_mtp_log` и `tele_mtp_inspector`.
18. Desktop `0088` регистрирует `api.tl` и `mtproto.tl` в ресурсах tele.
19. Desktop `0088` ограничивает просмотр логов размером и количеством записей.
20. Desktop `0088` связывает конструкторы TL с schema.jppgr.am.
21. Desktop `0195` добавляет HTML/CSS/JS произвольной TL-консоли.
22. Desktop `0195` добавляет `tele_tl_runtime` для разбора схемы и значений.
23. Desktop `0195` добавляет `tele_mtp_console_requests` для отправки запросов.
24. Desktop `0195` сериализует схему в JSON для webview.
25. Desktop `0195` отправляет запросы через низкоуровневый MTProto API.
26. Desktop `0218` расширяет список опасных методов и добавляет шаблонные правила.
27. Desktop `0298` меняет desktop-панельный контейнер, но не требует Qt-панели на Android.
28. На Android эквивалентом панели должен быть полноэкранный `BaseFragment`.
29. В Android branch `tele` есть `ConnectionsManager.sendRequest` и `sendRequestInternal`.
30. В Android `sendRequestInternal` сериализует `TLObject` перед `native_sendRequest`.
31. В Android ответ десериализуется в callback после native-границы.
32. В Android branch `tele` `TLRPC.java` является сгенерированным TL-представлением.
33. В дереве Android branch не найден отдельный checked-in `api.tl` или `mtproto.tl`.
34. Поэтому источник схемы Android нельзя считать установленным автоматически.
35. `TLRPC.java` запрещено редактировать по правилам `AGENTS.md`.
36. Existing `TeleHooks.init` уже запускает `TeleConfig`, базу, crash reporter и server client.
37. Existing `TeleCrash` пишет локальный текстовый отчёт и спрашивает перед отправкой.
38. Existing `FileLog.dumpResponseAndRequest` уже является важным наблюдаемым якорем.
39. Existing `FileLog` асинхронно ограничивает очередь protocol dump.
40. Эти существующие механизмы надо расширить, а не дублировать.

## 3. Границы результата пачки

41. Инспектор показывает захваченные запросы, ответы и ошибки.
42. Инспектор умеет фильтровать записи по направлению, DC, имени и времени.
43. Инспектор показывает TL-структуру как безопасный JSON-подобный объект.
44. Инспектор умеет копировать JSON без сетевой отправки.
45. Инспектор может открыть выбранный конструктор в schema.jppgr.am.
46. Инспектор не должен отправлять данные в schema.jppgr.am автоматически.
47. Консоль принимает произвольный API-метод из bundled schema.
48. Консоль даёт автодополнение методов, конструкторов, полей и типов.
49. Консоль валидирует обязательные поля до отправки.
50. Консоль показывает сериализационную ошибку без падения приложения.
51. Консоль показывает успешный TL-ответ и `TL_error`.
52. Консоль сохраняет локальную историю запросов с ограниченным размером.
53. Консоль умеет очищать локальную историю.
54. Опасный запрос всегда останавливается перед фактическим `sendRequest`.
55. Подтверждение опасного запроса нельзя заменить одним предупреждением в UI.
56. Пароль должен проверяться в существующем локальном password flow пачки 23.
57. Платные действия должны получать отдельное понятное подтверждение.
58. Краш без minidump должен иметь `Tele-Note` с причиной.
59. Freeze report должен иметь `Tele-Note: freeze N s`.
60. Freeze report должен сохраняться до следующего старта.
61. Отчёт отправляется только после явного действия пользователя.
62. Серверный запрос отправки не выполняется при пустом server URL.
63. Серверный запрос отправки не выполняется при выключенном server toggle.
64. Выключение фичи возвращает поведение stock.
65. Ни один новый путь не должен менять stock DB schema.
66. Ни один новый путь не должен писать аккаунтные данные в tele-server.
67. Логи должны иметь явные ограничения размера, времени жизни и очистки.

## 4. План TeleConfig

68. Каждая новая настройка должна быть отдельным `TeleConfig` item.
69. Для новых фич правило Android — default off.
70. Default off означает отсутствие перехвата, записи и сетевого действия.
71. Предложение `[INFERENCE]`: добавить общий `MTP_DIAGNOSTICS` с default `false`.
72. Предложение `[INFERENCE]`: `MTP_INSPECTOR` default `false`.
73. Предложение `[INFERENCE]`: `MTP_CONSOLE` default `false`.
74. Предложение `[INFERENCE]`: `MTP_CAPTURE_LOGS` default `false`.
75. Предложение `[INFERENCE]`: `MTP_INCLUDE_UPDATES` default `false`.
76. Предложение `[INFERENCE]`: `MTP_CONFIRM_DANGEROUS` default `false` не подходит безопасности.
77. Поэтому безопаснее сделать `MTP_CONFIRM_DANGEROUS` не выключаемой политикой.
78. В настройках она может отображаться как описание, а не как bypass-тумблер.
79. Предложение `[INFERENCE]`: `MTP_SHOW_SCHEMA_LINKS` default `false`.
80. Предложение `[INFERENCE]`: `MTP_LOCAL_HISTORY` default `false`.
81. Предложение `[INFERENCE]`: `MTP_CLEAR_ON_LOGOUT` default `true`.
82. Предложение `[INFERENCE]`: `DIAGNOSTICS_NO_DUMP` default `false`.
83. Предложение `[INFERENCE]`: `DIAGNOSTICS_FREEZE_REPORTS` default `false`.
84. Предложение `[INFERENCE]`: `DIAGNOSTICS_SERVER_UPLOAD` default `false`.
85. Предложение `[INFERENCE]`: `DIAGNOSTICS_INCLUDE_LOGS` default `false`.
86. Предложение `[INFERENCE]`: `DIAGNOSTICS_INCLUDE_ACCOUNT` default `false` запрещено.
87. Account IDs, usernames, peers и message text нельзя включать в tele-server report.
88. Existing `SEND_CRASH_REPORTS` сейчас имеет default `true` в ветке `tele`.
89. Его нельзя молча переименовать или поменять в рамках документационного плана.
90. Решение о миграции existing crash toggle в новый server upload toggle — открытый вопрос.
91. До решения сохранять совместимость ключа `send_crash_reports`.
92. Existing settings export/import должен включить все новые boolean items.
93. Секреты, password hashes и raw request bodies в export/import не включаются.
94. Значения лимитов и retention лучше хранить константами до отдельного решения.

## 5. Зарезервированные search IDs 1380–1399

95. Диапазон 1380–1399 должен быть выделен только новым строкам этой пачки.
96. Текущий `TeleSearch.kt` использует числовые GUID для поиска.
97. Существующие GUID находятся в диапазонах 950–1109.
98. Новые числа нельзя переиспользовать для другой страницы.
99. Раскладка ниже — план, а не существующее состояние кода.
100. `[INFERENCE]` 1380: `tele diagnostics` — вход в новую страницу.
101. `[INFERENCE]` 1381: `mtproto inspector` — вход в инспектор.
102. `[INFERENCE]` 1382: `mtproto console` — вход в консоль.
103. `[INFERENCE]` 1383: `capture mtproto requests` — включение захвата.
104. `[INFERENCE]` 1384: `capture mtproto responses` — включение ответов.
105. `[INFERENCE]` 1385: `include incoming updates` — включение update-потока.
106. `[INFERENCE]` 1386: `mtproto log retention` — описание ограничения.
107. `[INFERENCE]` 1387: `clear mtproto logs` — действие очистки.
108. `[INFERENCE]` 1388: `open TL schema links` — ссылки на схему.
109. `[INFERENCE]` 1389: `console request history` — локальная история.
110. `[INFERENCE]` 1390: `clear console history` — действие очистки.
111. `[INFERENCE]` 1391: `confirm dangerous methods` — обязательное подтверждение.
112. `[INFERENCE]` 1392: `no-dump crash reports` — краш без дампа.
113. `[INFERENCE]` 1393: `freeze reports` — watchdog и маркер.
114. `[INFERENCE]` 1394: `send diagnostic reports` — серверный upload.
115. `[INFERENCE]` 1395: `send pending crash report` — ручная отправка.
116. `[INFERENCE]` 1396: `diagnostic server status` — состояние URL/gate.
117. `[INFERENCE]` 1397: `MTProto` — поисковое слово.
118. `[INFERENCE]` 1398: `TL schema` — поисковое слово.
119. `[INFERENCE]` 1399: `freeze watchdog` — поисковое слово.
120. IDs должны быть добавлены в `TeleSearch.kt`, а не в stock search без причины.
121. Каждая строка должна открывать конкретный экран или страницу настройки.
122. Не добавлять мёртвые search rows для функций, которых нет в APK.
123. Переиспользовать existing `TeleSettingsActivity` row types.
124. Recycler row обязан перепривязывать состояние в `onBindViewHolder`.
125. Нельзя полагаться на состояние, установленное только в `onCreateViewHolder`.

## 6. Страница настроек

126. Добавить отдельный режим `[INFERENCE] MODE_DIAGNOSTICS`.
127. Не помещать консоль в обычную страницу interface без явного перехода.
128. Вход должен находиться в секции tele.
129. Инспектор и консоль должны быть ссылками, а не огромными inline-формами.
130. Захват MTProto должен быть отдельным toggle.
131. Захват по умолчанию выключен.
132. Update-записи должны быть отдельным toggle.
133. Сетевые raw bytes должны быть отдельной политикой и default off.
134. Кнопка очистки должна показывать размер перед удалением.
135. Кнопка открытия schema должна объяснять внешний домен.
136. Страница должна показывать, активен ли server URL.
137. Server URL пустой означает disabled, как в существующем `TeleSettingsActivity`.
138. Диагностическая страница не должна показывать пароль или его hash.
139. Кнопка «отправить pending report» должна быть недоступна без файла.
140. Settings search должен находить «MTProto», «TL», «inspector», «console».
141. Settings search должен находить «freeze», «crash», «diagnostic».
142. Для каждой строки добавить fork string в `strings_tele.xml`.
143. Stock `strings.xml` менять нельзя.
144. Описание должно говорить, что raw TL может содержать чувствительные данные.
145. Описание должно советовать очищать журнал после диагностики.

## 7. Источник и жизненный цикл TL-схемы

146. Desktop resource явно включает `api.tl` и `mtproto.tl`.
147. Android branch содержит сгенерированный `TLRPC.java`, но не эти source files.
148. Нельзя считать desktop `.tl` автоматически совместимым с Android layer.
149. Канонический источник должен быть зафиксирован maintainer-решением.
150. `[INFERENCE]` Рекомендуемый источник — TL-файлы того же Telegram upstream commit.
151. `[INFERENCE]` Из них CI должен генерировать компактный JSON для Android.
152. JSON должен содержать layer, methods, constructors, types и dangerous marker.
153. JSON должен быть bundled в `res/raw`, а не загружаться с web-сервера.
154. Нельзя использовать schema.jppgr.am как runtime schema dependency.
155. При сборке сравнивать schema layer с `TLRPC.LAYER`.
156. Несовпадение layer должно быть видимым предупреждением в консоли.
157. Несовпадение layer не должно молча отправлять запрос.
158. Схема должна обновляться при каждом upstream layer bump.
159. CI должен падать, если generated JSON не обновлён.
160. CI должен проверять deterministic ordering JSON.
161. CI должен проверять отсутствие duplicate method names.
162. CI должен проверять отсутствие неизвестных constructor references.
163. Генератор не должен редактировать `TLRPC.java`.
164. Текущая Android generated модель должна использоваться для известных объектов.
165. Dynamic runtime нужен для методов, которых нет как Java-класса.
166. `[INFERENCE]` Dynamic runtime должен реализовать TLObject-подобный bridge.
167. Bridge обязан сериализовать constructor ID и поля через `OutputSerializedData`.
168. Bridge обязан читать ответ по result type из schema JSON.
169. Bridge обязан поддерживать flags и `flags.N?Type` поля.
170. Bridge обязан поддерживать vectors, bytes, strings, ints, longs и bool.
171. Bridge обязан ограничивать глубину и размер рекурсивного parse.
172. Unknown constructor должен отображаться hex-значением и raw bytes limit.
173. Не превращать malformed network payload в бесконечную рекурсию.
174. Не хранить весь `NativeByteBuffer` после callback.
175. Копировать только bounded diagnostic representation.

## 8. Arbitrary TL console

176. Консоль принимает method name и typed fields из webview.
177. WebView не получает прямой доступ к `ConnectionsManager`.
178. `@JavascriptInterface` должен иметь минимальный allowlist методов.
179. Каждое bridge-сообщение должно проверять origin/state/session.
180. Нельзя принимать JavaScript URL или arbitrary file URL.
181. HTML/CSS/JS должны быть bundled assets приложения.
182. WebView JavaScript должен быть выключен для любых посторонних страниц.
183. Console bridge должен быть закрыт при уничтожении Fragment.
184. Консоль должна иметь account selector только среди локальных аккаунтов.
185. Default account — текущий account, без глобального singleton.
186. Использовать `ConnectionsManager.getInstance(account)`.
187. Не отправлять запрос через account 0, если выбран другой account.
188. Перед созданием request проверить `UserConfig` и login state.
189. Unauthorized methods должны использовать явно разрешённые flags.
190. Не давать webview произвольно менять request flags.
191. Разрешённые flags задать enum-политикой, а не integer passthrough.
192. DC override должен быть ограничен known DC values.
193. Любой unknown DC должен получить ошибку до native вызова.
194. Парсер должен возвращать структурированную ошибку поля.
195. Ошибка поля должна содержать путь, тип и краткий reason.
196. Не показывать содержимое password-полей в диагностической ошибке.
197. История должна хранить method, безопасный input summary, result summary и timestamp.
198. Raw input history должен быть отдельной настройкой и default off.
199. Raw output history должен быть отдельной настройкой и default off.
200. Ограничить количество history entries и общий размер на диске.
201. Удалять history при logout выбранного account.
202. Очищать history по кнопке без подтверждения только после показа размера.
203. Не помещать history в stock database.
204. Использовать `tele_kv` или отдельный `tele_*` storage через `TeleDatabaseHelper`.
205. Предпочтительно хранить history в файлах с atomic replace.
206. Это решение требует проверки существующих storage helpers.
207. Не создавать вторую систему encryption без требования security review.
208. Если raw TL хранится, применять Android private files directory.
209. Не писать raw TL в external storage.
210. Не включать raw TL в crash report.

## 9. Инспектор и перехват запросов

211. Java boundary начинается в `ConnectionsManager.sendRequest`.
212. Полный рабочий Java anchor — `sendRequestInternal`.
213. Перед `native_sendRequest` уже известны object, flags, DC, type и token.
214. В этом месте можно записать method name и bounded serialized summary.
215. После native callback уже известны response, error, network type и message id.
216. В этом месте можно записать result summary или error.
217. `FileLog.dumpResponseAndRequest` показывает существующий response/request hook.
218. Новый inspector должен иметь один fork coordinator вокруг этих hooks.
219. Не размножать interception в каждом caller `sendRequestTyped`.
220. `sendRequestTyped` должен оставаться thin wrapper.
221. Capture должна проверять `TeleConfig` до serialization copy.
222. Capture должна быстро выйти, если inspector выключен.
223. Не блокировать `stageQueue` ожиданием диска или webview.
224. Запись должна уходить на существующий background log queue.
225. Backpressure должен отбрасывать новые dumps, а не задерживать сеть.
226. Сохранять account index вместе с записью.
227. Сохранять request token только как локальный correlation id.
228. Сохранять request message id, если он доступен после native callback.
229. Сохранять DC и direction.
230. Сохранять monotonic duration, а wall timestamp — только для UI.
231. Не сохранять auth key, auth key id или session key.
232. Не сохранять proxy password и secret.
233. Payload text может содержать peer, message и payment data.
234. Поэтому default capture и raw payload должны быть off.
235. Inspector должен показывать redaction marker вместо запрещённых полей.
236. Redaction нельзя реализовать только после записи на диск.
237. Входящие updates имеют отдельный path `onUnparsedMessageReceived`.
238. Update path должен быть включаемым отдельно.
239. Включение updates может резко увеличить объём журнала.
240. Лимит должен проверяться до построения большого JSON.

## 10. Где Java заканчивается и начинается native

241. Java `ConnectionsManager` вызывает `native_sendRequest` для wire transport.
242. Java видит сериализованный объект до native вызова.
243. Java видит уже десериализованный response после native callback.
244. Java не видит полностью encrypted wire packet на Java boundary.
245. Java не видит все native retries, ACK и transport internals.
246. Java hook не является полным packet inspector.
247. Это ограничение надо явно показать в UI inspector.
248. Полный transport capture потребует JNI hook в tgnet.
249. Такой JNI hook затронет `jni/tgnet` и все ABI.
250. Его нельзя добавлять как скрытый побочный эффект Java патча.
251. `[INFERENCE]` Первый implementation slice должен быть Java-level TL inspector.
252. `[INFERENCE]` Native raw packet capture оставить за отдельным decision.
253. Если требуется native hook, добавить отдельный `tele_` callback.
254. Callback должен передавать только bounded metadata или opt-in bytes.
255. Callback не должен владеть Java byte array на network thread.
256. Callback должен копировать в bounded native ring buffer.
257. Reader должен дренировать ring buffer в background queue.
258. При переполнении считать dropped count.
259. Dropped count показывать пользователю рядом с log status.
260. Не использовать JNI callback для опасного console send.
261. Console send должен идти через штатный Java `ConnectionsManager` API.
262. Native changes должны быть отдельным commit и отдельным ABI gate.
263. Если native capture не принят, назвать inspector `Java TL inspector`.
264. Не обещать пользователю encrypted packet dump при Java-only реализации.

## 11. Опасные методы и подтверждение

265. Список 0195 включает account deletion, logout и resets.
266. Он включает password settings и channel/history/message deletion.
267. Он включает creator transfer.
268. Он включает paid stars, gifts, gift transfers и subscriptions.
269. Список 0218 добавляет participant history deletion.
270. Список 0218 добавляет saved и scheduled message deletion.
271. Список 0218 добавляет photo, story и sticker-set deletion.
272. Список 0218 добавляет contacts deletion и deletion by phones.
273. Список 0218 добавляет channel leave и chat-user deletion.
274. Список 0218 добавляет account TTL setters.
275. Список 0218 вводит pattern `.delete`.
276. Список 0218 вводит pattern `leave`.
277. Список 0218 вводит pattern для TTL, кроме `get`.
278. Эти списки должны быть перенесены в bundled schema metadata.
279. Но runtime safety не должна зависеть только от JS metadata.
280. Java runtime обязан повторно классифицировать method name.
281. Опасный method не должен отправляться при отмене диалога.
282. Подтверждение должно показывать точное имя метода.
283. Подтверждение должно показывать краткий список affected fields.
284. Подтверждение должно показывать, что действие irreversible или платное.
285. Raw arguments показывать только после redaction.
286. Для account password actions вызвать password flow пачки 23.
287. Для payment actions вызвать локальное подтверждение платежа.
288. Если password flow отсутствует, method должен быть rejected.
289. Если action classifier не уверен, method классифицировать как dangerous.
290. Unknown method не является безопасным только потому, что его нет в списке.
291. Не добавлять пользовательский toggle «skip confirmations».
292. Не сохранять факт подтверждения между запросами.
293. Confirmation state должен быть one-shot и привязан к request hash.
294. После изменения input confirmation становится недействительным.
295. После выбора другого account confirmation становится недействительным.
296. Список опасностей должен покрываться unit tests без отправки сети.
297. Tests должны проверять exact names и patterns.
298. Tests должны проверять payment invoice classification.
299. Tests должны проверять `getAccountTTL` как безопасный read.
300. Tests должны проверять `setAccountTTL` как dangerous.

## 12. Краш без дампа

301. Existing `TeleCrash` already installs an uncaught exception handler.
302. Existing `TeleCrash` writes report only while collecting is enabled.
303. Existing report includes platform, version, tele build and device.
304. Existing report includes thread and stack text.
305. 0202 должен добавить причины, когда dump отсутствует.
306. Возможные причины desktop-патча — graphics crash, no dump и older version.
307. Android reason codes должны быть определены явно.
308. `[INFERENCE]` Минимальный Android набор: `no_dump_written`, `process_killed`, `oom`.
309. Причина должна добавляться как `Tele-Note: <reason>`.
310. `Tele-Note` не должен содержать account id, username или message text.
311. Результирующий текст должен оставаться локально до выбора send.
312. Dialog при следующем старте должен показывать тип отчёта.
313. «Don't send» должен удалять pending report по существующему поведению.
314. «Send» должен использовать существующий `TeleCrash.sendPendingAsync`.
315. Server gate должен проверяться прямо перед network call.
316. URL должен нормализоваться существующим `TeleServer` helper.
317. Upload error не должен удалять pending report.
318. Успешный upload должен удалить только отправленный файл.
319. Не включать inspector logs автоматически в crash report.
320. Include logs должен быть отдельным явным действием.

## 13. Freeze watchdog и Tele-Note

321. 0203 использует watchdog главного потока.
322. Desktop threshold в patch assessment указан как 15 секунд.
323. Android implementation должна использовать monotonic clock.
324. Нельзя считать долгий sleep устройства freeze главного потока.
325. Watchdog heartbeat должен обновляться main-thread handler.
326. Watchdog reader должен работать на отдельном daemon/background thread.
327. При отсутствии heartbeat 15 секунд записать marker.
328. Marker должен содержать `Tele-Note: freeze N s`.
329. Marker должен содержать время старта эпизода.
330. Marker должен содержать build/platform metadata без аккаунтных данных.
331. Marker должен быть atomic write в private files directory.
332. Ограничить marker размером и количеством повторных записей.
333. Не писать marker каждую миллисекунду во время длинного freeze.
334. При восстановлении main thread обновить duration marker.
335. На следующем старте сначала проверить обычный crash report.
336. Если crash report есть, freeze marker не должен затереть crash report.
337. Если crash report отсутствует, freeze marker становится pending diagnostic.
338. После показа диалога удалить marker только после выбора пользователя.
339. При выключенном server gate marker можно оставить локально или удалить по policy.
340. Решение retention при выключенном gate — открытый server/privacy вопрос.
341. Watchdog не должен стартовать до готовности `ApplicationLoader` context.
342. Watchdog должен останавливаться в `aboutToQuit`-эквиваленте Android.
343. На Android process kill не вызывает надёжный shutdown callback.
344. Поэтому marker должен быть валиден при внезапном завершении процесса.
345. Не использовать UI object из watchdog thread.
346. Dialog и state transition выполняются на main thread.
347. Не собирать полный main-thread stack без platform-safe API.
348. `[INFERENCE]` Для Android stack snapshot нужен проверенный `Thread.getStackTrace` path.
349. Если snapshot нельзя получить безопасно, отправлять только marker note.
350. Tele-Note должен быть представлен в server API contract.

## 14. Хранилище, приватность и безопасность

351. Stock DB schema и `LAST_DB_VERSION` остаются нетронутыми.
352. Inspector history хранить только в `tele_*` storage или private files.
353. Crash and freeze files хранить в `context.filesDir`.
354. External storage не использовать для диагностических данных.
355. Не писать TL logs в Android system log целиком.
356. Logcat допускается только для размеров, token и redaction counters.
357. Строки payload в logcat запрещены default policy.
358. При копировании в clipboard показывать предупреждение о чувствительных данных.
359. Clipboard copy должен быть user-initiated.
360. Автоочистка clipboard для raw TL — `[INFERENCE]` и требует решения.
361. При logout удалять account-bound history и pending reports.
362. Multi-account state всегда ключуется `currentAccount`.
363. Не использовать static selected account внутри request coordinator.
364. Account selector должен обновлять все callbacks и UI labels.
365. При смене account очищать pending confirmation.
366. При смене account не смешивать correlation links.
367. Privacy description должна быть в настройках до включения capture.
368. Сетевой upload отчёта должен быть HTTPS.
369. Не посылать tele-server сырые Telegram request/response bodies.
370. Если maintainer разрешит debug upload, сделать explicit separate consent.
371. Tele-server должен принимать platform `android` и build metadata.
372. Формат `/v1/crash.php?act=report` сейчас используется `TeleCrash`.
373. Endpoint для freeze report пока не подтверждён.
374. Нельзя придумывать endpoint в коде без server contract.
375. Требуется server-side retention и redaction policy.

## 15. UI, потоки и recycling

376. WebView и Fragment UI создаются только на main thread.
377. `ConnectionsManager` callbacks приходят не на UI thread.
378. Фоновый callback должен доставить immutable snapshot на UI через `AndroidUtilities.runOnUIThread`.
379. WebView bridge должен принимать сообщения через main thread.
380. Disk writes выполняются через existing log/background queue.
381. `NativeByteBuffer` не должен переживать callback ownership.
382. Recycler holders обязаны полностью bind entry state.
383. Recycled holder не должен сохранять старый dangerous marker.
384. Recycled WebView state нельзя считать request identity.
385. Использовать stable local entry ID для inspector details.
386. Подробный экран должен проверять, что entry ещё существует.
387. Если entry удалён, показать «entry expired», а не старый объект.
388. Большие JSON не передавать через Intent extras.
389. Для detail view использовать bounded cache.
390. Обновление log list должно иметь debounce.
391. Не перерисовывать весь список на каждый incoming callback.
392. При уходе Fragment в background приостановить polling WebView.
393. При destroy снять JS interface и закрыть callback sink.
394. LiteMode должен отключать декоративные анимации inspector.
395. LiteMode не должен отключать safety confirmations.
396. На маленьком экране инспектор использует list/detail navigation.
397. На планшете `[INFERENCE]` можно использовать split layout.
398. Не копировать desktop panel geometry на Android.
399. Accessibility labels должны содержать method name и direction.
400. Danger confirmation должна быть доступна TalkBack.

## 16. Якоря stock и fork

401. Основной lifecycle anchor — existing `TeleHooks.init`.
402. Добавить отдельный `TeleMtp` coordinator в `tele/helpers`.
403. Не помещать TL runtime в `TeleHooks` object.
404. Основные Java request anchors — `ConnectionsManager.sendRequestInternal`.
405. Existing response dump anchor — callback внутри `sendRequestInternal`.
406. Incoming update anchor — `ConnectionsManager.onUnparsedMessageReceived`.
407. Log backend anchor — `FileLog` asynchronous dump path.
408. Settings anchor — `TeleSettingsActivity.buildRows`.
409. Search anchor — `TeleSearch.entries`.
410. Existing crash anchor — `TeleCrash.install` и `offerPending`.
411. Application anchor для watchdog — `ApplicationLoader` startup.
412. Новый stock-код ограничить gated calls в `TeleHooks` или `TeleMtp`.
413. Fork-код располагать в новых Kotlin-файлах `tele/`.
414. Не делать второй глобальный event bus.
415. Не редактировать `TLRPC.java`.
416. Не редактировать stock database version.
417. Не делать широкие переименования в hot files.
418. Для Java hot hunk добавить ранний toggle check.
419. Для network hook toggle check делать до allocation/copy.
420. При невозможности минимального stock hunk остановиться и поднять вопрос.

## 17. Коммиты и оценка усилий

421. Коммит A: `feat: add mtproto log capture` — M.
422. Коммит A покрывает 0088 Java inspector backend и bounded storage.
423. Коммит A не обещает native encrypted packet capture.
424. Коммит B: `feat: add mtproto inspector` — M.
425. Коммит B покрывает экран, WebView bridge и filters.
426. Коммит C: `feat: bundle mtproto schema` — M.
427. Коммит C покрывает generator, raw JSON и layer check.
428. Коммит D: `feat: add mtproto console` — L.
429. Коммит D покрывает dynamic TL runtime и arbitrary methods.
430. Коммит E: `fix: confirm dangerous mtproto methods` — S.
431. Коммит E покрывает 0218 exact list, payments и patterns.
432. Коммит F: `feat: add diagnostic reports` — M.
433. Коммит F покрывает 0202 no-dump report and Tele-Note.
434. Коммит G: `feat: report android freezes` — M.
435. Коммит G покрывает 0203 watchdog, marker and next-start flow.
436. Коммит H: `feat: expose mtproto tools` — S.
437. Коммит H покрывает 0298 fullscreen navigation and settings links.
438. Коммиты должны идти в queue order, если нет maintainer exception.
439. Сначала schema contract, затем runtime, затем UI.
440. Затем safety confirmation, чтобы console не имела unsafe промежутка.
441. Затем diagnostics, если server contract готов.
442. Native capture — отдельный commit только после решения о JNI.
443. Если native capture не принят, не добавлять пустые native stubs.
444. Каждый commit экспортируется отдельным Android patch.
445. `features.md` обновляется вместе с user-facing patch commit.
446. Этот документ сам по себе не изменяет PATCHLIST status.

## 18. Зависимости и порядок

447. База пачки 23 должна предоставить `TeleHooks.requirePassword`.
448. База пачки 23 должна обеспечить локальный пароль и reset policy.
449. Android 0051 `ViewAsTl` даёт полезные serialization/UI patterns.
450. Android 0067/0075 дают existing crash report path.
451. Сначала принять schema source и layer policy.
452. Затем реализовать parser tests без Android UI.
453. Затем реализовать request bridge и redaction.
454. Затем реализовать dangerous classifier.
455. Затем подключить console send.
456. Затем добавить inspector list/detail UI.
457. Затем добавить settings/search rows 1380–1399.
458. Затем добавить no-dump reports.
459. Затем добавить freeze watchdog.
460. Затем провести server integration review.
461. 0203 зависит от 0202 общего pending report flow.
462. 0298 зависит от готового 0195 UI, но не от desktop panels.
463. 0218 зависит от 0195 runtime.
464. 0195 зависит от 0088 capture/inspector infrastructure.
465. 0088 зависит от schema metadata для meaningful TL names.
466. Full arbitrary method support зависит от generated/current layer agreement.

## 19. Тесты переключателей и logcat

467. Gate начинается только после debug APK.
468. До ручного теста выполнить `./gradlew :TMessagesProj_App:assembleDebug`.
469. Установить правильный ABI APK на test device.
470. Проверять secondary account, а не основной аккаунт.
471. В OFF состоянии открыть обычные chats, profiles и settings.
472. В OFF состоянии проверить отсутствие inspector disk writes.
473. В OFF состоянии проверить отсутствие console WebView activity.
474. В OFF состоянии проверить отсутствие new JNI callback activity.
475. Включить inspector и сделать безопасный `help.getConfig` или другой read-only запрос.
476. Проверить одну request entry, response entry и duration.
477. Проверить ошибочный запрос с недоступным method.
478. Проверить malformed field и отсутствие crash.
479. Проверить фильтр по account и DC.
480. Проверить clear logs и размер private files после очистки.
481. Проверить schema link только по tap пользователя.
482. Отключить capture и убедиться, что новые entries не появляются.
483. Включить console и вызвать безопасный read-only API method.
484. Проверить TL response, `TL_error` и timeout/error display.
485. Проверить history on/off и clear history.
486. Переключить account и проверить отсутствие смешивания history.
487. Ввести `messages.deleteMessages` и отменить confirmation.
488. Убедиться, что request token не ушёл после отмены.
489. Повторить method и пройти password confirmation.
490. Для test account проверить, что exact method уходит только после подтверждения.
491. Проверить `channels.leaveChannel` как dangerous pattern/list item.
492. Проверить неизвестный `.deleteSomething` как dangerous pattern.
493. Проверить `account.getAccountTTL` как read-only.
494. Проверить `account.setAccountTTL` как dangerous.
495. Проверить payment invoice confirmation без реальной покупки.
496. Включить no-dump diagnostics и создать контролируемый test report path.
497. Нельзя намеренно крашить основной аккаунт ради теста.
498. Проверить pending dialog после cold start.
499. Нажать «don't send» и убедиться, что файл удалён.
500. Создать controlled main-thread stall в debug-only test hook.
501. Проверить marker после порога 15 секунд.
502. Перезапустить приложение и проверить freeze summary.
503. Проверить `Tele-Note: freeze N s` в local report fixture.
504. Проверить, что watchdog не показывает UI с background thread.
505. Включить server URL и upload gate только на test server.
506. Проверить HTTPS request и отсутствие Telegram account fields.
507. Отключить server URL и убедиться, что upload не выполняется.
508. Включить airplane mode и проверить сохранение pending report при ошибке.
509. Проверить logcat без raw payload строки.
510. Разрешённые logcat markers: `TeleMtp`, entry count, dropped count, file size.
511. Запрещённые logcat markers: auth key, phone, username, message text, raw bytes.
512. Проверить logcat во время fast request burst.
513. Проверить bounded queue и dropped counter.
514. Проверить rotation/recycling inspector rows.
515. Проверить LiteMode и отключённые анимации.
516. Проверить accessibility text для danger dialog.

## 20. Открытые решения

517. Какой exact Android TL source совпадает с `TLRPC.LAYER`?
518. Кто владеет generator для bundled schema в CI?
519. Нужно ли включать `mtproto.tl` из desktop origin/main или upstream Android source?
520. Подтверждён ли runtime arbitrary method с текущим native serializer?
521. Нужен ли JNI raw packet hook или достаточно Java TL boundary?
522. Должен ли inspector включать unparsed incoming updates?
523. Какой retention и максимальный размер log files принять?
524. Нужно ли encrypt local raw history или достаточно private files + opt-in?
525. Как разделить existing `SEND_CRASH_REPORTS` и новый upload gate?
526. Какой endpoint принимает freeze reports?
527. Поддерживает ли tele-server `platform=android` и `Tele-Note` сейчас?
528. Разрешены ли crash uploads без minidump на production server?
529. Сколько freeze reports хранить при выключенном upload gate?
530. Нужен ли отдельный consent перед первым raw TL capture?
531. Нужен ли clipboard auto-clear для raw TL?
532. Нужно ли запрещать console на logged-out account полностью?
533. Какие DC override values разрешены для Android test servers?
534. Как отображать layer mismatch: block, warning или read-only mode?
535. Какой формат schema JSON стабилизировать для будущих layers?
536. Ответы надо записать в `decisions.md` до закрытия пачки.

## 21. Features rows и gate

537. Для каждой user-facing функции добавить одну English row в `features.md`.
538. Row для MTProto inspector должна указать settings path и default off.
539. Row для arbitrary TL console должна указать dangerous confirmations.
540. Row для diagnostics должна указать no-dump and freeze scope.
541. Row для server upload должна указать explicit consent and server gate.
542. В desktop column использовать current numbers 88, 195, 218, 298, 202 и 203.
543. В Android column указывать фактические exported patch names после commit.
544. До экспорта нельзя придумывать номера Android patch files.
545. PATCHLIST rows остаются `todo` до появления commits и export.
546. После commits status становится `queued`, не `done`.
547. После debug APK и передачи на ручную проверку status становится `built`.
548. После человеческой проверки ON и OFF status становится `done`.
549. Batch gate требует все строки пачки, включая 0202 и 0203.
550. Gate должен перечислить console safe read, dangerous cancel и report flow.
551. Gate должен перечислить layer mismatch и schema update check.
552. Gate должен перечислить account switching and recycling tests.
553. Gate должен перечислить no-network behavior with server URL empty.
554. Gate должен перечислить logcat privacy review.
555. Нельзя считать пачку готовой только потому, что APK собрался.

## 22. Типичные ошибки

556. Ошибка: перехватывать только `sendRequestTyped` и терять обычный `sendRequest`.
557. Исправление: один coordinator на `sendRequestInternal`.
558. Ошибка: считать Java callback полным wire inspector.
559. Исправление: честно обозначить Java boundary и native gap.
560. Ошибка: передавать TL payload в WebView без лимита.
561. Исправление: bounded snapshot и hard size limits.
562. Ошибка: доверять dangerous list из JavaScript.
563. Исправление: повторная проверка в Kotlin runtime.
564. Ошибка: хранить schema только на schema.jppgr.am.
565. Исправление: bundled schema, внешний домен только для link action.
566. Ошибка: обновить layer без обновления schema JSON.
567. Исправление: CI consistency check.
568. Ошибка: править `TLRPC.java` вручную.
569. Исправление: generator/source decision, затем regenerated artifact вне ручной правки.
570. Ошибка: писать диагностические данные в stock DB.
571. Исправление: `tele_*`, `tele_kv` или private files.
572. Ошибка: послать account data вместе с crash report.
573. Исправление: allowlist metadata и redaction до upload.
574. Ошибка: считать `SEND_CRASH_REPORTS=true` доказательством нового gate.
575. Исправление: отдельно проверить существующий toggle и миграцию.
576. Ошибка: запускать watchdog с UI thread stack dump без лимита.
577. Исправление: bounded marker, safe snapshot и fallback note.
578. Ошибка: показывать dialog из network callback.
579. Исправление: `AndroidUtilities.runOnUIThread`.
580. Ошибка: забыть `currentAccount` при callbacks.
581. Исправление: передавать immutable account id в каждый entry.
582. Ошибка: хранить confirmation после редактирования input.
583. Исправление: one-shot request hash.
584. Ошибка: не учитывать Recycler recycling.
585. Исправление: полная установка state в `onBindViewHolder`.
586. Ошибка: игнорировать LiteMode.
587. Исправление: убрать декоративную анимацию, оставить безопасность.
588. Ошибка: считать panel patch 0298 отдельной Qt-задачей.
589. Исправление: Android fullscreen fragment поверх готовой консоли.
590. Ошибка: добавить native stubs без реального ABI поведения.
591. Исправление: либо полноценный JNI slice, либо Java-only inspector.

## 23. Definition of done

592. Schema source и layer policy подтверждены.
593. Bundled schema обновляется вместе с Telegram layer.
594. Console выполняет безопасный arbitrary TL read request.
595. Console показывает success и `TL_error`.
596. Dangerous exact methods требуют подтверждения.
597. Dangerous pattern methods требуют подтверждения.
598. Cancel не вызывает network request.
599. Inspector показывает bounded request/response entries.
600. Inspector не блокирует network thread.
601. OFF возвращает stock behavior и не пишет новые logs.
602. Multi-account entries не смешиваются.
603. Recycled rows показывают актуальное состояние.
604. LiteMode не ломает inspector или confirmations.
605. No-dump report имеет Tele-Note.
606. Freeze marker имеет Tele-Note и threshold metadata.
607. Upload происходит только через enabled server gate.
608. Upload не содержит account data.
609. Tele-server contract для freeze подтверждён.
610. Debug APK проверен на устройстве.
611. ON и OFF пройдены вручную.
612. Logcat privacy review пройден.
613. Features rows добавлены в том же patch commit.
614. PATCHLIST statuses отражают фактическую стадию.
615. Человеческая проверка закрывает batch gate.
616. До выполнения этих пунктов пачка 25 не считается done.
