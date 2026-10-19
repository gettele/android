# Пачка 23 — подарки: пароль и массовые действия

## 1. Назначение и границы

1. Этот документ — пошаговое руководство для пачки 23 из `docs/PATCHLIST.md`.
2. Название пачки в планировщике: «подарки: пароль и массовые действия».
3. Номера здесь — текущие номера очереди desktop `origin/main`.
4. Старые номера v7.2.9 не использовать; соответствие проверяется в `docs/desktop-numbers.md`.
5. Desktop-поведение сверено через `git show origin/main:patches/tdesktop/...`.
6. Android-якоря сверены через `git show tele:...` в checkout `Telegram`.
7. Desktop C++/Qt нельзя копировать: переносится наблюдаемое поведение.
8. Состав пачки: 0187, 0217, 0213, 0184, 0185, 0186, 0190, 0192, 0193, 0207 и 0224.
9. 0187 — локальная защита операций со звёздами и подарками.
10. 0217 — та же защита для bot payments и платных сообщений.
11. 0184 — несколько одинаковых звёздных подарков за один сценарий UI.
12. 0185 — приглушение скрытых подарков и мультивыбор сохранённых подарков.
13. 0186 — поиск в списке подарков.
14. 0190 — массовые show/hide, pin/unpin, transfer, sell/unlist, convert и коллекции.
15. 0192 — поиск, фильтры и CSV для истории звёздных транзакций.
16. 0193 — диапазон дат для длинных списков: media, gifts и transactions.
17. 0207 — копирование ссылки коллекции подарков.
18. 0224 — повтор загрузки коллекций подарков.
19. 0213 — общий последовательный раннер, который переживает flood wait и плохие элементы.
20. 0213 нельзя считать самостоятельным обходом tgnet-лимитов.
21. Его контракт с уведомлением о flood wait из пачки 22 должен быть согласован.
22. Все новые тумблеры обязаны иметь default `false`.
23. При OFF поведение Android должно быть ровно stock.
24. При OFF нельзя создавать раннер, observer, файл, chooser, запрос или фоновую работу этой пачки.
25. Код форка размещается в новых файлах `tele/`.
26. В stock-файлах разрешены только минимальный gated call, ранний return или открытие API.
27. `TLRPC.java` не изменять: это сгенерированный файл.
28. Stock-схему и `LAST_DB_VERSION` не изменять.
29. Fork-состояние хранить в `tele_kv` или собственных `tele_*` таблицах.
30. Не посылать tele-server данные аккаунта, подарков, контактов, сообщений или платежей.
31. Любой внешний запрос к api.changes.tg из будущей студии в эту пачку не добавлять.
32. 0207 и 0224 используют Telegram API, а не tele-server.
33. UI обновлять только на main thread.
34. Callback Telegram, storage и tgnet считать background callback до явного перехода на UI.
35. Состояние всегда ключевать `currentAccount` и `dialogId`.
36. Не использовать singleton account 0 внутри runner или password manager.
37. Recycler-ячейка обязана заново применять alpha, checked и badge в каждом bind.
38. Анимации списка и карточек обязаны уважать `LiteMode` и performance class.
39. Платёжные и необратимые действия не должны запускаться от bind, restore или retry UI.
40. `[INFERENCE]` означает предложение, которое ещё нужно подтвердить кодом или решением.
41. `[OPEN]` означает вопрос, который нельзя закрывать догадкой.
42. `[SOURCE]` означает наблюдение из указанного дерева или patch diff.
43. Цель — debug APK и ручное тестирование на отдельном тестовом аккаунте.
44. Успешная компиляция не является доказательством работы пачки.
45. Статусы PATCHLIST менять только после commit, export и ручной проверки.

## 2. Денежная безопасность — обязательное ограничение

46. Операции gifts могут тратить реальные Stars, TON или деньги.
47. Отправка подарка — платёжная операция даже когда в UI показывается только Stars.
48. Transfer может потребовать комиссию, а sell может выставить реальную цену.
49. Convert меняет подарок на Stars и может быть необратимым.
50. Buy resale, bot payment и paid message также являются денежными действиями.
51. Массовый retry не должен повторять уже успешно оплаченный элемент.
52. Перед каждой ручной проверкой выбрать тестовый аккаунт и тестового получателя.
53. Баланс тестового аккаунта должен быть минимальным, заранее пополненным только для теста.
54. Нельзя запускать destructive, transfer, convert, sell, unlist или payment сценарий на maintainer account.
55. Нельзя проверять quantity на аккаунте maintainer.
56. Нельзя проверять flood retry настоящей покупкой на аккаунте maintainer.
57. Для maintainer account разрешены только чтение, поиск, OFF-проверки и просмотр настроек.
58. В тест-плане явно записать номер тестового аккаунта, но не класть его в репозиторий.
59. Скриншоты и logcat должны скрывать peer id, invoice id, form id и баланс.
60. Не включать verbose logging тела invoice, hash, payment form или cloud password.
61. Подтверждение должно показывать получателя, количество, итоговую цену и тип действия.
62. Текст «Convert» должен предупреждать о необратимости, если это подтверждено API.
63. Если сервер возвращает неизвестную цену, действие отменить, а не продолжать.
64. Если availability или `per_user_remains` изменились, повторно показать итог перед оплатой.
65. Retry после timeout требует идемпотентного серверного результата, а не слепой повтор оплаты.
66. `[OPEN]` Нужен подтверждённый контракт серверной идемпотентности `sendStarsForm`.
67. До ответа на этот вопрос runner должен различать «form not sent» и «result unknown».
68. При `result unknown` показывать паузу и ручную проверку истории, не повторять автоматически.
69. Локальный пароль — дополнительная защита устройства, не замена cloud password.
70. Биометрия должна быть Android system prompt и не должна отправлять отпечаток tele-сервису.
71. При недоступной биометрии остаётся ввод локального пароля.
72. При отключённом локальном пароле stock подтверждения должны остаться неизменными.

