# Пачка 24: студия подарков

## 1. Назначение и границы

1. Этот документ — пошаговое руководство реализации пачки 24 для Android-ветки `tele`.
2. План источника — `docs/PATCHLIST.md`, текущая пачка 24 «студия подарков».
3. В пачке семь строк: 0197, 0204, 0234, 0198, 0201, 0247 и 0248.
4. Источник номеров — текущая очередь desktop `origin/main`, не старые номера v7.2.9.
5. `desktop-numbers.md` нужен для сверки старых номеров; для этой пачки используем 0197/0198/0201/0204/0234/0247/0248.
6. Цель первого среза — собрать подарок и сохранить корректный PNG.
7. Первый срез не должен ждать видео, GIF, WebM или TGS.
8. После PNG добавляются расширения студии отдельными коммитами.
9. Fake upgrade — локальная симуляция, не покупка и не изменение подарка на сервере.
10. Gift grid использует тот же модельный рендер, что и студия.
11. Rarity отображается как данные каталога, а не как серверная операция.
12. Третьесторонние данные `api.changes.tg` разрешены только при отдельном переключателе.
13. Переключатель каталога по умолчанию выключен.
14. При выключенном переключателе сторонний HTTP-запрос не выполняется.
15. Telegram API остаётся источником данных для Telegram-подарков и профилей.
16. Реализация не должна включать реальные покупки, апгрейды или списания Stars.
17. Тестирование выполняется на тестовом аккаунте и тестовом подарке без оплаты.
18. Аккаунт мейнтейнера запрещён для покупок и платежных проверок.
19. Все неуточнённые детали протокола помечаются `[INFERENCE]`.
20. Нельзя выдумывать URL, поля ответа или лимиты `api.changes.tg`.

## 2. Обязательное чтение и факты

21. Перед работой прочитать `AGENTS.md`.
22. Перед работой прочитать текущий раздел пачки 24 в `PATCHLIST.md`.
23. Прочитать разделы пачек 23 и 26.
24. Пачка 23 содержит локальный пароль Stars/подарков и массовые действия.
25. Пачка 23 ставит локальный пароль первым и использует его как гейт платёжных точек.
26. Пачка 24 зависит от 0198, 0204 и 0234 согласно плану.
27. Строка 0198 в плане зависит от 0201, хотя реализационно базовый ролл строится вместе.
28. Пачка 26 — кошелёк, движок и ключи; сама студия не требует wallet API.
29. Кошелёк становится зависимостью только для будущего дизайна money-карты.
30. Нельзя включать wallet-код в пачку 24 без отдельной строки плана.
31. Прочитать `decisions.md`: мейнтейнер решил портировать студию.
32. Решение мейнтейнера включает 0197, 0204, 0234 и fake upgrade 0198/0201.
33. В решениях указано: `api.changes.tg` используется как на desktop и скрыт тумблером.
34. В решениях указано: fake upgrade должен иметь roll-анимацию.
35. В решениях указано: 0201 идёт вместе с 0198.
36. В решениях указано: поддерживается история версий и каталоги, но без покупки.
37. Прочитать `portability.md`: Android имеет Canvas, RLottie и `StarGiftPatterns`.
38. Прочитать `desktop-numbers.md`: номера в этой пачке уже текущие.
39. Прочитать `architecture.md`: fork-код размещается в новых файлах `tele/`.
40. Прочитать `development.md`: код меняется в checkout `Telegram`, не в `main`.
41. По заданию файл этого руководства — единственное изменение в `main`.
42. Чекаут Android проверялся через `git show tele:<path>`.
43. Desktop-патчи проверялись через `git show origin/main:<patch>`.
44. Desktop 0197 добавляет отдельные модули data/render/export/store/video.
45. Desktop 0197 содержит студию, owned, sweep, код ссылки и экспорт.
46. Desktop 0198 добавляет fake upgrade и историю роллов.
47. Desktop 0201 вращает номер и модель до завершения ролла.
48. Desktop 0204 добавляет сетку, строки, drag, сохранение и экспорт.
49. Desktop 0234 добавляет custom models и regular gifts.
50. Desktop 0247 импортирует подарки любого пира.
51. Desktop 0248 добавляет rarity tiers и rarity pills.

## 3. Точки Android и существующий код

