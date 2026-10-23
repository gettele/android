# Пачка 15 — списки: пины, папки и лимиты

## Назначение документа

1. Этот файл задаёт реализацию всех строк пачки 15 из `docs/PATCHLIST.md`.
2. В пачку входят 0123, 0124, 0162, 0117, 0031, 0082 и 0156.
3. Номер 0123 — текущий Android-план для desktop-фичи, которая в старой нумерации была 0126.
4. Поэтому далее «новый 0126» означает переработанный desktop pin patch, текущий номер 0123.
5. 0124 — локальные папки сверх серверного лимита.
6. 0162 — синтетическая локальная папка `unsorted`.
7. 0117 — скрытие сообществ.
8. 0031 — переход к первому сообщению.
9. 0082 — мгновенное перемещение чатов без desktop freeze-механики.
10. 0156 — локальный mute папок и полное подавление уведомлений.
11. Вне этого документа остаются компактные строки, иконки папок, счётчики и другие строки пачки 16.
12. Вне этого документа остаются серверные лимиты, которые Telegram меняет ответом конфигурации.
13. Нельзя подменять отсутствие точной desktop-семантики догадкой.
14. Каждая такая граница явно помечена `[INFERENCE]` ниже.

## Источники и проверенная база

15. Прочитаны `AGENTS.md`, `PATCHLIST.md`, `decisions.md`, `portability.md`, `desktop-numbers.md` и `development.md`.
16. Прочитан локальный разбор `desk-0125-0164.md`.
17. Прочитан локальный разбор изменений `desk-delta.md`.
18. `decisions.md` требует для 0162 тот же механизм, что для локальных папок 0124.
19. `PATCHLIST.md` требует один общий порядок серверных и локальных пинов.
20. `PATCHLIST.md` перечисляет основной список, архив, фильтры, форумные темы и Saved Messages.
21. `portability.md` подтверждает `MessagesController.getDialogFilters()` как Android-точку для фильтров.
22. `portability.md` подтверждает `FilterTabsView` как Android-поверхность вкладок.
23. `portability.md` указывает `MessagesController.sortDialogs` для локального порядка, но точный текущий якорь надо проверить перед кодом.
24. В Android checkout через `git show tele:` прочитаны `TeleConfig.kt`, `TeleSearch.kt` и `TeleDatabaseHelper.kt`.
25. В `TeleConfig.kt` уже используется registry item и `getValue()` из Java.
26. В `TeleSearch.kt` текущие обычные GUID начинаются с 950 и уже заняли старые блоки.
27. В `TeleDatabaseHelper.kt` есть `tele_kv`; штатная схема Telegram не должна изменяться.
28. Попытка `git show origin/main:patches/tdesktop/0123-...` в Android checkout не нашла desktop checkout.
29. Поэтому точные desktop-пути не выдаются за просмотренные исходники.
30. Поведение desktop ниже основано на локальных разборах и PATCHLIST.
31. [INFERENCE] Перед кодом maintainer должен повторить `git show origin/main:<точный-путь>` в desktop checkout.
32. [INFERENCE] Имена Android методов, которых нет в проверенном выводе, являются якорями для поиска, а не обещанием API.
33. Источник поведения — desktop, источник кода — текущая Android ветка `tele`.
34. Код desktop нельзя копировать: Kotlin-хелперы должны быть написаны для Android.

## Непересекаемые правила проекта

35. Fork-код размещается в новых файлах под `TMessagesProj/src/main/java/tele/`.
36. Новые Java-члены stock-класса получают префикс `tele_`.
37. В stock-файле разрешён только маленький gated call, ранний return или вызов hook.
38. Нельзя редактировать `TLRPC.java`.
39. Нельзя менять stock SQL-схему или `LAST_DB_VERSION`.
40. Данные пачки хранятся в `tele_kv` или новых `tele_*` таблицах.
41. Пины и папки не должны попадать на tele-server.
42. Пины и папки не должны менять Telegram server state, кроме штатного pin/unpin серверной части.
43. Любой новый switch добавляется в `TeleConfig` с default `false`.
44. OFF должен быть неотличим от stock Android.
45. Каждая настройка получает строку в `strings_tele.xml`.
46. Каждая настройка получает row в текущем `TeleSettingsActivity`.
47. Каждая настройка получает запись export/import spec.
48. Каждая запись поиска получает keywords, страницу и стабильный ID.
49. Search ID не является dialog ID и никогда не отправляется в сеть.
50. UI меняется только на main thread.
51. DB и parsing выполняются не на main thread.
52. Любой callback проверяет account и жизненный цикл экрана.
53. Любой RecyclerView holder заново выставляет состояние при bind.
54. Анимации и переходы обязаны учитывать LiteMode.
55. Privacy-смысл локальных списков описывается прямо: данные остаются на устройстве.
56. Логирование не содержит названий чатов, usernames, message text или содержимого фильтра.

## Состав и порядок работ