## 3. Проверенные исходники и Android anchors

73. `[SOURCE]` Desktop 0184 добавляет quantity counter в `star_gift_box`.
74. `[SOURCE]` Desktop 0184 вызывает `payments.getPaymentForm`, затем `payments.sendStarsForm` для каждого элемента.
75. `[SOURCE]` Desktop 0184 останавливается на первой ошибке и показывает `Sent X of N`.
76. `[SOURCE]` Desktop 0184 ограничивает quantity доступностью подарка и `perUserRemains`.
77. `[SOURCE]` Android `SendGiftSheet.buyStarGift()` находится в `org/telegram/ui/Gifts/SendGiftSheet.java`.
78. `[SOURCE]` Android `buyStarGift()` вызывает `StarsController.getInstance(currentAccount).buyStarGift(...)`.
79. `[SOURCE]` Android `StarsController.buyStarGift` находится около строки 2619 ветки `tele`.
80. `[SOURCE]` этот метод сам создаёт `TL_payments_getPaymentForm` около строки 2653.
81. `[SOURCE]` успешная форма создаёт `TL_stars.TL_payments_sendStarsForm` около строки 2670.
82. `[SOURCE]` Android повторно вызывает `buyStarGift` после `StarsNeededSheet` при недостатке Stars.
83. Поэтому password gate должен стоять до form request, а не только перед последним callback.
84. Поэтому quantity runner должен переиспользовать существующий payment flow, не строить invoice вручную.
85. `[SOURCE]` Android `StarsController` содержит другие `sendStarsForm` около 1491, 1608, 2506 и 2906.
86. Каждая точка должна быть классифицирована по назначению, а не закрыта одним опасным глобальным if.
87. `[SOURCE]` Android `ProfileGiftsContainer` хранит `currentAccount`, `dialogId` и `StarsController.GiftsList`.
88. `[SOURCE]` `ProfileGiftsContainer` использует `TL_stars.saveStarGift` около 667, 827 и 914.
89. `[SOURCE]` `StarsController.GiftsList` имеет `togglePinned` и вызывает `toggleStarGiftsPinnedToTop`.
90. `[SOURCE]` `StarsController` держит `giftLists` и `giftCollections` на account-aware controller.
91. `[SOURCE]` Android `StarsIntroActivity` создаёт `StarsTransactionsLayout` около 262.
92. `[SOURCE]` класс `StarsTransactionsLayout` начинается около строки 1194.
93. `[SOURCE]` `AlertsCreator.ensurePaidMessageConfirmation` находится около строки 2420.
94. `[SOURCE]` этот метод уже принимает `currentAccount`, `dialogId`, count и callback цены.
95. `[SOURCE]` Desktop 0187 перечисляет действия TransferGifts, ConvertGifts, SellGifts, UpgradeGifts, BuyGifts и SendGifts.
96. `[SOURCE]` Desktop 0187 хранит пароль отдельно от action toggles.
97. `[SOURCE]` Desktop 0187 сбрасывает локальный пароль через cloud password.
98. `[SOURCE]` Desktop 0187 имеет десятисекундную задержку reset без cloud password.
99. `[SOURCE]` Desktop 0217 добавляет BotPayments и PaidMessages как отдельные actions.
100. `[SOURCE]` Desktop 0190 добавляет show, hide, pin, unpin, transfer, sell, unlist, convert и collection.
101. `[SOURCE]` Desktop 0190 перед batch проверяет невозможные элементы и показывает причину.
102. `[SOURCE]` Desktop 0192 CSV содержит id, date, direction, amount, nano, currency, peer, peer_id, type, title, description, gift, gift_slug, gift_id и msg_id.
103. `[SOURCE]` Desktop 0192 сначала догружает всю историю, если пользователь выбрал export до конца загрузки.
104. `[SOURCE]` Desktop 0193 использует диапазон календарных дат и применяет его к gifts, media и credits.
105. `[SOURCE]` Desktop 0224 повторяет загрузку gift collections после ошибки через 3 секунды.
106. `[SOURCE]` Desktop 0213 имеет `GiftBatch`, `Runner`, progress, finished и обработчик `FloodWait`.
107. `[SOURCE]` Desktop 0213 пропускает плохие элементы по `skipFailed` и не теряет выбранный список.
108. `[SOURCE]` Desktop 0213 перечисляет payment API: getPaymentForm, sendStarsForm, saveStarGift, transferStarGift, updateStarGiftPrice и convertStarGift.
109. `[SOURCE]` Desktop 0213 получает flood events из отдельного `tele_flood_wait` контракта.
110. `[SOURCE]` `[INFERENCE]` Android должен получить эквивалентный event contract от пачки 22, а не парсить текст ошибок в каждом UI.