52. Стоковый путь подарков находится в `org.telegram.ui.Stars` и `org.telegram.ui.Gifts`.
53. Проверить `StarGiftSheet.java` перед добавлением любого хука.
54. В `StarGiftSheet.java` `doUpgrade()` находится около строки 6199.
55. В `StarGiftSheet.java` результат применяется через `applyNewGiftFromUpdates()`.
56. Эти методы private; не дублировать весь sheet в fork-коде.
57. Если нужен доступ, сделать минимальный `public tele_` API по правилам AGENTS.
58. `StarGiftPreviewSheet.java` уже рисует preview и использует Canvas.
59. `StarGiftPatterns.java` уже рисует фоновые узоры на Canvas.
60. `ProfileGiftsView.java` уже рисует gift stickers, фон и частицы.
61. `StarsController.java` содержит списки подарков и запросы `TL_stars`.
62. `StarsController.getProfileGiftsList(dialogId)` — существующий профильный источник.
63. `StarsController.GiftsCollections` — существующий источник коллекций.
64. `ProfileGiftsContainer` — UI-путь списка подарков профиля.
65. `GiftSheet.GiftCell` — desktop-оценка называет его переиспользуемым рендерным ориентиром.
66. Сначала проверить точный класс GiftCell в текущем checkout; не предполагать пакет.
67. `StarsIntroActivity.setGiftImage` уже устанавливает изображение модели.
68. `RLottieDrawable` используется в gift sheet для анимированных моделей.
69. `LiteMode` уже ограничивает частицы и анимации в gift UI.
70. Любая новая анимация должна уважать `LiteMode.FLAG_PARTICLES`.
71. Проверить существующий animation duration и не создавать бесконечный invalidate.
72. `TeleConfig.kt` содержит `BoolItem`, `IntItem`, `FloatItem`, `StringItem`.
73. В `TeleConfig` настройки хранятся в `tele_config` SharedPreferences.
74. Вся новая настройка добавляется в `TeleConfig` с явным default.
75. Фичевые тумблеры должны иметь default `false`.
76. Сторонний каталог не может быть включён скрытым или аварийным fallback.
77. `TeleSettingsActivity` сейчас имеет `MODE_INTERFACE`, `MODE_IDS`, `MODE_DATA` и другие режимы.
78. Для студии предпочтительно добавить отдельную страницу gifts/studio.
79. Отдельный режим страницы — проектное решение; если его нет, использовать interface только временно.
80. `[INFERENCE]` Название нового режима может быть `MODE_GIFTS`; подтвердить перед кодом.
81. `TeleSearch` использует числовые GUID, сейчас существующие GUID начинаются с 950.
82. Диапазон 1360..1379 зарезервировать для этой пачки.
83. Числа ниже — предложенная стабильная схема, `[INFERENCE]`, пока не утверждена.
84. 1360 — `tele gift studio` страница.
85. 1361 — `gift studio` основной экран.
86. 1362 — `gift studio api catalog`.
87. 1363 — `gift studio png export`.
88. 1364 — `gift studio copy png`.
89. 1365 — `gift studio favorites`.
90. 1366 — `gift studio history`.
91. 1367 — `gift studio fake upgrade`.
92. 1368 — `gift roll animation`.
93. 1369 — `hide gift number during roll`.
94. 1370 — `hide gift model during roll`.
95. 1371 — `gift grid`.
96. 1372 — `gift grid saved layouts`.
97. 1373 — `gift grid any profile`.
98. 1374 — `gift studio more models`.
99. 1375 — `gift studio custom model`.
100. 1376 — `gift studio rarity`.
101. 1377 — `gift studio sweep`.
102. 1378 — `gift studio external catalog`.
103. 1379 — `gift studio export formats`.
104. Не переиспользовать GUID старых страниц для новых rows.
105. Добавить в поиск русские и английские слова для каждого пункта.
106. Поиск должен открывать страницу, а не запускать сетевой запрос.
107. Search IDs не являются account IDs и не уходят в сеть.

## 4. TeleConfig и экспорт настроек

108. Минимальный обязательный тумблер — `GIFT_STUDIO` default false.
109. Второй обязательный тумблер — `GIFT_STUDIO_EXTERNAL_CATALOG` default false.
110. Вызов external catalog всегда проверяет второй тумблер в сетевом слое.
111. Не полагаться только на видимость строки в UI.
112. `FAKE_GIFT_UPGRADE` default false, если функция имеет отдельный switch.
113. `GIFT_ROLL_ANIMATION` default false либо следует fake upgrade; решить явно.
114. `[INFERENCE]` Рекомендуется один master `FAKE_GIFT_UPGRADE` и дочерняя настройка roll.
115. `GIFT_GRID` default false до завершения PNG renderer.
116. `GIFT_RARITY` default false, если это отдельная display-фича.
117. `GIFT_EXPORT_VIDEO` default false до ручной проверки MediaCodec.
118. `GIFT_EXPORT_TGS` default false до проверки sticker-проверок.
119. `GIFT_CUSTOM_MODELS` default false до проверки загрузки `.tgs`.
120. Никакая настройка не должна менять Telegram API payload при выключении.
121. Для каждого Item добавить строку в спецификацию export/import.
122. Export должен сохранять только пользовательские настройки и локальные presets.
123. Export не должен сохранять account IDs, gift owner IDs или сообщения.
124. External URL можно экспортировать только как явный пользовательский preference.
125. Известный внешний каталог нельзя включать импортом без подтверждения.
126. Unknown settings при import пропускаются с логом по существующему правилу.
127. Если export/import helper ещё не выделен, не создавать второй формат без решения.
128. Названия ключей — snake_case и стабильны после релиза.
129. Рекомендуемые ключи: `gift_studio`, `gift_studio_external_catalog`.
130. Рекомендуемый ключ: `gift_fake_upgrade`.
131. Рекомендуемый ключ: `gift_roll_animation`.
132. Рекомендуемый ключ: `gift_grid`.
133. Рекомендуемый ключ: `gift_rarity`.
134. Рекомендуемые ключи форматов: `gift_export_png`, `gift_export_video`, `gift_export_tgs`.
135. Значения по умолчанию повторяют stock, то есть выключены.
136. Переключение настройки должно вызывать `TeleHooks.onConfigChanged`.
137. Изменение настройки не должно требовать рестарта, кроме тяжёлого renderer bootstrap.
138. Если рестарт действительно нужен, явно показать это в описании строки.
139. `[INFERENCE]` Для первой PNG-версии рестарт не должен быть нужен.

