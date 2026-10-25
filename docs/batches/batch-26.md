# Пачка 26: деньги — движок и ключи

## 1. Назначение и границы

1. Этот файл — план реализации пачки 26 из `docs/PATCHLIST.md`.
2. Пачка включает ровно шесть строк: 0278, 0308, 0309, 0285, 0307 и 0310.
3. Порядок строк в PATCHLIST не является безопасным порядком разработки.
4. Безопасный порядок зафиксирован ниже и является REQUIRED для очереди.
5. Решение мейнтейнера: портировать всю подсистему money.
6. В подсистему входят приватные ключи, несмотря на повышенный риск.
7. Решение мейнтейнера: Android-дифф накладывается на Android-ревизию движка.
8. Нельзя подменять Android-ревизию десктопным gitlink без сверки API.
9. Решение мейнтейнера: Rust пересобирается, а не принимается готовым бинарником вслепую.
10. Решение мейнтейнера: 0285 портируется и проверяется тестовым кошельком.
11. Решение мейнтейнера: страница настроек называется `MODE_MONEY`.
12. Все пользовательские настройки пачки должны быть выключены по умолчанию.
13. При выключенной настройке поведение должно совпадать со стоком Android.
14. 0308 — инфраструктура, а не пользовательский переключатель.
15. 0307 — проверка/исправление формата BoC, а не новый UI-переключатель.
16. Ворота пачки требуют сборку Rust на всех ABI.
17. Ворота требуют импорт приватным ключом на тестовом кошельке.
18. Ворота требуют смену фразы без backup на тестовом кошельке.
19. Ворота требуют проверку квоты комиссии смены ключа.
20. Ворота требуют копирование слов и очистку буфера через 60 секунд.
21. Нельзя считать пачку готовой только по успешной компиляции.
22. Нельзя считать тестовым кошельком аккаунт с существенным балансом.
23. Нельзя вставлять реальные секреты в исходники, логи, задачи или отчёты.
24. Строки с `[INFERENCE]` ниже обозначают проектное предложение, а не факт.
25. Неподтверждённые серверные свойства должны остаться открытым вопросом.

## 2. Что было проверено

26. Правила Android-форка находятся в `main/AGENTS.md`.
27. Архитектура очереди описана в `main/docs/architecture.md`.
28. Рабочий цикл сборки описан в `main/docs/development.md`.
29. Переносимость и Android-точки описаны в `main/docs/portability.md`.
30. Решения мейнтейнера находятся в `main/docs/decisions.md`.
31. Карта старых и текущих номеров находится в `main/docs/desktop-numbers.md`.
32. Оценка новых desktop-патчей находится в `local://desk-5.md`.
33. Текущий PATCHLIST помещает шесть строк в пачку 26.
34. Desktop-очередь прочитана через `git show origin/main:<patch>`.
35. Android checkout находится в `Telegram/`, ветка называется `tele`.
36. На момент осмотра Android HEAD: `efc8ce40b7f7a2833f2e49305c1a36cfa859f2e2`.
37. Gitlink Android wallet-engine в HEAD: `5c65e47cb8d68727c20d89382d0bc51292486b9a`.
38. Этот gitlink — ревизия `dkaraush/wallet-engine`, не desktop-релиз.
39. Последний видимый commit движка содержит key-rotation preparation.
40. Последний видимый commit движка содержит key-rotation preview.
41. Последний видимый commit движка содержит caller-supplied recipient key.
42. В видимой ревизии нет подтверждения поддержки desktop private-key API.
43. Поэтому 0308 требует re-port, даже если текущий wallet уже собирается.
44. Рабочее дерево submodule имеет локальные удаления и изменения.
45. Эти изменения не следует смешивать с новым патчем пачки.
46. Перед работой сохранить состояние submodule и проверить чистый checkout.
47. Текущий `.gitmodules` указывает `https://github.com/dkaraush/wallet-engine.git`.
48. Текущий `gram-wallet/Cargo.toml` использует path dependency `../wallet-engine`.
49. Текущий `gram-wallet/Cargo.toml` также использует `ton-connect-core` из движка.
50. Текущий `gram-wallet/Cargo.toml` использует `ton` из движка.
51. Текущий Rust toolchain зафиксирован как `1.96.1`.
52. Текущий Cargo release profile использует `codegen-units = 1`.
53. Текущий Cargo release profile использует `opt-level = "z"`.
54. Текущий Cargo release profile использует `panic = "abort"`.
55. Текущий `build_wallet_engine.sh` требует `cargo` и `rustup`.
56. Скрипт не вызывает `cargo-ndk` напрямую.
57. Скрипт сам выбирает target и NDK linker для каждой ABI.
58. Это различие важно: cargo-ndk нельзя молча считать уже подключённым.
59. Текущий CMake импортирует `libwallet_engine.a` для `${ANDROID_ABI}`.
60. Текущий CMake собирает сгенерированные C++20 bindings.
61. Текущий CMake собирает JNI bridge как object library.
62. Текущий JNI bridge входит в `tmessages.49`.
63. В prebuild уже наблюдаются архивы для `arm64-v8a`.
64. В prebuild уже наблюдаются архивы для `armeabi-v7a`.
65. В prebuild уже наблюдаются архивы для `x86_64`.
66. В prebuild уже наблюдаются архивы для `x86`.
67. Наличие текущего архива не доказывает наличие private-key функций.
68. На проверяемой машине команда `git lfs version` не найдена.
69. В проверенном `.gitattributes` Android-репозитория LFS-фильтр не обнаружен.
70. [INFERENCE] CI или будущий storage может потребовать git-lfs для больших артефактов.
71. Поэтому наличие LFS надо проверять до clone/pull, а не после неуспешной сборки.

## 3. Desktop-источники и точная семантика

