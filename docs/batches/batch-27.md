# Пачка 27 — деньги: интерфейс и карта

## Назначение и границы

1. Руководство описывает Android-перенос строк пачки 27 из `docs/PATCHLIST.md`.
2. Номера в заголовках и ниже — текущие номера desktop-очереди, не номера Android patch-файлов.
3. Объём пачки: 0288, 0290, 0313, 0286, 0296, 0307 и 0317.
4. Порядок строк реализации ниже выбирает безопасные зависимости, не меняет публичный список PATCHLIST.
5. Деньги здесь означает существующий Telegram Wallet/TON-кошелёк, а не Stars-баланс.
6. На Android дерево `tele` уже содержит полноценный Wallet: `GramWallet`, `WalletActivity`, `WalletCardComponent`, `WalletCardView`, `WalletCard3D`, `WalletCard2DView`, `WalletActionLayout` и `WalletCardGLRenderer`.
7. В desktop-очереди wallet — отдельная подсистема, но исходники desktop не копировать; переносить поведение на Android API.
8. Эта пачка меняет интерфейс, локальные предпочтения и отрисовку; перевод средств и подпись транзакций не переписывать.
9. Ни одна функция пачки не требует ввода нового приватного ключа или изменения сетевого протокола.
10. Все дополнительные network-запросы должны быть явно обоснованы; предпочтительно переиспользовать загруженные Android-данные.
11. Существующее wallet UI доступно только когда конфигурация сервера разрешает wallet.
12. Не путать доступность wallet с включением настройки tele «Turn off Money».
13. Пачка зависит от batch 26: WalletEngine обновлён, импорт приватных ключей и wallet-ready UI доступны.
14. Пачка зависит от batch 23 для общих local-passcode / dangerous-action решений, если wallet-карта, импорт или переходы требуют подтверждений.
15. Не добавлять новую проверку пароля к чтению карты, баланса или истории; подтверждение сохраняется только там, где его требует stock wallet.
16. Патчи 0287, 0289, 0292 и 0297 не добавляют работу этой пачке: 0287/0289/0292 покрыты stock, 0297 относится к Qt-окну.
17. По решению мейнтейнера 0307 и 0317 включают оба пути карты: 2D Canvas и 3D GL/шейдер.
18. Не упрощать 3D-дизайн до постоянной 2D-карты: низкий режим качества может принудительно выбирать 2D, но функциональность должна быть доступна.
19. Desktop-патчи 0286 и 0296 должны ссылаться на `tonscan.org`, как зафиксировано в PATCHLIST/decisions.
20. Не подменять заданный endpoint `tonscan.org` серверным `tonBlockchainExplorerUrl` без решения мейнтейнера.
21. Вся новая настройка — в `TeleConfig`, default off; отсутствие настройки означает точное stock-поведение.
22. Если эффект локальный и без отдельного переключателя, он всё равно должен быть ограничен соответствующей настройкой или включён по умолчанию только по явному решению.
23. Правила форка запрещают изменение `TLRPC.java`, stock-схемы и `LAST_DB_VERSION`.
24. Код форка помещать в новые файлы под `TMessagesProj/src/main/java/tele/`; stock-файлы получают минимальные gated hooks.
25. Fork-строки — только в `strings_tele.xml`, с префиксом `Tele`.
26. Эта пачка создаёт user-facing функции: после каждого реализованного патча обновить `main/features.md` по разделу `Money`, с местом, default, Android patch subject и desktop номером.
27. PATCHLIST статус менять только после фактического коммита/экспорта; этот документ не является свидетельством реализации.

## Опорные факты и исходные решения

28. Android-ветка `Telegram`/`tele` содержит Wallet-код в `org.telegram.ui.Wallet`.
29. В `WalletActivity` объявлены вкладки `TAB_TRANSACTIONS` и `TAB_COLLECTIBLES`.
30. `WalletActivity` держит `UniversalRecyclerView` списков истории, `GramWallet.TransactionsList` и `GramWallet.CollectiblesList`.
31. В `WalletActivity` есть `openTransactionSheet`, список `TransactionCell` и отдельный топ-панельный баланс.
32. `WalletActivity` уже содержит `use2DCard`, карту и переключение реализации в DEBUG-меню.
33. `WalletCardComponent` создаёт `WalletCard2DView` или `WalletCardView`; 3D реализация — через stock wallet GL renderer.
34. `WalletCardComponent` учитывает power-save режим и форсирует 2D при энергосбережении.
35. `WalletCardComponent` управляет балансом, QR, engraving, наклоном и переходом баланса на ActionBar; не ломать эти переходы при замене материала.
36. Desktop 0307 — большой самостоятельный патч: настройки выбора подарочной темы, локальное сохранение выбора, загрузка/проверка владения collectible, отрисовка gift-material на карте и исходящих transfer cards.
37. Desktop 0317 добавляет draggable gifts/stickers на карту; Android данные коллекций уже доступны в wallet UI.
38. Источником оформления выступают уникальные подарки (`TL_starGiftUnique`) и их backdrop/pattern/model.
39. Desktop 0286/0296 используют tonscan.org; PATCHLIST разрешает «copy»/«open» из истории и сообщения.
40. Desktop 0288 выключает wallet целиком и нормализует отображение переводов; Android использует единый флаг `AppGlobalConfig.walletAvailable`.
41. При 0288 предпочтение tele должно побеждать stock/server enablement; 0278 наоборот форсирует доступность, значит «Turn off Money» имеет приоритет.
42. PATCHLIST effort для пачки: S×5, L×2. Все оценки сохранять при разделении коммитов.
43. [INFERENCE] Точный текущий номер Android settings-search ID для каждого нового wallet-пункта надо сверить с деревом `TeleSearch` на момент реализации; диапазон 1420–1439 зарезервировать для этой пачки согласно заданию.
44. [INFERENCE] Не предполагать, что текущий search registry автоматически назначит эти ID; зарегистрировать их явно и проверить уникальность локальным поиском по существующим ID.
45. [INFERENCE] Все названия hook-функций ниже — целевые семантические якоря; перед изменением найти их точные определения/перегрузки на актуальной ветке `tele`.

