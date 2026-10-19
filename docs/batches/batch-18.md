# Пачка 18 — поле ввода, текст и цитаты

## 1. Назначение и границы

1. Этот документ описывает реализацию только пачки 18 из `docs/PATCHLIST.md`.
2. Название пачки: «поле ввода, текст и цитаты».
3. Основание плана — строки 0245, 0175, 0210, 0211, 0148, 0176, 0144, 0141, 0139, 0142 и 0146.
4. Порядок номеров здесь — текущая нумерация desktop-очереди.
5. Старые номера не следует подставлять вместо текущих.
6. Соответствие старых и новых номеров проверяется по `docs/desktop-numbers.md`.
7. Desktop-исходник этой инструкции сверялся через `git show origin/main:<path>`.
8. Android-исходник сверялся через `git show tele:<path>` в соседнем checkout `Telegram`.
9. Патчи в Android-очереди не редактируются вручную.
10. Изменения сначала делаются коммитами в ветке `tele` checkout `Telegram`.
11. Затем очередь экспортируется в `patches/android/`.
12. Этот документ не изменяет `PATCHLIST.md` и не меняет статусы строк.
13. Fork-код помещается в новые файлы под `TMessagesProj/src/main/java/tele/`.
14. Stock-файлы получают только минимальный gated-call.
15. `TLRPC.java` запрещено редактировать.
16. Stock-схема базы данных и `LAST_DB_VERSION` не меняются.
17. Fork-состояние хранится в `tele_kv` или новых `tele_*` таблицах.
18. Выключенный тумблер обязан оставить поведение Telegram без изменений.
19. Вызов helper при выключенном тумблере должен быть невозможен.
20. Все операции с View выполняются на главном потоке.
21. Ответы storage и tgnet считаются фоновыми до явного перехода на UI-поток.
22. Состояние helper-ов всегда получает `currentAccount` явно.
23. Нельзя хранить состояние ввода в singleton без ключа аккаунта и диалога.
24. Перерабатывать stock-архитектуру отправки целиком не следует.
25. Приоритет имеет data-layer hook, а не набор одинаковых hooks в ячейках.
26. UI-пути нужны только там, где stock не предоставляет data-layer extension point.
27. Декоративный markdown не должен менять текст draft или отправляемые entity преждевременно.
28. Цитаты должны становиться server entities только в gated send path.
29. Подпись стикера должна проходить тем же caption/entity path, что и media caption.
30. Рендер подписи стикера обязан быть одинаковым в пузыре, списке и уведомлении.
31. Обязательное ограничение пачки — plain-message ветка Android.
32. Rich-редактор desktop в Android отсутствует.
33. Поэтому rich-only часть desktop-патчей в Android не изобретается.
34. Любой остаток, для которого нет Android API, помечается `[INFERENCE]` или вопросом.
35. Отдельный поздний патч 0242 рассматривается ниже как соседняя отправочная зависимость.
36. 0242 не добавляет новую строку в таблицу пачки 18.
37. Его реализация не должна случайно попасть в коммит 0176 или 0148.
38. Пачка закрывается только после batch gate из раздела 19.
39. Сборка сама по себе не доказывает UX.
40. Ручная проверка on и off обязательна.

## 2. Что было подтверждено в исходниках

41. `ChatActivityEnterView` содержит `messageEditText` типа `EditTextCaption`.
42. Поле создаётся в `createMessageEditText`.
43. Этот метод находится примерно около anchor `messageEditText = new ChatActivityEditTextCaption`.
44. Поле уже вызывает `getTextToUse()` перед отправкой.
45. `sendMessageInternal` получает текст после media/docked веток.
46. `processSendingText` строит entities и вызывает `SendMessagesHelper`.
47. В preview-пути текст строится около `getEntities(text, true)`.
48. `ChatActivityEnterView` уже имеет `setFieldText` для восстановления текста.
49. `ChatActivity` хранит `replyingQuote` и `replyingMessageObject`.
50. `ChatActivityTextSelectionHelper.canShowQuote` фильтрует доступность цитирования.
51. `onQuoteClick` ограничивает диапазон через `quoteLengthMax`.
52. `onQuoteClick` вызывает `showFieldPanelForReplyQuote` при видимом поле.
53. `SendMessagesHelper` уже сериализует `replyQuote.getEntities()`.
54. Это позволяет не добавлять новые TL-типы.
55. `MediaDataController.getEntities` уже используется в Android send paths.
56. `ChatMessageCell.setMessageObject` и `draw` являются горячими anchors для пузыря.
57. `MessageObject.generateCaption` строит caption presentation.
58. `DialogCell.getCaptionMessage` выбирает caption для списка диалогов.
59. `DialogCell.getMessageStringFormatted` собирает notification/list text.
60. `SendMessagesHelper.sendSticker` уже имеет overload с caption.
61. Этот overload находится около anchor `sendSticker(... CharSequence caption ...)`.
62. `StickersAlert` имеет кнопку отправки набора, но не обязан отправлять caption напрямую.
63. `ChatActivityEnterView.onStickerSelected` отправляет стикер через `SendMessagesHelper`.
64. `ChatActivityEnterView.onGifSelected` является отдельным media path.
65. `Calcmula.kt` уже содержит сетевой choke point.
66. `Calcmula` ограничивает timeout 10 секунд.
67. `Calcmula` ограничивает body 64 KiB.
68. `Calcmula` кэширует до 32 записей на пять минут.
69. `CalcmulaPreview.kt` уже является UI-кандидатом для чипа.
70. `CalcmulaPreview` должен оставаться account/dialog-bound через `ChatActivity`.
71. `EditTextCaption` уже имеет `TextWatcher` и quote spans.
72. `EditTextCaption` уже добавляет/удаляет `QuoteSpan` для ручного форматирования.
73. `EditTextCaption` уже обрабатывает paste и action mode.
74. Это предпочтительнее исправления `EditTextBoldCursor`.
75. `LiteMode` импортирован существующим Calcmula preview.
76. Любая новая анимация должна учитывать `LiteMode`.
77. `ChatActivityEnterView` хранит docked media state в текущем Android queue.
78. `DockedMedia.send` уже вызывается перед обычным текстом.
79. Новая feature не должна обходить `DockedMedia.send`.
80. `SendMessagesHelper.prepareSendingVideo` работает во worker thread.
81. В video path используется `VideoEditedInfo.muted`.
82. Это является anchor для соседней опции silent-video.
83. Введённые anchors — символы и вызовы, а не гарантированные номера строк.
84. После rebase номера строк нужно находить exact symbol поиском.
85. Если overload отличается, искать ближайший вызов по имени и аргументам.
86. Нельзя копировать desktop C++-реализацию в Kotlin.
87. Desktop исходник служит описанием поведения и ограничений.
88. Android implementation должна использовать собственные entities и spans.
89. Каждый helper получает только нужные параметры.
90. Activity reference в долгоживущем worker не сохраняется.