57. Сначала выделить общий `LocalLists`/`LocalPins` слой без UI-решений.
58. Первым пользовательским commit сделать 0123 — локальные пины.
59. Вторым сделать 0124 — локальные фильтры-папки.
60. Третьим сделать 0162 — `unsorted` на механизме 0124.
61. После общего механизма сделать 0117 — скрытие сообществ.
62. Затем сделать 0031 — переход к первому сообщению.
63. Затем сделать 0082 — мгновенное перемещение.
64. Последним сделать 0156 — mute папок и `silence completely`.
65. Такой порядок позволяет 0162 использовать готовый local-folder resolver.
66. 0117, 0031 и 0082 не должны блокировать storage-патчи.
67. 0156 намеренно идёт после фильтров, потому что считает принадлежность к папке.
68. Оценки из PATCHLIST: 0123 L, 0124 L, 0162 L.
69. Оценка 0117: S.
70. Оценка 0031: S.
71. Оценка 0082: S.
72. Оценка 0156: M.
73. Общая оценка не означает разрешение объединить несколько features в один commit.
74. Один commit должен давать одну экспортируемую Android-фичу.

## Плановые commits

75. `feat: keep local dialog pins` — 0123, L.
76. Зависит от текущих TeleConfig, TeleHooks, tele_kv и Android 0042 message-menu infrastructure.
77. Этот commit содержит формат v2, merge, local drag и все scopes.
78. `feat: keep local dialog folders` — 0124, L.
79. Зависит от 0123 только в смысле общего local-list storage; прямой pin API не нужен.
80. Этот commit содержит fork-фильтры вне серверной синхронизации.
81. `feat: add unsorted folder` — 0162, L.
82. Зависит от 0124 и от проверки порядка `getDialogFilters()`.
83. Synthetic filter не добавляется в Telegram server request.
84. `debloat: hide communities` — 0117, S.
85. Не зависит от локального списка; зависит от найденных community display hooks.
86. `feat: jump to chat beginning` — 0031, S.
87. Не зависит от 0124; должен использовать штатную history pagination.
88. `feat: move chats instantly` — 0082, S.
89. Зависит от подтверждённого move/reorder stock call, но не от desktop animation.
90. `feat: mute dialog folders` — 0156, M.
91. Зависит от 0124 и 0162 resolver; default off.
92. Если «silence completely» требует отдельный switch, он остаётся в commit 0156.
93. Если desktop source показывает только один switch, не создавать второй switch.
94. Это правило предотвращает дублирование pref key и search result.

## TeleConfig и defaults

95. Добавить `LOCAL_PINS = BoolItem("local_pins", false)`.
96. Добавить `LOCAL_FOLDERS = BoolItem("local_folders", false)`.
97. Добавить `UNSORTED_FOLDER = BoolItem("unsorted_folder", false)`.
98. Добавить `HIDE_COMMUNITIES = BoolItem("hide_communities", false)`.
99. Добавить `JUMP_TO_BEGINNING = BoolItem("jump_to_beginning", false)`.
100. Добавить `INSTANT_CHAT_MOVE = BoolItem("instant_chat_move", false)`.
101. Добавить `MUTE_FOLDERS = BoolItem("mute_folders", false)`.
102. [INFERENCE] `SILENCE_COMPLETELY` добавлять только если desktop UX имеет отдельный persisted control.
103. Если отдельный control подтверждён, его default также `false`.
104. Нельзя использовать default `true` из desktop для Android.
105. Нельзя считать 0162 исключением из общего off-by-default правила.
106. Включение родительского `LOCAL_FOLDERS` не включает `UNSORTED_FOLDER` автоматически.
107. Включение `MUTE_FOLDERS` не меняет mute обычных чатов.
108. При выключении setting local state не удалять.
109. При повторном включении state должен восстановиться из local storage.
110. Вызовы Java используют `TeleConfig.X.getValue()`, не внутреннее `.value`.
111. Config change должен обновлять открытые списки без restart.
112. Перестроение list/filter rows выполняется через UI dispatcher.
113. DB migration и JSON parsing не должны блокировать settings screen.

## Search IDs 1180–1199