## Порядок работ и отдельные коммиты

46. Перед началом подтвердить, что batch 26 импортирован/собран и ветка `tele` содержит ожидаемые wallet-engine изменения.
47. Также проверить batch 23 для password/action primitives; использовать готовый механизм, не заводить второй passcode.
48. Порядок коммитов: сначала 0288, затем 0290, 0313, 0286, 0296, после этого 0307 и 0317.
49. 0288 — `feat: turn off money`, S.
50. 0290 — `feat: dim wallet address groups`, S.
51. 0313 — `feat: hide wallet balances`, S.
52. 0286 — `feat: copy wallet transaction links`, S.
53. 0296 — `feat: open transfer transaction links`, S.
54. 0307 — `feat: design wallet card with gifts`, L.
55. 0317 — `feat: place gifts on wallet card`, L.
56. Subject коммита — imperative lowercase, максимум пять слов, не включать desktop номер в заголовок.
57. Каждый патч — отдельный commit в Android tree, экспортируется в очередь; соответствующие PATCHLIST и `features.md` обновления включить в процесс согласно репо-правилам.
58. Рабочие изменения выполняются в `Telegram` branch `tele`; не редактировать экспортированные `.patch` вручную.
59. Точный номер Android patch после очереди заранее не обещать: format-patch нумеруется текущей позицией.
60. 0288 первым задаёт главный поведенческий контракт для остальных: скрытая money UI не должна открываться из ссылок или переводов.
61. 0290 и 0313 локальны, не зависят от explorer.
62. 0286 вводит общий URL-builder, 0296 использует его, поэтому эти два коммита строго упорядочены.
63. 0307 строит выбор дизайна/передачу theme; 0317 добавляет размещение gift-стикеров только поверх готового дизайна.
64. Не начинать L-карту до проверки доступности batch 26 API и 3D renderer в обеих режимах.
65. Перед каждым патчем проверить settings group, search registry, export/import preferences и существующий stock equivalent.
66. Если текущий stock содержит требуемое поведение, не дублировать его: зафиксировать отсутствие работы в PATCHLIST примечании.

## MODE_MONEY, настройки и поиск

67. Страница настроек денег называется `MODE_MONEY`, slug/deeplink — согласовать с текущими режимами, например `money`.
68. Страница должна быть доступна через Tele settings и находиться поиском; не размещать wallet-функции среди privacy/debug без причины.
69. Определить отдельные `TeleConfig` items по функциям, не один общий boolean для всех изменяемых интерфейсов.
70. Предлагаемые имена: `NO_MONEY`, `DIM_WALLET_ADDRESS`, `HIDE_OTHER_WALLET_BALANCES`, `WALLET_TRANSACTION_LINKS`, `WALLET_GIFT_CARD_DESIGN`, `WALLET_GIFTS_ON_CARD`.
71. Имена Kotlin-полей и реальный стиль `TeleConfig` подогнать к текущим conventions.
72. `NO_MONEY` — default off, restart required.
73. `DIM_WALLET_ADDRESS` — default off, чтобы off сохранял исходную интенсивность Android-адреса.
74. `HIDE_OTHER_WALLET_BALANCES` — default off; скрывает только дополнительные строки над картой, не общий баланс.
75. `WALLET_TRANSACTION_LINKS` — default off; включает новые copy/open entry points в истории и меню перевода.
76. `WALLET_GIFT_CARD_DESIGN` — default off; дочерний выбор/дизайн показывать только при on и доступном Money.
77. `WALLET_GIFTS_ON_CARD` — default off; виден только если дизайн включён, Money доступен, а collectibles содержат подарки.
78. [INFERENCE] Desktop-опция дизайна включена в зависимости от `NoMoney`; на Android дочерние строки MODE_MONEY скрывать/disable при `NO_MONEY`.
79. Добавить каждый параметр в экспорт/импорт settings spec; неизвестный ключ старых версий должен безопасно игнорироваться по стандартному поведению.
80. Если сохранение выбора уникального подарка требуется, использовать fork storage (`tele_kv` или `tele_*`), отдельно от stock wallet database.
81. Не хранить приватные ключи, recovery words, полный адрес пользователя или транзакционные данные в настройке дизайна.
82. Для поиск-ID 1420–1439 выделить по одному стабильному ID на строку/синонимы в пределах диапазона; не назначать второй ID одному элементу без существующего паттерна.
83. Предложенный поиск-словарь: 1420 money/wallet/кошелёк, 1421 disable/turn off/hide money, 1422 transaction/history/explorer, 1423 tonscan/transaction link/copy, 1424 address/groups/dim, 1425 balance/other balances/hide, 1426 gift/card/design/collectible, 1427 sticker/drag/place, оставшиеся 1428–1439 оставить доступными для дополнительных wallet-term aliases, не создавать фиктивные settings.
84. [INFERENCE] Если registry задаёт ID на search result, а не keyword, точное распределение 1420–1439 уточнить по реализации поиска; важен фиксированный непересекающийся диапазон, объявленный централизованно.
85. Поиск должен вести к корректной странице и раскрывать родительскую настройку только если это уже поддерживает TeleSearch.
86. Строки UI/summary/descriptions написать так, чтобы явно сообщать о restart, сетевых ссылках и необратимых wallet действиях.
87. Для 0288 объяснить, что это выключает Money и его связанные переходы, а не удаляет установленный wallet или ключи.
88. Для карты не показывать «Buy»/purchase action, который может отправить TON без существующего wallet confirmation.

