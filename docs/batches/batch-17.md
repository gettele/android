# Пачка 17 — отправка

## 1. Назначение и границы

1. Этот документ описывает реализацию только пачки 17 из `docs/PATCHLIST.md`.
2. Название пачки: «отправка».
3. Исходные строки пачки: 0130, 0318, 0153, 0157, 0259, 0254, 0215, 0220, 0226, 0269.
4. В пачку входят также retry, очередь за загрузкой, silent-отправка и send-options.
5. Документ не меняет `PATCHLIST.md` и не добавляет новый патч вне перечисленных строк.
6. Номера — текущие номера desktop-очереди.
7. Старые номера сверялись с `docs/desktop-numbers.md`.
8. Desktop-исходник следует читать из `origin/main`.
9. Android-исходник следует читать из ветки `tele`.
10. Рабочий checkout Android — соседний `Telegram/`.
11. Патчи экспортируются только после commit в checkout Android.
12. `.patch` вручную не редактируется.
13. Fork-код создаётся под `TMessagesProj/src/main/java/tele/`.
14. Stock-файлы получают минимальный gated-call.
15. `TLRPC.java` не редактируется.
16. Stock-схема базы не меняется.
17. Fork-состояние хранится в `tele_kv` и `tele_*`.
18. OFF должен быть строго равен поведению Telegram.
19. Все новые фичи имеют настройку `TeleConfig`.
20. Исключение — исправления, которые всегда исправляют ошибку.
21. «Always-on» ниже означает отсутствие пользовательского переключателя.
22. «OFF» означает default `false`.
23. Desktop default `true` не переносится автоматически.
24. Это следует из AGENTS.md, а не из предположения.
25. Сетевые запросы fork-кода должны проходить offline-гейты.
26. Аккаунт передаётся во все helper-и явно.
27. UI-изменения выполняются на main thread.
28. Callbacks tgnet и storage считаются background callbacks.
29. Recycled views обязаны полностью восстанавливать состояние в bind.
30. Анимации обязаны уважать `LiteMode`.

## 2. Решения и исходные документы

31. Решение по 0130 и 0318: подтверждение вторым тапом переносится.
32. Решение по 0153: MKV переносится частично, сначала device-проверка.
33. Решение по 0157: используется нативный opus-энкодер голосовых.
34. Решение по 0158 папкам: `Telegram/<чат>`, без SAF.
35. Решение по отправочным настройкам: Android default OFF.
36. Решение по 0259: альбомы остаются одним блоком.
37. Решение по 0269: chunking по 100 сообщений.
38. Решение по 0215: secret chats не ретраятся.
39. Решение по 0226: зависит от уже имеющегося Android 0058.
40. Android 0058 предоставляет `SendOrder.kt`.
41. Android 0057 предоставляет quick replies.
42. Android 0086 предоставляет docked media.
43. Android 0056 предоставляет базовый `PunctualScheduled`.
44. Android 0058 уже имеет очередь текста за media upload.
45. Эти факты взяты из PATCHLIST и desk notes.
46. Проверять их надо на `git show tele:<path>` перед кодированием.
47. [INFERENCE] Номера строк в исходниках могут измениться при rebase.
48. Поэтому anchor — символ, метод и соседний вызов, не голый line number.
49. [INFERENCE] Названия Java overload могут отличаться между upstream-снимками.
50. При несовпадении искать exact symbol через `rg`.

## 3. Сводка трудоёмкости и порядок

51. 0130 — M: общий confirm-helper и три picker-пути.
52. 0318 — S: тот же helper в `StickersAlert`.
53. 0153 — S: проверка расширения/codec и media attributes.
54. 0157 — L: UI, конвертация, временный файл, отправка voice.
55. 0259 — S: единичные send-запросы поверх форварда.
56. 0254 — S: exact-name quick-reply dispatch.
57. 0215 — M: retry state machine в upload operation.
58. 0220 — S: menu action и bulk retry.
59. 0226 — M: queue state UI и release action.
60. 0269 — M: selection limit и chunked delete/send.
61. Рекомендуемый порядок: 0130, 0318.
62. Затем 0153 и 0157.
63. Затем 0215.
64. Затем 0220.
65. Затем 0226.
66. Затем 0259.
67. Затем 0254.
68. Затем 0269.
69. Каждый пункт — отдельный commit.
70. Shared helper разрешён только если он уже нужен предыдущим commit.
71. Первая сборка после native-зависимостей может быть долгой.
72. Batch gate выполняется после всех десяти commit.
73. Порядок не означает merge в один commit.
74. Зависимости должны быть видны в commit subjects.
75. [INFERENCE] Точные названия subject выбрать по фактической реализации.