## 5. Порядок коммитов и оценка

140. Коммит 1: `feat: add gift studio png renderer`.
141. Усилие коммита 1 — L по плану, но scope ограничен PNG.
142. Коммит 1 добавляет экран, state, Canvas renderer и сохранение PNG.
143. Коммит 1 использует Telegram gift data и не требует external catalog.
144. Коммит 1 добавляет `features.md` строку для PNG studio.
145. Коммит 2: `feat: add gift studio catalog`.
146. Усилие коммита 2 — M/L из-за HTTP, cache и протокола.
147. Коммит 2 добавляет `api.changes.tg` только за OFF-by-default toggle.
148. Коммит 2 добавляет модели, backdrops, symbols и custom text если ответ это подтверждает.
149. Коммит 3: `feat: add gift studio exports`.
150. Усилие коммита 3 — M; PNG остаётся базовым результатом.
151. Коммит 3 добавляет copy/share/save hooks и локальные favorites/history.
152. Коммит 4: `feat: add fake gift upgrade roll`.
153. Усилие коммита 4 — M; реальные `buyStarGift` пути не трогать.
154. Коммит 4 добавляет локальный случайный выбор с rarity weights.
155. Коммит 5: `feat: hide gift roll result details`.
156. Усилие коммита 5 — S, но его можно объединить с коммитом 4.
157. Коммит 5 закрывает номер и модель до конца ролла.
158. Коммит 6: `feat: add gift grid builder`.
159. Усилие коммита 6 — L; renderer переиспользуется из коммита 1.
160. Коммит 6 добавляет drag/reorder, rows, saved grids и export PNG.
161. Коммит 7: `feat: add gift studio rarity labels`.
162. Усилие коммита 7 — S.
163. Коммит 7 добавляет tier parsing и pills только при наличии данных.
164. Коммит 8: `feat: open any profile gifts in grid`.
165. Усилие коммита 8 — M; зависит от grid и profile gifts list.
166. Коммит 9: `feat: add gift studio formats`.
167. Усилие коммита 9 — L; MediaCodec/rlottie/TGS проверяются отдельно.
168. Коммит 9 не должен блокировать PNG-релиз.
169. Если queue conventions требуют один patch на одну строку, разделить коммиты 1–9.
170. Не редактировать `.patch` вручную.
171. Экспортировать commits из `Telegram` через `git format-patch`.
172. Только после экспорта обновить статусы и `features.md`.
173. `[INFERENCE]` Точные subject names должны соответствовать фактическому объёму diff.
174. Не обещать L-функции в features.md до ручной проверки.

## 6. PNG-first: модель данных и renderer