## 0288 — выключить Money целиком (S)

89. Цель — один пользовательский выключатель, который после рестарта ведёт себя как `walletAvailable = false` независимо от серверного wallet флага.
90. При off настройки значение `AppGlobalConfig.walletAvailable` должно оставаться исходным; не форсировать wallet и не создавать состояние.
91. При on «Turn off Money» побеждает `FORCE_WALLET` из batch 26, если тот включён.
92. Restart-required необходим, поскольку wallet/ton-connect и конфиги могут кэшироваться при запуске.
93. Хранить preference в TeleConfig и читать его только в минимальном override `AppGlobalConfig.ConfigBoolean.get()` для ключа `wallet_available`.
94. Не менять глобальное значение для других config keys.
95. Не патчить каждое UI место, уже правильно использующее `walletAvailable`; минимальный override закрывает существующие стоковые гейты.
96. Отдельно проверить uncovered paths, перечисленные ниже: они не обязательно используют walletAvailable.
97. В `MessageObject` для `TL_messageActionGramTransfer` и `TL_messageActionWalletTonConnectRequest` вернуть обычный нейтральный сервисный текст, исключив wallet-ссылки/интерактивные подписи.
98. В `ChatActionCell.hasWalletActionLayout()` отключить отдельную wallet-transfer карточку; сообщение должно рендериться безопасным сервисным видом.
99. Не терять базовый текст, дату или возможность открыть обычный чат при замене карточки на сервисную строку.
100. В `MessagesController` обработку `TL_updateWallet*` гейтить до запуска ton-connect / обновления скрытых экранов; не ломать общую обработку остальных Updates.
101. В `LaunchActivity` остановить/deeplink wallet routes на раннем guard; показать спокойный toast/alert «Money отключён» и вернуться в безопасный экран.
102. Проверить ссылки `LinkManager`: отключённый wallet не должен открывать внутренний wallet fragment и не должен вызывать отсутствующий handler.
103. Ton-connect сессии не удалять локально и не посылать серверу revoke только из-за переключения UI; это было бы отдельным изменением поведения.
104. Убедиться, что стоковый wallet UI скрывается в `SettingsActivity`, `ProfileActivity`, `ChatAttachAlert`, `DialogsActivity`, `PasscodeActivity`, `LogoutActivity` и `GramWallet.ensureLocalWalletBalances` за общим config getter.
105. [INFERENCE] Точный список неохваченных UI/updates путей зависит от текущей версии Android; проверить все `walletAvailable` и `TL_updateWallet` consumers в коде перед завершением.
106. Настройку не включать автоматически из-за отсутствия сети или ответа сервера.
107. NO_MONEY — локальный визуальный/функциональный выключатель; не отправляет сведения о пользователе на third-party или tele сервер.
108. Изменение конфигурации не должно стирать адреса, историю, фразу, ключи, импортированные кошельки или локальные backups.
109. Проверить состояние при включённом batch-26 FORCE_WALLET: no-money всё равно скрывает feature.
110. Проверить ссылку на перевод и кнопку Ton Connect при выключенной Money: никаких wallet sheet, deep link или предложения «подключить кошелёк».
111. Для включённой настройки принять restart и иметь явное сообщение/описание; не делать частичную live-подмену незавершённых сервисов.
112. Включение обратно и перезапуск должны восстановить ровно stock/server wallet доступность.

## 0290 — тусклые группы адреса (S)

113. Цель — визуальное чередование групп адреса, как в iOS, при сохранении полной копируемой строки.
114. В `WalletActivity.formatTransactionAddress` Android сейчас имеется закомментированная идея приглушения; сверить фактическую строку перед правкой.
115. Уже существующий `WalletImportFragment.formatAddressTwoLines` применяет `TextAlphaSpan(0.75f)`; использовать согласованный оттенок/альфу, не заводить новый способ группировки.
116. Применять span к отображаемым группам без изменения строки, копируемого значения или clipboard.
117. Учитывать короткие/невалидные/пустые адреса и разделитель; не падать при количестве групп меньше ожидаемого.
118. Основной хук — форматтер адреса деталей транзакции; карту форматировать только если дизайн требует, и согласовать с существующим engraving.
119. Настройка `DIM_WALLET_ADDRESS` default off должна охватывать все целевые места согласованно.
120. Не применять к суммы, transaction hash, QR payload или чужим ссылкам.
121. Не создавать логирование полных адресов.
122. Тестировать формат строки при LTR/RTL locale и dynamic font size; адрес сам остаётся LTR.
123. Рецайкл: если адресная view переиспользуется, каждый bind должен полностью очистить старые spans прежде чем применять новое значение.
124. Отдельно сверить детали транзакции, экран импорта, wallet card embossing; последний может не входить в 0290, если поведение изменения карты не требуется.