## 4. Коммиты, оценка, зависимости и порядок

111. Коммит A: `feat: add local gift password`.
112. A покрывает password model, biometric prompt, action policy и gift payment gates.
113. A — effort M.
114. A зависит от существующих `TeleConfig`, settings rows и Android password primitives.
115. Коммит B: `feat: protect paid message payments`.
116. B покрывает 0217: paid messages, bot payment forms и их action mapping.
117. B — effort S.
118. B зависит от A и `AlertsCreator.ensurePaidMessageConfirmation`.
119. Коммит C: `feat: send gift quantities`.
120. C покрывает 0184: quantity UI, clamping, one final confirmation и serial sends.
121. C — effort M.
122. C зависит от A и `StarsController.buyStarGift`.
123. Коммит D: `feat: select and dim profile gifts`.
124. D покрывает 0185: dim hidden gifts, checked state и selection mode.
125. D — effort L.
126. D зависит от A для destructive/paid action entry points.
127. Коммит E: `feat: search profile gifts`.
128. E покрывает 0186: text/type chips и filtering loaded/loaded-next pages.
129. E — effort M.
130. E зависит от D и `StarsController.GiftsList`.
131. Коммит F: `feat: run bulk gift actions`.
132. F покрывает 0190: actions, preflight reasons, transfer, sale and conversion.
133. F — effort M.
134. F зависит от A, D и runner infrastructure.
135. Коммит G: `feat: survive gift batch waits`.
136. G покрывает 0213: shared runner, flood pause, skip bad item, resume and summary.
137. G — effort M, but can become L if JNI contract from batch 22 is absent.
138. G depends on batch 22 flood event implementation.
139. Коммит H: `feat: search and export star transactions`.
140. H покрывает 0192: filters, full-history load and CSV share sheet.
141. H — effort M.
142. H depends on account-aware Stars transactions data.
143. Коммит I: `feat: filter lists by date`.
144. I покрывает 0193: shared date state for media, gifts and transactions.
145. I — effort M.
146. I depends on E and H, but media date hook may be isolated.
147. Коммит J: `feat: copy gift collection links`.
148. J покрывает 0207 рядом со stock Share action.
149. J — effort S.
150. J can precede E after exact collection URL contract is confirmed.
151. Коммит K: `fix: retry gift collections`.
152. K покрывает 0224 and only retries collection loading.
153. K — effort S.
154. K depends on the existing `GiftsCollections.load` lifecycle.
155. Recommended order: A, B, C, D, E, F, G, H, I, J, K.
156. Do not merge G into every UI commit.
157. Do not make F start before A has a tested gate.
158. Do not export a patch before its commit and feature row exist.
159. Export each Android commit separately with `git format-patch`.
160. Build once after K and again after any native flood integration.
161. `[INFERENCE]` If batch 22 is not `done`, G must be queued but not claimed complete.
162. `[OPEN]` Confirm whether 0213 is allowed to depend on an unbuilt batch-22 callback.
163. Planned effort summary: S×3, M×7, L×1 as recorded in PATCHLIST.
164. The L item is 0185 because list mode, action bar and recycling interact.
165. Payment safety is a release blocker independent of effort estimate.

## 5. TeleConfig, settings, search IDs and export/import