114. Диапазон 1180–1199 зарезервировать за пачкой 15.
115. Перед merge проверить фактический registry и не переиспользовать занятый ID.
116. [INFERENCE] Текущий checkout не показывает полный будущий registry; таблица ниже — план стабильных записей.
117. Если collision обнаружен, перенести весь блок и обновить этот документ до кода.
118. 1180 — `LOCAL_PINS`, title «local pins past the limit».
119. 1181 — alias «pin chats», указывает на 1180, не новый toggle.
120. 1182 — `LOCAL_FOLDERS`, title «local folders past the limit».
121. 1183 — alias «folders past the limit», указывает на 1182.
122. 1184 — `UNSORTED_FOLDER`, title «unsorted folder».
123. 1185 — alias «unfiled chats», указывает на 1184.
124. 1186 — `HIDE_COMMUNITIES`, title «hide communities».
125. 1187 — alias «hide similar channels», указывает на 1186 только после сверки desktop wording.
126. 1188 — `JUMP_TO_BEGINNING`, title «jump to the first message».
127. 1189 — alias «chat beginning», указывает на 1188.
128. 1190 — `INSTANT_CHAT_MOVE`, title «move chats instantly».
129. 1191 — alias «instant chat move», указывает на 1190.
130. 1192 — `MUTE_FOLDERS`, title «mute folders».
131. 1193 — alias «silence folder notifications», указывает на 1192.
132. 1194 — help «mixed server and local pin order».
133. 1195 — help «pins in archive, topics, filters and Saved Messages».
134. 1196 — help «local folder migration».
135. 1197 — help «unsorted excludes archive».
136. 1198 — help «local list data never syncs».
137. 1199 — help «server limits remain server-defined».
138. IDs 1181, 1183, 1185, 1187, 1189, 1191 and 1193 are aliases, not items.
139. IDs 1194–1199 must open a detail/help row or the canonical feature row.
140. Alias records must not be put in `TeleConfig` a second time.
141. Search entries include English and Russian keywords where current registry allows them.
142. Keywords for 1180: `pin`, `pinned`, `local`, `limit`, `закрепить`, `пин`.
143. Keywords for 1182: `folder`, `filter`, `local`, `limit`, `папка`, `фильтр`.
144. Keywords for 1184: `unsorted`, `unfiled`, `not in folders`, `без папки`.
145. Keywords for 1186: `community`, `channel recommendations`, `similar channels`, `сообщества`.
146. Keywords for 1188: `first message`, `beginning`, `start`, `начало`, `первое сообщение`.
147. Keywords for 1190: `move`, `instant`, `reorder`, `переместить`, `сразу`.
148. Keywords for 1192: `mute`, `folder`, `notifications`, `silence`, `мьют`, `уведомления`.
149. Search result path must match the canonical new settings page.
150. Search callback must read config on main thread.

## Общая модель локальных списков

151. Создать один helper для account-aware local list state.
152. Helper принимает `account`, `scope` и операцию; account 0 нельзя зашить.
153. Scope должен различать main, archive, filter, forum topic и Saved Messages.
154. Scope должен включать dialog ID там, где список относится к topic или filter.
155. [INFERENCE] Итоговый строковый ключ `tele_kv` не фиксировать до проверки serializer conventions.
156. Рекомендуемый ключ имеет версию, account и scope, например `pins.v2.<account>.<scope>`.
157. Двоеточия или точки допустимы только после проверки существующих ключей.
158. JSON schema должна отвергать неизвестную версию безопасно.
159. Неверный JSON не должен очищать рабочий список без резервного чтения.
160. Дубликаты ID удалять детерминированно при загрузке.
161. Отсутствующий peer не должен вызывать crash.
162. Нельзя хранить только отображаемую позицию без canonical ID.
163. Local state не должен сериализовать весь `TLRPC.Dialog`.
164. `hash` хранить только если он действительно нужен для merge.
165. [INFERENCE] Тип и ширина `hash` должны быть взяты из desktop patch, а не выбраны произвольно.
166. Запись должна быть атомарной: сначала новый JSON, затем replace одной DB operation.
167. Неполную запись считать старой версией, а не пустым списком.
168. После commit DB публиковать notification на UI thread.
169. Notification не должен содержать message text или account credentials.
170. Reader должен иметь deterministic sort при одинаковой позиции.

## 0123 / новый 0126: desktop pin redesign

171. Server pin и local pin находятся в одном пользовательском порядке.
172. Поля записи v2: `id`, optional `hash`, `local`.
173. `local=false` означает серверный элемент в local merged order.
174. `local=true` означает локальный pin сверх серверного лимита.
175. Старый v1 без `local` читать как all-local.
176. V1 migration должна выполняться один раз и быть идемпотентной.
177. Миграция v1 не должна отправлять эти записи на Telegram.
178. Server response является источником текущего server subset.
179. `merge(server, local)` сохраняет local interleaving.
180. Пропавший с сервера server pin удалять после reconciliation.
181. Server pin, появившийся после refresh, вставлять после предыдущего server neighbor.
182. Нельзя просто дописывать все local pins хвостом.
183. Это отличие от старой модели `kLocalBase`.
184. Перетаскивание разрешено между server и local pins.
185. После drag строится единый порядок.
186. На сервер отправляется только server subset.
187. Local subset не передаётся в `savePinnedOrder`.
188. [INFERENCE] Точная форма server reorder request должна быть взята из текущего Java API.
189. [INFERENCE] Ошибку pin limit надо найти по фактическому callback `TL_messages_toggleDialogPin`.
190. Не искать ошибку по тексту, если response имеет устойчивый код/тип.
191. При обычном успешном server pin `local=false`.
192. При превышении лимита новый pin получает `local=true`.
193. Unpin server+local entry превращает его в server state, если desktop это подтверждает.
194. Unpin чистого local entry удаляет запись из local list.
195. [INFERENCE] Формулировка пункта 193 требует сверки exact desktop transition; не менять remote pin без ответа сервера.
196. Reconcile после reload должен быть безопасен при повторном update.
197. Несовпадение server hash не должно терять local position молча.
198. [INFERENCE] Поведение stale hash при совпавшем ID надо подтвердить в desktop source.
199. Порядок должен работать для main list.
200. Порядок должен работать для Archive.
201. Порядок должен работать для custom filter.
202. Порядок должен работать для forum topic.
203. Порядок должен работать для Saved Messages.
204. Saved Messages не заменяется облачными Saved tags.
205. Локальные pins остаются на одном устройстве и аккаунте.
206. Для topic ключ включает root/topic context.
207. Для Saved scope не путать self dialog с обычным peer ID.
208. Для filter scope использовать стабильный filter identity.
209. [INFERENCE] Стабильность ID локальной папки после удаления/создания должна быть проверена stock filter model.
210. Merge должен выполняться data layer, не в каждой `DialogCell`.
211. `DialogCell` получает уже рассчитанное состояние и не сортирует сам.
212. UI refresh должен использовать diff/notification, а не полный storm reload.
213. Если полного diff API нет, использовать существующий dialogs reload notification.
214. Проверить, что recycled cell очищает pin marker перед bind.
215. Проверить, что скрытая local запись не создаёт серверный badge.
216. Локальный pin не должен менять unread, mute или read state.