72. Desktop 0278 меняет `main/main_app_config.cpp`.
73. Desktop 0278 вызывает `Tele::ForceWallet()` в `AppConfig::walletAvailable()`.
74. Desktop 0278 помечает настройку restart-required.
75. Desktop 0278 добавляет toggle в debug/experimental section.
76. Desktop 0278 добавляет money, ton, crypto и gram search keywords.
77. Android-аналогом является `AppGlobalConfig.ConfigBoolean.get()`.
78. Android-изменение должно быть одним тонким override для `walletAvailable`.
79. [INFERENCE] Имя Android item: `FORCE_WALLET`.
80. [INFERENCE] Ключ Android item: `force_wallet`.
81. Desktop 0308 меняет Docker-подготовку Rust wallet-engine.
82. Desktop 0308 сначала фиксирует upstream `i582/wallet-engine` revision.
83. Desktop 0308 затем fetch-ит `gettele/money` branch `tele/<revision>/5`.
84. Desktop 0308 применяет `patches/wallet-engine.patch`.
85. Desktop 0308 меняет cache version суффиксом `.tele5`.
86. Android не имеет права предполагать существование такой ветки на 5c65e47.
87. Android должен перенести изменения по смыслу и API.
88. Desktop 0309 добавляет `tele_wallet_keys.cpp` и `.h`.
89. Desktop 0309 добавляет новый исходник в `Telegram/CMakeLists.txt`.
90. Desktop 0309 добавляет toggle private keys и экспорт settings spec.
91. Desktop 0309 расширяет wallet content, engine и session.
92. Desktop 0309 использует marker `tele/private-key-wallets`.
93. Marker хранит адрес, public anchor и признак предложения ротации.
94. Marker не хранит приватный ключ.
95. Desktop 0309 распознаёт private-key input через engine.
96. Desktop 0309 вычисляет адрес из private key на mainnet.
97. Desktop 0309 принимает private key отдельно.
98. Desktop 0309 принимает address плюс 12 recovery words.
99. Desktop 0309 проверяет слова до сетевого восстановления.
100. Desktop 0309 использует отдельный recovery client.
101. Desktop 0309 отменяет незавершённый recovery при закрытии UI.
102. Desktop 0309 запрещает backup для private-key wallet.
103. Desktop 0309 предлагает заменить длинный ключ на 12 слов.
104. Desktop 0309 показывает предупреждение о прекращении действия старого ключа.
105. Desktop 0309 сохраняет только публичный marker состояния.
106. Desktop 0309 очищает clipboard через 60 секунд, если содержимое не изменилось.
107. Desktop 0310 добавляет copy words в recovery phrase UI.
108. Desktop 0310 снимает desktop wait semantics для copy action.
109. Android уже не имеет подтверждённого десятисекундного таймера в этом экране.
110. Поэтому Android-порт 0310 — прежде всего явная кнопка копирования.
111. Desktop 0285 добавляет toggle `WalletRotate`.
112. Desktop 0285 показывает кнопку только при disabled backup.
113. Desktop 0285 переиспользует rotation quote и confirmation flow.
114. Desktop 0285 очищает rotation guard после подтверждения нового ключа сервером.
115. Desktop 0285 отдельно логирует quote, submit и завершение rotation.
116. Desktop 0285 не вызывает обычный `disableBackup` для нового режима.
117. Desktop 0307 разрешает BoC cell с одной или двумя references.
118. Desktop 0307 меняет `gram/gram_boc.cpp`.
119. Android не должен переносить этот C++ parser механически.
120. Android должен проверить Rust `wallet-engine` BoC path.
121. Desktop patch headers и hunks — источник намерения, не код для копирования.

## 4. Целевая очередь и зависимости

122. Первым идёт 0278: `feat: force wallet`.
123. Усилие 0278: S.
124. Зависимость 0278: существующий Android money stack.
125. 0278 блокирует UI и импорт следующих патчей.
126. Вторым идёт 0308: `misc: build wallet engine`.
127. Усилие 0308: L.
128. Зависимость 0308: 0278 не техническая, но money API должен быть зафиксирован.
129. 0308 блокирует 0309, 0285 и 0307.
130. Третьим идёт 0309: `feat: import private wallets`.
131. Усилие 0309: L.
132. Зависимости 0309: 0278, 0308 и существующий money stack.
133. Четвёртым идёт 0285: `feat: rotate wallet phrase`.
134. Усилие 0285: M.
135. Зависимости 0285: 0278, 0308 и 0309 private-secret model.
136. Пятым идёт 0307: `fix: quote key change fee`.
137. Усилие 0307: S.
138. Зависимости 0307: 0285 и 0308.
139. Шестым идёт 0310: `feat: copy wallet words`.
140. Усилие 0310: S.
141. Зависимость 0310: money UI; 0308 не обязателен для простой кнопки.
142. Для одной линейной очереди 0310 всё равно экспортировать после 0307.
143. Нельзя коммитить 0309 до доступного ABI/API private-key signing.
144. Нельзя коммитить 0285 до доказанной fee quote.
145. Нельзя коммитить 0307 до фикстуры BoC с двумя references.
146. Нельзя объявлять batch `built` до всех шести экспортированных patch files.
147. Коммиты должны быть в Telegram checkout на ветке `tele`.
148. Коммиты здесь должны появиться только после export.
149. `.patch` файлы нельзя редактировать вручную.
150. Каждый user-facing commit одновременно обновляет `features.md`.
151. [INFERENCE] Текущая очередь имеет 0096 Android patches; новые патчи добавятся в конец.
152. [INFERENCE] Номера экспортированных Android patch files будут определены только export-ом.
153. В документации указывать desktop number отдельно от Android patch filename.

## 5. Настройки и MODE_MONEY