166. Add a parent `GIFTS_BULK` boolean item with key `gifts_bulk`, default OFF.
167. Add `LOCAL_PASSWORD` as a password-setting item, with no plaintext default.
168. Add `GIFT_PASSWORD_BUY` boolean, default OFF.
169. Add `GIFT_PASSWORD_SEND` boolean, default OFF.
170. Add `GIFT_PASSWORD_TRANSFER` boolean, default OFF.
171. Add `GIFT_PASSWORD_CONVERT` boolean, default OFF.
172. Add `GIFT_PASSWORD_SELL` boolean, default OFF.
173. Add `GIFT_PASSWORD_PAID_MESSAGES` boolean, default OFF.
174. Add `GIFT_PASSWORD_BOT_PAYMENTS` boolean, default OFF.
175. Add `GIFT_QUANTITY` boolean, default OFF.
176. Add `GIFT_SELECT` boolean, default OFF.
177. Add `GIFT_HIDDEN_DIM` boolean, default OFF.
178. Add `GIFT_SEARCH` boolean, default OFF.
179. Add `STAR_TRANSACTIONS` boolean, default OFF.
180. Add `LIST_DATES` boolean, default OFF.
181. Add `GIFT_COLLECTION_LINK` boolean, default OFF.
182. Add `GIFT_COLLECTION_RETRY` boolean, default OFF.
183. Add `GIFT_BATCH_RUNNER` boolean, default OFF.
184. Add `GIFT_BIOMETRIC` boolean, default OFF.
185. Keep each item in `TeleConfig.kt`; do not invent a second preferences registry.
186. The parent row should gate child rows in `TeleSettingsActivity.buildRows`.
187. Enabling a child may offer to enable the parent, but must not silently enable payments.
188. Local password setup is a screen/action, not a boolean containing the secret.
189. Put rows under a Gifts / payments group in the actual settings page structure.
190. Put password reset next to password setup, not in an unrelated privacy page.
191. Add search/deeplink entries with reserved IDs 1340 through 1359.
192. 1340: `tele gifts`, root gifts action page.
193. 1341: `local password`, password setup/reset page.
194. 1342: `gift password buying`, buy gift gate.
195. 1343: `gift password sending`, quantity/send gate.
196. 1344: `gift password transfer`, transfer gate.
197. 1345: `gift password convert`, convert gate.
198. 1346: `gift password sell`, sell and unlist gate.
199. 1347: `paid messages password`, paid message gate.
200. 1348: `bot payments password`, bot invoice gate.
201. 1349: `send several gifts`, quantity UI.
202. 1350: `select several gifts`, profile selection mode.
203. 1351: `dim hidden gifts`, hidden gift appearance.
204. 1352: `search gifts`, gift search/filter page.
205. 1353: `gift date filter`, saved gift date range.
206. 1354: `search star transactions`, transaction search.
207. 1355: `export star transactions csv`, CSV share action.
208. 1356: `transaction date filter`, transaction date range.
209. 1357: `media date filter`, shared media date range.
210. 1358: `gift collection link`, copy/share collection URL.
211. 1359: `gift collection retry`, retry loading collections.
212. `[INFERENCE]` IDs 1340–1359 are a reserved block and must be checked against the current search registry before code.
213. Do not reuse an existing GUID even if a title is similar.
214. Search entries must route to the exact screen or row, not just the settings root.
215. Search keywords include `stars`, `credits`, `payments`, `bulk`, `quantity`, `multiple`, `gift`, `transfer`, `convert`, `sell`, `CSV`, `calendar` and `date`.
216. Search titles and setting labels go to `strings_tele.xml`.
217. Do not edit stock `strings.xml`.
218. Add every setting key to the existing export/import specification.
219. Password material must never be exported as plaintext or reversible key material.
220. Export may include enabled action policy, biometric preference and feature toggles.
221. Import of a password hash must be rejected unless its format and device binding are explicit.
222. `[INFERENCE]` Safest default is to omit local password state from export and require setup again.
223. Import must not enable any payment gate without an explicit user action after import.
224. On config change, refresh visible rows and invalidate only affected gift UI.
225. Turning OFF a gate must not cancel an already confirmed server request.
226. Turning OFF runner stops starting new batch work; it cannot falsify a completed result.

## 6. Local password, biometrics and reset

227. Create a fork helper such as `tele/helpers/GiftPassword.kt`.
228. Keep action policy in one helper, not duplicated in each gift screen.
229. Define actions equivalent to Buy, Send, Transfer, Convert, Sell, PaidMessages and BotPayments.
230. Include Upgrade only if Android has a reachable paid upgrade request in this batch.
231. `[INFERENCE]` Upgrade should remain a policy action even if its UI is delivered later.
232. `requirePassword(account, action, continuation)` must be account-aware.
233. `requirePassword` must call continuation exactly once.
234. A cancelled biometric prompt must not call continuation.
235. A cancelled password dialog must not call continuation.
236. A destroyed fragment must not reopen a dialog from a stale continuation.
237. A successful unlock may be cached briefly for one user-confirmed series.
238. Cache key must include account and action, and expire on background/timeout.
239. `[INFERENCE]` A single cache entry for all accounts is unsafe and prohibited.
240. Show one password prompt before a quantity series, not once per gift.
241. Show one password prompt before a selected bulk series, not once per gift.
242. Re-prompt when the action changes from transfer to convert or payment.
243. Biometrics must use `BiometricPrompt` on the current activity/fragment lifecycle.
244. Check device capability and enrolled biometrics before displaying the biometric button.
245. Never log biometric result, local password text, salt or derived hash.
246. Clear password `CharSequence`/byte buffers after verification where the API permits.
247. Do not use a reversible plaintext SharedPreferences value.
248. Do not use the cloud password itself as local password storage.
249. `[INFERENCE]` Store only a salted verifier, preferably wrapped by Android Keystore.
250. `[INFERENCE]` Reuse existing fork Argon2 utility only after confirming parameters and lifecycle suitability.
251. Do not assume desktop OpenSSL KDF output is compatible with Android.
252. Version the verifier format so migration is explicit and testable.
253. Bind verifier metadata to account, not to the current selected fragment.
254. Store fork data in `tele_kv` keyed by account, or a dedicated tele table.
255. Do not touch stock account password rows or stock DB version.
256. On logout, clear local verifier and unlock cache for that account.
257. On account switch, immediately invalidate unlock state from the previous account.
258. On process restart, require password or biometric again.
259. Password setup requires new password and repeat field.
260. Password change requires current local password first.
261. Reset button must say that Stars/gifts protection is removed.
262. If cloud password exists, request it through the stock cloud-password API.
263. Reuse the existing Android cloud-password UI/API discovered in the current branch.
264. `[OPEN]` Exact Android cloud-password class/method must be confirmed before wiring reset.
265. Do not invent `TLRPC` constructors for cloud password.
266. Cloud reset success clears only the local verifier and local unlock cache.
267. Cloud reset failure leaves the local verifier untouched.
268. If no cloud password exists, require a visible countdown before reset.
269. The countdown must survive neither process death nor account switching.
270. The reset path must not silently call any payment or gift request.
271. Password setup and reset are local-only and need no tele-server request.
272. Gate `StarsController` before each `getPaymentForm` path that buys a gift.
273. Gate `sendStarsForm` paths only where the form action is a protected bot payment or paid message.
274. Do not gate unrelated subscription or stock payments unless explicitly mapped.
275. Gate `AlertsCreator.ensurePaidMessageConfirmation` after stock price confirmation and before payment continuation.
276. Use `currentAccount` passed by the caller for every gate.
277. Add a small `tele_` exposure in stock code instead of copying private payment logic.
278. Keep OFF path byte-for-byte close to stock control flow.