175. Первый экран принимает выбранную коллекцию и модель.
176. Источник обычного Telegram gift — `StarsController` и `TL_stars`.
177. Источник уникального gift — `TL_stars.TL_starGiftUnique` или saved gift.
178. Нужные атрибуты ищутся через существующие `StarsController.findAttribute` helpers.
179. Обязательные части renderer: backdrop, pattern/symbol, model, title, number.
180. Missing attribute не должен приводить к null dereference.
181. Nullable TL-поля проверять до чтения.
182. Renderer должен иметь чистую функцию состояния → Canvas operations.
183. UI View и Bitmap renderer не должны расходиться по геометрии.
184. Для PNG создать `Bitmap.Config.ARGB_8888`.
185. Размер bitmap задаётся явным preset, а не размером экрана.
186. `[INFERENCE]` Presets cover/tile/sticker/card требуют согласования размеров.
187. До согласования сделать один документированный дефолтный размер.
188. Не выводить bitmap размером из `dp` напрямую без density policy.
189. Scale должен быть умножением целевого размера, а не растяжением после рендера.
190. Ограничить максимальное число пикселей до allocation.
191. `[INFERENCE]` Конкретный максимум нужно взять из desktop policy либо утвердить.
192. При превышении максимума показать ошибку и ничего не сохранять.
193. Не держать одновременно UI bitmap и export bitmap без необходимости.
194. После записи вызвать `recycle` только если объект больше не используется.
195. PNG сохранять через `MediaStore` в Pictures/tele либо через существующий helper.
196. Проверить Android API policy для public Pictures без legacy path.
197. Для share использовать существующий `FileProvider` pattern из `ViewAsTl`.
198. Для copy PNG положить PNG bytes в clipboard как URI с grant permission.
199. Не класть приватный gift JSON в clipboard вместе с PNG.
200. Имя файла очищать от `/`, `\\`, control chars и чрезмерной длины.
201. Имя файла не должно содержать Telegram username или peer ID.
202. `[INFERENCE]` Формат имени: collection-model-number.png; утвердить privacy wording.
203. Сохранение в Pictures требует scoped-storage-safe code.
204. Ошибка MediaStore должна быть видна пользователю и попасть в FileLog без данных gift.
205. Renderer работает с последним состоянием на UI thread.
206. Загрузку модели и JSON выполнять на background queue.
207. После background result делать `AndroidUtilities.runOnUIThread`.
208. Проверять generation token перед применением старого ответа.
209. Не обновлять detached Activity или destroyed Fragment.
210. Account берётся из текущего fragment/sheet, не из account 0.
211. `StarsController.getInstance(currentAccount)` обязателен.
212. `MessagesController.getInstance(currentAccount)` обязателен.
213. `UserConfig.getInstance(currentAccount)` обязателен.
214. Gift bitmap не должен менять stock gift sheet state.
215. Если rendering uses ImageReceiver, дождаться loaded image либо показать ошибку.
216. Не сохранять placeholder как успешный PNG.
217. PNG smoke test должен проверять alpha, размеры и наличие ненулевых пикселей.
218. Такой smoke test — локальный renderer test, не покупка и не сетевой тест.

## 7. Каталог api.changes.tg

219. `api.changes.tg` — третьесторонний источник, не Telegram endpoint.
220. Вызов разрешён только при `GIFT_STUDIO_EXTERNAL_CATALOG == true`.
221. Проверка toggle находится в самом HTTP client, а не только в Activity.
222. При OFF не создавать URL connection, OkHttp call или DNS lookup.
223. При OFF не читать cached external data как будто она свежая.
224. Cached data можно показывать локально только после явного решения privacy policy.
225. Рекомендуемое поведение OFF — stock Telegram catalog и локально сохранённые presets.
226. `[INFERENCE]` Показ старого внешнего cache при OFF требует отдельного opt-in и описания.
227. Сначала выписать фактические endpoints из desktop 0197/0234 patch.
228. Не переносить endpoint по названию из комментария или документа без ответа сервера.
229. Для каждого endpoint записать method, path, query, headers и response schema.
230. Если desktop строит URL динамически, перенести правила нормализации отдельно.
231. Если API не документирует versioning, зафиксировать observed schema в тестовом fixture.
232. Не отправлять account ID, username, phone, contacts, message IDs или gift owner IDs.
233. Внешний запрос должен содержать только публичный catalog key и app protocol data.
234. `[INFERENCE]` Даже публичный gift slug нельзя считать безопасным без проверки desktop request.
235. Подтвердить, какие query fields нужны для collection/model/backdrop/symbol.
236. Ответ валидировать ограничениями до JSON mapping.
237. Не принимать массивы неограниченного размера.
238. Не загружать произвольные URL из response без allowlist схемы.
239. Допустимы только HTTPS URL, если desktop protocol не докажет иное.
240. Запретить redirects на HTTP и file/content URI.
241. Ограничить response body до согласованного размера.
242. `[INFERENCE]` Лимит 4 MiB известен для TeleServer, но не переносится автоматически сюда.
243. Для каталога нужен отдельный лимит, полученный из API contract.
244. Таймауты connect/read/write задать явно.
245. Не ретраить 4xx, schema errors и authentication-like errors.
246. Для 429 соблюдать `Retry-After`, если он присутствует.
247. Для 5xx разрешить ограниченный exponential backoff.
248. Backoff не должен блокировать UI thread.
249. Ограничить параллельные catalog requests одним на account/catalog key.
250. Debounce повторный выбор коллекции в UI.
251. Cancel obsolete model request при смене коллекции.
252. Cache key включает catalog version и collection/model key.
253. Cache сохранять в fork storage, не в stock DB.
254. Не смешивать external cache между аккаунтами, если response содержит owned data.
255. Для публичных parts cache можно shared, но `[INFERENCE]` это требует privacy review.
256. Предпочтительно key cache по account и catalog revision до решения.
257. Cache TTL брать из response headers либо desktop contract.
258. Не выдумывать TTL; при отсутствии TTL использовать explicit conservative value после решения.
259. ETag/If-None-Match использовать только если API это поддерживает.
260. Нельзя логировать полный URL с чувствительными query values.
261. В FileLog писать host, path category, status, latency и schema error code.
262. Не писать raw response, model JSON или external URLs в обычный logcat.
263. Для users включить объяснение, что включение отправляет запрос третьей стороне.
264. При network OFF fork switch запрос блокируется на низком уровне.
265. Применить тот же offline guard, что требует `AGENTS.md` для tele network.
266. `[INFERENCE]` Конкретное имя offline switch нужно найти в актуальном TeleConfig перед кодом.