## Хуки для пинов

217. Найти фактическую обработку `TL_messages_toggleDialogPin` в текущем `tele` checkout.
218. [INFERENCE] PATCHLIST называет этот путь, но точная строка и callback не проверены.
219. Оставить в stock-коде вызов `TeleHooks` до/после штатного запроса.
220. Не менять generated request class.
221. Обрабатывать limit error только при включённом `LOCAL_PINS`.
222. При OFF вернуть stock callback без local write.
223. После local fallback запрос не повторять бесконечно.
224. Успешный remote pin должен удалить устаревший local duplicate.
225. Unpin callback должен различать server failure и local-only removal.
226. Найти фактический `sortDialogs` и точки его вызова.
227. [INFERENCE] `sortDialogs` назван в документах, но конкретная перегрузка может отличаться.
228. Подмешивать local order до cell adapter, а не после draw.
229. Не менять сортировку непрочитанных и muted диалогов, если это не часть pin order.
230. Проверить `MessagesStorage` load/save dialogs, не добавляя stock columns.
231. Проверить `NotificationCenter.dialogsNeedReload` и `dialogFiltersUpdated`.
232. Notification после DB completion должен идти main thread.
233. Background DB callback не должен держать ссылку на Activity.
234. При account switch очистить in-memory cache и загрузить новый account.
235. При process death восстановить v2 перед первым visible list bind.
236. Если серверный список пришёл позже local state, сначала показать безопасный stock порядок.
237. Затем выполнить merge и один refresh.
238. Не показывать local pins как подтверждённые server pins до reconciliation.

## 0124: локальные папки сверх лимита

239. Local folder — fork filter, не Telegram `dialogFilter` server object.
240. Local folder имеет title, stable local ID, include/exclude rules и order.
241. [INFERENCE] Точный набор rule fields нельзя фиксировать без desktop patch 0124.
242. Сохранить только поля, необходимые `includesDialog` и UI editor.
243. Не сериализовать `TLRPC.DialogFilter` целиком, если это меняет stock schema.
244. Серверные filters читать штатным путём.
245. Local filters хранить отдельно в `tele_kv` с account scope.
246. Local filters не участвуют в `messages.updateDialogFilter`.
247. Перетаскивание local folder не отправляет server reorder.
248. Серверный filter limit не должен блокировать создание local folder.
249. Никакое число local folder limit не придумывать.
250. [INFERENCE] Если desktop задаёт hard local cap, взять число и UX из source before coding.
251. Если hard cap отсутствует, local list растёт до безопасных device/storage limits.
252. [INFERENCE] Device/storage policy не является доказанным desktop behavior и требует решения maintainer.
253. UI title/name validation должна быть локальной и не отправляться.
254. Переименование local folder не вызывает Telegram request.
255. Удаление local folder должно удалять только local rows.
256. Удаление не должно удалять чаты из Telegram.
257. Local folder order должен сохраняться после restart.
258. Filter membership пересчитывается при dialog/filter update.
259. `includesDialog` должен получать account context явно.
260. `includesDialog` не должен читать account 0 singleton.
261. Фильтр может включать archive только если это desktop rule.
262. [INFERENCE] Правило archive для local folders надо получить из patch.
263. Скрытие All Chats и local folders не должны конфликтовать.
264. Сначала сформировать canonical filter list.
265. Затем применить `HIDE_ALL_CHATS_FOLDER` к default filter.
266. Затем добавить/удалить local filters по их setting.
267. Затем добавить unsorted synthetic filter.
268. Порядок должен быть documented и covered by tests.
269. Не отдавать synthetic filters в edit screen как remote filters.
270. Не показывать server suggestion controls для local filters.
271. Recycled tab row обязан очищать local icon/title state.
272. Filter tab selection после config change должна оставаться по stable ID.
273. Если выбранная папка удалена, fallback на All Chats без network call.
274. Local folder state не влияет на Telegram unread counters.
275. Local folder state не влияет на server read cursor.