## 4. TeleConfig и настройки

76. Каждый toggle добавляется в `TeleConfig.kt`.
77. Каждый toggle имеет default `false`.
78. 0130: `confirm_send_media`.
79. 0318 использует тот же `confirm_send_media`.
80. 0153: `mkv_as_video`.
81. 0157: `audio_as_voice`.
82. 0259: `forward_one_by_one`.
83. 0254: `quick_replies_by_name`.
84. 0215: `retry_upload_chunks`.
85. 0220: `retry_all_failed`.
86. 0226 использует `queue_behind_media`.
87. 0269: `selection_over_100`.
88. Silent default — отдельная настройка не обязательна.
89. Silent default использует stock pref `silent_<dialogId>`.
90. Глобальный silent-toggle допускается только после подтверждения существующего API.
91. Не дублировать `SharedPreferences` для `silent_<dialogId>`.
92. `audio_as_voice` должен раскрывать зависимые options только ON.
93. `mkv_as_video` также раскрывает codec caveat.
94. `forward_one_by_one` раскрывает flood warning.
95. `retry_upload_chunks` раскрывает secret-chat limitation.
96. Settings section — `sending`.
97. 0130 и 0318 могут быть одной collapsible group.
98. `TeleSettingsActivity.buildRows` добавляет строки.
99. Search IDs обязаны быть стабильными.
100. Зарезервированный диапазон этой пачки: 1220..1239.
101. Рекомендуемая таблица ID: 1220 `confirm_send_media`.
102. 1221 `mkv_as_video`.
103. 1222 `audio_as_voice`.
104. 1223 `forward_one_by_one`.
105. 1224 `quick_replies_by_name`.
106. 1225 `retry_upload_chunks`.
107. 1226 `retry_all_failed`.
108. 1227 `queue_behind_media`.
109. 1228 `selection_over_100`.
110. 1229 `silent_default` если отдельная строка будет утверждена.
111. 1230 `send_media_confirmations` group.
112. 1231 `upload_retry_delay` только если появится user-facing option.
113. 1232 `scheduled_retry` только если этот batch расширят.
114. 1233 `mkv_codec_hint` — search-only label, не toggle.
115. 1234 `voice_conversion` group.
116. 1235 `send_options` group.
117. 1236 `retry_failed_media` alias search term.
118. 1237 `held_messages` alias search term.
119. 1238 `bulk_forward` alias search term.
120. 1239 `confirm sticker gif voice` alias search term.
121. Не создавать лишнюю настройку для always-on bugfix.
122. Search ID не равен pref key.
123. Список ID надо внести в `TeleSearch`.
124. Deeplink должен открывать sending group.
125. Export/import spec должен содержать каждый реальный item.
126. Group-only и alias IDs не экспортируются.
127. Ресурсы идут в `strings_tele.xml`.
128. Stock `strings.xml` не трогается.
129. Описания должны говорить о лимитах.
130. OFF-путь не должен вызывать helper.

## 5. 0130/0318: подтверждение второго тапа