## 0313 — скрыть дополнительные балансы над картой (S)

125. Цель — скрыть дополнительный баланс других/старых кошельков и earnings, не скрывая текущий wallet balance.
126. Якорь — `WalletActivity.updateWalletTopPanel()` и его три visibility calls для `waltButton`, `oldWalletsButton`, `gramEarningsButton`.
127. Обернуть только видимость целевых рядов; не менять computed totals и не менять транзакционные данные.
128. Настройка `HIDE_OTHER_WALLET_BALANCES`, default off.
129. Скрытая строка должна оставаться доступной после выключения настройки и повторного открытия wallet.
130. Контролы рецайклятся/пересоздаются при `createView`: состояние применить и при первоначальной сборке, и при обновлении `updateWalletTopPanel()`.
131. Проверить разные состояния: нет дополнительных средств, есть старый wallet balance, есть earnings, одновременно несколько значений и loading state.
132. Не скрывать privacy-sensitive amounts лишь при первом запуске: настройка постоянная, не сбрасывать данные.
133. Quick hide на long-press через `ItemOptions` допускается только если его UX/механизм сохраняет настройку и не конфликтует с текущим long-press.
134. [INFERENCE] PATCHLIST называет под-тумблер MODE_MONEY; быстрый скрывающий контекстный menu следует трактовать как optional UI только после подтверждения фактического desktop parity.

## 0286 — ссылки на транзакции кошелька (S)

135. Общий URL-builder создаёт только `https://tonscan.org/transaction/<validated-hash>`.
136. Не включать пользовательские адреса/имена/telegram user id в URL.
137. Hash берётся из уже загруженного transaction object в `GramWallet.TransactionsList`.
138. URL-encode/validate сегмент hash, не конкатенировать произвольную строку из clipboard или сообщения.
139. В `WalletActivity.openTransactionSheet` рядом с «open in explorer» добавить «copy link»; существующее open направление привести к tonscan.org согласно решению.
140. В списке истории `TransactionCell` добавить long-press `ItemOptions` с copy/open только если текущая строка имеет пригодный transaction hash.
141. Обычный tap по строке и существующий transaction sheet оставить нетронутыми.
142. Использовать `AndroidUtilities.addToClipboard` / существующий clipboard helper и показывать короткое подтверждение после копирования.
143. Для open использовать штатный Android browser/`Browser` route, не WebView внутри wallet.
144. Никакого third-party request при открытии/копировании кроме намеренного пользовательского перехода в браузер; не fetch-ить explorer для preview.
145. Не передавать содержимое wallet history в telemetry/tele-server.
146. `tonscan.org` — внешний сервис; при отсутствии интернета открыть browser error обычным способом, не повторять transaction API запросы.
147. Проверить URL по hash без схемы, пустому hash, спецсимволам и неожиданному длинному значению; повреждённую запись не показывать как action.
148. Если строка transaction уже содержит explorer URL, не считать его доверенным: генерировать URL заново по принятому Tonscan base.
149. [INFERENCE] Адресная ссылка (wallet account address) не названа в PATCHLIST как обязательная часть 0286; не расширять на неё без подтверждения.
150. Пункт long-press должен быть доступен screen reader semantics; не завязывать действие только на недоступный right-click.
151. При выключенной Wallet (0288) действия не отображаются и action handler повторно проверяет `walletAvailable`.

## 0296 — ссылки из перевода в чате (S)

152. Патч зависит от URL-builder 0286; не дублировать сборку URL.
153. В `ChatActivity.fillMessageMenu` для `TL_messageActionGramTransfer` добавить copy/open пункты при включённой Wallet и настройке ссылок.
154. Найти транзакцию через `GramWallet.getInstance(account).findTransaction(msg)`; корректно использовать `currentAccount`.
155. Показывать оба действия только если найдена транзакция и `tx_hash` непустой/валидный.
156. Если истории еще нет или результат pending, не отображать фиктивный URL и не запускать автоматическую догрузку.
157. Проверять action code/идентификаторы на конфликты `MessageMenu.ALL` и добавлять registry, если существует общий список действий.
158. Ранний guard в action callback повторно проверяет availability, hash и контекст сообщения.
159. Открывать browser только после явного пользовательского нажатия; копирование тоже только по явному действию.
160. Не раскрывать приватные комментарии перевода, sender id или текст сообщения стороннему explorer.
161. В history row и chat menu выдавать одинаковый Tonscan link для одного transaction hash.
162. Учитывать pending transfer: если `findTransaction` ссылается на pending запись без on-chain hash, опции скрыты.
163. Не выводить «transaction not found» toast просто из-за того, что сервер ещё не загрузил историю.

## 0307 — дизайн карты по подарку (L)