## 0162: unsorted и принятое решение

276. `unsorted` — виртуальный filter, а не серверная папка.
277. Его вычисление использует тот же resolver, что local folders.
278. В него входят чаты, не включённые ни в один другой видимый folder.
279. Archive должен быть отдельным согласно PATCHLIST/desk analysis.
280. Чаты с unread должны оставаться в unsorted, если desktop semantics это требует.
281. [INFERENCE] Точный приоритет unread против explicit exclude надо подтвердить в desktop source.
282. Не дублировать чаты, явно включённые в local folder.
283. Не считать All Chats обычной пользовательской папкой при вычислении membership.
284. Synthetic ID должен быть зарезервирован и не конфликтовать с server filter IDs.
285. [INFERENCE] Численное значение synthetic ID не подтверждено; выбрать после аудита диапазона.
286. `getDialogFilters()` — основной hook для добавления synthetic filter.
287. Existing `HIDE_ALL_CHATS_FOLDER` hook должен сохранить свой OFF behavior.
288. `FilterTabsView` получает synthetic tab только при `UNSORTED_FOLDER` ON.
289. Settings editor не должен позволять менять synthetic rules.
290. Synthetic filter не участвует в server filter save.
291. On toggle off убрать tab и вернуть selection безопасно.
292. On toggle on пересчитать membership после загрузки filters.
293. Cache invalidation слушает `dialogFiltersUpdated`.
294. Cache также инвалидируется при local-folder add/edit/delete.
295. При process restart unsorted не требует network request.
296. При отсутствии cache fallback — пустой список до loaded dialogs, без crash.
297. Не считать temporary loading state окончательным unsorted membership.
298. Проверить forum topics и Saved Messages отдельно.
299. [INFERENCE] Участие Saved Messages в unsorted зависит от desktop rule.
300. Кнопка unsorted не должна создавать Telegram folder object.
301. Документация settings прямо говорит «локально, без синхронизации».
302. Tele server не получает folder names, IDs или membership.

## Миграции и восстановление

303. Добавить fork migration version в существующий `tele_kv` convention.
304. Не использовать `LAST_DB_VERSION`.
305. Migration runner должен быть idempotent.
306. Старый отсутствующий key означает empty state, не ошибку.
307. Pin v1 records без local bit читать как local=true.
308. После успешного v2 write старый key удалить только атомарно.
309. При write failure старый key сохранить.
310. Не мигрировать server filter rows в local rows автоматически без доказанного mapping.
311. Existing stock filters остаются stock source of truth.
312. Local folder migration должна сохранить title/order/rules, если поля поддерживаются.
313. Неподдерживаемые fields логировать как count, без содержимого.
314. Не терять local state при выключении feature.
315. Не экспортировать account IDs в global settings backup.
316. Export/import local lists — отдельное решение, не копировать автоматически.
317. [INFERENCE] PATCHLIST требует export/import для settings, но не утверждает экспорт больших peer lists.
318. До решения maintainer экспортировать только bool switches.
319. При импорте неизвестные keys пропускать и логировать key name без data payload.
320. DB migration тестировать на пустой, v1, v2 и повреждённой записи.
321. Двойной запуск migration не создаёт дублей.
322. Account A migration не читает account B.
323. Переключение аккаунта во время async migration отменяет stale UI result.
324. Удаление приложения удаляет local DB как обычные app-private данные.
325. Резервное копирование Android не должно становиться серверной синхронизацией.

## Stock hooks и потоки

326. `MessagesController.getDialogFilters()` проверен как существующий hook для All Chats gating.
327. `MessagesStorage.loadDialogFilters()` проверен как stock load path.
328. `NotificationCenter.dialogFiltersUpdated` существует и должен быть использован для invalidation.
329. `MessagesController.sortDialogs` назван в анализе как order hook.
330. [INFERENCE] Проверить конкретные overloads и не добавлять вызов по догадке.
331. `FilterTabsView` — UI hook для tab presentation, не data source.
332. [INFERENCE] Точный bind method FilterTabsView надо найти symbol search до edits.
333. `ChatActivity` — UI host для topic/Saved pin views.
334. [INFERENCE] Точный pin strip/menu callback в ChatActivity не подтверждён этим чтением.
335. `MessageMenu`/`fillMessageMenu` — существующий pattern для menu items.
336. Pin list action menu не должен обходить common menu registry без необходимости.
337. `NotificationsController.processNewMessages` — data-layer notification hook для folder mute.
338. `MessagesController.isDialogMuted` — central mute query, проверенный в Android sources.
339. [INFERENCE] Точная перегрузка `isDialogMuted(dialogId, topicId, chat)` должна быть сверена перед hook.
340. Folder mute resolver должен быть pure/read-only относительно notification callback.
341. UI notification settings changes post to main thread.
342. Notification worker may run background; it must use immutable snapshot of folder state.
343. Never query views from notification worker.
344. Never write DB synchronously from `DialogCell.onDraw`.
345. On main thread only apply prepared merged order.
346. On storage thread only parse/serialize and transact.
347. On network callback marshal result before touching local cache/UI.
348. Add account to every helper method, cache key and notification payload.
349. Test two accounts with identical dialog IDs.
350. Check holder recycling after account switch.