## 3. TeleConfig, строки и настройки

91. Каждый реальный пользовательский переключатель добавляется в `TeleConfig.kt`.
92. Все новые переключатели пачки 18 имеют default `false`.
93. OFF не должен создавать spans, запросы, chips или новые меню.
94. Предлагаемые pref keys должны быть snake_case.
95. `live_markdown` — родительский переключатель 0245.
96. `live_markdown_quotes` — отдельный подтумблер `>` и `>!`.
97. `sticker_captions_show` — показ caption стикера.
98. `sticker_captions_send` — захват и отправка caption стикера.
99. `multi_quote` — дописывание второй и следующих цитат.
100. `quote_voice_transcription` — отдельный switch только если UX требует независимого отключения.
101. `[INFERENCE]` Решение по умолчанию: 0211 наследует `multi_quote`, без второго server behavior switch.
102. Если отдельный switch не нужен, его search entry остаётся alias, не config item.
103. `calcmula_suggestions` — подсказки и отправка без вычисления для 0148.
104. `calcmula_inline_result` — чип результата после `=` для 0176.
105. `link_preview_rewrite_only` — 0144.
106. `recent_typed_emoji` — 0141, fix с явным выключением.
107. `copy_markdown_html` — 0139.
108. `code_block_line_numbers` — 0142.
109. `shot_to_docked_media` — 0146.
110. `silent_video_as_gif` относится к отдельному позднему 0242, не к core row 18.
111. `[INFERENCE]` Если maintainer решит 0141 always-on fix, удалить его config item до кода.
112. `[INFERENCE]` Если 0146 считается покрытым docked media, оставить только missing send hook.
113. Настройки помещаются в существующую секцию `sending` или `interface` по feature.
114. 0139 и 0142 относятся к `interface`/`messages`, если структура уже разделена.
115. 0141 относится к `sending`/`interface` и не меняет серверные данные.
116. 0175 показывает caption в `interface`, отправляет caption в `sending`.
117. В collapsible group скрывать дочерние rows до включения родителя.
118. Для markdown quotes дочерний row скрывать до `live_markdown`.
119. Для sticker send скрывать зависимые caption-length options до `sticker_captions_send`.
120. Ресурсы идут в `strings_tele.xml` с префиксом `Tele`.
121. Stock `strings.xml` не трогается.
122. Описания должны явно называть лимит и off behavior.
123. Export/import должен включать каждый фактический config item.
124. Group-only и alias search IDs в export/import не включаются.
125. Значение search ID не равно pref key.
126. Deeplink для группы должен открывать `sending` или `interface`.
127. Строки должны быть пригодны для локалей с другим порядком аргументов.
128. В описаниях не обещать поддержку rich-сообщений.
129. В описаниях не обещать background conversion, если его нет.
130. В описаниях не обещать отправку caption без проверки прав и лимита.

### Зарезервированные Search IDs 1240..1259

131. Диапазон 1240..1259 резервируется только для пачки 18.
132. 1240 — «live markdown».
133. 1241 — «markdown quotes».
134. 1242 — «sticker captions».
135. 1243 — «send stickers with captions».
136. 1244 — «multiple quotes».
137. 1245 — «quote voice transcription».
138. 1246 — «calcmula suggestions».
139. 1247 — «calcmula inline result».
140. 1248 — «rewrite link only for preview».
141. 1249 — «typed emoji in recent».
142. 1250 — «copy as Markdown or HTML».
143. 1251 — «line numbers in code blocks».
144. 1252 — «send shots to docked media».
145. 1253 — alias «bold italic code markdown».
146. 1254 — alias «blockquote expandable quote».
147. 1255 — alias «sticker caption notification preview».
148. 1256 — alias «calculation result chip».
149. 1257 — alias «copy entities formatting».
150. 1258 — alias «caption link preview rewrite».
151. 1259 — alias «emoji recent code block shot».
152. IDs 1240..1252 point at real settings or their group rows.
153. IDs 1253..1259 are search aliases only.
154. `[INFERENCE]` Final wording may be localized, IDs must not change after release.
155. Add the IDs to `TeleSearch` beside the existing sending entries.
156. Keep search results scoped to the correct settings mode.
157. Search must find «цитата», «расшифровка», «стикер», «подпись» and English aliases.
158. Search must find «Markdown», «HTML», «calcmula», «код» and «эмодзи».
159. Search must not expose disabled child rows as independently enabled.
160. Search tests must cover each ID exactly once.

## 4. Коммиты, трудоёмкость и порядок