164. Цель — выбрать collectible gift и взять из него цвета/backdrop/pattern/model для кошельковой карты.
165. Android интерфейс уже абстрагирует рендер через `WalletCardComponent`; использовать оба backend, не переписывать wallet view.
166. 2D path — `WalletCard2DView`/Canvas; 3D path — `WalletCardView`/`WalletCard3D` и `WalletCardGLRenderer`.
167. Сохранить QR, номер/engraving, баланс, USD amount, holder text, layout/rotation, overscroll tilt и balance-to-actionbar transition.
168. Данные подарка брать из `TL_starGiftUnique`/`GramWallet.CollectiblesList`, используя backdrop colors, pattern/model идентификаторы, существующий `Gifts.kt`/`StarGiftSheet` аналог.
169. Не импортировать desktop Qt/C++ rendering; адаптировать материал к Android Canvas/shaders/assets.
170. Ввести модель `WalletCardDesign` в `tele/` с цветами и идентификаторами документа, без хранения больших bitmap/GL texture в preferences.
171. Сохранять выбор локально per-account в Tele storage; ключ состояния должен включать account id или использовать штатное account scoped storage.
172. Не писать пользовательские данные в stock `wallet_*` db; никакой stock schema migration.
173. Сохранять stable gift id/slug и metadata; при отсутствии документа или утрате подарка корректно перейти к default design.
174. [INFERENCE] В desktop выбора есть «sync with status» и выбранный подарок; на Android UI формы выбора следует сверить с desktop diff/стоковыми gift sheet перед кодом.
175. Проверить владение gift перед установкой; не использовать по одному только slug из внешнего input.
176. Не загружать всю коллекцию повторно при каждом redraw или fragment recreation.
177. Если локальный список недостаточен, загрузку запускать единично через GramWallet/StarsController существующий API, paging/cancellation как в текущем ownership list.
178. Не отправлять gift selection на сервер без требования протокола; обычный card design локален.
179. Реализовать экран/выбор через Android `ItemOptions`/sheet или существующий `StarGiftSheet`, не вводить desktop right-click flow.
180. Для 2D и 3D одинаковые цвета, pattern, foreground contrast и selection semantics.
181. Использовать текущие Canvas shader/material code paths и GLSurface lifecycle; не создавать GL resources на UI thread.
182. `WalletCardGLRenderer` callbacks работают на GL thread; передавать immutable snapshot design через установленный renderer queue, безопасно вызывать `requestRender`.
183. Любое GL texture/program/resource освобождать при контексте/renderer teardown; не держать Activity/View через static cache.
184. Не использовать `Bitmap.createBitmap` на каждый кадр; кэшировать только реально неизменный raster/generated asset в ограниченном cache с корректной инвалидизацией.
185. Любые новые shader uniforms/asset load выполнять при setup/render thread по существующему паттерну; сообщать о shader compile failure и сохранять корректную stock card.
186. [INFERENCE] «не показывать fallback к 2D на ошибке GL» не требуется; fallback допускается лишь как безопасная отказоустойчивость renderer и не подменяет поддержку 3D.
187. 2D-дизайн должен быть pixel-aligned с card drawing dimensions и учитывать density, clipping/radius, QR button cutout и flecks.
188. 3D-дизайн должен учитывать geometry, lighting, model/view transforms, QR/button overlays, engraving mask, flecks и diamond overlay.
189. Не менять wallet address/QR под влиянием выбранного подарка.
190. Не анимировать тяжелые flecks/tilt при LiteMode/performance class/power save; следовать существующим гейтам `LiteMode` и `WalletCardComponent.powerSaveMode`.
191. Если stock `WalletCardComponent` форсирует 2D в power-save, дизайн в 2D всё равно отображает тот же gift theme.
192. Отключение настройки дизайна сразу возвращает точный stock theme в обоих типах transfer card и WalletActivity.
193. Если настройка выключена, не читать gift metadata и не создавать дополнительные cache entries.
194. Отправленные пользователем transfer cards в `WalletActionLayout` должны использовать тот же выбор дизайна, без применения темы к входящим переводам если desktop behavior явно только outgoing.
195. Уточнить точный scope входящих/исходящих карточек по desktop: исходный diff подписывается на текущую карту только outgoing transfers.
196. При смене design обновить уже видимую карту и transfer view через NotificationCenter/listener; всё изменение view — UI thread.
197. Сохранение prefs не должно происходить из draw callback.
198. Не блокировать UI ожиданием загрузки подарочного asset/модели; показать default material пока данные доступны.
199. При удалённом/недоступном уникальном gift очистить выбранный id и вернуться к default; никаких повторных бесконечных fetch.
200. Выбор цвета текста должен иметь читаемый контраст относительно фона в светлой и тёмной системной теме.
201. Сохранять выбор дизайна отдельно от stars purchase history и wallet transaction history.

## 0317 — подарки-стикеры на карте (L)