## 0117: скрытие сообществ

351. Setting default is false; OFF leaves recommendations and community rows stock.
352. Reuse the existing community display mode instead of inventing a second filter.
353. `MessageObject` joined-community service type is an identified candidate hook.
354. `MessagesController.getChannelRecommendations` is an identified candidate hook.
355. `ProfileActivity` community recommendation surface is an identified candidate.
356. [INFERENCE] Exact current community list adapters must be found with symbol search.
357. Apply filtering at data layer where possible, then protect visible UI fallback.
358. Do not hide ordinary channels by matching title or generic channel type.
359. Test community, group, channel and bot adjacent rows.
360. On config toggle rebuild visible list on main thread.
361. Recycled row must clear hidden placeholder and restore stock row when OFF.
362. No local storage is needed unless desktop provides a remembered per-peer exception.
363. Do not send any request to tele-server.

## 0031: переход к первому сообщению

364. Setting default is false; OFF leaves existing chat opening and history behavior unchanged.
365. Add one message-menu/chat-menu action only when toggle is ON.
366. Use stock `ChatActivity` history pagination and `scrollToMessageId` style API.
367. [INFERENCE] Exact first-message request and anchor are not confirmed; inspect current ChatActivity.
368. Do not fake message ID 1 for channels or migrated chats.
369. Use server-provided oldest message or loaded history boundary.
370. Handle empty chat, forbidden chat and deleted history without crash.
371. Keep topic root ID when jumping from a forum topic.
372. Saved Messages needs its own dialog context.
373. Action must not mark arbitrary messages read beyond stock scroll behavior.
374. Loading indicator and cancellation belong to existing ChatActivity lifecycle.
375. Do not issue duplicate pagination requests after rotation.
376. If offline, show stock failure/empty state rather than stale invented position.
377. Test cold start, warm start, archive, topic, channel and Saved Messages.

## 0082: мгновенное перемещение

378. This Android port carries only the idea of immediate move.
379. Desktop freeze/Qt animation is explicitly not ported.
380. Setting default is false; OFF uses stock move animation and behavior.
381. [INFERENCE] Exact stock move callback and adapter notification must be located first.
382. Call existing folder move operation, then refresh list without waiting for desktop-style freeze.
383. Do not bypass server filter permission checks.
384. Local-folder move writes local state only when destination is local.
385. Server-folder move keeps existing Telegram request semantics.
386. Mixed move must not leak local filter IDs to network requests.
387. Avoid optimistic UI that survives a rejected server move.
388. On failure restore the pre-move order from immutable snapshot.
389. Recycled cells must rebind after move and account switch.
390. Respect LiteMode: no new animation when reduced motion is active.
391. Test drag/tap move, cancellation, slow network and process rotation.

## 0156: mute folders and silence completely

392. Setting default is false, as required by decisions and AGENTS.
393. `isDialogMuted` is the central per-dialog decision and must consult folder mute only when ON.
394. Folder mute is local to account/device and stored in `tele_kv`.
395. A folder mute set contains stable local/server folder IDs, not chat copies.
396. [INFERENCE] Exact key shape must follow local-folder serializer after 0124.
397. Resolve chat membership with the same canonical filter resolver used by tabs.
398. Avoid recursive dependency: mute resolver must not trigger filter reload.
399. In `NotificationsController.processNewMessages`, folder mute suppresses ordinary notifications.
400. `silence completely` must also suppress mention/reply exceptions only if desktop confirms that scope.
401. [INFERENCE] The exact mention/reply branches must be verified in current NotificationsController.
402. Do not alter unread counters unless desktop patch explicitly does so.
403. Do not alter server mute settings or `notifySettings`.
404. Chat-level explicit unmute must not silently erase folder mute.
405. Folder-level unmute removes only that folder ID.
406. If a chat belongs to two muted folders, one unmuted folder is insufficient to notify it.
407. If it belongs to no muted folder, keep stock mute result.
408. Notification channel IDs remain stock; this feature creates no new channel.
409. Test foreground, background, FCM, mention, reply, topic and archive notifications.
410. Test folder rename/delete and stale folder references.
411. Clean stale mute IDs during local-folder migration, not during notification draw.
412. Log only account and boolean reason code, never peer identity.

## Settings, resources and features.md