## 7. Quantity, selection and mass actions

279. Quantity UI belongs in `SendGiftSheet` next to the existing gift send controls.
280. It is visible only when `GIFT_QUANTITY` and parent `GIFTS_BULK` are ON.
281. Default quantity is one.
282. Minimum quantity is one.
283. Maximum quantity is the minimum of server availability and per-user remaining.
284. If a limit is absent, do not invent an arbitrary high limit without decision.
285. `[OPEN]` Confirm a safe client-side hard cap for network and UX protection.
286. Stepper decrement at one is disabled.
287. Stepper must not accept negative, overflowed or non-numeric values.
288. Send button displays quantity and estimated total price.
289. Re-fetch or validate price before final payment form request.
290. Final confirmation includes recipient, gift, quantity, total Stars and anonymous/upgraded flags.
291. Final confirmation is separate from the local-password prompt.
292. `StarsController.buyStarGift` is called serially for each quantity item.
293. A failure stops new sends unless user explicitly chooses a safe resume action.
294. Report `Sent X of N`, the first error category and whether result is unknown.
295. Do not call the same continuation twice when `StarsNeededSheet` is dismissed.
296. After each success, refresh balance and gift list through existing notifications.
297. Respect `per_user_remains` and limited stock as the batch progresses.
298. If remaining availability shrinks, stop before over-requesting.
299. Do not run a payment loop on the UI thread.
300. The UI thread only starts the runner and receives progress.
301. Selection mode starts from long press or explicit menu action in `ProfileGiftsContainer`.
302. The long-press action must be gated by `GIFT_SELECT` and parent.
303. Store selected gift IDs, not mutable cell references.
304. Selected key must include account, dialog and collection context.
305. Collection selection is disabled unless the API supports it for that list.
306. `[INFERENCE]` Start with the all-gifts profile list; collection tabs need separate API validation.
307. Hidden gifts use alpha about 0.45 only when dim toggle is ON and must keep accessibility text.
308. Checked state and alpha are both reapplied in every `GiftCell` bind.
309. Never infer hidden state from alpha; use the server object flag.
310. Selection footer shows selected count and only actions valid for every selected item.
311. Invalid items are explained before the action, not silently dropped.
312. Show/hide uses `saveStarGift` sequentially and reports partial result.
313. Pin/unpin uses `toggleStarGiftsPinnedToTop` and respects server `pinnedGiftsLimit`.
314. Pin action must refuse or explain items over the server limit.
315. Transfer validates ownership, transfer time and recipient before starting.
316. Transfer confirmation includes recipient, count and any Stars fee.
317. Transfer uses `transferStarGift` through the existing stock gift flow.
318. Convert confirmation includes count, total Stars and explicit irreversible warning.
319. Convert uses the existing `convertStarGift` request, not a local balance mutation.
320. Sell validates owner, resale eligibility, minimum/maximum and currency.
321. Sell and unlist require separate confirmations because one creates a listing and one removes it.
322. A batch action must snapshot IDs before network work and remove completed IDs from pending state.
323. Gift update notifications must remove deleted/transferred/converted IDs from selection.
324. Rebind list cells after every gift update; recycled cells must not retain old checked state.
325. 0207 copy collection link is a read/local clipboard action, but still needs URL validation.
326. Place 0207 beside stock Share in the collection long-press/menu path.
327. Use Android clipboard and share sheet with a content URI where appropriate.
328. Do not send collection links to tele-server.

## 8. GiftBatch runner, flood wait and threading