## 8. Форматы и ограничения

267. PNG — обязательный первый формат.
268. PNG не требует MediaCodec и не требует native encoder.
269. GIF требует кадровый renderer и ограничение количества кадров.
270. MP4 требует MediaCodec и постоянный frame timing.
271. WebM требует codec availability на конкретном устройстве.
272. TGS требует JSON layer rules, gzip policy и Telegram sticker constraints.
273. Не объявлять GIF/MP4/WebM/TGS поддержанными только потому, что кнопка нарисована.
274. Desktop 0197 явно имеет отдельные video и TGS modules.
275. Android должен иметь отдельные format capability checks.
276. `MediaCodecList` проверять до показа export action.
277. Codec failure возвращать в UI как unsupported, не как пустой файл.
278. rlottie model frames читать через существующий `RLottieDrawable` API.
279. Не обращаться к RLottie из background thread, если API не гарантирует thread safety.
280. Кадр для PNG можно получить без запуска бесконечной animation.
281. LiteMode должен отключать декоративные частицы и снижать анимацию.
282. В LiteMode fake roll обязан иметь короткую или отсутствующую animation.
283. Не отключать финальный статичный результат в LiteMode.
284. TGS gzip OS byte fix относится к desktop 0230, не к основному PNG commit.
285. Если TGS добавляется, связать отдельным патчем с 0230 и описать лимиты.
286. Стикерные ограничения должны проверяться до сохранения `.tgs`.
287. Экспорт MP4 не может обещать прозрачность: H.264 её не имеет.
288. `[INFERENCE]` WebM alpha зависит от codec/profile устройства и требует matrix test.
289. Размер canvas для видео должен быть чётным, если codec требует even dimensions.
290. Указать пользователю, если codec уменьшил requested size.
291. Не создавать raw frame для каждого кадра без bounded pool.
292. Не держать весь GIF/MP4 в RAM.
293. Сохранять временные frames в cache/files и удалять в finally.
294. При отмене Activity закрывать codec, muxer и streams.
295. Partial output удалять или помечать как incomplete.
296. Share action доступен только после atomic close.
297. Формат export выбирается только после capability check.
298. PNG output может использовать MediaStore pending row и publish после записи.
299. Удалять pending row при исключении.
300. Проверять свободное место до большой операции.
301. Свободное место не заменяет allocation limit.
302. Ошибки OutOfMemory перехватывать на границе export и показывать безопасную ошибку.
303. Не отправлять экспортированный файл автоматически.
304. Send/share требует явного действия пользователя.

## 9. Fake upgrade и roll

305. Fake upgrade не вызывает `StarsController.buyStarGift`.
306. Fake upgrade не вызывает `payments.getPaymentForm`.
307. Fake upgrade не вызывает `payments.sendStarsForm`.
308. Реальный `StarGiftSheet.doUpgrade()` должен оставаться платёжным путём.
309. Хук fake должен срабатывать только в отдельной fork action.
310. При выключенном fake toggle stock menu и stock payment не меняются.
311. Локальный результат строится из доступных public attributes.
312. Атрибуты можно брать из `getStarGiftUpgradePreview`/upgrade attributes, если это только preview.
313. Проверить фактические TL constructors в текущем `TL_stars`.
314. Не создавать Java-класс для отсутствующего generated TL типа.
315. Не редактировать `TLRPC.java`.
316. Если нужного поля нет, передать maintainer blocker вместо генерации фиктивного поля.
317. Rarity weights должны быть получены из фактического model/backdrop data.
318. При отсутствии weight использовать deterministic fallback и явно показать unknown.
319. Не считать равномерный random «rarity weighted» без доказанного веса.
320. Для reproducible debug test поддержать seed, но не хранить секреты.
321. Production fake result может использовать secure random, если это не платежный токен.
322. Number выдавать локально и не путать с серверным unique gift number.
323. Slug fake result не должен быть отправляемым Telegram slug.
324. В UI явно писать `fake`/`local preview`.
325. Историю fake results хранить отдельно от saved gifts.
326. История не должна появляться в профиле как owned gift.
327. История должна быть ограничена количеством и размером payload.
328. Не хранить полный model JSON без лимита.
329. `[INFERENCE]` Размер history limit нужно согласовать; desktop имеет собственный лимит.
330. Roll state имеет phase: preparing, rolling, final, failed, cancelled.
331. В phase rolling number скрывается либо показывает placeholder.
332. В phase rolling model скрывается либо рисуется нейтральный placeholder.
333. Не показывать финальные number/model в accessibility text до final.
334. В phase final атомарно раскрыть number, model и rarity.
335. Roll cancellation не должен оставлять скрытый UI в открытом sheet.
336. `onDetachedFromWindow` отменяет callbacks и animations.
337. Использовать generation token для background model responses.
338. Номер и модель меняются на UI thread.
339. Timer очищается при final, failure и dismiss.
340. LiteMode уменьшает duration или заменяет roll статичным переходом.
341. Системная reduced motion policy должна быть уважена вместе с LiteMode.
342. У fake roll не должно быть сетевого запроса за оплатой.
343. Разрешён только запрос публичных preview/catalog data при соответствующем toggle.
344. В logcat писать `fake_roll_start`, `fake_roll_done`, `fake_roll_cancel` без account data.
345. Не логировать random seed в release-like builds.