413. Add titles/descriptions to `strings_tele.xml`; do not edit stock `strings.xml`.
414. Place 0123 under the chats or interface page chosen by current settings structure.
415. Place 0124 and 0162 under chats/interface, with child visibility only if parent is ON.
416. Place 0117 under interface/chats according to existing page contract.
417. Place 0031 and 0082 under chats.
418. Place 0156 under notifications if 0169 has landed; otherwise current closest page.
419. [INFERENCE] A notifications page may not exist before 0169; do not create a second navigation convention.
420. Every row description says whether behavior is local, server-affecting or display-only.
421. Add all bool items to export/import spec.
422. Do not export transient merged order unless maintainer approves peer-list export.
423. Add exactly one English `features.md` row per user-facing feature.
424. Row 0123: «local pins can exceed Telegram's pin limit and keep one mixed order».
425. Row 0124: «local folders can exceed Telegram's server folder limit without server sync».
426. Row 0162: «unsorted shows chats not included in another folder, with archive rules explained».
427. Row 0117: «hide community rows and recommendations from the chat UI».
428. Row 0031: «jump from a chat menu to its first available message».
429. Row 0082: «move chats immediately without desktop-only freeze animation».
430. Row 0156: «mute all chats in selected folders locally, optionally silencing exceptions».
431. Each row names settings path, default `off`, Android patch filename and current desktop number.
432. Desktop links use current numbers 0123, 0124, 0162, 0117, 0031, 0082 and 0156.
433. Do not link new 0126 as current desktop number in features.md.
434. If a patch is split, both Android patch filenames appear in the same feature row.
435. Update PATCHLIST status only after export and manual verification.

## Exact behavior and limits

436. Pin limit is the Telegram server limit returned by current account/configuration.
437. [INFERENCE] No numeric pin limit is stated in the reviewed docs; never hard-code one.
438. Local pin creation happens only after a confirmed server-limit outcome or an explicit local action defined by desktop.
439. Local pins do not count against Telegram server quota.
440. Mixed drag sends only server entries and keeps local entries on device.
441. Folder limit is the Telegram server limit; local folder records are not sent.
442. [INFERENCE] No numeric local-folder cap is stated; do not invent one.
443. `unsorted` has no server quota because it is synthetic.
444. Bookmark limits from batch 14 are unrelated and must not be reused here.
445. Mute set has no server quota and should be bounded by available local folder IDs.
446. Community hiding has no numeric limit.
447. Jump-to-beginning has no numeric limit but must respect API pagination.
448. Instant move has no numeric limit but must respect server permissions.
449. Any desktop numeric limit discovered in `git show origin/main` must be copied verbatim into this section.
450. Until then, mark it `[INFERENCE]` and leave behavior uncommitted.

## Решения и вопросы перед кодом

451. Решение: локальные пины и локальные папки не являются облачным Saved Messages.
452. Решение: один mixed order для server/local pins, а не server-first плюс local tail.
453. Решение: v1 pin records читаются как local; v2 явно хранит `local`.
454. Решение: 0162 использует тот же механизм virtual/local folders, что 0124.
455. Решение: 0162 не создаёт server filter и не отправляет membership.
456. Решение: Android defaults для всех новых switches — OFF.
457. Решение: 0156 выключен по умолчанию, включая возможный `silence completely` child.
458. Вопрос: точный numeric local-folder cap задан ли desktop patch 0124?
459. Вопрос: exact server error type/text для pin-limit в текущем `TL_messages_toggleDialogPin`?
460. Вопрос: при unpin server+local entry подтверждено ли превращение в server-only entry?
461. Вопрос: как desktop разрешает stale `hash` при совпавшем dialog ID?
462. Вопрос: входит ли Saved Messages в unsorted и local-folder membership?
463. Вопрос: сохраняется ли Archive отдельно от unsorted всегда или только при default filter state?
464. Вопрос: нужен ли отдельный `SILENCE_COMPLETELY` item либо это часть `MUTE_FOLDERS`?
465. Вопрос: должен ли export/import включать большие account-scoped peer/filter lists?
466. До ответа на вопросы код не должен выбирать числовой лимит или тихую fallback-семантику.

## Privacy and offline contract

451. Local pin order never reaches tele-server.
452. Local folder names and rules never reach tele-server.
453. Unsorted membership never reaches tele-server.
454. Mute folder state never reaches tele-server.
455. Hide communities and jump behavior send no third-party request.
456. Server pin reorder uses Telegram's existing request only for server entries.
457. Server folder changes use Telegram's existing request only for server filters.
458. Respect existing Android offline/connection switches where they gate fork network work.
459. Do not add a tele-server fallback for a missing peer or folder.
460. Keep local identifiers inside app-private storage.
461. Logcat must not expose peer IDs if privacy logging is disabled.
462. Export/import must not accidentally upload local lists through telemetry.
463. Account switching is a privacy boundary, not merely a UI refresh.
464. Clearing app data clears local list state as expected for app-private data.

## Test plan: defaults and toggles