329. Create `tele/helpers/GiftBatch.kt` with a small typed request/step interface.
330. Runner input contains account, action, immutable IDs, `skipFailed`, progress and finished callbacks.
331. Runner output contains attempted, succeeded, skipped, failed, unknown and wait seconds.
332. Runner owns one active operation per `(account, batchId)`.
333. A second start from double tap must be rejected.
334. Progress text includes current index, total and current wait.
335. During wait, disable destructive controls and show Cancel if safe.
336. Cancel stops starting new items but does not cancel an already sent request unless stock supports it.
337. Flood event must pause the runner without adding another request.
338. Use native flood wait event from batch 22 when available.
339. Do not parse only `FLOOD_WAIT_N` from Java errors because tgnet may consume and retry it.
340. `[SOURCE]` desk-3 records Android tgnet auto-resend and native consumption of ordinary flood responses.
341. `[OPEN]` Define whether batch-22 event reports initial wait, resend, or both.
342. Runner must not double-wait when tgnet already schedules resend.
343. After wait completion, resume the same pending index.
344. An error classified as sold out, privacy denied, too early, already burned or invalid skips only that item when `skipFailed` is true.
345. Unknown payment result never auto-skips into another payment.
346. Network timeout is not automatically equivalent to a failed payment.
347. Runner callbacks hop to `AndroidUtilities.runOnUIThread` before touching views.
348. Background runner state may use a per-account executor, but no global mutable account.
349. Keep a weak owner reference so a closed sheet cannot leak an Activity.
350. On owner destruction, finish with detached progress and no UI callback.
351. Persist only resumable non-payment metadata if needed; never persist payment form secrets.
352. `[INFERENCE]` Prefer in-memory runner for quantity sends until idempotency is proven.
353. Batch progress may be logged as counts, never IDs, prices or invoice payloads.
354. Logcat tag should be `TeleGiftBatch`, gated by a developer build/log switch.
355. Log events: start, item result category, flood pause, resume, cancel and finish.
356. Redact exception text if it contains invoice or account data.
357. 0224 collection retry waits three seconds, then performs one controlled reload.
358. Do not create an endless retry loop for collections.
359. Retry count and next retry must be per account and collection owner.
360. Retry on lifecycle recreation only if request state is still valid.
361. `GiftsCollections.load` should expose a small `tele_` retry hook if private.
362. Do not invalidate every account's gift cache for one account's retry.

## 9. Search, transactions, CSV and date ranges

363. Gift search is local filtering over loaded gift descriptors and server-loaded next pages.
364. Search fields must be confirmed from non-null TL objects before dereference.
365. Candidate fields are title/name, slug, model, backdrop, collection and gift ID.
366. `[INFERENCE]` Exact searchable fields must follow `TL_stars` fields present in this branch.
367. Search is case-insensitive and Unicode-safe.
368. Search chips may mirror `ResaleGiftsFragment.Filter` only where the Android class exists.
369. Search must not send a tele-server query.
370. Keep search query when RecyclerView rebinds and clear it on owner change.
371. Empty result shows the active filters and a clear action.
372. Transaction screen is `StarsIntroActivity.StarsTransactionsLayout`.
373. Add an opt-in search field and chips only when `STAR_TRANSACTIONS` is ON.
374. Filter categories include gifts and other categories only if represented by loaded transaction entries.
375. Do not label a category whose source object is absent.
376. Full-history loading must be paginated with a bounded request guard.
377. Export requested before `allLoaded` becomes a pending export state.
378. On load error, clear pending export and show retry; never export a partial file as complete.
379. CSV uses UTF-8 and a stable header.
380. Header should follow the desktop field order from `[SOURCE]` line 102.
381. Escape commas, quotes and line breaks with RFC 4180 quoting.
382. Prefix dangerous spreadsheet formulas or document the safe import behavior.
383. `[OPEN]` Decide whether formula-prefixing is required by maintainer policy.
384. Amount and nano amount remain separate columns; do not round silently.
385. Date serialization must be explicit UTC or local with a documented header contract.
386. `[INFERENCE]` Use ISO-8601 UTC for deterministic exports unless product decision says local date.
387. File name includes account-independent `transactions-yyyy-MM-dd.csv`.
388. Do not include phone number, cloud secret, local verifier or invoice token.
389. Share via Android `Intent.ACTION_SEND` and a FileProvider/content URI.
390. Keep file in app cache or export directory with cleanup after share where supported.
391. A share target receives exactly the chosen CSV, not the full tele database.
392. Date filter is a closed date range in the user-visible calendar.
393. The day end is exclusive internally to avoid 23:59:59 rounding.
394. Use the actual device timezone consistently for calendar selection.
395. `[INFERENCE]` This follows desktop `QDateTime` behavior; confirm timezone policy.
396. Media date hook belongs near `SharedMediaLayout`/`MediaDataController` range loading.
397. Gift date hook belongs near `ProfileGiftsContainer` and `GiftsList` pagination.
398. Transaction date hook belongs near the credits transaction list and local filtering.
399. Date filtering must not mutate server cache or delete out-of-range objects.
400. Reset date range returns normal pagination and removes empty-state date explanation.
401. Show range chip, from/to dates and clear action.
402. Do not let recycled rows retain hidden state when date range changes.
403. Date filter must be account and peer scoped.

## 10. Threading, privacy, lifecycle and performance checklist