154. Добавить `MODE_MONEY = "money"` в `TeleSettingsActivity`.
155. `sectionTitle()` для MODE_MONEY должен возвращать `tele · money`.
156. Добавить money section link в root sections.
157. Иконку выбирать из уже используемых stock/tele ресурсов.
158. Не редактировать stock `strings.xml`.
159. Новые названия и описания помещать в `strings_tele.xml`.
160. Все ключи новых строк должны иметь префикс `Tele`.
161. Добавить `FORCE_WALLET` с default `false`.
162. `FORCE_WALLET` требует restart после изменения.
163. Добавить `PRIVATE_KEY_WALLETS` с default `false`.
164. Добавить `ROTATE_WALLET_PHRASE` с default `false`.
165. Добавить `COPY_WALLET_WORDS` с default `false`.
166. 0308 и 0307 не требуют пользовательского toggle.
167. Если security review потребует master gate, он тоже default off.
168. Не прятать дочерние rows за несуществующим toggle.
169. Private-key import row может быть виден в MODE_MONEY, но off делает его недоступным.
170. Rotation row должна быть видна только для подходящего wallet state.
171. Copy row должна быть видна только на экране показа secret phrase.
172. Toggle обработка должна идти через `TeleConfig.set`.
173. После изменения вызвать `TeleHooks.onConfigChanged` только если нужен runtime refresh.
174. FORCE_WALLET должен показывать restart hint, а не менять state на лету.
175. В Java-коде обращаться к item через `.value` согласно текущему TeleConfig API.
176. В новом Java-коде не вводить `.getValue()` без адаптера.
177. В settings export/import добавить все четыре boolean items.
178. Не включать секрет, private key или mnemonic в export/import.
179. Экспорт должен содержать только настройки и не секретное состояние.
180. Состояние private wallet хранить только в wallet storage/tele marker.
181. [INFERENCE] Marker public metadata лучше хранить в `tele_kv`.
182. [INFERENCE] Формат marker должен быть версионированным JSON.
183. Схему stock database менять запрещено.
184. Если marker требует таблицу, имя должно начинаться с `tele_`.
185. Не трогать `TLRPC.java`.
186. Не делать второй глобальный singleton для account state.
187. Каждый wallet lookup должен использовать `currentAccount`.
188. Данные UI обновлять на main thread.

## 6. Поиск настроек и IDs

189. Текущий `TeleSearch.kt` лежит в `tele/ui/settings/TeleSearch.kt`.
190. Текущие GUID находятся в диапазоне примерно 950–1109.
191. Для money зарезервировать диапазон 1400–1419.
192. GUID 1400 — root/section `tele money`.
193. GUID 1401 — `force wallet`.
194. GUID 1402 — `import wallets from private keys`.
195. GUID 1403 — `update wallet phrase without backup`.
196. GUID 1404 — `copy wallet words`.
197. GUID 1405–1419 оставить свободными, пока нет новых rows.
198. [INFERENCE] Если в реализации появятся дополнительные money toggles, выдавать им 1405+.
199. Не переиспользовать старые GUID для money.
200. Каждый search entry должен открывать `MODE_MONEY`.
201. Search keywords должны включать `money`, `wallet`, `ton`.
202. Для private key добавить `private key`, `hex`, `secret`.
203. Для rotation добавить `recovery phrase`, `key rotation`, `words`.
204. Для copy добавить `copy`, `secret words`, `recovery phrase`.
205. Search title и row title должны совпадать по смыслу.
206. Не показывать private key в search result или analytics.
207. Проверить отсутствие коллизий через полный список `TeleSearch`.
208. Проверить поиск на английском интерфейсе.
209. Локали могут менять строки, но search keywords должны остаться полезными.
210. Search callback должен создавать fragment на main thread.

## 7. 0278: включить wallet раньше сервера

211. Desktop anchor: `AppConfig::walletAvailable()`.
212. Android anchor: `AppGlobalConfig.ConfigBoolean.get()`.
213. Добавить минимальный `tele_` branch только для key `wallet_available`.
214. При FORCE_WALLET off вернуть исходное значение без изменений.
215. При FORCE_WALLET on вернуть true только для wallet key.
216. Не подменять другие config booleans.
217. Не менять `MessagesController.config` напрямую из settings UI.
218. Restart required нужен из-за конфиг-кеша.
219. Проверить, что debug default true не маскирует ошибку.
220. Проверить production-like false server response.
221. Проверить запуск с walletAvailable=false и toggle off.
222. Проверить запуск с walletAvailable=false и toggle on.
223. Проверить cold start после изменения toggle.
224. Не считать серверный отказ обходом авторизации.
225. FORCE_WALLET не должен создавать wallet state сам.
226. FORCE_WALLET не должен отправлять сетевой запрос.
227. FORCE_WALLET не должен включать private-key import.
228. Он только разрешает существующему Android money UI пройти config gate.
229. Логировать только состояние флага, без account id и wallet address.
230. Если стоковый getter приватный, сделать только нужный API public.
231. Новые поля/методы stock-класса именовать с префиксом `tele_`.
232. Сохранить off-path как byte-for-byte минимальный stock hunk.
233. Commit 0278 экспортировать до native work.

## 8. 0308: перенос diff wallet-engine