465. Build a debug APK with all seven toggles OFF.
466. Compare list tabs, pins, folders, communities and notifications with stock behavior.
467. Confirm no `tele` DB writes occur when each feature is OFF.
468. Turn only `LOCAL_PINS` ON; pin at server limit and exceed it.
469. Verify local pin appears and survives process kill.
470. Drag server above local, local above server and mixed ranges.
471. Verify remote request contains server subset only.
472. Unpin server/local combinations and verify merge transitions.
473. Repeat in main, Archive, custom filter, forum topic and Saved Messages.
474. Turn `LOCAL_FOLDERS` ON; create, rename, reorder and delete local folders.
475. Verify server folder list and requests are unchanged by local-only operations.
476. Restart and verify local folder order and membership.
477. Turn `UNSORTED_FOLDER` ON; verify unfiled chats appear.
478. Put a chat into another folder and verify it leaves unsorted.
479. Test archive and unread behavior against agreed desktop rule.
480. Turn `HIDE_COMMUNITIES` ON/OFF while recommendations are visible.
481. Verify ordinary channels are not hidden accidentally.
482. Turn `JUMP_TO_BEGINNING` ON and test old, empty, deleted and paginated chats.
483. Turn `INSTANT_CHAT_MOVE` ON/OFF and verify rejected remote moves restore state.
484. Turn `MUTE_FOLDERS` ON; test normal, mention, reply and background notifications.
485. If separate silence control exists, test it independently and with parent OFF.
486. Switch accounts while each list is loaded and verify no cross-account state.
487. Rotate activity and kill process during every asynchronous operation.
488. Test LiteMode ON and OFF for moves and tab refresh animations.
489. Verify recycled rows after scrolling far enough to reuse holders.
490. Verify no behavior changes after toggles are disabled without restart.

## Logcat and diagnostic checks

491. Use a dedicated tag such as `TeleLocalLists`; confirm exact tag before implementation.
492. Log operation names: `load`, `migrate`, `merge`, `write`, `server-fallback`.
493. Log counts and scope class, not peer IDs or titles.
494. Log migration version transitions, not JSON payloads.
495. Log rejected server move as error class, not request body.
496. Log account number only if existing Tele diagnostics permit it.
497. On DB parse failure log version and exception class, then use safe empty fallback.
498. On callback after account switch log stale callback discarded.
499. On UI update from background thread log a violation during debug builds.
500. Confirm OFF produces no local-list log lines.
501. Confirm local pin produces no tele-server HTTP log.
502. Confirm local folder and unsorted operations produce no Telegram folder request.
503. Confirm remote pin order logs only server request count.
504. Remove verbose diagnostics or gate them behind existing debug setting before release.
505. Never log filter membership, usernames, message text or bookmark-like previews.

## Pitfalls and review checklist

506. Do not use one process-global list for all accounts.
507. Do not append local pins after all server pins; redesign requires interleaving.
508. Do not treat v1 records as server records; v1 means local.
509. Do not call server reorder with local IDs.
510. Do not store local filters in stock `dialog_filter` rows.
511. Do not use a negative synthetic ID without checking stock ID allocation.
512. Do not let `getDialogFilters()` recursively call itself while building unsorted.
513. Do not mutate `dialogFilters` while iterating it in `includesDialog`.
514. Do not change All Chats hiding when local features are OFF.
515. Do not calculate mute membership from a recycled view.
516. Do not update notification UI from a DB thread.
517. Do not infer a folder's archive behavior from its title.
518. Do not hide every channel when hiding communities.
519. Do not fabricate message ID 1 as the first message.
520. Do not reuse desktop freeze code on Android.
521. Do not ignore server error callbacks after optimistic move.
522. Do not clear local state when a setting is switched OFF.
523. Do not create duplicate search items for aliases.
524. Do not claim a limit number without source evidence.
525. Do not modify `TLRPC.java`, stock DB schema or generated patches by hand.
526. Do not claim success from compilation alone.
527. Keep stock hunks minimal so upstream rebases remain reviewable.
528. Review every added hook for OFF path equivalence.
529. Review every cache for account and scope keying.
530. Review every holder for bind-time reset.
531. Review every network path for local-only short circuit.

## Batch gate

532. All seven commits must be committed on Android branch `tele`.
533. All seven commits must be exported into `patches/android/`.
534. `features.md` must contain all user-facing rows before the gate.
535. PATCHLIST rows remain `todo` until export; then use the repository status flow.
536. Assemble `./gradlew :TMessagesProj_App:assembleDebug` with all batch changes.
537. Install the correct ABI APK on a device or emulator.
538. Exercise every toggle ON, OFF and default where applicable.
539. Exercise all listed scopes: main, archive, filter, topic and Saved Messages.
540. Exercise process death, account switch, rotation and recycled rows.
541. Exercise offline and server-error paths without tele-server traffic.
542. Capture logcat for migration, merge, server fallback and stale callbacks.
543. Hand the APK to a human for the device checks above.
544. Only human verification may change status to `done`.
545. A build passing without manual list and notification checks is not a closed gate.
546. If a limit or desktop transition remains unresolved, leave it as `[INFERENCE]` and block only that implementation decision.
547. Do not silently narrow the batch to the easiest rows.
548. Do not mark 0162 done before 0124 local folders are verified.
549. Do not mark 0156 done before folder membership and notification exceptions are verified.
550. The batch is complete only when pin, folder, unsorted, community, jump, move and mute behavior all pass.