404. Start every request through the caller's `currentAccount` controller.
405. Use `MessagesController.getInstance(account)` and `StarsController.getInstance(account)` only with explicit account.
406. No static `selectedGifts` shared between profiles.
407. No static unlock result shared between accounts.
408. No Activity reference kept by runner after destruction.
409. Use `AndroidUtilities.runOnUIThread` for dialog, toast, adapter and cell changes.
410. Use storage queue only for tele persistence; never block UI on verifier or CSV generation.
411. CSV assembly can run off main thread, then return a URI on main.
412. Biometric prompt must be attached to a live FragmentActivity.
413. Re-check account and dialog before a delayed continuation starts network work.
414. Re-check gift ID existence before each bulk operation.
415. A gift list update can invalidate selection while a batch is waiting.
416. Use immutable ID snapshot plus current server object lookup on resume.
417. `GiftCell` bind sets alpha, checked, enabled, accessibility and action badge every time.
418. LiteMode disables or shortens optional quantity/selection animations.
419. Avoid a custom animation that runs when LiteMode says reduce motion.
420. Large gift lists must not duplicate all TL objects for every filter.
421. Prefer IDs and filtered index lists over deep copies.
422. Search debounce is optional; if added, cancel stale query callbacks.
423. Do not do regex or CSV work on the main thread for the full history.
424. Date filter should page server data instead of unboundedly loading all gifts where API supports dates.
425. If API lacks date bounds, bound local memory and state the limitation.
426. Payment confirmation screens must remain readable with large font and accessibility services.
427. Do not hide hidden gifts from accessibility when merely dimming them.
428. Clipboard/share of collection link is user-triggered and must not run on bind.
429. No collection URL should contain local account secrets.
430. Privacy text must explain that CSV may expose peer and transaction metadata to the chosen share target.
431. Network offline switches must be checked at the lowest new request layer.
432. Stock Telegram Stars requests continue to behave stock when this batch is OFF.
433. No tele-server network is introduced by this batch.
434. No notification channel is introduced by this batch.
435. No stock DB schema migration is introduced by this batch.

## 11. Решения и открытые вопросы

436. Решение мейнтейнера: собственный локальный пароль плюс биометрия.
437. Решение мейнтейнера: reset через cloud password.
438. Решение мейнтейнера: пароль гейтит gifts, stars, bot payments and paid messages.
439. Решение по умолчанию: CSV через Android share sheet.
440. Решение по умолчанию: date filter применим ко всем длинным спискам.
441. Решение мейнтейнера: mass gift actions и общий runner.
442. `[OPEN]` Подтвердить точный Android cloud-password API на ветке `tele`.
443. `[OPEN]` Подтвердить hard cap quantity, если сервер не сообщает остаток.
444. `[OPEN]` Подтвердить стратегию `result unknown` после timeout платежа.
445. `[OPEN]` Подтвердить timezone CSV и календарного диапазона.
446. `[OPEN]` Подтвердить formula-injection policy для CSV.
447. `[OPEN]` Подтвердить event contract между 0205/0212 и GiftBatch 0213.
448. `[OPEN]` Подтвердить, какие actions разрешены в collection tabs.
449. `[OPEN]` Подтвердить, нужно ли защищать sell/unlist одним или двумя toggles.
450. `[OPEN]` Подтвердить, считать ли quantity «Send gifts» отдельным action от «Buy gifts».
451. До решений не подменять неизвестное поведение молчаливым fallback.
452. Любое изменённое решение сначала отражается в PATCHLIST и этом guide.

## 12. Pitfalls и защитные проверки

453. Не ставить password gate только в кнопке: payment form может быть вызван из другого пути.
454. Не ставить gate после `sendStarsForm`: деньги уже могли уйти.
455. Не вызывать continuation и из biometric callback, и из password fallback.
456. Не хранить verifier в обычном экспортируемом JSON.
457. Не считать отменённый `StarsNeededSheet` успешной покупкой.
458. Не повторять payment form после неопределённого результата без истории.
459. Не запускать selected bulk action по старым `ViewHolder` ссылкам.
460. Не использовать alpha как единственный признак hidden.
461. Не применять pin limit локально без ответа server config.
462. Не оставлять selected IDs после transfer/delete/update.
463. Не загружать транзакции бесконечно из-за pagination cursor без прогресса.
464. Не экспортировать CSV до `allLoaded`.
465. Не помещать newline в CSV без правильного quoting.
466. Не смешивать local date и UTC при сравнении границ.
467. Не показывать collection retry бесконечно после offline.
468. Не обновлять RecyclerView с storage thread.
469. Не обращаться к account 0 из helper convenience method.
470. Не игнорировать LiteMode ради красивой gift animation.
471. Не включать новую сетевую фичу дефолтно для «удобства».
472. Не менять PATCHLIST на `done` только по logcat compile.
473. Не проверять реальные деньги на maintainer account.

## 13. On/off, logcat и ручные тесты