131. Цель: первый тап выбирает sticker, GIF или voice.
132. Первый тап не отправляет выбранный media.
133. UI показывает выбранное состояние в send box.
134. Второй тап отправляет текущий объект.
135. Смена объекта сбрасывает pending confirmation.
136. Отмена picker-а сбрасывает pending confirmation.
137. Удаление draft сбрасывает pending confirmation.
138. Текстовые сообщения этим toggle не затрагиваются.
139. Фото и документы этим toggle не затрагиваются.
140. Scheduled media не должен обходить confirmation.
141. Paid media не должен обходить confirmation.
142. Stars и gift flows не входят в этот helper.
143. Основной hook — `EmojiView.EmojiViewDelegate.onStickerSelected`.
144. GIF hook — `onGifSelected` в том же delegate.
145. Voice hook — путь завершения записи в `ChatActivityEnterView`.
146. Проверить точное имя voice callback в ветке `tele`.
147. Общий helper — `tele/helpers/TeleSendConfirm.kt`.
148. Helper получает account, dialogId, media kind.
149. Helper не хранит Activity reference.
150. Pending state keyed by account and dialog.
151. Не использовать singleton state без account key.
152. State очищается при `onDestroy`/dialog change.
153. Первый тап должен быть idempotent при duplicate callback.
154. Второй тап должен повторно проверить permissions.
155. Второй тап должен повторно проверить dialog rights.
156. Второй тап должен уважать slowmode.
157. Второй тап должен уважать silent pref.
158. Для LiteMode не добавлять тяжёлую анимацию.
159. Recycled sticker cells не владеют pending state.
160. Confirm UI должен быть доступен keyboard-less.
161. Для доступности обновить content description.
162. Для 0318 hook — `StickersAlert` selection callback.
163. `StickersAlert` не должен отправить напрямую.
164. Он вызывает общий helper или delegate.
165. OFF: вызвать существующий stock callback без fork state.
166. ON: первый callback consumed только для pending state.
167. Двойной callback от picker не считать вторым тапом без проверки item id.
168. Не подтверждать thumbnail preload.
169. Не подтверждать inline bot results.
170. [INFERENCE] Текст кнопки подтверждения зависит от существующих ресурсов.
171. Использовать fork string, если stock string не подходит.
172. Не менять глобальный send button label.
173. В лог писать только kind и account, без содержимого.
174. Логирование должно быть debug-only.
175. Проверить rotation/recreate.
176. Проверить multi-account.
177. Проверить voice recording cancellation.
178. Проверить sticker pack close.
179. Проверить GIF download pending.
180. Проверить slow connection.

## 6. 0153: MKV как видео

181. PATCHLIST требует частичный перенос.
182. Сначала определить фактический Android stock behavior.
183. Hook искать в `SendMessagesHelper.prepareSendingDocument`.
184. Также проверить `prepareSendingVideo`.
185. Проверять extension case-insensitively.
186. Проверять MIME, если он уже известен.
187. Не менять имя файла пользователя.
188. Не подменять MKV на MP4 без реального transcode.
189. MKV может быть неподдержанным контейнером для Telegram video.
190. [INFERENCE] Нужен device test для конкретных codec tracks.
191. Если Android MediaMetadataRetriever не читает track — сохранить file path.
192. Если сервер отвергает video attributes — fallback должен быть stock document.
193. Fallback не должен маскировать exception.
194. Feature toggle OFF обязан идти в stock document path.
195. ON допускает video classification только при подтверждённых metadata.
196. Не добавлять новый TL field.
197. Использовать существующий `TL_documentAttributeVideo`.
198. Установить duration/width/height только из валидных metadata.
199. Не писать zero dimensions как валидные.
200. Не обещать streaming compatibility без device evidence.
201. LiteMode не относится к container classification.
202. Проверить отправку как file в secret chat.
203. Проверить protected content restrictions.
204. Проверить album mixed media.
205. Проверить caption and spoiler.
206. Проверить scheduled send.
207. Проверить retry после failed upload.
208. Если результат неоднозначен, оставить статус частичным.
209. Документировать конкретные codec samples в commit notes.
210. Не скачивать внешний probe binary.

## 7. 0157: аудиофайл как voice