234. Зафиксировать исходный Android gitlink `5c65e47...` в рабочей заметке.
235. Не переписывать существующий submodule pointer до review diff.
236. Получить desktop patch через `git show origin/main:patches/tdesktop/0308-*`.
237. Отдельно выписать изменения Docker и `build/prepare/prepare.py`.
238. Android не использует desktop Docker prepare pipeline.
239. Android source of truth — `jni/wallet-engine` и `jni/gram-wallet`.
240. Сверить desktop wallet-engine.patch с Android wallet-engine.patch.
241. Перенести только функции, необходимые Android wallet bridge.
242. Не переносить Windows/Mac build assumptions.
243. Не копировать desktop C++ wallet classes в Android.
244. Сначала добавить Rust API и Rust tests в engine revision.
245. Затем обновить UniFFI-generated surface.
246. Затем обновить `gram-wallet` adapter.
247. Затем обновить Android JNI bridge.
248. Затем обновить Java model и UI.
249. Сгенерированные headers не редактировать вручную.
250. Генерировать `wallet_engine.hpp` и `.cpp` из matching host library.
251. Генерировать `gram_wallet.hpp` и `.cpp` тем же bindgen invocation.
252. Проверить, что C++ bindings соответствуют именно собранной Rust library.
253. [INFERENCE] Private-key API может потребовать `detect_private_key`.
254. [INFERENCE] Private-key API может потребовать `private_key_public_key`.
255. [INFERENCE] Private-key API может потребовать `private_key_address`.
256. [INFERENCE] Эти названия наблюдались в desktop 0309, но не подтверждены Android API.
257. Не объявлять API доступным, пока `git grep` и bindgen не подтверждают его.
258. Для rotated words сохранить разницу anchor key/signing key.
259. Для private key не превращать raw key в обычный mnemonic без доказательства.
260. Rust ошибки не должны включать secret bytes.
261. Rust debug output должен быть отключён для release archive.
262. Проверить `zeroize` на всех новых secret buffers.
263. Проверить отсутствие `println!` с phrase/key/address.
264. Проверить C ABI/UniFFI exception conversion на invalid key.
265. Проверить invalid length до network call.
266. Проверить wrong format до protected-secret access.
267. Проверить address derivation deterministic test vectors.
268. Проверить key signing deterministic test vectors, если API допускает.
269. Проверить mainnet/testnet parameter явно в каждом test.
270. Не вводить network fallback при ошибке derivation.

## 9. Rust/NDK workflow

271. Установить Rust toolchain `1.96.1` через rustup.
272. Установить targets `aarch64-linux-android`.
273. Установить target `armv7-linux-androideabi`.
274. Установить target `x86_64-linux-android`.
275. Установить target `i686-linux-android`.
276. Установить NDK `27.2.12479018`.
277. Установить CMake `3.22.1`.
278. Убедиться, что Android SDK path корректен.
279. Проверить `ANDROID_NDK_HOME` перед запуском скрипта.
280. Проверить `cargo --version` и `rustup target list --installed`.
281. Проверить `git submodule update --init TMessagesProj/jni/wallet-engine`.
282. Если источник/архив помечен LFS, установить git-lfs до checkout.
283. Выполнить `git lfs install` один раз на машине.
284. Выполнить `git lfs pull` только в репозитории, где LFS реально настроен.
285. [INFERENCE] Не добавлять LFS-файлы в очередь без решения о размере APK/репозитория.
286. Текущий `build_wallet_engine.sh` требует cargo/rustup, не cargo-ndk.
287. cargo-ndk MAY использоваться как диагностический эквивалент.
288. Если включать cargo-ndk, не дублировать ручной linker setup.
289. Для arm64 target cargo-ndk ABI соответствует `arm64-v8a`.
290. Для armv7 target cargo-ndk ABI соответствует `armeabi-v7a`.
291. Для x86_64 target cargo-ndk ABI соответствует `x86_64`.
292. Для i686 target cargo-ndk ABI соответствует `x86`.
293. Предпочтительный текущий путь — `build_wallet_engine.sh`.
294. Скрипт импортирует `prebuild/common.sh`.
295. `common.sh` задаёт API 21 по умолчанию.
296. `common.sh` задаёт все четыре ABIs по умолчанию.
297. `common.sh` выбирает Darwin/Linux NDK host tag.
298. `common.sh` задаёт reproducible path flags.
299. `common.sh` задаёт `SOURCE_DATE_EPOCH` по умолчанию 1.
300. Скрипт проверяет наличие `wallet-engine/Cargo.toml`.
301. Скрипт использует `jni/gram-wallet` как adapter directory.
302. Скрипт создаёт временный wallet-engine build directory.
303. Скрипт задаёт `CARGO_BUILD_JOBS` и отключает incremental.
304. Скрипт сначала собирает host cdylib для metadata.
305. Скрипт запускает Rust C++ bindgen с `--locked`.
306. Скрипт копирует шесть generated files в prebuild include.
307. Скрипт строит staticlib отдельно для каждого ABI.
308. Скрипт передаёт Android clang linker явно.
309. Скрипт сохраняет output как `libwallet_engine.a`.
310. Скрипт переименовывает `rust_eh_personality` через llvm-objcopy.
311. Скрипт запускается из `build_all.sh` после `build_tlottie.sh`.
312. `build_all.sh` перед запуском удаляет prebuild lib/include/pkgconfig.
313. Поэтому backup старых архивов делать вне tracked output directories.
314. После build проверить шесть generated headers/CPP files.
315. После build проверить четыре `lib/<abi>/libwallet_engine.a`.
316. Проверить archive symbols через `nm`/`llvm-nm` на каждой ABI.
317. Не утверждать private API наличие по одному arm64 archive.
318. CMake path: `TMessagesProj/jni/CMakeLists.txt`.
319. CMake target `wallet_engine` — imported static library.
320. CMake target `wallet_engine_cpp` — generated C++ wrapper library.
321. CMake target `wallet_engine_jni` — JNI object library.
322. JNI sources: `wallet/WalletEngineBridge.cpp` и `wallet/GramWalletAdapter.cpp`.
323. CMake требует C++20 для wallet wrapper и bridge.
324. JNI object library linked into `tmessages.49`.
325. Android Gradle native build uses `jni/CMakeLists.txt`.
326. Gradle pins NDK 27.2.12479018 and CMake 3.22.1.
327. `./gradlew :TMessagesProj_App:assembleDebug` remains batch build command.
328. Full native build may take tens of minutes.
329. Do not use `git clean` until prebuild artifacts are backed up or reproducible.
330. Record Rust, NDK, CMake, bindgen and submodule revisions in evidence.