202. Цель — перетаскивать принадлежащие пользователю collectible gifts на плоскость карты и убирать их повторным тапом/контекстным действием.
203. Desktop behavior переносить на Android touch drag, а не имитировать mouse drag.
204. Использовать `WalletActivity` / `TAB_COLLECTIBLES`, `fillCollectibles`, `CollectibleCell` и `GramWallet.CollectiblesList` как source.
205. Карта принимает overlay layer только на main wallet screen; другие card components и transfer cards не получают stickers, если требования отдельно не расширятся.
206. Overlay должен сохранять модель, позицию, размер, rotation/depth и z-order в ограниченной account-scoped записи.
207. [INFERENCE] Точная persisted schema позиции не дана desktop оценкой; спроектировать компактную версионированную запись с gift ids и normalized coordinates, не сохранять pixel coordinates.
208. Нормализованные координаты восстанавливать при resize/orientation/density changes; clamp за пределы drawable face.
209. Рисовать с учётом projected card face для 3D, в той же coordinate mapping системе, что `WalletCardComponent.getFrontFaceTransform`/`frontFace`.
210. Для 2D overlay применять соответствующую face transform, а не экранные координаты.
211. Поддержать hit-testing после transform, clipping rounded card bounds и исключить QR button/interactable controls.
212. Учитывать z-order: overlays не заслоняют QR, wallet balance, address/engraving, button или scanner affordance.
213. Drag preview работает только пока пользователь тянет; после drop сохранять локальное состояние, после cancel сбрасывать transient state.
214. При recycle/detach отменять drag state, gesture listeners, animations и временные references.
215. При удалении стикера не удалять сам gift и не менять коллекцию/владение.
216. Не делать gift покупку, upgrade, transfer или claim по жесту; перетаскивание исключительно presentation-only.
217. Long press или drag handle выбирать по конфликтам RecyclerView swipe/scroll; тестировать touch slop, scroll direction и nested wallet header.
218. На экране списка collectibles не захватывать вертикальный scroll до начала горизонтального/drag жеста к карте.
219. Для accessibility предусмотреть действие «Добавить на карту»/«Убрать с карты» на gift item, не только drag.
220. Ограничить число одновременных stickers и общую площадь/overdraw; лимит согласовать с maintainer и документировать.
221. [INFERENCE] Порог количества и размер gift art desktop diff требует уточнить, не брать произвольную бесконечность.
222. Не запускать model animation/particle effect на каждом gift при idle; соблюдать LiteMode, `LiteMode.isEnabled`/performance class и power-save.
223. Анимации drop/remove отменяются при `onPause`, закрытии wallet и смене вкладки.
224. Рендерер не должен сохранять Activity/context в `static`/process-global object.
225. Проверить 2D и 3D surface recreation при пересоздании Activity, повороте, background/foreground и GL context loss.
226. Восстановление saved placement не выполняет сеть; коллекция и assets загружаются тем же управляемым data flow, что wallet collectibles.
227. Не хранить копию image content, private files или payment data в tele.db.
228. Если подарок больше не принадлежит пользователю, удалить его sticker placement при следующей подтверждённой ownership refresh.
229. [INFERENCE] Проверку ownership можно привязать к уже загруженному `CollectiblesList`; сетевой revalidation при каждом запуске не нужен.
230. Передавать изменения model через observer на UI thread; renderer получает immutable snapshot.

## История, балансы, покупки, цены и карта

231. Историю транзакций берёт stock `GramWallet.TransactionsList`, не отдельная локальная копия.
232. UI истории сохраняет stock pagination, loading/error behavior, pending transactions и account isolation.
233. Любая сортировка/перезагрузка истории остаётся ответственностью stock `GramWallet`; не запускать повторный запрос из каждой bind операции.
234. TON balance, USD estimate и other-wallet totals отображаются stock-полями; новые настройки не должны переписывать курс/сумму.
235. `WalletCardComponent` использует `MessagesController.config.tonUsdRate` и balance данные; новые gift styles менять только skin, не quote computation.
236. Purchase flow с Stars, платным сообщением и bot payments остаётся stock и отделён от TON transaction links.
237. [INFERENCE] «Покупка цены/истории» вне списка 27: для покупки collectible использовать existing `StarsController`/`StarGiftSheet`, не реализовывать новый buy endpoint в этой пачке.
238. Историческая цена collectible (desktop 0083/current desktop 0085) относится к другой пачке; не добавлять колонку price history здесь.
239. Экран Wallet и TON USD estimate не смешивать со Stars balance/Stars purchase history.
240. При запуске purchase flow существующие batch 23 `TelePasscode`/dangerous action safeguards должны оставаться обязательными; эта пачка не ослабляет их.
241. Карта может получать модель и паттерн подарка из загруженной коллекции; не использовать сторонний каталог покупки.
242. Для сетевых wallet calls применять стандартные `ConnectionsManager`/wallet API, имеющиеся в GramWallet; third-party browser links — только user-triggered.
243. Tonscan external website получает transaction hash и IP/browser metadata в соответствии с обычным HTTP; UI должно сделать это очевидным по тексту действия.
244. Не делать explorer prefetch, price lookup или image download на Tonscan при простом отображении истории.
245. TON rates и wallet state приходят через Telegram/stock config; не переключать на api.changes.tg, tele server или сторонний endpoint.
246. Поддержка выбора карты и скрытия баланса local-only; не синхронизировать через Telegram account state.
247. Карты locations/maps (Яндекс/2ГИС/OSM/Google) из решения 0138 относятся к location viewer и не входят в money card.
248. Для 0138 сохраняется выбор web map service только в соответствующем chat/location feature; не отправлять wallet locations через map provider.
249. [INFERENCE] Если «карта» в текущем UX обозначает wallet card, не путать её с географической картой; названия в strings должны говорить «карта Wallet/кошелька».
250. Любой будущий map deep link должен быть default-off, provider контролироваться настройкой, без координат/аккаунта в tele-server; это не реализация batch 27.
251. Tele-network offline switches проверять на низком уровне для каждого нового запроса, хотя в этой пачке не нужен запрос к tele backend.
252. Third-party network: tonscan.org — единственный предусмотренный внешний explorer, и только по explicit copy/open interaction.
253. Не добавлять remote price source, analytics, tele-server endpoint или generic endpoint selector для этих patch rows.
254. Wallet server enablement остаётся server-controlled за исключением `NO_MONEY`, который может только отключить; включить wallet при server false может только batch 26 toggle и только с явным пользовательским выбором.
255. При устройстве без сети показывать последний известный balance/history по stock behavior, не превращать карту в сетевой gate.