211. UI hook — `ChatAttachAlertAudioLayout`.
212. Data hook — `MediaController`/`SendMessagesHelper`.
213. Использовать существующий native opus encoder.
214. Не добавлять новый third-party encoder.
215. Входной audio file должен быть readable.
216. Конвертация выполняется off main thread.
217. UI progress обновляется через `AndroidUtilities.runOnUIThread`.
218. Пока конвертация идёт, блокируется только соответствующая send operation.
219. Остальная переписка не блокируется.
220. Отмена удаляет временный opus file.
221. Failure удаляет временный opus file.
222. Success передаёт voice waveform и duration.
223. Waveform строится существующим helper-ом.
224. Не трогать `TLRPC.java`.
225. Hook в `SendMessagesHelper.sendMessage` должен быть gated.
226. Сохранить account id во временной job.
227. Не использовать currentAccount из UI позднее callback.
228. Secret chats сохраняют stock-compatible путь.
229. Paid media не превращать в voice.
230. Music metadata не должна попадать в caption автоматически.
231. Audio filename не должен становиться message text без stock behavior.
232. Проверить silent sending отдельно.
233. Проверить voice chat recording отдельно.
234. Проверить Bluetooth input не требуется для file conversion.
235. Обработать permission/read errors штатным dialog.
236. Retry conversion не должен повторно отправить уже отправленный voice.
237. Не создавать duplicate upload при rotation.
238. Переживание process death не обещается без durable job.
239. [INFERENCE] Durable conversion queue отсутствует в описанных Android системах.
240. Поэтому process-death recovery — вопрос, не скрытая гарантия.
241. L effort включает UI и native conversion coordination.
242. Настройка default OFF означает обычный document send.
243. Settings label не должен говорить «compress».
244. Label должен говорить «send audio as voice».
245. Проверить max duration stock voice limit.
246. При превышении лимита fallback должен быть document.
247. При неподдержанном input codec показать ошибку, не пустой voice.
248. Проверить mp3, m4a, ogg, wav.
249. Проверить album selection.
250. Проверить share-intent audio.

## 8. 0259: пересылка по одному

251. Основной hook — `SendMessagesHelper` forward entry.
252. Найти overload, принимающий `ArrayList<MessageObject>`.
253. Не раскалывать album media.
254. Обычные сообщения отправлять отдельными operations.
255. Сохранять исходный порядок.
256. Сохранять reply/forward metadata.
257. Ограничить parallelism согласно flood behavior.
258. Не считать local UI insertion успешной отправкой.
259. Ошибка одного item должна быть видима.
260. Остальные items не теряются.
261. Retry item должен иметь собственный local id.
262. Flood wait должен остановить или задержать runner.
263. [INFERENCE] Exact flood callback в Java недоступен до native hook.
264. В пачке 17 не добавлять JNI flood center.
265. Не переиспользовать one-by-one для albums.
266. Проверить protected messages.
267. Проверить secret chats.
268. Проверить scheduled forwards.
269. Проверить Saved Messages.
270. Проверить bot chats.
271. Проверить mixed text/photo/document selection.
272. OFF должен использовать stock batch forward.
273. ON хранит runner state per account.
274. Runner отменяется при leaving chat.
275. UI progress не должен обращаться к detached fragment.
276. Меню должно показывать итог successes/failures.
277. Не отправлять account data на tele server.
278. Tele logging не должен содержать message text.
279. Effort S только при наличии stock per-message send API.
280. Если API требует новый coordinator, пересмотреть effort.

## 9. 0254: быстрый ответ по точному имени

281. Hook — `ChatActivityEnterView` send path.
282. Resolver — `QuickRepliesController`.
283. Exact `/name` matching требует полного shortcut.
284. Prefix match не должен отправлять автоматически.
285. Не применять к bots.
286. Не применять к Stars.
287. Не применять к scheduled messages.
288. Не применять в secret chats, если controller не поддерживает их.
289. Зависимость — Android 0057.
290. Получить quick-reply content перед отправкой.
291. Content может быть text/photo/document.
292. Каждый item формируется свежим `SendMessageParams`.
293. Не передавать shortcut id в обычный forward API.
294. Отсутствующий remote media reference не считать local-file failure.
295. Обычный текст `/name` остаётся обычным, если exact reply не найден.
296. Не менять slash autocomplete UI без необходимости.
297. Проверить case sensitivity существующего controller.
298. Проверить Unicode shortcut names.
299. Проверить draft restore.
300. Проверить retry generated item.
301. Проверить caption entities.
302. Проверить per-account quick reply cache.
303. OFF — существующий slash behavior.
304. ON — только точный shortcut.
305. Не делать сеть tele.
306. [INFERENCE] Нужные публичные методы controller надо подтвердить grep-ом.
307. Если метод private, expose минимальным `tele_` API.
308. Не копировать content вручную в UI.
309. Preserve silent preference.
310. Preserve schedule date absence.

## 10. 0215: retry чанков загрузки