## 10. 0309: private-key import

331. Existing entry point is `WalletImportFragment`.
332. Existing UI has 12-word and 24-word tabs.
333. Existing UI creates `GramWallet.SecretPhrase` from words.
334. Existing `GramWalletStorage` stores encrypted wallet material in noBackup files.
335. Existing storage serializes writes on a single worker.
336. Existing storage callbacks return to main thread.
337. Existing `WalletEngine2` exposes phrase derivation JNI methods.
338. Existing JNI accepts `jbyteArray`, not Java `String`, for phrase bytes.
339. Keep private key bytes as byte arrays or sensitive wrapper objects.
340. Never use Android `String` for raw private key lifetime longer than required.
341. Add a private-key section only when `PRIVATE_KEY_WALLETS.value` is true.
342. Import UI should support raw key input format approved by engine.
343. Do not infer whether hex means seed, Ed25519 secret, or another format.
344. Record the exact accepted format in a maintainer decision.
345. If address-plus-12-words recovery is ported, validate both fields locally.
346. Derive/display address before submit where possible.
347. Display address in a copyable, non-secret field.
348. Reject invalid address before network request.
349. Reject invalid key length before protected storage access.
350. Reject unsupported prefix/encoding before import request.
351. Use `WalletEngine2` native method for derivation/signing.
352. Add a Java result object that owns no long-lived secret after callback.
353. Clear input field when import succeeds or fragment is destroyed.
354. Clear intermediate `byte[]` in `finally` blocks.
355. Do not put key in Intent extras, saved instance state, clipboard logs or URI.
356. Disable Android autofill for raw private-key input.
357. Disable screenshots for the input screen unless an explicit security decision says otherwise.
358. Do not call `FileLog` with exception text that may contain input.
359. Return generic UI errors such as invalid key or derivation failed.
360. Store only wallet address, public anchor and secret-kind marker.
361. Store encrypted key material only through the existing wallet storage abstraction.
362. [INFERENCE] Add `SecretKind.PRIVATE_KEY` beside existing mnemonic kind.
363. [INFERENCE] The encrypted file format needs a version byte and kind discriminator.
364. [INFERENCE] A migration must reject unknown kind instead of treating it as mnemonic.
365. Never silently convert a private key into Telegram backup words.
366. `GramWalletStorage.init` must not upload or back up private key material.
367. `GramWallet.enableBackup` must reject private-key wallets.
368. Logout/wipe must delete private-key records like other local wallet records.
369. Private-key marker must not be sufficient to reconstruct a key.
370. Marker updates must be atomic and account-scoped.
371. Use `GramWallet.getInstance(currentAccount)` for every operation.
372. Do not use account 0 from a static helper.
373. Native handle lifetime must follow fragment/account lifetime.
374. Cancel pending import when fragment closes.
375. Cancel pending network recovery when activity is destroyed.
376. Keep derivation off the UI thread.
377. Hop to `AndroidUtilities.runOnUIThread` before any view update.
378. Keep JNI calls serialized if the Rust client is not thread-safe.
379. Avoid concurrent import and rotation for one account.
380. Add a per-account busy guard before starting import.
381. Add a timeout with generic error and secret cleanup.
382. Do not retry an import automatically after ambiguous server result.
383. Require explicit user action to retry.
384. If import proof uses MTProto, preserve existing `ConnectionsManager` account.
385. If recovery uses Toncenter, enforce existing network/privacy policy.
386. The current JNI config visibly uses `https://toncenter.com`.
387. [INFERENCE] Do not add a second provider until provider policy is decided.
388. Verify that domain/certificate policy is acceptable before shipping.
389. Never send private key to Tele server or third-party telemetry.
390. Never include private key in crash reports.

## 11. 0285: phrase rotation without backup

391. Existing Android hooks are in `GramWallet.PendingDisableBackup`.
392. Existing `GramWallet` has `prepareDisableBackup` and `disableBackup` paths.
393. Existing `WalletKeysBackupFragment.fillItems` builds backup actions.
394. Existing `WalletSecretPhraseFragment` displays phrase content.
395. Existing `WalletTestPhraseFragment` quizzes phrase words.
396. Reuse UI and authorization lifecycle, not the semantic disable-backup request.
397. Add a separate rotation action under `MODE_MONEY` gate.
398. Show it only when `wallet.isBackupEnabled()` is false.
399. Require wallet passcode/biometric authorization before quote.
400. Request fresh fee quote before revealing new words.
401. Show fee in TON and exact expiration/validity if API exposes it.
402. Do not display a stale quote after account state changes.
403. Prepare replacement key through Rust `prepare_key_rotation` equivalent.
404. Hold the new phrase only in a sensitive object.
405. Show words in existing phrase screen and quiz.
406. Explain that old words stop working after confirmed rotation.
407. Explain that the network charges a fee.
408. Require explicit confirmation after quote.
409. On cancel, discard prepared secret and pending operation.
410. On success, atomically replace local secret/key metadata.
411. Refresh `TL_wallet.WalletState` on the main thread callback.
412. Rebuild `WalletEngine2` with the server public key after state update.
413. Do not assume server accepts the key without proof.
414. Do not clear old key until server confirmation is durable.
415. Do not claim success from a local prepared BoC.
416. Add log events with operation id only if operation id is non-secret.
417. Never log phrase, raw key, full address or signature.
418. Log quote phase, send phase and terminal error category only.
419. Preserve the existing `PendingDisableBackup` path unchanged for stock.
420. New path must be gated by `ROTATE_WALLET_PHRASE`.
421. Off path must not add a button or network request.
422. Test insufficient-fee error without submitting a transaction.
423. Test invalid/expired quote without submitting a transaction.
424. Test duplicate submit guard.
425. Test process death before confirmation.
426. Test process death after send but before state callback.
427. Test restart reconciliation with server state.
428. Test server keeps old public key after send.
429. Test server switches to new public key after send.
430. Test `awaitingServerKey` equivalent if Android model needs one.
431. [INFERENCE] Server behavior for no-backup rotation is not proven by source.
432. This is a REQUIRED maintainer/device decision before release.