## Потоки, кэш и приватность

256. Все callback-данные `ConnectionsManager`, `MessagesStorage`, GramWallet background queue и GL renderer не трогают View напрямую.
257. Перед view mutation перейти на UI через `AndroidUtilities.runOnUIThread`/fragment `runOnUIThread`.
258. Renderer callbacks только enqueue GL work/immutable data; никакого GL call с UI thread.
259. Состояние per-account брать через `currentAccount`, `GramWallet.getInstance(account)` и `MessagesController.getInstance(account)`.
260. Не использовать singleton account 0 при построении меню, истории, cards, preferences и observer.
261. В observer callbacks проверять target wallet/account, чтобы баланс/дизайн одного аккаунта не попал в другой.
262. Регистрация notification observer синхронизируется с attach/detach; повторный attach не дублирует observer.
263. При fragment destroy удалять callbacks, post-runnables, observers, delayed tasks, subscriptions и GL references.
264. Список истории использует RecyclerView/UniversalAdapter; каждое поле holder полностью перепривязывать в bind.
265. На recycled `TransactionCell` сбрасывать click/long-click, subtitle, accessibility label, spans и visibility предыдущей транзакции.
266. При настройке NO_MONEY очистить/заменить wallet affordance на bind, а не только при создании cell.
267. При смене gift design сообщить NotificationCenter/локальному observer и обновить видимые cells; не вызывать полный network reload.
268. Cache keys включают gift id/model id/pattern id и material version; изменение цветов инвалидирует текстуру.
269. Ограничить cache size, освобождать GL textures и bitmap при context teardown; не накапливать каждую выбранную тему.
270. Не помещать секретные слова, private key, mnemonic, transfer memo или полный raw response в logcat/FileLog/crash report.
271. URL copy не записывать в analytics; clipboard используется только по явному запросу пользователя.
272. Очистка clipboard по timer из batch 26 для секретных фраз сохраняется; transaction URL не является секретом, но не копируется без действия.
273. Не сохранять адреса/history в shared logs или `tele_kv`; только уже штатное wallet storage.
274. Для настройки hide balances проверять privacy preference на bind/render каждый раз, включая UI refresh после конфигурационного изменения.
275. Учитывать screen capture policy стока; карта не должна случайно добавлять новый screenshot bypass.
276. Все локальные caches должны очищаться/переиндексироваться безопасно после смены account/logout.

## Тестирование на emulator/device

277. До тестирования проверить debug build всех ABI после batch 26, включая Rust wallet-engine ABI, а не только Java compile.
278. Для wallet tests использовать только test wallet и test funds; никаких mainnet средств в ручном чек-листе.
279. Не импортировать чужой приватный ключ и не просить пользователя прислать seed phrase.
280. Создать тестовый аккаунт/кошелёк отдельный от primary account; убедиться, что passcode установлен согласно batch 23 procedures.
281. Сначала проверить wallet availability stock path: server false + обычные настройки, server true + NO_MONEY off.
282. Проверить NO_MONEY on после полного restart; настройки Wallet, attach actions, перевод-карточка, link/deeplink и ton-connect route выключены.
283. Проверить, что сообщения о переводах остаются понятными, а чат не теряет текст/высоту/дату.
284. С FORCE_WALLET on из batch 26 подтвердить приоритет NO_MONEY on после restart.
285. Выключить NO_MONEY, перезапустить и проверить возвращение wallet/ton-connect stock behavior.
286. Проверить batch 23 local passcode и wallet passcode before/after NO_MONEY; не должно быть обхода подтверждения транзакции.
287. На двух account slots подтвердить независимость истории, balance, settings и card design.
288. Для 0290 проверить address details, import screen, short address, long address, copy raw address, RTL и крупный шрифт; off/on.
289. Для 0313 проверить balance combinations: none, previous wallet, earnings, both; restart fragment/rotate; off/on.
290. Для 0286 проверить transaction sheet copy URL, open URL и long-press history row; сравнить с `https://tonscan.org/transaction/<hash>`.
291. При history pending/error/empty hash проверить отсутствие explorer action; убедиться, что тап по обычному ряду работает как прежде.
292. Для 0296 открыть outgoing и incoming transfer message; тестировать доступную транзакцию, pending, history-not-loaded и Wallet off.
293. Проверить правильный `currentAccount` для одинаковых сообщений/tx in separate account slots.
294. В тестовом режиме проверить network logs: Tonscan не вызывается без explicit open, приложение не делает explorer fetch и не передаёт wallet data tele-server.
295. Проверить действие copy без network и содержимое clipboard; не попадать в clipboard seed/private key.
296. Для 0307 проверить default stock design off; включить gift design; выбрать принадлежащий collectible gift; повторно открыть Wallet — выбор persisted локально.
297. Проверить gift selection после удаления/недоступности gift, offline, asset missing и смены аккаунта: корректный stock fallback, crash-free.
298. Проверить 2D Canvas card на низкой производительности и 3D GLSurface на GPU; оба показывают тему, QR, balance, address, flecks и overlays.
299. Проверить GL context loss, background/foreground, orientation, fragment recreation и быстрое закрытие sheet при создании модели.
300. Проверить power saver, Android LiteMode и low performance: 2D/облегчённый режим без лишних непрерывных кадров.
301. Проверить contrast и читабельность balance/address/title на светлой/тёмной теме и для разных backdrop colors.
302. Проверить, что выбор подарка не изменяет wallet address, QR payload, transaction signing, balance и отправку TON.
303. Для 0317 drag collectible на карту, cancel, drop, move, remove, rotate, reopen; placement восстанавливается по normalized position.
304. Проверить gesture scroll history vs drag, RecyclerView recycling, быстрый tab switch и detach durante animation.
305. Проверить accessible actions add/remove sticker без drag; TalkBack labels не должны сообщать секретные данные.
306. Проверить 2D/3D placement transforms, hit testing, clipping края и исключение QR/button area.
307. Убедиться, что drag/remove не вызывает Stars purchase, gift transfer, TON payment, server mutation или wallet transaction.
308. Проверить no gift ownership, stale saved id, пустую коллекцию и большое число подарков без долгих блокировок UI.
309. Проверить случаи airplane mode/offline switch; локальные настройки дизайна доступны без tele-server.
310. При каждом патче протестировать default/off и on; если настройка требует рестарт — проверить оба направления с перезапуском.