## 10. Gift grid и любой пир

346. Grid строится поверх PNG renderer, а не копирует его.
347. 0204 добавляет grid cells, rows, drag/reorder и saved grids.
348. 0247 добавляет импорт подарков любого профиля/пира.
349. Профильный источник — `StarsController` с явным `dialogId`.
350. `dialogId` передавать из открытого profile fragment.
351. Не читать профильные gifts через account 0.
352. Для current account проверить access/visibility как делает stock.
353. Не обходить Telegram privacy, hidden или unsaved flags.
354. Сохранённый grid должен хранить публичный gift reference и display options.
355. `[INFERENCE]` Формат reference нужно выбрать после проверки TL identity fields.
356. Не хранить полный `TLRPC` object как устойчивую базу без versioning.
357. При удалённом/недоступном gift cell показывать missing state.
358. Missing state нельзя silently заменить чужим gift.
359. Grid cells должны иметь stable order и row index.
360. Drag reorder работает только на UI thread.
361. Recycler/View recycling обязан повторно bind-ить selected/hidden/ribbon state.
362. Для long lists применять bounded visible rendering.
363. Не создавать View на каждую ячейку всего профиля.
364. Export grid ограничить числом rows и cells после согласования.
365. `[INFERENCE]` Desktop patch показывает лимит rows/cells, но Android limit нужно подтвердить.
366. Saved grids хранить в `tele_*` таблице или `tele_kv` JSON.
367. Малый список presets допустимо хранить в `tele_kv`.
368. Большие grids лучше отдельной `tele_gift_grids` таблицей.
369. Не изменять stock DB version и stock SQL schema.
370. Account scope должен быть частью storage key/table column.
371. Gift grid data не синхронизируется в Telegram cloud без отдельного решения.
372. Переименование grid локальное.
373. Delete grid удаляет только fork data и не удаляет gifts.
374. Import from another peer выполняется read-only.
375. Доступ к чужим gifts не должен создавать payment action.
376. `Open in gift grid` меню гейтится `GIFT_GRID`.
377. `Grid` settings page открывает saved grids без внешнего HTTP при OFF.
378. Rarity pill показывает unknown, если rarity отсутствует.
379. Rarity tier enum маппить только по подтверждённым response values.
380. Не считать неизвестный tier legendary по умолчанию.

## 11. Хранилище и приватность

381. SharedPreferences годятся для booleans и небольших options.
382. `TeleDatabaseHelper` уже создаёт `tele_kv` и fork tables.
383. Catalog cache, history и grids не помещать в stock tables.
384. Разделить ключи по account, если данные могут быть account-specific.
385. Cache metadata: revision, fetchedAt, etag if supported, byte size.
386. При чтении cache проверять schema version.
387. Corrupt JSON удалять атомарно и писать короткий FileLog.
388. Запись через temp file/transaction и rename.
389. Не писать external response прямо поверх рабочей версии.
390. Ограничить cache disk usage и удалять oldest entries.
391. `[INFERENCE]` Точные cache TTL/size лимиты требуют maintainer decision.
392. История fake result не содержит Telegram auth data.
393. User-owned gift list может содержать account-private data; не отправлять наружу.
394. External catalog request не должен включать owned list.
395. Публичный slug и model key валидировать перед HTTP.
396. Sanitise text labels перед Canvas и filenames.
397. Ограничить длину title/subtitle/number.
398. Запретить control chars и bidi spoofing в filename.
399. Не сохранять secret/payment forms в studio state.
400. Не вызывать локальный пароль Stars для чистого PNG preview.
401. Если action способен купить/изменить gift, сначала гейт пачки 23.
402. Fake upgrade не должен обходить пароль для реального payment action.
403. Batch 26 wallet не должен появляться в gift studio menu.
404. Wallet card design — отдельная зависимость будущей пачки 27.
405. Никакого TON transfer, purchase, upgrade или collection mutation из studio.
406. Проверять notification/account lifecycle при logout.
407. На logout очищать account-scoped in-memory callbacks.
408. Shared public cache не должен пережить logout с private fields.
409. В privacy UI объяснить third-party catalog request.
410. При OFF показывать только stock/local content.