474. Перед тестом создать резервную заметку о тестовом аккаунте и остатке Stars.
475. Установить debug APK на отдельное устройство или профиль.
476. Проверить два аккаунта и переключение между ними.
477. Включить только parent, проверить видимость дочерних rows.
478. Убедиться, что все новые toggles OFF после чистой установки.
479. OFF: открыть stock gift sheet; UI и запросы должны быть stock.
480. OFF: открыть profile gifts; нет dim, selection, search chips или bulk footer.
481. OFF: открыть Stars transactions; нет tele search или export entry.
482. OFF: открыть media; нет date chip.
483. OFF: вызвать stock paid message confirmation; нет дополнительного gate.
484. OFF: снять logcat и убедиться в отсутствии `TeleGiftPassword`/`TeleGiftBatch` start.
485. ON parent: задать локальный пароль на тестовом аккаунте.
486. ON buy: quantity one запрашивает пароль/биометрию до payment form.
487. ON buy: неверный пароль не вызывает `getPaymentForm`.
488. ON buy: отмена биометрии возвращает в sheet без запроса.
489. ON buy: повторная биометрия на живом Activity вызывает один continuation.
490. ON buy: quantity two показывает одну password prompt и отдельное итоговое подтверждение.
491. ON buy: проверка остатка ограничивает stepper.
492. ON buy: успешный тест отправляет только минимальное количество тестовых Stars.
493. ON buy: искусственно плохой второй элемент даёт `Sent 1 of 2` и не повторяет первый.
494. ON transfer: проверить получателя и fee на тестовом аккаунте, затем один тестовый gift.
495. ON convert: увидеть irreversible warning; выполнить только на disposable test gift.
496. ON sell: проверить price/currency and separate confirmation; не использовать maintainer account.
497. ON paid messages: password gate стоит до continuation после `ensurePaidMessageConfirmation`.
498. ON bot payment: тестировать только тестовый bot/invoice с нулевой или минимальной ценой.
499. ON selection: long press enters mode and selected cells remain checked after scroll.
500. ON selection: recycled cell cannot inherit checked or dim state from another gift.
501. ON selection: hide/show reports partial result when one element is invalid.
502. ON selection: pin refuses over server limit with visible reason.
503. ON selection: transfer/convert/sell show count, destination/price and final confirmation.
504. ON search: query matches case-insensitively and clear restores list.
505. ON search: collection tabs do not expose unsupported action.
506. ON transactions: load pages until all loaded, then export through share sheet.
507. ON transactions: cancel share leaves no payment or mutation request.
508. ON CSV: verify UTF-8, header, quoting, date, amount/nano and no secrets.
509. ON date: choose one day; boundary timestamps are included exactly once.
510. ON date: choose range; media, gifts and transactions each show matching empty state.
511. ON date: clear range restores normal pagination.
512. ON collection link: long press/share copies only validated t.me URL.
513. ON collection retry: one failure retries after three seconds, then stops.
514. ON flood: use a safe test endpoint or controlled test-server account, never paid maintainer action.
515. ON flood: runner displays wait, sends no duplicate request, then resumes pending index.
516. ON flood: inspect `TeleGiftBatch` start/pause/resume/finish counts in logcat.
517. ON unknown payment result: runner pauses and requires manual history check.
518. Switch account during wait; old account must not resume work on new account.
519. Rotate Activity during search and selection; state must not address a dead view.
520. Enable LiteMode; no unbounded gift animation and cells remain usable.
521. Repeat critical ON scenarios after process restart.
522. Repeat all scenarios with parent OFF after ON to verify clean gate-off.
523. Suggested logcat filter: `TeleGiftPassword|TeleGiftBatch|TeleGiftCsv|StarsController`.
524. Logs must show account index only if local debug policy permits; never show account IDs.
525. Logs must redact URLs containing tokens, invoice fields and password errors.
526. Record build variant, device ABI, Android version and toggle state with test result.

## 14. features.md, export and batch gate

527. Add one English `features.md` row for local gift password, desktop 0187, default OFF.
528. Add one row for paid message and bot payment password, desktop 0217, default OFF.
529. Add one row for sending several gifts, desktop 0184, default OFF.
530. Add one row for dim hidden gifts and selecting several, desktop 0185, default OFF.
531. Add one row for gift search, desktop 0186, default OFF.
532. Add one row for bulk gift actions, desktop 0190, default OFF.
533. Add one row for star transaction search/export, desktop 0192, default OFF.
534. Add one row for date filters, desktop 0193, default OFF.
535. Add one row for collection links, desktop 0207, default OFF.
536. Add one row for collection retry, desktop 0224, default OFF.
537. Add one row for gift batch flood handling, desktop 0213, default OFF or implementation parent policy.
538. Each row must name the actual tele settings section and exported patch filename.
539. Feature rows are English and user-facing; implementation details remain here.
540. Update rows in the same commit as the exported patch, never later.
541. Update PATCHLIST statuses only after actual patch export.
542. Do not hand-edit an Android `.patch` file.
543. Before gate, check every affected callsite and every features row.
544. Assemble with `./gradlew :TMessagesProj_App:assembleDebug` in `Telegram`.
545. Native flood integration, if present, must build every ABI split.
546. Install the ABI matching the test device and keep the test APK identifiable.
547. Gate requires manual ON, OFF and default-state checks.
548. Gate requires password, biometric and cloud-reset checks on test account.
549. Gate requires quantity and one selected bulk action with real but minimal test Stars.
550. Gate requires transfer/convert/sell/payment safety checks only on test accounts.
551. Gate requires CSV share, date ranges, collection link and collection retry.
552. Gate requires controlled flood wait and no duplicate payment.
553. Gate requires two-account isolation, rotation and Recycler recycling checks.
554. Gate requires LiteMode and privacy/log redaction checks.
555. Gate requires no tele-server request for this batch.
556. Gate requires no stock DB schema change and no `TLRPC.java` change.
557. Gate requires logcat evidence with secrets and peer metadata redacted.
558. A successful build alone leaves every PATCHLIST row `todo` or `built`, not `done`.
559. Human verification is the only transition to `done`.
560. Never perform destructive or payment tests on the maintainer account.
561. Never claim this batch complete while any `[OPEN]` payment or flood contract blocks safe behavior.