## 12. 0307: two-reference BoC fee quote

433. Desktop accepts request cell refs equal to 1 or 2.
434. Android currently routes BoC validation through Rust adapter.
435. Android JNI exposes `isValidCellBoc` from `WalletEngine2`.
436. Do not add a desktop `gram_boc.cpp` parser to Android.
437. First add a deterministic two-reference BoC fixture.
438. Fixture must not contain a real wallet secret or funded address.
439. Validate the fixture with Rust unit tests.
440. Validate it through C++ generated bindings if applicable.
441. Validate it through `WalletEngine2.isValidCellBoc` JNI.
442. Validate fee quote preparation with the fixture path.
443. Confirm one-reference legacy BoC remains accepted.
444. Confirm malformed refs are rejected.
445. Confirm data-size checks remain strict.
446. Confirm more than two refs is rejected where protocol requires it.
447. Confirm invalid BOC cannot trigger network request.
448. Confirm error text does not echo BOC if it may contain secrets.
449. If Android engine already accepts two refs, record 0307 as verification-only.
450. If it rejects them, port the minimal Rust parser change.
451. Keep parser change in wallet-engine revision, not generated C++.
452. Rebuild all four ABIs after parser change.
453. Re-run fee quote on test wallet only.
454. Do not use live-money fee quote as the first test.
455. [INFERENCE] Exact BoC fixture bytes must come from engine test vectors or maintainer.
456. Do not invent bytes and call them protocol-valid.

## 13. 0310: copy secret words

457. Existing phrase surfaces include `showRecoveryPhraseAlert`.
458. Existing phrase surfaces include `WalletSecretPhraseFragment`.
459. Existing quiz surface is `WalletTestPhraseFragment`.
460. Add a Copy Words action only when `COPY_WALLET_WORDS` is on.
461. Keep default off even though desktop default is on.
462. Add the row to MODE_MONEY with keywords `copy`, `words`, `recovery phrase`.
463. Copy the minimum required string, not a debug representation.
464. Show a generic copied confirmation.
465. Schedule clear after 60 seconds.
466. Clear only if clipboard still equals the copied text.
467. Do not clear a newer user clipboard value.
468. Clear all intermediate Java arrays after writing clipboard.
469. Android clipboard may be observed by the system keyboard.
470. Add warning text that copy is a security exposure.
471. Do not promise OS-level clipboard secrecy.
472. Avoid clipboard history metadata where Android API allows.
473. Do not log copied text.
474. Test copy on API levels supported by minSdk 23.
475. Test app background/foreground during 60-second delay.
476. Test clipboard replacement before timeout.
477. Test fragment destruction before timeout.
478. Test rotation/configuration change.
479. Test 12-word and 24-word phrase surfaces.
480. Test private-key wallet: copy words must not expose raw key accidentally.
481. If private key display has a separate action, gate it separately.
482. Do not label a private key as recovery words.

## 14. Secret-handling contract

483. Secrets include mnemonics, raw private keys, derived signing keys and signatures.
484. Public address and public key are not secrets, but still avoid unnecessary logs.
485. Secret inputs must live in `byte[]`/sensitive native buffers only as long as needed.
486. Use `try/finally` or `Closeable` cleanup on every new secret path.
487. Native code must zero temporary buffers before returning.
488. Native code must reject null/empty/invalid-size buffers first.
489. JNI exceptions must be generic and secret-free.
490. Rust code should use the existing `zeroize` dependency.
491. Rust code must not derive a key using an ambiguous network default.
492. Every address derivation must state network explicitly.
493. Every signing operation must use the account's current wallet identity.
494. Imported private wallet must be marked non-backupable.
495. No private key may enter `SharedPreferences`.
496. No private key may enter `tele_kv`.
497. No private key may enter `Intent` extras.
498. No private key may enter `Bundle` saved state.
499. No private key may enter URL query, HTTP header or telemetry.
500. No private key may enter `FileLog`, crash text or `TeleCrash`.
501. No private key may enter generated settings export.
502. No private key may enter clipboard except explicit user action.
503. Clear clipboard after 60 seconds if unchanged.
504. The app must refuse backup operation for private-key wallet.
505. The app must refuse cloud sync operation for private-key wallet.
506. The app must distinguish mnemonic and private-key storage kinds.
507. Storage decryption failure must fail closed.
508. Unknown storage version must fail closed.
509. Partial write must leave previous valid wallet record intact.
510. Wipe must remove staging and committed secret files.
511. Logout must wipe account-local private wallet records.
512. Multi-account tests must prove no cross-account secret access.
513. Do not use a static account-0 cache.
514. Security review must inspect native and Java copies separately.
515. Security review must inspect generated C++ bindings.
516. Security review must inspect release symbols and debug logs.
517. Security review must inspect screenshots and clipboard behavior.
518. Security review must inspect backup/restore behavior.
519. A security concern blocks `done`, not merely a warning in docs.

## 15. Network endpoints and policy