## 12. Потоки, аккаунты и lifecycle

411. Activity/Fragment creation и View binding — main thread.
412. HTTP, disk JSON, model parsing и Bitmap compression — background queue.
413. Telegram callbacks из ConnectionsManager переходят на main перед UI.
414. `MessagesStorage` callbacks не трогают View напрямую.
415. Canvas draw выполняется на UI thread.
416. Не запускать network из `onDraw`.
417. Не запускать disk write из `onDraw`.
418. Debounce controls and cancel previous request.
419. Store `currentAccount` in screen/state constructor.
420. All account callbacks capture account and validate it before applying.
421. On account switch close or recreate studio; do not reuse state silently.
422. On fragment destroy cancel HTTP, file and animation callbacks.
423. On configuration change restore only local selection, not stale response.
424. Saved state must not include bitmap bytes.
425. Recreate bitmap from bounded state or discard it.
426. `TeleHooks.onConfigChanged` refreshes visible settings and menu actions.
427. Menu actions re-evaluate toggle on every open.
428. Recycler holders rebind every selected/hidden/rating flag.
429. Use `AndroidUtilities.runOnUIThread` for callbacks.
430. Use account-specific `NotificationCenter` when observing gifts.
431. Remove observers in `onDestroy`/detach.
432. LiteMode updates must invalidate studio animation safely.
433. Background worker must not retain Activity context.
434. Use application context for cache/storage.
435. Use fragment context only for UI and permission/share.

## 13. Manual tests and logcat

436. Before tests install debug APK built from full queue.
437. Use a secondary test account, never maintainer account for purchases.
438. Use a gift that is already available; do not buy it.
439. Test default OFF after clean install.
440. Open gift menu with all new toggles OFF.
441. Confirm no studio-only action changes stock gift display unexpectedly.
442. Confirm no `api.changes.tg` request in logcat with external catalog OFF.
443. Confirm no DNS/HTTP connection to external host with external catalog OFF.
444. Turn `GIFT_STUDIO` ON without external catalog.
445. Open studio from settings and from allowed gift menu.
446. Select collection, model, backdrop and symbol.
447. Render default card and inspect no clipping.
448. Save PNG to Pictures/tele.
449. Reopen PNG from system gallery.
450. Verify dimensions, alpha and no zero-byte file.
451. Copy PNG and paste/share it to a test destination manually.
452. Verify cancellation removes pending MediaStore row.
453. Rotate device during render and save.
454. Background result must not update destroyed screen.
455. Switch account while catalog is loading.
456. Verify old account result is discarded.
457. Enable external catalog and capture host/path/status metadata only.
458. Verify response schema rejection with malformed fixture, not live destructive call.
459. Test timeout and airplane mode.
460. Test 429/5xx behavior using local fixture or controlled test endpoint.
461. Confirm rate limiting prevents request storm when tapping model repeatedly.
462. Enable fake upgrade.
463. Open only a gift eligible for preview/fake operation.
464. Confirm UI labels result as fake/local preview.
465. Observe rolling number/model are hidden until final.
466. Confirm final rarity and selected attributes appear together.
467. Dismiss during roll; no callback or leaked animation.
468. Repeat fake roll and inspect bounded local history.
469. Confirm Stars balance unchanged before and after.
470. Confirm no payment request in logcat.
471. Confirm `buyStarGift`, `sendStarsForm` and payment form are absent.
472. Test LiteMode ON and reduced motion.
473. Roll must be shorter or static and final result correct.
474. Enable grid after PNG renderer is verified.
475. Add several gifts from own profile read path.
476. Add gifts from another test profile with permitted visibility.
477. Reorder cells and rows; close and reopen.
478. Export grid PNG and inspect all selected rows.
479. Test missing gift reference without substituting another gift.
480. Test rarity known, unknown and malformed values.
481. Unknown tier must show unknown, not legendary.
482. Test 20+ cells and bounded scrolling.
483. Test process death/restart and cache migration.
484. Test logout and account switch for private grid data.
485. Test each toggle OFF again after ON.
486. Off must restore stock menus, requests, animations and storage writes.
487. Capture logcat tags for `TeleGiftStudio`, `TeleGiftCatalog`, `TeleGiftRoll`.
488. Never include tokens, phone, username, account ID or raw response in logcat.
489. Log slow render duration and output size only.
490. Log export format and failure class only.
491. Check Android StrictMode/main-thread violations where available.
492. Check allocation/OOM around maximum PNG size.
493. Check codec unsupported path before enabling video formats.
494. Manual testing must explicitly record device ABI and Android API level.
495. A compile result alone is not acceptance evidence.

## 14. features.md and patchlist updates