## Features, PATCHLIST и batch gate

311. Для каждой user-facing фичи добавить строку `features.md` на английском, в секции настройки `Money`/`MODE_MONEY`.
312. Строка сообщает простыми словами, что делает опция, где найти, default, Android patch и исходный desktop номер.
313. Не добавлять planning details, тестовые секреты или технические anchors в user-facing `features.md`.
314. После экспорта обновить статусы каждой строки PATCHLIST по факту; `queued` — лишь exported patch, не означает tested.
315. Собрать debug APK командой из development guide после всех семи коммитов; собрать/проверить native Rust все ABI как часть зависимости batch 26.
316. Передать APK для ручного теста на emulator/device и список шагов; только human verification переводит пачку `done`.
317. `built` допустим после успешной сборки и передачи APK, а `done` — только после включённого и выключенного поведения, подтверждённого человеком.
318. Не утверждать работоспособность карты, explorer links или wallet safety только по сборке.
319. Ручной тестовый wallet — строго test wallet; зафиксировать testnet/mainnet окружение в build instructions и проверить, что actions не используют production funds.
320. Если сервер не поддерживает тестовый Wallet/transaction, тестировать UI/URL с тестовыми fixture только в unit/manual non-signing режиме; не создавать фиктивный success.
321. Release APK не собирать с тестовыми секретами/временными endpoint overrides.
322. Не менять endpoint policy скрытно между debug и release.

## Открытые вопросы и фиксированные ответы

323. Explorer endpoint: решено Tonscan.org для 0286 и 0296; не оставлять выбор на усмотрение реализации.
324. 2D или 3D card design: решено обе; 3D shader обязателен, 2D вариант также обязателен.
325. Отключение money при FORCE_WALLET: NO_MONEY имеет приоритет; restart-required.
326. Где хранить gift selection/placements: только локальная fork storage; точный формат решить при реализации с account scoping и versioning.
327. Покупки: не создавать новый purchase flow; использовать stock Stars/Wallet APIs и batch-23 action/password protections.
328. Rates/prices: отображать stock Wallet/Telegram rate; не вводить сторонний pricing endpoint или purchase price history в эту пачку.
329. Географические карты: 0138 остаётся отдельной настройкой provider; money-card не относится к map providers.
330. Third-party requests: Tonscan вызывается только внешним browser intent после действия пользователя; никаких background explorer запросов.
331. `0313` quick-hide menu и `0307` sync-with-emoji-status UI не описаны полностью в Android patchlist; подтвердить desktop scope при реализации и пометить [INFERENCE] места.
332. Search IDs 1420–1439 должны быть уникальными; окончательно распределить после проверки существующего `TeleSearch` API, не выдумывать экранные ID.
333. `WalletCardGLRenderer` lifecycle и существующие shader assets — изучить перед патчем, рендеринг/texture updates выполнять на GL thread.
334. Если текущая ветка уже содержит часть этих функций, переиспользовать stock, сократить патч без изменения acceptance criteria и обновить план примечанием.
335. Любое неизвестное поведение, связанное с реальными деньгами, приватными ключами или signing — эскалировать maintainer до изменения flow; не проверять догадку реальным платежом.

## Сводка готовности по строкам

336. 0288 готов, когда выключатель полностью блокирует wallet UI/routes и показывает безопасные сервисные переводы, сохраняя ключи и данные.
337. 0290 готов, когда alternating address groups согласованы, raw value остаётся неизменным, а off возвращает stock rendering.
338. 0313 готов, когда только дополнительные balances скрываются/возвращаются, а общий баланс не затронут.
339. 0286 готов, когда history actions дают корректный Tonscan URL только для валидной транзакции и не делают фонового network traffic.
340. 0296 готов, когда чат-меню открывает/копирует ровно URL найденной transaction, pending/unknown transaction не показывает action.
341. 0307 готов, когда одна выбранная collectible theme отображается на карте и transfer card через 2D и 3D, с безопасным fallback и сохранением stock interaction.
342. 0317 готов, когда пользователь может перетащить/снять принадлежащие ему stickers, state локально сохраняется, renderer и touch lifecycle безопасны.
343. Общая пачка готова только после всех коммитов/экспорта, tests, debug APK и человеческого emulator/device gate.
344. Главное правило безопасности: никакого реального платежа/покупки при тестах; не собирать и не логировать секреты; действие с деньгами остаётся под stock Wallet confirmation и batch 23.