520. Existing Android wallet engine configuration names Toncenter at `https://toncenter.com`.
521. Existing wallet Java code uses Telegram MTProto wallet TL requests.
522. Existing transaction lookup uses `TL_wallet` requests and current account.
523. Existing wallet state arrives through `TL_wallet.WalletState`.
524. Existing updates include `TL_update` wallet update types.
525. Import proof must use the existing account's `ConnectionsManager`.
526. Rotation fee quote may use Toncenter through wallet-engine.
527. Do not add a Tele-server endpoint for balances, keys or transactions.
528. Do not send account data to Tele server.
529. Do not add third-party endpoint without a setting and privacy decision.
530. Keep provider URL centralized in wallet engine config.
531. Validate HTTPS and host before network use.
532. Apply timeout and cancellation to every recovery request.
533. Do not retry signing or broadcast blindly.
534. A retry after ambiguous broadcast may double-spend or duplicate operation.
535. Persist operation id only in the existing durable wallet journal path.
536. Do not create a second send journal in `tele.db`.
537. Test offline mode before any secret authorization.
538. Test provider failure before any secret authorization.
539. Test MTProto failure after proof generation.
540. Test Toncenter failure after local preparation.
541. Record endpoint and network in logcat without secrets.
542. A network error must not expose phrase or raw key in UI.

## 16. Threading and lifecycle anchors

543. `WalletImportFragment` creates and updates views on main thread.
544. Phrase parsing and key derivation belong off main thread.
545. Rust JNI calls may block on provider/network; never run them in click handler.
546. Existing wallet callbacks hop through `AndroidUtilities.runOnUIThread`.
547. Preserve that callback convention for new import and rotation paths.
548. Storage worker is `GramWalletStorage` single-thread executor.
549. Do not call UI methods from storage worker.
550. Deliver storage completion once and outside storage lock.
551. Cancel callbacks when fragment weak reference is gone.
552. Cancel native client when account logout occurs.
553. Cancel native client when wallet is disabled by 0288 later.
554. [INFERENCE] Batch 26 need not implement batch 27 no-money UI.
555. Do not add 0288 behavior to this batch.
556. Rotation state must be account-local and generation-checked.
557. Ignore stale callback after a newer import/rotation starts.
558. Ensure button loading state clears on every terminal result.
559. Ensure phrase fields clear on error and success.
560. Ensure RecyclerView rows rebind current toggle values.
561. Ensure MODE_MONEY refresh after toggle change.
562. Ensure restart-required state is visibly communicated.
563. Test activity recreation while native call is pending.
564. Test account switch while native call is pending.
565. Test logout while native call is pending.

## 17. Build and evidence procedure

566. Start from a clean `Telegram` branch `tele` at the documented upstream base.
567. Do not alter `main/UPSTREAM` for this feature batch.
568. Initialize required submodules with `git submodule update --init`.
569. Verify wallet-engine gitlink and submodule HEAD separately.
570. Install Rust toolchain and all four Android targets.
571. Run `TMessagesProj/jni/prebuild/build_wallet_engine.sh` first.
572. For a clean native rebuild run `TMessagesProj/jni/prebuild/build_all.sh`.
573. Capture stdout and stderr to an external, untracked evidence file.
574. Never capture secret input or wallet words in that evidence file.
575. Verify generated bindings have matching timestamps/revision metadata.
576. Verify archive exists for every ABI.
577. Verify CMake imports each ABI archive.
578. Run `./gradlew :TMessagesProj_App:assembleDebug`.
579. Select the device ABI, normally `arm64-v8a`.
580. Install with `adb install -r <arm64-debug-apk>`.
581. Keep APK and logcat evidence outside the queue until reviewed.
582. Capture `adb logcat -c` before each scenario.
583. Capture only filtered tags after each scenario.
584. Useful observed tags include `[gram-wallet]` and Rust/JNI error tags.
585. Do not use `logcat | grep` patterns that print secret payloads.
586. Redact account ids, wallet addresses and operation ids where required.
587. Evidence for 0278: config getter behavior after cold restart.
588. Evidence for 0308: four Rust archives and CMake target success.
589. Evidence for 0309: derived address, proof result and local storage kind only.
590. Evidence for 0285: fee quote, confirmation, server state and new phrase quiz.
591. Evidence for 0307: one-ref and two-ref BoC validation.
592. Evidence for 0310: copy action and delayed clear without secret text.
593. A successful build is evidence of build only, not wallet correctness.
594. A logcat line saying success is not proof of on-chain finality.
595. Confirm final wallet state from trusted server response.
596. Confirm no unexpected network endpoint was contacted.

## 18. Test wallet strategy and real-money warnings

597. Use a dedicated disposable test wallet created for this batch.
598. Use the maintainer-approved test backend if available.
599. [INFERENCE] Current Android JNI config visibly defaults to mainnet.
600. Therefore do not assume testnet merely because the wallet is called test wallet.
601. Ask maintainer to provide network and funding instructions before device test.
602. Fund only the minimum amount needed for fee quote and rotation.
603. Never use a production seed phrase for any test.
604. Never import a phrase copied from a real wallet.
605. Never paste a real private key into Android clipboard.
606. Disable cloud clipboard synchronization on the test device.
607. Disable keyboard learning/history for the test input.
608. Use a freshly wiped emulator or dedicated physical device.
609. Verify device backup is disabled for app data where possible.
610. Verify no screen recording or accessibility logger is active.
611. Verify test wallet address before any send or rotation.
612. Verify displayed address against an independent trusted tool.
613. Keep a second independent recovery copy offline and encrypted.
614. Do not place recovery copy in repository or chat.
615. First test invalid private key with zero balance.
616. Next test valid private key with zero balance.
617. Next test valid private key import without sending funds.
618. Next test phrase display and copy with zero balance.
619. Next test fee quote without confirmation.
620. Next test cancelled rotation.
621. Next test confirmed rotation with minimum fee balance.
622. Verify old secret no longer signs after confirmed rotation.
623. Verify new secret restores the same address where protocol says so.
624. Verify server public key and local public key converge.
625. Verify restart after rotation before any further transaction.
626. Verify no duplicate transaction after activity recreation.
627. Verify wipe removes local imported key.
628. Verify reimport after wipe requires explicit key input.
629. Use a test-only address for two-reference BoC fixture.
630. Do not test 0307 by crafting a live spend transaction.
631. Stop immediately on unexpected address, fee, nonce or public key.
632. Stop immediately on any phrase/key in logcat.
633. Stop immediately on an unexpected provider or upload.
634. Stop immediately if old key remains usable after confirmed rotation.
635. Report the exact state and preserve non-secret logs for diagnosis.