311. Hook — `FileUploadOperation`.
312. Область примерно описана как `FileUploadOperation.java:550–677`.
313. Точный anchor — upload request failure callback.
314. Retry только failed chunk.
315. Уже успешные chunks не отправлять повторно.
316. Сохранять offset, part size и file id.
317. Retry state per account and operation.
318. Не использовать один global retry counter.
319. Максимум/задержка должны соответствовать desktop patch.
320. [INFERENCE] Числа задержек нельзя угадывать без чтения origin/main patch.
321. Взять их из desktop implementation или decisions.
322. Не retry permanent auth/permission errors.
323. Не retry secret-chat uploads.
324. Не retry cancelled operations.
325. Cancel очищает retry callback.
326. Retry должен уважать connectivity.
327. Не создавать busy loop.
328. Применять exponential/backoff только по подтверждённой спецификации.
329. UI progress должен оставаться монотонным.
330. Recycler cells должны rebind paused/retrying state.
331. Error text не показывать как серверную success.
332. Проверить upload group.
333. Проверить large file.
334. Проверить network toggle.
335. Проверить app background.
336. Проверить process recreation limitation.
337. LiteMode не должен отключать retry.
338. OFF — stock one-shot behavior.
339. ON — retry only the failed part.
340. Logcat tag должен быть коротким и без path.

## 11. 0220: Retry all

341. Hook — `ChatActivity.fillMessageMenu`.
342. Menu registry — `tele/helpers/MessageMenu.kt`.
343. Пункт виден только если failed messages существуют.
344. Action должен быть gated `retry_all_failed`.
345. Retry all собирает текущий account only.
346. Не ретраить чужой account.
347. Не включать cancelled messages.
348. Не включать permanent failures.
349. Порядок — по исходному времени/порядку списка.
350. Не дублировать уже active retry.
351. После запуска пункт скрывается или disabled до результата.
352. Recycled menu popup должен bind state.
353. Success удаляет failed marker.
354. Failure оставляет item retryable.
355. Partial result показывает count.
356. Не показывать message text в logcat.
357. Не менять server history напрямую.
358. Проверить menu в topic.
359. Проверить Saved Messages.
360. Проверить channel rights.
361. OFF — пункт отсутствует и stock menu равен stock.
362. `OPTION_RETRY` должен быть единой константой.
363. Не добавлять второй retry action key.
364. `TeleHooks.onConfigChanged` обновляет visible menus.
365. [INFERENCE] Toast resource name надо сверить со stock resources.

## 12. 0226: отпустить сообщение очереди

366. Основа — `SendOrder.kt` из Android 0058.
367. Hook меню — `MessageMenu.kt` и `ChatActivity.fillMessageMenu`.
368. Hook bubble — `ChatMessageCell` bind/action path.
369. Held message должен быть видимым.
370. Held state не должен выглядеть sent.
371. Пункт «send now» виден только held item.
372. Release снимает dependency на upload.
373. Release не отменяет active upload, если он ещё нужен другому item.
374. Если upload уже успешен, release flushes immediately.
375. Если upload failed, release должен показать failure.
376. Не удалять message из queue до send result.
377. Очередь keyed by account, dialog and media group.
378. Учитывать отрицательные local ids.
379. Раннее сообщение с отрицательным id сравнивается корректно.
380. Учитывать upload groups.
381. Учитывать active sending media до server ack.
382. Flush после final media RPC success/failure.
383. Cancel вызывает `markCancelled`.
384. После очистки send/upload state нужен targeted flush.
385. Ответы мимо очереди сохраняются.
386. Force-send не должен нарушить order других items.
387. OFF использует существующий queue_behind_media semantics.
388. Если `queue_behind_media` OFF, no held state.
389. `send_older_replies` остаётся независимым.
390. `double_enter_send` не менять в этой строке.
391. Проверить bubble action after recycle.
392. Проверить rotation.
393. Проверить upload cancellation.
394. Проверить two accounts.
395. Проверить album upload group.
396. Проверить scheduled conflict.
397. Проверить secret chat exclusion.
398. Не добавлять third-party queue.
399. Log queue transitions only debug.
400. UI updates main thread.

## 13. 0269: более 100 сообщений