161. Один desktop row соответствует одному Android commit.
162. Shared helper допускается только если он нужен предыдущему commit.
163. Commit subjects должны быть lowercase, imperative и не длиннее пяти слов.
164. 0245 — L: live parser, spans, quote parsing, caption/draft integration.
165. 0175 — L: caption send path plus three render surfaces and editing.
166. 0210 — M: reply quote state and append/truncate behavior.
167. 0211 — S: transcription selection gate over existing quote helper.
168. 0148 — M: raw-calculation action and send menu integration.
169. 0176 — M: inline result chip and insertion lifecycle.
170. 0144 — S: preview-only link rewrite gate.
171. 0141 — S: sent typed emoji accounting.
172. 0139 — M: entity writer to Markdown/HTML and context menus.
173. 0142 — M: code line-number rendering and width handling.
174. 0146 — S: shot result to existing docked media store.
175. Первый commit — `feat: render live markdown`.
176. Второй commit — `feat: add sticker captions`.
177. Третий commit — `feat: append multiple quotes`.
178. Четвёртый commit — `feat: quote transcriptions`.
179. Пятый commit — `feat: add calcmula suggestions`.
180. Шестой commit — `feat: show calcmula chip`.
181. Седьмой commit — `feat: rewrite preview links`.
182. Восьмой commit — `fix: remember typed emoji`.
183. Девятый commit — `feat: copy message markup`.
184. Десятый commit — `feat: number code lines`.
185. Одиннадцатый commit — `feat: dock sent shots`.
186. `[INFERENCE]` Subjects нужно сверить с фактическим изменением перед commit.
187. Зависимость 0245 → 0139: writer переиспользует entity semantics 0245.
188. Зависимость 0175 → 0146 отсутствует, кроме общего docked caption UX.
189. Зависимость 0210 → 0211 обязательна.
190. Зависимость 0091/0092 Android → 0148/0176 обязательна.
191. Зависимость 0051/0052/0062 → 0144 обязательна.
192. Зависимость 0047 → 0139 обязательна для message-menu action.
193. Зависимость 0093/0096 → 0146 является частичной и требует проверки.
194. После каждого commit экспортировать patch только обычной командой queue.
195. После всех одиннадцати commit выполнить batch gate.
196. Низкоприоритетный 0242 не смешивать с этим порядком.
197. Низкоприоритетный 0236 captioned stickers in docked также не смешивать.
198. Нельзя откладывать базовую entity migration до ручной проверки.
199. Нельзя объединять все rows в один «input features» commit.
200. Нельзя создавать второй markdown parser в 0139.

## 5. 0245: живой Markdown и цитаты