## 19. Questions requiring maintainer decision

636. Which exact private-key encoding is supported: hex, base64, or both?
637. Is the raw key Ed25519 seed, expanded secret, or another TON key form?
638. Should address-plus-12-words recovery be included in desktop 0309 (import by private key)?
639. Which TON network must the test wallet use?
640. Does the configured Toncenter endpoint support that network?
641. Does server accept no-backup key rotation without `TL_wallet.disableBackup`?
642. Does server return the new public key in `TL_wallet.WalletState` immediately?
643. How should Android reconcile an old served key after rotation?
644. What exact fee quote validity window must UI display?
645. Is 60-second clipboard clear sufficient for Android system clipboard history?
646. Should copy action remain default off despite desktop default-on 0310?
647. Is private-key display allowed only after wallet passcode/biometric unlock?
648. Should FORCE_WALLET be visible in MODE_MONEY or a debug sub-group?
649. Which release ABIs are mandatory: all four or arm64 only?
650. Is committing generated prebuilt archives required in this queue?
651. Is git-lfs required in CI for generated archives or submodule objects?
652. Who signs off the Rust diff and generated bindings?
653. Who signs off private-key storage and backup exclusion?
654. Who owns manual device interaction at the batch gate?
655. Do not close these questions by guessing.

## 20. features.md and export requirements

656. Add one English row per user-facing feature in `features.md`.
657. Rows are required for FORCE_WALLET if exposed to users.
658. Rows are required for private-key import.
659. Rows are required for phrase rotation without backup.
660. Rows are required for copy secret words.
661. Each row states what it does in one plain sentence.
662. Each row states `tele · money` as the location.
663. Each row states the default, which is off for new toggles.
664. Each row names the exported Android patch file after export.
665. Each row names its desktop source number: 0278, 0309, 0285 or 0310.
666. 0308 build infrastructure need not be a user-facing row.
667. 0307 may be described in patch notes, not as a toggle.
668. Do not invent Android patch numbers before `git format-patch`.
669. Export with the documented `git format-patch` command.
670. Verify only expected patch files changed in `main/`.
671. Update PATCHLIST status truthfully after export.
672. `todo` becomes `wip` only after a commit exists in Telegram tree.
673. `wip` becomes `queued` only after export exists in patches/android.
674. `queued` becomes `built` only after debug APK is handed over.
675. `built` becomes `done` only after human on/off verification.
676. Keep this batch guide unchanged while implementation proceeds unless plan changes.

## 21. Batch gate checklist

677. 0278 off returns stock walletAvailable behavior.
678. 0278 on takes effect only after restart.
679. 0308 cleanly builds Rust with the pinned toolchain.
680. 0308 creates all four ABI archives.
681. 0308 generated bindings compile as C++20.
682. 0308 JNI object links into `tmessages.49`.
683. 0309 private-key import is hidden/disabled when off.
684. 0309 invalid key is rejected locally.
685. 0309 valid key derives expected address.
686. 0309 imported wallet is marked non-backupable.
687. 0309 private key is encrypted at rest through wallet storage.
688. 0309 private key is absent from logs, exports and telemetry.
689. 0285 button appears only for no-backup wallet and enabled toggle.
690. 0285 quote shows fee before confirmation.
691. 0285 cancelled flow does not broadcast.
692. 0285 confirmed flow is tested on disposable wallet.
693. 0285 server/local keys reconcile after restart.
694. 0307 accepts one-reference fixture.
695. 0307 accepts two-reference fixture.
696. 0307 rejects malformed fixture.
697. 0310 copy is hidden when toggle off.
698. 0310 copy works when toggle on.
699. 0310 clears unchanged clipboard after 60 seconds.
700. 0310 does not clear replacement clipboard content.
701. All UI callbacks run on main thread.
702. All account operations use the active account.
703. No stock DB schema or `TLRPC.java` was edited.
704. No real-money wallet was used.
705. No secret appeared in evidence.
706. `features.md` rows and patch references are complete.
707. All six patch files are exported.
708. `assembleDebug` succeeds for the full app.
709. APK is handed to maintainer with numbered manual steps.
710. Only human verification may move the batch to `done`.

## 22. Planned commit summary

711. `feat: force wallet` — 0278, S, first.
712. `misc: build wallet engine` — 0308, L, after Android API review.
713. `feat: import private wallets` — 0309, L, after 0308.
714. `feat: rotate wallet phrase` — 0285, M, after 0309.
715. `fix: quote key change fee` — 0307, S, after 0285.
716. `feat: copy wallet words` — 0310, S, after money UI.
717. Не использовать `build:`: правила Android-очереди допускают `feat:`, `fix:`, `debloat:` и `misc:`.
718. Keep subjects lowercase and imperative.
719. Keep each subject within repository commit-word limits.
720. Do not combine all six rows into one commit.
721. Do not commit docs-only implementation claims as feature completion.
722. Do not add compatibility shims for an old engine API.
723. Remove obsolete private-key paths after clean cutover.
724. Leave unresolved server behavior explicitly documented.
725. The batch is complete only after the gate, not after this plan.