401. Цель — снять UI selection cap, не серверный limit.
402. Разрешить selection больше 100 только при `selection_over_100` ON.
403. Default OFF сохраняет stock cap.
404. Requests нарезаются чанками по 100.
405. Chunking выполняется data layer.
406. Hook — `ChatActivity` selection bookkeeping.
407. Delete hook — `MessagesController.deleteMessages`.
408. Forward path согласуется с 0259.
409. Каждый chunk имеет result callback.
410. Не считать весь batch success до всех chunks.
411. Failed chunk сохраняет retryable state.
412. Flood wait не создаёт tight loop.
413. Rights checks выполняются перед каждым chunk.
414. Protected/service exclusions сохраняются.
415. Topic peer id передаётся в каждый request.
416. Saved Messages передаётся явно.
417. Account id не брать из static current account.
418. Selection action mode показывает точный count.
419. Recycler action mode rebinds count.
420. Rotation не должна повторно послать chunk.
421. Duplicate callback idempotent по operation id.
422. Operation отменяется при leaving screen.
423. Отмена не удаляет уже подтверждённые chunks.
424. Проверить delete, forward и copy separately.
425. Пачка PATCHLIST требует chunking по 100.
426. Не менять Telegram API лимит.
427. Не редактировать TLRPC.
428. [INFERENCE] Точная модель operation id требует чтения существующего controller.
429. Без этого не вводить глобальный mutable counter.
430. Logcat пишет chunk index/count без message contents.

## 14. Папки загрузок

431. Папки по чатам связаны с 0158 и находятся в другой пачке.
432. В пачке 17 только не ломать save path.
433. Не добавлять папку как скрытую зависимость.
434. Реализация 0158 должна использовать `MediaController.saveFile`.
435. Путь: публичная `Telegram/<чат>`.
436. SAF не используется по решению maintainer.
437. Имена должны быть безопасны для filesystem.
438. Chat title не писать в tele server.
439. Account separation проверяется при выборе path.
440. [INFERENCE] Точный API MediaStore зависит от upstream snapshot.
441. Не фиксировать строку API без `git show tele`.
442. Download failures не должны менять send retries.
443. Upload path и download path не смешивать.
444. Folder toggle, если добавляется, default OFF.
445. OFF — stock public folder.

## 15. SendMessagesHelper anchors

446. Найти `sendMessage` overloads.
447. Найти `prepareSendingDocument`.
448. Найти `prepareSendingVideo`.
449. Найти `sendSticker`.
450. Найти `sendMedia` с caption.
451. Найти forward `ArrayList<MessageObject>` overload.
452. Добавлять только `TeleHooks` call или `tele_` exposure.
453. Не переименовывать stock методы.
454. Не переформатировать соседний код.
455. Каждая ветка проверяет `TeleConfig` до fork work.
456. Ошибки передаются в helper, не глотаются.
457. Callback account захватывает immutable account.
458. UI callback маршалится на main.
459. Media metadata nullable-check обязателен.
460. `VideoEditedInfo.muted` используется только по существующей семантике.
461. Silent video option не менять без отдельного toggle.
462. Sticker caption зависит от 0175 и не изобретать здесь.
463. Docked media зависит от 0096, не дублировать.
464. Upload retry не создаёт новый `FileUploadOperation` для успешного part.
465. Scheduled send не включать в one-by-one.

## 16. PunctualScheduled и scheduled

466. `PunctualScheduled.kt` уже есть в ветке `tele`.
467. Базовый scheduler проверяет `scheduled_messages_v2`.
468. Для batch 17 его не расширять без PATCHLIST строки.
469. `date <= now` и `mid > 0` — существующие условия.
470. Ошибки scheduled retry относятся к отдельной доработке 0095.
471. Не смешивать retry upload 0215 и scheduled retry.
472. Если send-options вызывают scheduled path, сохранять `schedule_date`.
473. Quick reply 0254 scheduled не поддерживает.
474. One-by-one 0259 scheduled требует явного исключения.
475. [INFERENCE] Не менять PunctualScheduled без отдельного commit.

## 17. Потоки, аккаунты и recycling