201. Цель — маркеры остаются в тексте, но форматируются декоративными spans.
202. Поддерживаемые маркеры: `**`, `__`, `~~`, `||`, одиночный backtick.
203. Fence ````` ``` ````` должен иметь отдельную code-block обработку.
204. Маркеры не удаляются из `Editable` во время набора.
205. Маркеры визуально приглушаются, а содержимое получает соответствующий style.
206. `TeleLiveMarkdownSpan` не является server entity.
207. Span должен быть безопасен при вставке, undo и selection.
208. TextWatcher не должен вызывать рекурсивный TextWatcher loop.
209. Ввод внутри replacement span должен инвалидировать только нужный диапазон.
210. При смене текста пересчитывать парные markers без O(n²) на длинном поле.
211. `[INFERENCE]` Практический лимит сканирования поля — 4096 code points.
212. Если лимит принят, после него декорация не рисуется, текст не меняется.
213. Лимит сообщения остаётся `MessagesController.getMaxMessageLength()`.
214. Нельзя считать UTF-16 units пользовательским лимитом без проверки stock semantics.
215. Поле чата подключается в `ChatActivityEnterView.createMessageEditText`.
216. Caption-поля подключаются в `ChatAttachAlert` и `EditTextCaption` paths.
217. Редактор подписи должен использовать тот же `LiveMarkdownText` extractor.
218. `getTextToUse()` должен получать plain text с нужными spans.
219. `MediaDataController.getEntities` вызывается после декорации, не вместо неё.
220. Декоративные spans не должны дублировать entities.
221. Quote prefix распознаётся только при включённом `live_markdown_quotes`.
222. Обязательный prefix — `> ` в начале строки.
223. Expandable prefix — `>! ` в начале строки.
224. Prefix без пробела не превращается в quote.
225. Обычный знак `>` внутри строки остаётся обычным текстом.
226. Несколько quote-строк объединяются в один blockquote entity.
227. Непрерывные строки quote образуют один block.
228. Пустая строка завершает quote block.
229. `[INFERENCE]` Вложенные `>>` не поддерживать без решения maintainer.
230. Вложенные markers должны остаться обычным текстом, если не поддержаны.
231. `>!` создаёт `TL_messageEntityBlockquote` с collapsed flag.
232. Entity offsets считаются после удаления prefix из отправляемого текста.
233. Если stock API ожидает prefixes, helper должен преобразовать обратно перед send.
234. Не менять `messageOwner.message` до окончательной сборки entities.
235. Draft сохраняет исходные markers, а не визуально очищенный текст.
236. Selection copy из поля по умолчанию копирует обычный текст с markers.
237. HTML/Markdown copy из сообщения сериализует уже server entities.
238. Live parser не должен срабатывать в секретном чате без проверки entity support.
239. При неподдержанном `TL_messageEntityBlockquote` оставить stock text path.
240. OFF должен обходить `LiveMarkdown` полностью.

### Draft и migration для 0245

241. Текущие cloud/device drafts могут содержать text и entities отдельно.
242. Не менять stock draft schema.
243. При чтении draft не восстанавливать декоративные spans из server entities без gate.
244. При включении опции построить spans на UI из draft text.
245. При выключении опции удалить только fork spans, не менять text.
246. Draft migration нужен для локально сохранённых 0245 caption/text.
247. Хранить migration version в `tele_kv`, не в stock DB version.
248. Migration должна быть идемпотентной.
249. Старые drafts без migration marker считаются version zero.
250. Version zero не переписывать, пока пользователь не сохранит его снова.
251. Entity offsets проверять после каждой нормализации line ending.
252. Не выполнять migration на background callback, пока поле attached не проверено.
253. При rotation не создавать второй watcher.
254. При process recreation один watcher должен восстановить тот же draft.
255. При draft deletion очищать pending quote state.
256. При отправке использовать account id, с которым draft был прочитан.
257. При смене диалога удалять spans текущего поля и pending quote.
258. При смене аккаунта нельзя показать draft другого аккаунта.
259. Для local drafts учитывать существующий `LOCAL_DRAFTS` switch.
260. 0245 не должен обходить privacy gate cloud drafts.

## 6. 0175: подписи к стикерам

261. Решение maintainer: отправка, правка и показ везде.
262. Нужны два независимых поведения: send и show.
263. При `sticker_captions_send` текст поля берётся как caption.
264. Пустое поле отправляет обычный стикер.
265. Поле с emoji-only query не считать caption автоматически.
266. Caption стикера должен пройти server caption length limit.
267. При превышении лимита отправку отменить с понятным UI error.
268. Не обрезать молча пользовательский caption.
269. При обычном sticker picker selection сохранить reply и quote metadata.
270. `ChatActivityEnterView.onStickerSelected` — основной UI anchor.
271. `SendMessagesHelper.sendSticker(... CharSequence caption ...)` — data anchor.
272. `StickersAlert` должен передавать выбор в общий callback.
273. `StickersAlert` не должен отправлять напрямую в обход confirm/send menu.
274. Двойной tap confirmation из пачки 17 должен сохраняться.
275. Стикер из pack box обязан использовать тот же confirm helper.
276. GIF caption path не превращать автоматически в sticker caption.
277. Emoji set documents не принимать без отдельного решения.
278. Edit caption должен использовать существующий edit-message route.
279. Для редактирования сохранять entities и caption text.
280. Не менять `TLRPC` для sticker caption.
281. В пузыре caption располагается под sticker body.
282. При show OFF не рисовать caption в `ChatMessageCell`.
283. При show ON `ChatMessageCell` добавляет caption layout только для sticker media.
284. `MessageObject.generateCaption` должен включать caption text/entities.
285. Вызов layout должен быть безопасен при recycled cell.
286. В `setMessageObject` сбрасывать предыдущий sticker caption state.
287. В `draw` использовать current message/account, не cached previous object.
288. LiteMode запрещает тяжёлую caption animation.
289. Caption custom emoji animation должна уважать `LiteMode`.
290. Список диалогов использует `DialogCell.getCaptionMessage`.
291. При show ON list preview содержит caption после sticker label.
292. При нескольких album captions применять stock rule и не склеивать молча.
293. `[INFERENCE]` Если больше одной caption в album, выбрать stock preview policy.
294. Уведомления должны получать caption через notification text builder.
295. Не отправлять caption в notification service отдельно.
296. Notification text не должен содержать секретные hidden entities.
297. Protected message policy не меняется.
298. Secret chat caption должен пройти существующий secret send path.
299. Voice transcription и caption не смешиваются.
300. Copy selection из sticker caption должно работать как обычный text selection.
301. Recycled `DialogCell` обязан полностью сбрасывать caption visibility.
302. Recycled `ChatMessageCell` обязан сбрасывать caption layout and height.
303. Настройки show/send применяются без restart через `TeleHooks.onConfigChanged`.
304. При off send нельзя добавлять caption к `SendMessageParams`.
305. При off show нельзя резервировать дополнительную высоту пузыря.

## 7. 0210 и 0211: несколько цитат

306. Один reply server object всё ещё содержит одну reply quote.
307. Повторная quote action при активном reply не заменяет первую quote.
308. Она дописывает новый block в поле ввода.
309. Existing reply target остаётся тем же.
310. `ChatActivityTextSelectionHelper.onQuoteClick` — основной anchor.
311. `ChatActivity.replyingQuote` — pending quote state.
312. `ChatActivityEnterView.setFieldText` — insertion hook.
313. Quote append должен сохранять caret после вставленного блока.
314. Между блоками вставлять ровно один newline boundary.
315. Авторский prefix добавлять только если он доступен.
316. Не включать имя автора в text дважды.
317. Entity offsets пересчитывать после prefix.
318. `quoteLengthMax` ограничивает каждую выбранную quote.
319. Message max length ограничивает итоговое поле.
320. При нехватке лимита обрезать новую quote, не старые quotes.
321. При полностью пустом остатке показать отказ и не менять поле.
322. `[INFERENCE]` UX отказа — короткий Bulletin без отправки.
323. Existing `ReplyQuote.from` должен оставаться источником selected text.
324. Reply metadata не должен стать отдельной второй reply header.
325. `TL_messageEntityBlockquote` добавляется только при enabled gate.
326. Quote entities не должны пересекаться с code entity.
327. Quote parser должен очищать только свой input block.
328. Разные аккаунты не разделяют `replyingQuote`.
329. Разные dialog IDs не разделяют pending append state.
330. Leaving chat очищает pending state.
331. Rotation восстанавливает text/reply из ChatActivity, не static helper.
332. `canShowQuote` для 0211 снимает только transcription запрет.
333. Остальные noforward, encrypted и service restrictions остаются.
334. Голосовая расшифровка цитируется только после выбора диапазона.
335. Full transcription quote может остаться stock quote path.
336. `ChatActivity.canShowQuote` — exact gate для transcription.
337. Transcription selection callback передаёт selected text и entities.
338. Не повторять network transcription request, если текст уже открыт.
339. Не цитировать локальный placeholder вместо расшифровки.
340. Не включать audio waveform в text quote.
341. При отсутствии transcription entity не показывать quote action.
342. Voice quote должен наследовать `multi_quote` gate.
343. `[INFERENCE]` Отдельный `quote_voice_transcription` switch оставлять только при подтверждённом UX.
344. Entity source transcription должен быть null-safe.
345. Callback с detached Activity игнорировать.
346. UI callback переходить на main thread.
347. Test selection с emoji и RTL text.
348. Test selection на границе surrogate pair.
349. Test selection на границе quote block.
350. Test quote in topic and thread.
351. Не менять quote behavior при OFF.

## 8. 0148 и 0176: calcmula

352. Existing 0091 вычисляет сообщение, начинающееся с `= `.
353. Existing 0092 показывает preview while typing.
354. 0148 добавляет menu action send without calculating.
355. 0176 добавляет result chip after `=`.
356. `Calcmula.kt` остаётся единственной сетевой точкой.
357. Любой запрос проверяет `TeleConfig.CALCMULA` на низком уровне.
358. Сетевой вызов запрещён при `CALCMULA` OFF.
359. Preview также требует `CALCMULA_PREVIEW` или нового child gate.
360. 0148 child gate не должен обходить родительский CALCMULA.
361. «Send without calculating» отправляет исходный query plain text.
362. Он не меняет query на result.
363. При ошибке вычисления поле не очищается.
364. Existing 0091 restore draft behavior сохраняется.
365. Calcmula chip располагается над `ChatActivityEnterView`.
366. `CalcmulaPreview.kt` — UI anchor для chip.
367. Chip показывает result, а не исходный URL или account data.
368. Tap по chip вставляет result согласно решению maintainer.
369. `[INFERENCE]` Вставка должна заменять текущий `= query`.
370. Второй tap по уже применённому result не дублирует текст.
371. Chip скрывается при смене dialog.
372. Chip скрывается при очистке поля.
373. Chip hidden при multiline query, если parser не поддерживает multiline.
374. `[INFERENCE]` Multiline поддерживать только после отдельного решения.
375. Async callback проверяет generation token поля.
376. Старый результат не должен попасть в новый query.
377. Callback обновляет View на main thread.
378. `LiteMode` не отключает сам вычисление, только animation.
379. Chip animation в LiteMode должна быть мгновенной.
380. Cache hit не должен блокировать UI thread.
381. Cache limits остаются 32 entries и 5 minutes.
382. HTTP timeout остаётся 10 seconds.
383. Body limit остаётся 64 KiB.
384. Не логировать query, result или message text.
385. Debug log может содержать account id и state only.
386. Настройки описывают единственный внешний запрос к calcmula.app.
387. Privacy copy не должен отправлять account, peer или message identifiers.
388. Offline switch должен остановить fetch до URL creation.
389. `SendMessagesHelper` не должен вычислять повторно при paid confirmation.
390. Existing WeakHashMap processed guard сохранить.
391. Caption calculation path требует отдельный test.
392. Sticker caption не вычислять, если feature sticker caption off.
393. `send without calculating` должен работать для caption только если 0091 уже поддерживает caption.
394. `[INFERENCE]` При неясном media-caption semantics оставить stock caption.
395. 0176 chip должен использовать account-bound `CalcmulaPreview`.
396. Уничтожение Activity отменяет UI callback.
397. Не создавать executor на каждый символ.
398. Search IDs 1246 и 1247 ведут в sending.
399. Export/import включает только утверждённые config items.
400. OFF-тест проверяет отсутствие calcmula log/network.

## 9. 0144: rewrite только для preview

401. Existing 0051/0052 реализуют paste rewrite rules.
402. 0144 не переписывает отправляемый текст.
403. Он применяет rewrite только к URL preview request.
404. `EditTextCaption` paste hook остаётся обычным paste behavior.
405. `ChatActivity` preview setup — основной gated call.
406. При `NO_LINK_PREVIEWS` feature не выполняется.
407. При auto-preview disabled feature не выполняется.
408. Manual preview action должна применять rules только к preview URL.
409. Original text в поле не изменяется.
410. Draft сохраняет оригинальный URL.
411. Preview replacement не должен менять entities текста.
412. Rewrite rules загружаются из уже существующего storage.
413. Не добавлять отдельный network service для rules.
414. Invalid rule оставляет stock preview behavior.
415. Redirect loop ограничить существующим rewrite limit.
416. `[INFERENCE]` Если лимит не найден, запросить решение перед кодом.
417. Preview generation callback проверяет current field generation.
418. Stale preview не показывать после смены текста.
419. `t.me` links не переписывать по desktop rule.
420. Secret chat и protected content ограничения не меняются.
421. Search ID 1248 должен находиться через «preview link».
422. OFF snapshot должен совпадать со стоковым URL.
423. On test должен сравнить field text до/после.
424. Не считать server webpage title пользовательским текстом.
425. Tele network offline switch должен блокировать только fork request.

## 10. 0141: typed emoji в recent

426. Цель — отправленные typed emoji учитываются в recent.
427. Отправленный sticker не должен считаться typed emoji автоматически.
428. Custom emoji entity нужно отличать от обычного Unicode emoji.
429. Считать emoji только после успешного принятия send operation.
430. Не считать текст при локальном preview.
431. Не считать text, который остался в поле после failed send.
432. `SendMessagesHelper` send success/accepted path — data anchor.
433. `Emoji`/`MediaDataController` recent API — storage anchor.
434. Account-specific recent list обязателен.
435. Не использовать account 0.
436. Duplicate emoji в одном сообщении должны иметь stock frequency semantics.
437. Счётчики не должны превышать Android recent limit.
438. LiteMode не меняет recent behavior.
439. OFF не вызывает recent helper.
440. `[INFERENCE]` Если Android уже добавляет typed emoji в recent, строку закрыть как n/a.
441. Перед кодированием проверить stock behavior на exact branch.
442. Search ID 1249 должен описывать typed emoji, не stickers.
443. Privacy: recent emoji — локальные данные, сеть не нужна.
444. Process death не должен терять stock recent persistence.
445. Multi-account test должен различать recent lists.

## 11. 0139: copy как Markdown/HTML

446. Desktop writer сериализует entities в Markdown и HTML.
447. Android helper должен жить в `tele/helpers/`, например `CopyMarkup.kt`.
448. Writer принимает plain text и `ArrayList<TLRPC.MessageEntity>`.
449. Writer не мутирует original message or entities.
450. Markdown output сохраняет bold, italic, strike, spoiler.
451. Markdown output сохраняет inline code и pre/code.
452. Markdown output сохраняет links с безопасным escaping.
453. Markdown output сохраняет blockquotes и expandable blockquotes.
454. HTML output использует escaping для text content.
455. HTML output использует `<blockquote>` и expandable attribute по entity.
456. HTML output сохраняет `<a href>` только для URL entity.
457. Unsupported entity должна быть plain text, не потерей текста.
458. Overlapping entities сортируются по offset и depth.
459. Adjacent same-style entities можно объединить.
460. UTF-16 offsets должны соответствовать Telegram entity offsets.
461. Surrogate pairs нельзя разрезать в середине.
462. URL escaping должен предотвращать broken Markdown delimiters.
463. Newline handling должен быть deterministic.
464. Copy action добавляется в `MessageMenu` registry.
465. `ChatActivity.fillMessageMenu` добавляет actions только при config ON.
466. Selection copy path должен добавлять actions тоже.
467. Caption copy использует caption entities.
468. Sticker caption copy доступен только при show ON и nonempty caption.
469. Protected messages не получают обходной copy path.
470. `AndroidUtilities.addToClipboard(plain, html)` использовать для HTML clip.
471. Markdown action кладёт Markdown string как plain clipboard value.
472. HTML action кладёт plain fallback плюс HTML MIME.
473. Bulletin подтверждает успешное копирование без текста сообщения.
474. Не логировать содержимое clipboard.
475. Menu order/hide integration использовать существующий `MessageMenu`.
476. Search ID 1250 относится к interface/message menu.
477. Export/import включает `copy_markdown_html` toggle.
478. OFF меню не содержит новых actions.
479. Test entities: bold, italic, strike, spoiler, code, pre, URL, mention, quote.
480. Test selection, caption, sticker caption and album.

## 12. 0142: номера строк code blocks

481. Android code blocks строятся через `MessageObject.TextLayoutBlock`.
482. `ChatMessageCell` code rendering — основной draw anchor.
483. `MessageObject` layout generation — data/measurement anchor.
484. Нумерация должна быть визуальной, не менять `messageOwner.message`.
485. Номера не добавлять в copy text.
486. Номера не добавлять в server entities.
487. Номер каждой строки начинается с 1 внутри code block.
488. Несколько code blocks имеют независимую нумерацию.
489. Inline code не получает номера.
490. Pre без code language всё равно считается code block.
491. Ширина gutter учитывает максимальное число строк.
492. При изменении ширины cell layout пересоздаётся.
493. Recycled cell сбрасывает previous line-number state.
494. Номера не должны вылезать за bubble bounds.
495. RTL code text сохраняет code direction, gutter стабилен.
496. Long lines должны следовать Android StaticLayout wrapping policy.
497. `[INFERENCE]` Номер для wrapped visual line не повторять, пока не подтверждён UX.
498. Accessibility text не должен дублировать номера без решения.
499. LiteMode не отключает static numbers.
500. Search ID 1251 находится через «code block lines».
501. OFF rendering должен совпадать со stock width and height.
502. On rendering добавляет только согласованный gutter.
503. Test code 1, 9, 10, 99 и 100 строк.
504. Test code with emoji, tabs, RTL and long unbreakable tokens.
505. Не переносить desktop rich-IV line number code.

## 13. 0146: shot в docked media

506. Android 0093 создаёт shot result в `TeleShotActivity`.
507. Android 0096 предоставляет `DockedMedia` и `DockedStore`.
508. 0146 должен передать shot в существующий docked store.
509. `TeleShotActivity.send()` — главный кандидат hook.
510. `DockedMedia` должен проверять `DOCKED_MEDIA` низкоуровнево.
511. Если docked выключен, shot использует stock send/share behavior.
512. Shot не отправляется дважды при rotation.
513. Docked item получает account id и dialog id.
514. Docked item получает caption только через field caption path.
515. Не создавать второй attachment queue.
516. Удаление из docked strip должно удалить только локальный item.
517. Отправка docked shot должна уважать silent preference.
518. Scheduled sending должен использовать существующий schedule path.
519. Protected content restrictions должны остаться.
520. LiteMode не анимирует тяжёлую bitmap insertion.
521. Recycler strip rebind должен восстановить item state.
522. Search ID 1252 относится к sending.
523. `[INFERENCE]` Если `TeleShotActivity` anchor назван иначе, искать метод `send` по классу.
524. Проверить Android 0096 exported queue, не только рабочее дерево.
525. OFF не вызывает `DockedMedia` helper.
526. On проверяет shot → strip → send end-to-end.

## 14. Соседняя отправочная опция 0242

527. 0242 находится в поздней low-priority пачке, не в core rows 18.
528. Android stock already sends silent video as video in обычном path.
529. Desktop choice «silent video as GIF» не переносится как default.
530. Если 0242 реализуется, новый switch должен быть `silent_video_as_gif`, default OFF.
531. Hook искать в `SendMessagesHelper.prepareSendingVideo`.
532. Проверять отсутствие audio track по валидным metadata.
533. При ON устанавливать `VideoEditedInfo.muted` только для supported path.
534. Не менять GIF already handled by stock.
535. Не транскодировать без реального Android encoder path.
536. Не применять к round video, secret chat или paid media без решения.
537. Fallback должен быть stock video, а не silent failure.
538. Add separate commit and separate batch gate.
539. Search ID для 0242 не занимать в диапазоне 1240..1259.
540. Эта оговорка предотвращает случайный scope creep пачки 18.

## 15. Потоки, аккаунты, recycling и privacy

541. TextWatcher работает на main thread.
542. Network calculation работает не на main thread.
543. Callback всегда возвращается через `AndroidUtilities.runOnUIThread`.
544. Storage draft callback тоже переходит на main thread.
545. Worker captures immutable account id.
546. Worker captures immutable dialog id.
547. Worker не читает позже `UserConfig.selectedAccount`.
548. ChatActivity callback проверяет `classGuid`/lifecycle.
549. Destroyed fragment не получает UI update.
550. Dialog change increments generation token.
551. Account change invalidates all generation tokens.
552. Every recycled cell resets caption and code state in bind.
553. Every recycled list cell resets sticker preview text.
554. No helper holds a View longer than its lifecycle.
555. LiteMode controls only visual work, never message semantics.
556. Avoid allocating parser objects on every keystroke where possible.
557. Reuse immutable marker definitions.
558. Avoid copying full message text for every cell draw.
559. Copy writer may allocate once per user action.
560. Entity writer must not modify server object.
561. Calcmula query is user text and must not enter logs.
562. No account id, peer id or message text goes to tele server.
563. Calcmula is the only third-party request in these rows.
564. Calcmula request is controlled by its own setting.
565. Offline gate is checked at fetch choke point.
566. Link rewrite does not add network traffic.
567. Sticker captions do not add network traffic.
568. Markdown entities do not add network traffic.
569. Notification caption rendering must obey hidden/protected policies.
570. Secret chat path must not leak clipboard HTML metadata.
571. Protected message copy remains stock restricted.
572. Draft migration must remain local to account and dialog.
573. Do not add stock database columns.
574. `tele_kv` migration marker must be versioned.
575. No static pending quote across accounts.
576. No static pending Calcmula chip across dialogs.
577. No animation ignoring LiteMode.
578. No stale async result after recycle.
579. No caption rendered from previous holder object.
580. No child setting active while parent is OFF.

## 16. Решения и вопросы до кодирования

581. Решение maintainer: 0245 использует decorative spans, не auto-formatting.
582. Решение maintainer: `>` и `>!` — отдельный подтумблер.
583. Решение maintainer: sticker caption отправляется и показывается везде.
584. Решение maintainer: 0210 — plain Android path, rich part n/a.
585. Решение maintainer: 0211 снимает transcription quote запрет.
586. Решение maintainer: 0176 — chip над полем, tap inserts.
587. Решение maintainer: 0148 зависит от Android 0091/0092.
588. Решение maintainer: 0242 default reverse option only, late batch.
589. Вопрос 1: нужен ли отдельный `quote_voice_transcription` switch?
590. Рекомендация: нет, наследовать `multi_quote` и сохранить одну настройку.
591. Вопрос 2: поддерживать ли nested `>>` quotes?
592. Рекомендация: нет без отдельного решения.
593. Вопрос 3: точный лимит live parser?
594. Рекомендация: следовать stock message limit и не добавлять искусственный лимит.
595. Если performance потребует cap, согласовать его как UX limit.
596. Вопрос 4: считать ли 0141 fix always-on?
597. Рекомендация: сначала проверить Android stock, затем решить.
598. Вопрос 5: caption в emoji sticker set разрешён?
599. Рекомендация: сначала обычные stickers, emoji set оставить off.
600. Вопрос 6: multiline calcmula result?
601. Рекомендация: не поддерживать без подтверждённого API.
602. Вопрос 7: accessibility code line numbers?
603. Рекомендация: visual-only до отдельного accessibility решения.
604. Вопрос 8: copy HTML MIME на всех Android API?
605. Проверить `AndroidUtilities.addToClipboard` существующий overload.
606. Вопрос 9: shot docked поддерживает scheduled media?
607. Ответить по Android 0096 фактическим hook, не предполагать.
608. Вопрос 10: нужна ли отдельная настройка 0146?
609. Если docked master уже существует, можно сделать gated extension без нового item.
610. Все unresolved items должны остаться `[INFERENCE]` в commit plan.

## 17. Pitfalls и запреты

611. Не превращать decorative marker spans в server entities дважды.
612. Не удалять `>` из draft text при отключении option.
613. Не отправлять collapsed quote как обычный quote.
614. Не создавать второй reply header для multiple quotes.
615. Не цитировать full voice transcript при selection-only UX.
616. Не dereference nullable transcription objects.
617. Не использовать `UserConfig.selectedAccount` в callback.
618. Не обновлять View из `Calcmula` executor.
619. Не использовать account 0 в `Emoji` recent update.
620. Не добавлять caption напрямую в `TLRPC.java`.
621. Не хранить caption state в recycled `ChatMessageCell` без bind reset.
622. Не показывать caption в DialogCell только при создании holder.
623. Не обходить `ProtectedMessages` в copy action.
624. Не логировать expressions, links, captions или message text.
625. Не выполнять calcmula fetch при disabled parent.
626. Не применять link rewrite при `NO_LINK_PREVIEWS`.
627. Не обнулять stock caption при sticker feature OFF.
628. Не смешивать 0242 с 0176.
629. Не смешивать 0236 docked stickers с 0175 core send.
630. Не менять stock DB version.
631. Не добавлять комментарии в stock-код.
632. Не делать широкую переформатировку Java файлов.
633. Не читать номер строки как стабильный API после rebase.
634. Не утверждать support codec без device evidence.
635. Не утверждать rich quote support на Android.
636. Не считать compile доказательством визуального результата.
637. Не обновлять `features.md` плановым текстом до exported patch.
638. После user-facing export добавить features rows в том же docs commit.
639. Один features row должен соответствовать одной пользовательской feature.
640. `features.md` остаётся на английском.

## 18. План ручных on/off проверок и logcat

641. Установить debug APK пачки на secondary account.
642. Проверить cold start с каждым новым setting OFF.
643. Ввести `**bold**`, `__italic__`, `~~strike~~`, `||spoiler||`.
644. Убедиться, что markers видимы в plain text и декорация локальна.
645. Отправить текст и проверить server entities.
646. Выключить live markdown и повторить; результат должен быть stock.
647. Включить quotes child и отправить `> quote`.
648. Проверить `>! expandable` в пузыре и при copy.
649. Проверить обычный `>` без пробела.
650. Проверить multiline quote и empty line boundary.
651. Проверить draft save, restart, restore, edit and send.
652. Проверить rotation во время ввода.
653. Выбрать sticker при непустом поле.
654. Проверить send caption, edit caption and resend.
655. Проверить sticker caption в chat bubble.
656. Проверить sticker caption в chat list preview.
657. Проверить notification preview caption.
658. Проверить sticker caption OFF: no send and no render change.
659. Проверить recycled cells after fast scroll.
660. Выделить quote, reply, выделить вторую quote.
661. Убедиться, что первая quote остаётся.
662. Проверить limit truncation and refusal.
663. Проверить multiple quote OFF: stock replacement behavior.
664. Открыть voice transcription и выделить часть.
665. Вставить voice quote в existing reply.
666. Проверить no transcription and full selection.
667. Проверить topic, group, secret chat restrictions.
668. Ввести `= 2+2` и дождаться preview.
669. Проверить chip tap replacement.
670. Проверить send without calculating.
671. Проверить timeout/error and field restoration.
672. Проверить no network with CALCMULA OFF.
673. Проверить stale result after changing dialog.
674. Paste a rewritable link with preview ON.
675. Проверить field remains original.
676. Turn no-link-previews ON; rewrite must not run.
677. Send typed emoji and reopen recent list.
678. Проверить failed send does not count emoji.
679. Проверить two accounts have independent recent lists.
680. Select formatted message and open message menu.
681. Copy as Markdown and inspect plain clipboard.
682. Copy as HTML and inspect HTML clipboard MIME.
683. Проверить protected message menu remains restricted.
684. Проверить caption and sticker caption copy.
685. Send code block with 1, 10, 100 lines.
686. Проверить wrapped lines and RTL code.
687. Scroll recycled code cells and compare gutter.
688. Capture shot and dock it above field.
689. Remove shot, restore it, send it once.
690. Check silent preference and schedule path for docked shot.
691. Repeat all representative scenarios with every setting OFF.
692. Logcat filter should include `TeleLiveMarkdown` only in debug diagnostics.
693. Logcat filter should include `TeleCalcmula` state without query text.
694. No log line may contain caption, message, URL or expression.
695. Verify no `AndroidRuntime` crash on rotation.
696. Verify no `IndexOutOfBoundsException` at entity offsets.
697. Verify no stale `NullPointerException` from transcription.
698. Verify no duplicate TextWatcher callbacks.
699. Verify no network request when calcmula is OFF.
700. Manual tester records APK version and account id locally, not in logs.

## 19. features.md rows and batch gate

701. After each exported user-facing patch, add its English row to `features.md`.
702. 0245 row: live Markdown decoration and optional quote markers, default off.
703. 0175 rows: send sticker captions and show sticker captions everywhere, default off.
704. 0210 row: append multiple quotes to one reply, default off.
705. 0211 row: quote selected voice transcription, with multiple quotes, default off or with parent.
706. 0148 row: Calcmula suggestions and send without calculating, default off.
707. 0176 row: Calcmula result chip after equals, default off.
708. 0144 row: rewrite links only for previews, default off.
709. 0141 row: remember typed emoji in recents, default off unless reclassified as always-on fix.
710. 0139 row: copy message text as Markdown or HTML, default off.
711. 0142 row: number lines in code blocks, default off.
712. 0146 row: send shots to docked media, default off or with docked master.
713. Each row names settings location, Android patch filename and desktop number.
714. Do not put implementation notes in the user-facing row.
715. Do not claim 0242 is part of batch 18.
716. Export all eleven Android commits after they are committed in `Telegram`.
717. Check that every exported patch applies to a pristine `UPSTREAM` queue.
718. Update `PATCHLIST.md` statuses only after actual queue export.
719. Build with `./gradlew :TMessagesProj_App:assembleDebug`.
720. The build must include all ABI splits.
721. Hand the correct arm64 APK to the maintainer.
722. Human tester runs the on/off matrix from section 18.
723. Human tester specifically checks caption rendering in three surfaces.
724. Human tester specifically checks multiple quote and voice transcription.
725. Human tester specifically checks Calcmula chip and no-network OFF.
726. Human tester specifically checks Markdown entities after send.
727. Human tester specifically checks copy Markdown/HTML clipboard formats.
728. Human tester specifically checks code-block layout and recycled cells.
729. Human tester specifically checks docked shot is not duplicated.
730. Mark a row `built` only after APK is handed over.
731. Mark a row `done` only after human verifies on and off.
732. A batch is not done because unit tests pass.
733. A batch is not done because logcat is quiet.
734. A batch is not done while any exported patch is missing.
735. A batch is not done while `features.md` rows are missing.
736. A batch is not done while OFF differs from stock.
737. A batch is not done while account or recycle tests are unperformed.
738. This is the final gate for «поле ввода, текст и цитаты».
739. Any unresolved `[INFERENCE]` must be answered before code freeze.
740. Any behavior not supported by the inspected Android branch remains a question, not a guarantee.