496. Every user-facing patch needs one English row in `features.md`.
497. PNG studio row belongs under a settings page that owns its switch.
498. Include plain sentence, location, default and Android patch link.
499. Include desktop links for 0197, 0204, 0234, 0198, 0201, 0247 and 0248.
500. Do not add formats to features.md before those formats are manually verified.
501. Separate rows are appropriate for studio, fake upgrade, grid and rarity.
502. External catalog description must disclose third-party request and OFF default.
503. The features row must not claim fake result is a real upgrade.
504. The features row must not imply ownership or payment.
505. `PATCHLIST.md` status stays `todo` until code is committed.
506. Set `wip` only when Telegram tree has an unfinished commit.
507. Set `queued` only after export to `patches/android/`.
508. Set `built` only after debug APK is assembled and handed over.
509. Set `done` only after human on/off verification.
510. Update all seven rows, not only the first PNG row.
511. If format support is split, keep remaining rows truthful and `todo`.
512. Features links use actual exported patch filenames, not planned names.
513. Never create placeholder patch links.
514. Changelog/new-settings metadata is updated with actual IDs after commit.

## 15. Batch 23 and batch 26 gates

515. Batch 23 must provide local Stars/gift password before any paid action integration.
516. Studio PNG and fake preview do not require invoking the batch 23 password.
517. Any real upgrade path must call batch 23 guard first.
518. Batch 23 mass gift runner is not needed for local fake rolls.
519. Batch 23 test account rule still applies: no maintainer purchases.
520. Batch 26 wallet is not a prerequisite for plain gift studio PNG.
521. Wallet card gift design belongs to batch 27 and is out of this scope.
522. Do not import wallet-engine or Rust work into batch 24.
523. If a shared model helper is needed by wallet, expose a neutral read-only helper later.
524. Gift studio must not call wallet balances, keys or transfers.
525. Batch 24 gate begins only after all seven rows are exported.
526. Gate command is `./gradlew :TMessagesProj_App:assembleDebug` in Telegram checkout.
527. The first native build can be long; do not claim gate from Java compilation only.
528. Select the correct ABI APK for manual installation.
529. Hand APK to maintainer with numbered manual test steps.
530. Maintainer verifies default, ON and OFF states.
531. Maintainer verifies no external request while external catalog is OFF.
532. Maintainer verifies no real purchase or account mutation.
533. Only then mark batch rows `done`.
534. If video/GIF/TGS are unfinished, they cannot be marked `done`.
535. A batch gate failure returns the affected row to `wip` or `todo` with evidence.
536. Do not close gate on maintainer account purchases.

## 16. Open decisions before implementation

537. [INFERENCE] Confirm whether studio page is `MODE_GIFTS` or remains under interface.
538. [INFERENCE] Confirm exact 1360..1379 mapping with maintainer before changing TeleSearch.
539. Confirm the exact `api.changes.tg` endpoint and response schema from desktop patch.
540. Confirm whether external cache is visible when toggle is later turned OFF.
541. Confirm catalog cache TTL, max bytes and per-account sharing policy.
542. Confirm default PNG dimensions and supported presets for first commit.
543. Confirm whether copy PNG uses clipboard URI or only share/save.
544. Confirm Pictures collection name and localized filename policy.
545. Confirm max bitmap pixels and max grid rows/cells.
546. Confirm fake number policy: local sequence, placeholder or omitted.
547. Confirm fake result history retention and clear action.
548. Confirm roll duration and LiteMode duration.
549. Confirm how model JSON is obtained from Telegram preview APIs.
550. Confirm whether regular gifts are in first studio release or 0234 follow-up.
551. Confirm whether custom `.tgs` models are in first release or follow-up.
552. Confirm exact rarity enum values and unknown handling.
553. Confirm whether owned gifts from another peer include unsaved/hidden entries.
554. Confirm accessibility behavior while number/model are hidden.
555. Confirm whether video/GIF/TGS are separate toggles or capability-only actions.
556. Confirm test fixture policy for malformed external responses.
557. Do not resolve these questions by inventing protocol behavior.

## 17. Definition of done

558. PNG studio opens on Android and renders a selected gift.
559. PNG save, copy/share and cancellation work without leaks.
560. Studio works per account and survives ordinary recreation.
561. External catalog is OFF by default and produces zero third-party requests when OFF.
562. External responses are bounded, validated, cached and rate-limited.
563. Fake upgrade never spends Stars and clearly shows local preview.
564. Roll hides number/model until final and respects LiteMode.
565. Gift grid imports allowed gifts from any selected peer.
566. Grid state persists only in fork storage and exports through shared renderer.
567. Rarity labels handle known and unknown values safely.
568. Video/GIF/WebM/TGS are either tested and documented or explicitly not enabled.
569. All seven PATCHLIST rows have truthful statuses.
570. All user-facing verified rows exist in `features.md`.
571. Debug APK is built from the complete queue.
572. Human tests cover ON, OFF, default, account switch and network failure.
573. No real purchases are made.
574. No maintainer account is used for purchase or destructive gift testing.
575. Only after these conditions can batch 24 close.