476. Main thread: rows, menus, cells, progress labels.
477. Background: encoder, file IO, upload callbacks, storage reads.
478. `AndroidUtilities.runOnUIThread` — переход к UI.
479. `MessagesStorage` callback нельзя bind-ить прямо.
480. `ConnectionsManager` callback нельзя трогать view напрямую.
481. Every helper receives `currentAccount` at creation.
482. `MessagesController.getInstance(account)` only with explicit account.
483. `UserConfig.getInstance(account)` only with explicit account.
484. Multi-account test is mandatory for state isolation.
485. Recycled `ChatMessageCell` clears held/failed flags before bind.
486. Recycled menu clears conditional item visibility before rebuild.
487. Recycled picker clears confirmation highlight.
488. Dialog switch clears pending confirm state.
489. `LiteMode` suppresses optional animation only.
490. LiteMode must not suppress correctness retry.
491. Avoid Activity leaks in encoder callbacks.
492. Weak references are acceptable only with cancellation path.
493. Do not retain Fragment after destroy.
494. Notification channels are not part of this batch.
495. If a notification is added, use dedicated channel id.

## 18. Privacy and network

496. No tele-server request is needed for these features.
497. Message text must never leave device for telemetry.
498. File paths must never enter tele-server requests.
499. Retry metadata stays local.
500. Quick reply content stays Telegram account scope.
501. Offline switches apply to fork-only network work.
502. Telegram API calls remain Telegram API calls when user enabled feature.
503. Do not interpret `-teleoffline` as disabling stock sends.
504. Secret chat limitations are explicit in UI/help.
505. Protected content rules remain stock rules.
506. Payment/Stars media is not silently transformed.
507. Error logs redact peer/message content.
508. Debug logs may include operation kind and numeric chunk index.
509. Account id in logs must be local index only.
510. Production logs should be quiet.

## 19. Exact UX and limits

511. Confirm: first tap selects, second tap sends.
512. Confirm applies sticker, GIF, voice only.
513. Retry chunk: retry failed part, not whole file.
514. Retry all: only retryable failed messages.
515. Queue release: one held message can bypass dependency.
516. Selection: chunks of 100.
517. Forward: albums stay together.
518. MKV: classify only with valid metadata.
519. Audio voice: native encoder and stock voice limits.
520. Quick reply: exact slash name only.
521. Silent: per-chat `silent_<dialogId>`.
522. No new server endpoint is required.
523. No new tele endpoint is required.
524. Telegram methods remain stock MTProto methods.
525. [INFERENCE] UI wording needs final localization review.
526. Use no claims about unsupported codecs.
527. Show partial failure counts.
528. Never claim retry succeeded before callback.
529. Keep progress monotonic.
530. Respect cancellation.

## 20. Planned commits

531. `feat: confirm media sends` for 0130.
532. `feat: confirm sticker picker sends` for 0318.
533. `feat: send mkv as video` for 0153.
534. `feat: send audio as voice` for 0157.
535. `feat: retry failed upload parts` for 0215.
536. `feat: retry failed messages` for 0220.
537. `feat: release held messages` for 0226.
538. `feat: forward messages individually` for 0259.
539. `feat: send exact quick replies` for 0254.
540. `feat: chunk large selections` for 0269.
541. Actual subjects must obey repository commit rules.
542. Maximum subject length is 50 characters.
543. Each commit is exported to `patches/android/`.
544. Features rows are added in the same commit as each user-facing patch.
545. Features rows are English.
546. Each row names setting page, default, patch, desktop source.
547. Always-on fixes may have no setting row only if truly invisible.
548. If a fix changes UX, it needs a row or maintainer decision.
549. Do not update features.md in this documentation-only assignment.
550. This guide only specifies that future implementer obligation.

## 21. Test matrix

551. Build debug APK after all commits.
552. Test every new toggle OFF first.
553. OFF must match stock behavior.
554. Test every toggle ON second.
555. Confirm sticker first/second tap.
556. Confirm GIF first/second tap.
557. Confirm voice first/second tap.
558. Confirm cancellation.
559. Confirm picker recreation.
560. MKV valid video sample.
561. MKV unsupported codec sample.
562. MKV fallback file sample.
563. Audio mp3 to voice.
564. Audio m4a to voice.
565. Audio conversion cancellation.
566. Audio duration over limit.
567. Forward text one-by-one.
568. Forward photo one-by-one.
569. Forward album remains grouped.
570. Forward flood/error behavior.
571. Exact quick reply.
572. Near-match quick reply remains text.
573. Quick reply media.
574. Quick reply retry.
575. Upload failed first chunk.
576. Upload failed middle chunk.
577. Upload failed final chunk.
578. Retry all partial result.
579. Retry after cancellation.
580. Held message visible.
581. Release held message.
582. Release after upload failure.
583. Negative local id ordering.
584. Two accounts held independently.
585. Selection 101 messages OFF.
586. Selection 101 messages ON.
587. Selection 201 messages gives three chunks.
588. Delete chunk failure.
589. Forward chunk failure.
590. Topic selection.
591. Saved Messages selection.
592. Secret-chat exclusions.
593. Protected-content exclusions.
594. Rotation between selection and send.
595. Process background/foreground.
596. LiteMode ON.
597. LiteMode OFF.
598. Slow network.
599. Offline/online transition.
600. Multi-account.

## 22. Logcat and evidence

601. Use dedicated tags: `TeleSendConfirm`, `TeleUpload`, `TeleRetry`, `TeleQueue`.
602. Do not log message text.
603. Do not log file path.
604. Do not log username.
605. Log account index, operation kind and state.
606. Log chunk index only.
607. Log retry reason class, not raw sensitive error.
608. Log UI transition only debug builds.
609. Capture success callback evidence.
610. Capture failure callback evidence.
611. Capture cancel evidence.
612. Capture queue release evidence.
613. Capture chunk count evidence.
614. Capture OFF-path evidence.
615. Record exact device/API/ABI.
616. Native build must include all required ABIs if touched.
617. This batch should not touch JNI.
618. If a proposed solution needs JNI, stop and surface dependency.
619. Do not call a compile result a device result.
620. Do not call a plausible path verified.

## 23. Decisions/questions before coding

621. Confirm whether 0130 applies voice file selection as well as recording.
622. Confirm exact stock picker callback names in `tele`.
623. Confirm whether 0153 accepts only extension or MIME plus metadata.
624. Confirm supported MKV codec set from device test.
625. Confirm maximum voice duration from stock path.
626. Confirm exact retry delay/max-attempt values in `origin/main`.
627. Confirm whether 0220 includes scheduled failures.
628. Confirm album definition for 0259.
629. Confirm quick-reply exact matching case policy.
630. Confirm whether 0269 covers copy or only delete/forward.
631. Confirm whether selection cap is UI-only or request cap.
632. Confirm 0158 remains separate from batch 17.
633. Confirm whether silent default needs a new global row.
634. Confirm search ID allocation does not collide with existing IDs.
635. Confirm feature rows and patch filenames after export.
636. [INFERENCE] These are questions because supplied docs do not establish all details.
637. Do not resolve them by guessing.
638. Record answers in decisions.md if maintainer decides.
639. Update this guide only in a later documentation change.
640. Keep implementation scope unchanged until answered.

## 24. Batch gate

641. All ten PATCHLIST rows must be committed.
642. All ten patch files must be exported.
643. `PATCHLIST.md` statuses move truthfully.
644. `features.md` rows exist for user-facing changes.
645. Debug APK is assembled.
646. Device/emulator tests run with toggles OFF and ON.
647. Gate device tests include the exact matrix above.
648. Gate checks logcat for retry and queue transitions.
649. Gate checks no tele-server upload of account data.
650. Gate checks multi-account isolation.
651. Gate checks secret-chat exclusions.
652. Gate checks LiteMode behavior.
653. Gate checks recycled-cell state.
654. Gate checks cancellation cleanup.
655. Human maintainer verifies the APK.
656. `built` means APK assembled, not manually verified.
657. `done` means human verification passed.
658. Do not mark done from compilation alone.
659. A failed device test keeps the row open.
660. A partial MKV result keeps 0153 partial.
661. Batch gate is after implementation, not after this guide.
662. This file is the implementation handoff.
663. No commit is made by this assignment.
664. No Android source is edited by this assignment.
665. No patch file is edited by this assignment.
666. The only requested output is this Markdown guide.
667. [INFERENCE] Exact source anchors require final branch grep.
668. The named classes and methods are the required search anchors.
669. The defaults and limits above are contractual where cited.
670. Unconfirmed details remain explicitly marked.
