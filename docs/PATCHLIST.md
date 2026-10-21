# PATCHLIST

план переноса фич [tele](https://github.com/nitreojs/tele) (telegram desktop) на telegram android. основа — [docs/portability.md](portability.md): из 333 оценённых патчей tele 222 переносимы, 37 частично, 53 не переносимы, 17 уже в стоке android, 4 уже перенесены нашими патчами (127 исходных патчей v7.2.9 и 206 новых — 0125–0322 и lib_ui). здесь переносимые разбиты на **пачки** (batches): порядок реализации, зависимости и статусы. решения мейнтейнера по спорным патчам — [docs/decisions.md](decisions.md).

анализ исходных патчей: [nitreojs/tele](https://github.com/nitreojs/tele) v7.2.9, патчи 0001–0127. колонка «№» указывает патч tele по **текущей нумерации очереди десктопа** (`tele/patches/tdesktop/NNNN-*.patch`; очередь была перенумерована, старый → новый — [docs/desktop-numbers.md](desktop-numbers.md)); файлы в `patches/android/` нумеруются **по позиции в очереди** (`git format-patch`), соответствие наш→исходный — в таблицах ниже. номера в `` `NNNN-…` `` внутри примечаний — файлы `patches/android/`, голые номера — патчи десктопа.

## статусы

| статус | значит |
|---|---|
| `todo` | не начат |
| `wip` | в работе (есть коммит в дереве, не доведён) |
| `queued` | закоммичен в очереди и экспортирован в `patches/android/`, ждёт ворот своей пачки |
| `built` | пачка собрана, дебаг-apk передан на ручное тестирование |
| `done` | проверено вручную (тумблер on и off) |
| `skip` | не переносится или не нужен; причина в последней секции |

## пачки и ворота

порядок пачек = порядок сборки. пачка закрывается только через **ворота сборки**: все её патчи закоммичены и экспортированы → `./gradlew :TMessagesProj_App:assembleDebug` → apk передан на ручное тестирование → человеческая верификация → статусы `done`. правило подробнее: [AGENTS.md](../AGENTS.md), [docs/development.md](development.md#the-batch-gate).
Гайды исполнителей: [11 — база приватности](batches/batch-11.md) · [12 — follow-up и быстрые тумблеры](batches/batch-12.md) · [13](batches/batch-13.md) · [14](batches/batch-14.md) · [15](batches/batch-15.md) · [16](batches/batch-16.md) · [17](batches/batch-17.md) · [18](batches/batch-18.md) · [19](batches/batch-19.md) · [20](batches/batch-20.md) · [21](batches/batch-21.md) · [22](batches/batch-22.md) · [23](batches/batch-23.md) · [24](batches/batch-24.md) · [25](batches/batch-25.md) · [26](batches/batch-26.md) · [27](batches/batch-27.md) · [28](batches/batch-28.md) · [29](batches/batch-29.md) · [30](batches/batch-30.md)

инфраструктурные патчи (без номера tele) помечены `infra` и реализуют сразу пачку настроек tele: `0002`, `0015`, `0059`, `0063`, `0077` (редактор), `0106`, `0110`, `0113`, `0116`, `0120`.

---

## пачка 0 — фундамент: инфраструктура, брендинг, сборка

всё, без чего не работает ничего: конфиг, секция настроек, брендинг, номер сборки. ворота пачки 0 — первая сборка дебаг-релиза всего проекта.

| № | патч | статус | примечание |
|---|---|---|---|
| misc | свои api-креденциалы (`TELE_API_ID`/`TELE_API_HASH` из local.properties) | done | `0001-misc-support-custom-api-credentials` |
| infra | kotlin-плагин + скелет `tele/` (TeleConfig, TeleHooks, db) | done | `0002-misc-enable-kotlin-and-add-the-tele-skeleton` |
| infra | секция настроек «tele» (страница, строка в главных настройках, deeplinks позже) | done | `0003-feat-add-the-tele-settings-section` |
| 0007, 0089 | переименовать приложение в tele + иконка | done | `0004-misc-call-the-app-tele`; оба debug-оверлея манифеста. иконки — `0039-...`, `0043-...` и финально `0046-feat-apply-the-generated-icon-set`: актив из `android_icons/` (генерился студийным тулом) — лаунчер + round + foreground + monochrome-слой + градиентный фон, иконка уведомлений `tele_stat_notification` (4 места `setSmallIcon`), иконка секции tele — белый пузырь на `IconBackgroundColors.BLUE` (уменьшена до 17dp). строки корня tele-настроек — на `TextCell` с линейными `msg2_*`-иконками, как на внутренних экранах настроек. package rename — позже |
| misc | свои имена пакетов (release `.tele`, debug `.tele.dev`) | done | `0006-misc-use-fork-package-names`; release-сборка — пакет `org.telegram.messenger.tele`, debug — `org.telegram.messenger.tele.dev`; не конфликтует с Telegram/Beta на устройстве |
| misc | отключение google-services (чужой firebase) | done | `0007-misc-disable-google-services-integration`; fcm-push не работает до своей конфигурации |
| 0001, 0047 | номер сборки tele в шапке списка чатов и рядом с версией в настройках | done | `0005-feat-show-the-tele-build-number`; `TELE_BUILD` из local.properties, 0 = dev |

## пачка 1 — быстрые тумблеры интерфейса

маленькие независимые фичи: каждая — один-два хука. назначение пачки — обкатать очередь и ворота сборки.

| № | патч | статус | примечание |
|---|---|---|---|
| 0017 | секунды во времени сообщений (+ время в сервисных сообщениях) | done | `0008-feat-show-seconds-in-message-times`; хук `formatterDay` в `LocaleController` |
| 0030 | скрыть папку «Все чаты» | done | `0009-debloat-hide-the-all-chats-folder`; гейт в `getDialogFilters()` |
| 0021, 0062 | скрыть кнопки звонков + подтверждение перед звонком | done | `0010-debloat-hide-call-buttons` (гейт по `phone_calls_available` в ChatActivity+ProfileActivity), `0011-feat-confirm-calls-before-starting` (VoIPHelper) |
| 0025 | открывать ссылки без подтверждения | done | `0012-feat-open-links-without-confirmation`; условие в `showOpenUrlAlert` |
| 0075 | имена вместо номеров в шапке чата | done | `0013-feat-show-names-instead-of-phone-numbers-in-chat-hea` |
| 0011 | поднять лимит аккаунтов (4→8) | done | `0014-feat-remove-the-account-limit`; always on |
| 0053 | спойлеры раскрыты всегда | done | `0015-feat-reveal-spoilers-automatically`; текст+медиа в `MessageObject` |
| 0072, 0122 | скрыть кнопки упоминаний/реакций и их бейджи в списке | done | `0016-debloat-hide-mention-and-reaction-badges`; гейт на `mentionString`/`drawMention` в `DialogCell` |
| 0038 | статичные видео-аватары | done | `0017-feat-turn-off-animated-userpics`; гейт в `ImageReceiver` + ветка видео в `ProfileActivity`; проверено только отсутствие анимации у статичных аватаров — аккаунта с видео-аватаром нет |
| 0098 | не применять счётчики replies к отложенным | done | `0018-fix-ignore-reply-counters-on-scheduled-messages`; always on |
| infra | применение тумблеров без перезапуска | done | `0019-fix-apply-interface-toggles-without-restart`; `TeleHooks.onConfigChanged`: пересоздание форматтеров + оповещение UI |
| 0001 | надпись сборки tele в шапке списка чатов при наличии истории | done | `0020-fix-show-the-tele-build-label-in-the-chats-header`; вордмарк `telegram_logo_2` — вектор, строками не меняется; заголовок берётся из `TeleHooks.storiesHeaderTitle`. фикс регресса: emoji-статус рядом с заголовком гасился (альфа статуса была привязана к логотипу, который в текстовом режиме скрыт) — теперь статус виден и позиционируется за текстом заголовка |

## пачка 2 — приватность

| № | патч | статус | примечание |
|---|---|---|---|
| 0003 | скрыть сторис везде | done | `0021-feat-add-privacy-toggles-for-stories-ghost-mode-scre`; гейт в `StoriesController.hasStories()` (обе перегрузки) + репост в сторис |
| 0004 | смотреть сторис незаметно | done | тот же патч; подавлен `TL_stories_readStories` в `markStoryAsRead`, живые сторис блокируются в `StoryViewer.open` |
| 0032, 0064 | ghost mode + расширенные опции | done | online/typing/read; contents-read глушится на сетевом слое — `0023-fix-hide-viewed-receipts-at-the-network-layer` (4 точки `readMessageContents`). **не сделано:** offline-after-send, schedule-трюк |
| 0026 | исчезающие медиа без сжигания (+ «mark as viewed») | done | `0022-...` (гейт) + `0024-feat-add-mark-as-viewed-action-for-disappearing-medi`; пункт «mark as viewed» в меню сообщения через `TeleHooks.forceMarkViewed`. ttl-фото открываются не в `PhotoViewer`, а в `SecretMediaViewer`; сжигание идёт через `ChatActivity.sendSecretMessageRead` → `markMessageAsRead2` → `createTaskForMid` + `readMessageContents` — гейт стоит там (`sendSecretMessageRead`/`sendSecretMediaDelete`). **не покрывается:** view-once в стиле extended-media-preview — сервер сжигает их при загрузке `getExtendedMedia`, подавлять нечем |
| 0027 | скриншоты исчезающих медиа | done | тот же патч; `FLAG_SECURE` снимается в `PhotoViewer` (per-open) и в `SecretMediaViewer` (per-open, до `addView`) при `ttl_seconds != 0`; условие — `TeleHooks.isDisappearing` (любая media с `ttl_seconds != 0`, не только документы) |
| 0111 | никогда не блокировать скриншоты | done | гейты в `PhotoViewer`, `SecretMediaViewer` (перенесён из конструктора в `openMedia` — иначе тумблер замораживается на первом открытии), `SecretVoicePlayer`, `StoryViewer.allowScreenshots` + choke в `FlagSecureReason.updateWindowSecure` (12.x ведёт FLAG_SECURE «по причинам»: секретные чаты, noforwards, voice-once в чате, экран пароля) |
| 0094 | черновики только на устройстве | done | тот же патч; гейт `TL_messages_saveDraft` в `MediaDataController` |

игнор-лист (0016, 0073) и остаток ghost-режима (0032/0064: per-chat ghost, ghost-schedule, offline-after-send) перенесены в пачку 12 («база приватности») — сначала они, потом всё, что на них опирается.

**отложенный баг (разбор после):** после холодного старта на аккаунте с активными историями строка историй не показывается (шапка падает в режим «без историй»: заголовок сборки + emoji-статус от actionBar). Данные в базе есть; `updateStoriesVisibility` «залипает» в скрытом состоянии после старта — цикл любого тумблера (постит `storiesUpdated`) возвращает строку. Воспроизводится холодным перезапуском. Не связано с правками заголовка 0020 — на предыдущем билде пачки 2 старт в это же состояние не попадал (возможно, гонка старта, требуется разбор).

## пачка 3 — профиль и ID

| № | патч | статус | примечание |
|---|---|---|---|
| 0014, 0046, 0096, 0023 | id пира и DC в профиле (варианты формата, одна строка) | done | `0025-feat-show-the-peer-id-and-data-center-in-the-profile`; хелпер `tele/helpers/PeerId.kt` (bot api: чат −id, канал/супергрупп −100…; dc из `photo.dc_id` → `photo_small/big.dc_id`, свой профиль — `getCurrentDatacenterId()`; города: 1,3 Miami; 2,4 Amsterdam; 5 Singapore); строки в `ProfileActivity` после username (юзер, чат) и bio (карточка юзера), у чатов — вне блока about/public, чтобы показывались всем; клик — меню копирования. строки форка в `strings_tele.xml` включены в генерацию локали (`TelegramBuildAppPlugin.kt`, `stringsXml`) — иначе `LocaleController.getString` даёт `LOC_ERR:null`. 0046 впитан: тумблеры сразу в настройках tele |
| 0029 | id сообщения в меню сообщения | done | `0026-feat-show-the-message-id-in-the-message-menu`; пункт «ID: N» первым в меню сообщения через `fillMessageMenu` (option 118), копирует bare id |
| 0055 | копировать id кастомного эмодзи | done | `0028-...`; long-press на эмодзи → пункт «copy emoji ID» первым в меню; hit-test — `ChatMessageCell.tele_emojiIdAt` (текст + подпись), id живёт в `ChatActivity.tele_pressedEmojiId`/`tele_menuEmojiId` |
| 0078 | локальные имена людей | done | `0029-...`; хранилище — `tele_kv` ключ `local_names` (JSON), `tele/helpers/LocalNames.kt`; подмена в `UserObject.getUserName/getFirstName`; пункт «set a name for me» в меню профиля («…»); тумблер `local_names` |
| 0071 | username-алиасы | done | `0030-feat-link-your-own-usernames-to-chats-locally`; `tele/helpers/Aliases.kt` (`tele_kv`, ключ на аккаунт: алиас → dialogId); пункт «set an alias for me» в меню профиля рядом с локальным именем; резолв — перехват в `LaunchActivity.runLinkRequest`: `@алиас` открывает чат напрямую. автодополнение — `MentionsAdapter.showUsersResult` (алиасы первыми в результатах; `0033` — при полностью введённом алиасе подсказка не пропадает); подмена при отправке — `MediaDataController.getEntities` (`Aliases.mentionFor`): текст алиаса **не уходит на сервер** — при наличии публичного username подставляется `@username` + `TL_messageEntityMention`, без него — реальное имя (из `first_name`/`last_name`, не локальное) + `inputMessageEntityMentionName` с `InputUser`; чат — `@username`; строка `alias` в профиле; пункт «open the real @X» в контекстном меню тега (`ChatActivity.didLongPressUsername`); тап по `@алиас` открывает чат; инлайн-боты — `MentionsAdapter.searchForContextBot`: алиас резолвится в бота и уходит в inline-запрос.; с 0079 подмена не трогает алиас внутри code/pre/ссылок и частично отформатированный (как `ReplaceableMention` в tdesktop) и сдвигает остальные entities на разницу длин — раньше форматирование после алиаса съезжало |
| 0013, 0065 | id подарков (обычных и коллекционных) | done | `0027-...`; строка «Gift ID» в `StarGiftSheet` после `tableView.clear()` (3 пути: уникальный — `gift_id`, сохранённый — `savedStarGift.gift.id`, из сообщения — `stargift.id`); `tele/helpers/Gifts.kt`; тумблеры `show_gift_ids`/`show_regular_gift_ids` |

## пачка 4 — меню сообщения и боты

| № | патч | статус | примечание |
|---|---|---|---|
| 0057, 0054, 0090 | настраиваемое меню сообщения (порядок/скрытие) | done | `0047-feat-hide-message-menu-items`; скрытие готово: `tele/helpers/MessageMenu.kt` — реестр код→имя, хранение скрытых кодов в `tele_kv`, фильтр в конце `fillMessageMenu` (все три вызова), редактор `tele/ui/settings/TeleMenuActivity.kt` из tele > interface > editor. **порядок (0054) готов** — `0057-feat-reorder-message-menu-items`: сохранённый порядок кодов применяется стабильной сортировкой в том же фильтре (коды вне списка — после, в стоковом порядке), в редакторе строки тянутся долгим тапом (ItemTouchHelper), каждое перемещение персистится. **видимая ручка (0057)** — stock `list_reorder` слева от каждой строки, касание ручки запускает drag; фикс открытия редактора: `HeaderCell`/`TextInfoPrivacyCell` больше не ошибочно unwrap-ятся как drag-wrapper. **порядок и ручка не проверены на девайсе** |
| 0028, 0005 | пейлоады кнопок ботов: поповер при зажатии + копирование | done | `0042-feat-show-bot-button-payloads-on-long-press`; зажатие callback/switch-inline/webview-кнопки открывает диалог с пейлоадом и Copy (непечатаемые байты — hex). слот — существующий `ChatActivity.didLongPressBotButton`, где url/copy уже обрабатывались, а остальные типы молчали; тумблер `bot_button_payloads` (интерфейс, по умолчанию вкл) — `0045` |
| 0033 | view as TL (schema.jppgr.am) | done | `0059-feat-view-messages-and-peers-as-tl`: default-off тумблер `view_as_tl`, свежий `messages.getMessages`/`channels.getMessages` для меню сообщений и full-запросы user/group/channel из профиля; бинарная TL-сериализация → URL-safe Base64/raw-deflate → schema.jppgr.am, длинные ссылки открываются через временный FileProvider redirect. **не подключены:** story/topic/sticker/gift/folder контекстные меню; ручное открытие ссылки не проверено |
| 0092 | кликабельные кастом-эмодзи в эмодзи-only сообщениях | n/a | на Android путь уже есть: `checkTextBlockMotionEvent` принимает `TYPE_EMOJIS`, тап по спану вызывает `didPressAnimatedEmoji` → `EmojiPacksAlert` с превью; десктопу патч был нужен потому, что там эмодзи-only рендерится как unwrapped media без ссылок. проверить тапом по большому кастом-эмодзи |
| 0102 | seen/reacted счётчики раздельно | n/a | на Android уже раздельно: `MessageSeenView` строится из `TL_messages_getMessageReadParticipants` (только прочтения), реакции идут через пилл (`ReactedUsersListView`) — смешения, которое чинит десктопный патч, нет |
| 0103 | отправить inline-запрос как текст | n/a | на Android кнопка отправки уже шлёт текст поля (`processSendingText`), панель инлайна — отдельный тап по результату; десктопный пункт нужен был потому, что Enter отправлял подсвеченный результат |
| 0066 | инлайн-результаты без via | done | `0041-feat-send-inline-results-without-via`; тумблер `inline_no_via` (секция privacy + поиск): `via_bot_id` не ставится ни при отправке (`params.containsKey("bot")`), ни в ретрае (ветка `replyMarkup`), локальная отрисовка честная. **не проверено на девайсе**; игры/webview-результаты могут требовать via — поэтому тумблер по умолчанию выключен |
| 0101 | поиск по алиасам | done | `0031-feat-search-chats-and-mentions-by-alias`; зависит от 0071. поиск чатов — `DialogsSearchAdapter.searchDialogsInternal` после `MessagesStorage.localSearch`: диалоги, чей алиас содержит запрос, добавляются в выдачу, в ячейке видно `Имя @алиас`; `@` в строке ввода — `MentionsAdapter.showUsersResult` больше не требует непустой серверной выдачи, алиасы подставляются всегда. Серверные алиасы в поиске чатов — `0084-feat-find-chats-by-server-aliases` (пачка 8) |
| 0103 | управление локальными именами и алиасами | done | `0035-feat-manage-local-names-and-aliases-from-tele-settin`; зависит от 0071/0029. `tele/ui/settings/TeleNamesActivity.kt` — два экрана из настроек tele («your data»): список «Имя → значение», тап открывает диалог редактирования с кнопкой Delete, долгий тап открывает профиль (`0036` — индекс строки сдвинут на заголовок). Диалоги алиаса и локального имени — один общий в `TeleHooks`: `ChatActivity` и `ProfileActivity` больше не держат свои копии (`0037`), поэтому подпись, линия, отступы и Delete одинаковые везде; тема чата прокидывается через `getResourceProvider()` плейсхолдеры диалогов приглушены, `@` в поле алиаса — приглушённый префикс (`0034`) |
| 0121 | алиасы для inline-ботов | done | покрыто 0030: `MentionsAdapter.teleAliasRealUsername` резолвит алиас в бота до инлайн-запроса (`searchForContextBot`); подтверждено пользователем (memeindexerbot/zaza); серверные алиасы (`@calc` → `@calcmulabot`) — 0079, проверено на эмуляторе |

## пачка 5 — ссылки

| № | патч | статус | примечание |
|---|---|---|---|
| 0052 | чистка трекинг-параметров | done | `0050-feat-clean-tracking-parameters-from-links`; `tele/helpers/Tracking.kt` — полная таблица правил из tele (глобальная + провайдеры, amazon /ref= в путях, t.me не трогаем). два тумблера в privacy: `clean_opened_links` (хук в `openClickableLink`, одна точка для всех ссылок сообщений) и `clean_sent_links` (в `getEntities` после алиасов, офсеты энтити пересчитываются). **не проверено на девайсе** |
| 0077 | перезапись вставляемых ссылок по правилам + редактор | done | `0051-feat-rewrite-pasted-links-by-rules` + `0052-feat-edit-link-rewrite-rules`; `tele/helpers/LinkRewrites.kt` — правила двух типов: домены (from→to, сохраняя www/m/mobile, несколько to выбираются стабильно по url) и regex-паттерн (find → replace с `$1..$9`, `$$` литерально). хук — перехват `android.R.id.paste` в `EditTextCaption`: перезаписанный текст вставляется в курсор, подписанный тост перечисляет замены; если правила ничего не изменили — стоковая вставка. тумблер `rewrite_pasted_links` (links-группа privacy, off) + редактор `TeleRulesActivity` (добавить/редактировать/удалить, поля с темой текущего диалога, поиск настроек). `0053-fix-rewrite-pasted-links-before-the-rich-paste-hook`: у поля ввода своя вставка — `handleRichHtmlPaste` перехватывает клипы с text/html до `EditTextCaption`, переписывание вынесено в `teleRewritePaste()` и вызывается раньше; вставка из клавиатуры (Gboard коммитит через `InputConnection.commitText`, минуя paste-механизмы) — `0054-fix-rewrite-links-pasted-from-the-keyboard`: `EditTextCaption` оборачивает InputConnection. `0060-feat-add-link-rewrite-presets`: шесть tele presets, enabled-флаг, нормализация доменов и стабильный выбор target по URL; desktop-совместимые поля читаются с миграцией. проверено на эмуляторе: страница правил, themed-поля и чекбоксы открываются и читаемы`
| 0086 | `@username` → t.me в окне создания ссылки | done | `0049-feat-turn-username-into-a-t.me-link-in-the-link-box`; `EditTextCaption.showInputDialog` OK → `LinkRewrites.usernameToLink` (regex как в tele: `^@([a-zA-Z][a-zA-Z0-9_]{3,31})$`), always on |
| 0085 | контроль превью ссылок (частично) | done | `0055-feat-disable-link-previews`; тумблер `no_link_previews` (links-группа privacy): гейт в `isMessageWebPageSearchEnabled` — единственная точка, где и запускается поиск превью по тексту, и флаг уходит в черновики (превью не вылезает и при отправке из черновика). ручное добавление превью (`setWebPage` напрямую) работает. `0056-fix-send-with-no_webpage-when-previews-are-disabled`: сток сбрасывает поле `messageWebPageSearch` в true на больших изменениях текста, а send читает поле напрямую — без этого фикса сообщение уходило без `no_webpage` и сервер вешал превью сам. **открыто:** — (0085 закрыт). `0061-feat-skip-link-previews-for-pasted-links`: выбор режима `automatic link previews`, provenance вставки через `EditTextCaption.teleNotifyPastedUrl` (обычная вставка, rich HTML, IME commitText), гейт только на автоматический поиск — явный выбор preview в `MessagePreviewView` не блокируется; при подавлении уходит `searchLinks=false` → `no_webpage`. `0062-feat-add-manual-link-previews`: режим `only the ones you add` + пункт `Add a link preview` в меню выделения поля ввода (URL резолвится существующим `searchLinks`, автопоиск глушится до очистки поля). **не проверено на девайсе** |
| 0024 | скрыть спонсорские сообщения | done | `0048-feat-hide-sponsored-messages-and-the-proxy-sponsor-c`; тумблер `hide_sponsored`: `getSponsoredMessages` возвращает null — чаты и боты не запрашивают и не рендерят рекламу. **не проверено на девайсе** |
| 0034 | скрыть спонсорский канал MTProxy | done | тот же патч, тумблер `hide_proxy_sponsor`: proxy-ответ `help.promoData` обнуляет `did` и ставит `noDialog` — стоковый путь сам убирает существующий диалог. PSA не тронуты. **не проверено на девайсе** |

## пачка 6 — отправка

| № | патч | статус | примечание |
|---|---|---|---|
| 0050, 0118, 0119 | очередь текста за загружающимся медиа (+ ответы мимо очереди, форс-отправка) | done | `0066-feat-queue-text-behind-uploading-media`; тумблеры в sending: `queue_behind_media`, `send_older_replies`, `double_enter_send`. Исправлено после device-теста: delayed upload с уже установленным `sendRequest` больше не исключается; сравнение учитывает отрицательные local IDs (раннее сообщение = больший ID), upload groups и активные sending-media до server ack; flush теперь после финального media RPC success/failure; cancel вызывает `markCancelled` + targeted flush после очистки send/upload state. Вторая причина невыхода из очереди найдена и исправлена: held-текст не регистрируется в `sendingMessages` (это происходит только внутри `performSendMessageRequest`), поэтому existence-check в flush молча выбрасывал held-записи — заменён на явный `cancelled`-флаг; safety recheck повторяется раз в 2с только пока held очередь не опустела |
| 0095 | отложенные отправляются вовремя | done | `0064-feat-send-scheduled-messages-on-time`; тумблер `punctual_scheduled` (секция sending): локальный таймер `tele/helpers/PunctualScheduled.kt` каждые 20с — из `scheduled_messages_v2` берутся server-scheduled (mid>0, не секретные) с `date <= now` и отправляются штатным `TL_messages_sendScheduledMessages` (тот же запрос, что «send now»); работает пока приложение живо и онлайн, при офлайне сервер отсылает сам (может опоздать). старт — `ApplicationLoader` после `checkUnsentMessages` |
| 0100 | фото в HD по умолчанию | done | `0063-feat-send-photos-in-HD-by-default`; тумблер `hd_photos` (секция sending): один гейт в `MediaController.MediaEditState.isHighQuality()` — при отсутствии per-photo выбора (`highQuality == null`) дефолт HD, покрывает все UI-пути (PhotoViewer, attach-панель, редактор); стоковый пер-photo HD-тоггл и запоминание `photoHighQualityDefault` работают как раньше |
| 0093 | gif как видео и видео как gif | частично n/a | «видео как gif» уже в стоке: mute в PhotoViewer (`videoEditedInfo.muted`) → сток добавляет `TL_documentAttributeAnimated` (`SendMessagesHelper` 11213+) — видео уходит гифкой; «gif как видео» требует транскода gif→mp4 (на desktop `Media::Encode`, на android нет готового пути — длительность gif неоткуда взять), отложено до отдельной проработки |
| 0069 | реплай на удалённое: скип или цитата | done | `0071-feat-skip-or-quote-deleted-messages-when-replying`, follow-up `0072-fix-saved-drafts-and-deleted-replies.patch`; выбор в your data: `reply to deleted messages` — `skip them` (по умолчанию) или `quote them`. В 0072: Reply скрыт в меню и режиме выделения, Forward заблокирован в выделении и action guard (удалённое сообщение отсутствует на сервере); после удаления удержанного выделение сбрасывается, пузырь перерисовывается через forceUpdate. Сборка debug успешна; **ручная проверка на устройстве ожидается** |
| 0008 | quick replies в группах и каналах | done | `0065-feat-offer-quick-replies-in-groups`: тумблер `quick_replies_in_groups`; `/` autocomplete показывает Business quick replies в разрешённых группах. Исправлено после device-теста: shortcut content fetch-ится через `messages.getQuickReplyMessages`; IDs больше не уходят в обычный `messages.forwardMessages` (который трактовал shortcut IDs как IDs history и давал чужой текст/стикер). Каждый item отправляется как fresh text/photo/document через `SendMessageParams`, поэтому retry использует send/upload путь; отсутствующий локальный файл у серверного document не считается причиной отказаться от remote media reference. Private-chat replay не менялся |
| 0114 | пересылка защищённых как копий | done | `0067-feat-forward-protected-messages-as-copies`; перехват в `SendMessagesHelper.sendMessage(ArrayList<MessageObject>, …)` — единой точке форвардов: защищённые (noforwards у сообщения или пира) отправляются свежими копиями. Текст сохраняет entities и web preview; фото и документы сначала скачиваются при отсутствии локального файла, затем загружаются как новые media (не remote reference, который сервер отклоняет с `CHAT_FORWARDS_RESTRICTED`); GIF/video явно принудительно идут через upload; sticker/voice/round используют штатную document-ветку. Опросы клонируются с новым id (correct-флаги квизов не переносятся), контакты и статичные локации/venue копируются из полей media. Paid media, игры, сторис, опросы с медиа, неотвеченные квизы и live locations не копируются — показывается причина. Гейты forward-меню и selection в ChatActivity/PhotoViewer через `ProtectedMessages.allowsForward`/`peerNoForwards`; копии не очищают draft целевого чата. Текст/фото/стикеры подтверждены пользователем; GIF/video ещё требуют ручной проверки после принудительного upload fix.

## пачка 7 — локальное хранение истории

| № | патч | статус | примечание |
|---|---|---|---|
| 0019, 0058 | хранить удалённые сообщения (в т.ч. самоудалённые) | done | `0068-feat-keep-deleted-messages`; тумблеры в your data: `keep_deleted_messages` (все удаления — свои, чужие, серверные) и `keep_messages_you delete yourself` (только исходящие при ручном удалении), пометка — `mark deleted messages with`: fading, текст «deleted» у времени или иконка корзины. Как в десктопе: удалённое остаётся в чате помеченным (строка не удаляется из messages_v2), повторное удаление убирает локально; гейт в `ChatActivity` (messagesDeleted, 8-й аргумент userInitiated), реестр in-chat — ленивая копия tele.db; снятие копий в `MessagesStorage.markMessagesAsDeletedInternal` (все пути) + канал-очистка; секретные/service/disappearing не удерживаются. Экран «Deleted messages»: список чатов → сообщения чата полными пузырями (ChatMessageCell — прямые дети списка, setParentViewSize в dispatchDraw, срезы градиента синхронны отрисовке). Проверено вручную: keep/self-keep, пометки fading/text/icon, повторное удаление, экран и очистка. Выделение снимается и когда сохраняются все удаляемые сообщения: гейт вызывает `updateVisibleRows`, стоковый вызов в `processDeletedMessages` срабатывает только при реальном удалении (проверено на эмуляторе). off = сток |
| 0018, 0061 | история правок сообщения (+ просмотр как чат) | done | `0069-feat-keep-the-edit-history-of-messages`; тумблер `edit_history` (your data). Снятие версий в `MessagesStorage.putMessages` (load_type == -2): состояние из БД до перезаписи (original, если первая правка) и новое после восстановления attachPath/params; дедуп по SHA-256 (`tele_message_edits`, tele.db v4), порядок по edit_date. Просмотр — «Edit history» в меню сообщения: в стиле чата — прозрачный appbar поверх обоев (setAddToContainer(false), в root после списка), SizeNotifierFrameLayout + обои, версии полными ячейками (ChatMessageCell — прямые дети списка, setParentViewSize в dispatchDraw), stackFromEnd, подписи версий и даты по центру. Проверено вручную: фазы градиента, аппбар, bottom-anchored. Правки до включения тумблера не собираются; версии переживают удаление сообщения |
| 0099 | сохранённые черновики (частично: без rich-IV) | done | `0070-feat-save-drafts-for-later`, follow-up `0072-fix-saved-drafts-and-deleted-replies.patch`; снимок поля ввода — текст с entities, ответ, превью ссылки и файлы. 0072: Save as draft из long-press фото-пикера; восстановление reply после инициализации view; latest draft — кнопкой боковой панели (тап — вставить, долгое нажатие — браузер); вставленные файлы открываются в пикере с выбранными файлами и текстом; отправка через пикер делает текстом подписи caption, очередь остаётся fallback-путём. Проверено вручную |

## пачка 8 — tele server

сервер tele: клиент только скачивает публичный список и матчит локально; аккаунтные данные не отправляются никогда.

| № | патч | статус | примечание |
|---|---|---|---|
| 0009 | метки с tele-сервера (verified/scam/fake/support) | done | https-фетч + Argon2-ключ (`tele/helpers/TeleBadges.kt`); применение флагов к `TLRPC.User`/chat (`TeleBadges.applyUser/applyChat`), hook `putUser/putChat` ставит флаги новым объектам. Флаги живут только в памяти (`0078-fix-keep-badges-in-memory`): исходные значения запоминаются на объект, в `cache4.db` пишутся копии со стоковыми флагами (`MessagesStorage.putUsersInternal/putChatsInternal`), clear и выпадение пира из фида возвращают сток, пустой URL выключает метки сразу. Argon2 не считается на UI-потоке (`0080-fix-hash-badges-in-background`): поиск пира кэшируется на фид, промахи из `putUser`/биндов досчитываются в фоновой очереди, затем помечается актуальный объект и обновляется UI (раньше загрузка нового аккаунта блокировала UI ~40 с и давала ANR). Строки БД, испорченные до 0078, чинятся при следующем свежем объекте от Telegram. `0081-feat-keep-tele-server-data-fresh` — фид как в десктопе: `tele_badges.json` хранит url + etag + фид и грузится при старте (только для того же url); обновление через 10 с после старта и каждые 10 мин, `If-None-Match` (etag = sha256 тела) → 304, лимит 4 МиБ, UA `tele/<версия>-tele.<сборка>`; разбор строгий (битые запись, ключ или параметры argon2 отклоняют весь фид; `icon` только цифрами, `supportText` ≤ 64 символов); метки tele только добавляются к флагам Telegram (раньше `checkmark: false` в фиде снимал настоящую галочку); применяется ко всем активным аккаунтам; ключи argon2 переживают обновления фида с теми же параметрами. Настройки server: url проверяется (https, http только для localhost; без query/fragment/userinfo), кнопка reset, refresh/clear показывают результат (`server data updated`, `server data is up to date`, `couldn't refresh the server data: …`, `the tele server url is invalid`), clear сразу перекачивает фид; пункты server — в поиске настроек. Проверено на эмуляторе: кэш в новом формате, 304 → up to date, clear → updated, невалидный url отклонён без сохранения, пустой url → сток и кэш удалён. Проверено вручную |
| 0012 | бейджи верификации везде | done | базовые `verified/scam/fake/support` применяются из сервера и рисуются стандартными значками; custom icon — в профиле слева от имени (0076/0077), в списках `DialogCell` и заголовке чата (0077). `0083-feat-show-tele-badges-in-bubbles-and-settings`: тумблер `bubble_badges` («badges next to names in messages», interface, выкл. по умолчанию) — у имён отправителей в пузырях иконка сервера в слоте bot verification и галочка после имени (`ChatMessageCell`; ключ бейджей в `isUserDataChanged` перестраивает ячейку, когда поиск дорешался в фоне); шапка Settings — иконка и галочка сервера у своего имени, строки аккаунтов — иконка сервера (`tele/ui/TeleNameBadges.kt`). Личный канал в профиле — `DialogCell`, покрыт 0077. Проверено на эмуляторе: шапка Settings (иконка + галочка, off — сток); бейджи в пузырях не проверены — на тестовом аккаунте нет группы с авторами из фида. Проверено вручную |
| 0012 | кастомные бейджи везде | done | `0077-feat-show-tele-custom-badges-everywhere`: продолжение 0012/0076 — кастомная иконка сервера рисуется слева от имени в профиле (left drawable, как сток bot verification), в `DialogCell` (списки чатов, пользователи и каналы) и в значке аватара заголовка `ChatActivity`. Галочка и кастомная иконка независимы, как сток verified + bot verification. Эмодзи-статус/premium справа — сток-слоты. `TeleBadges`: кэш `iconDocumentId` включая отрицательные результаты (без argon2 на повторных биндах), обновления фида шлют `UPDATE_MASK_CHAT \| UPDATE_MASK_NAME \| UPDATE_MASK_STATUS` — профиль ребайндится после загрузки бейджей. Анимация: штатный механизм `SwapAnimatedEmojiDrawable`; на слабых устройствах/эмуляторах без Premium LiteMode (PRESET_LOW) отключает анимацию ВСЕХ кастом-эмодзи — сток-поведение, не регрессия. Проверено на эмуляторе: on — иконка + галочка в профиле и шапке чата, off — сток. Проверено вручную |
| 0081 | очистка кэша бейджей + тултипы верификации | done | кнопка clear cached data в настройках server (0073, с 0081 сразу перекачивает фид и показывает результат). `0082-feat-explain-tele-badges-in-profiles`: тап по иконке сервера в профиле показывает тултип с `description` (`HintView2` над бейджем, следует за анимацией шапки; `tele/ui/LeftDrawableTap.kt` ловит тап по left drawable без правки `SimpleTextView`); `description` с иконкой заменяет строку bot verification внизу профиля, как `OverrideVerifyDetails` в десктопе; `supportText` вместо «support» в профиле, шапке чата и строках поиска/контактов. Проверено на эмуляторе: тултип «приван» у tangenx, строка описания с иконкой, «official tele bot» в шапке чата tele Bot. Проверено вручную |
| 0091 | юзернеймы с tele-сервера | done | `0079-feat-show-tele-server-usernames`; `tele/helpers/TeleUsernames.kt`: алиасы из секции `usernames` фида вставляются в строку юзернеймов профиля (юзеры и каналы) по `position`, как `WithServerUsernames` в tdesktop (0 — первым, без позиции — в конец); только отображение, объекты пира не мутируются. `@алиас` резолвится в реальный username (`UserNameResolver.resolve`, `MessagesController.openByUserName`); локальные алиасы 0071 приоритетнее; тумблер `server_usernames` («usernames from the server», вкл. по умолчанию). @-подсказки: алиас предлагает своего владельца (`Aliases.mentionPeers` в `MentionsAdapter.showUsersResult`, без дублей с обычной выдачей); при отправке `@алиас` становится `@username` + `TL_messageEntityMention` (`Aliases.replaceForSend`, локальные алиасы раньше серверных); inline-боты по серверному алиасу (0121). Серверные алиасы в поиске чатов (часть tdesktop 0101) — `0084-feat-find-chats-by-server-aliases`: алиасы, начинающиеся с запроса (точные первыми), добавляются к локальной выдаче; если ровно один целевой username не загружен, он резолвится и поиск перезапускается. Мёртвый `applyUsernames` из 0074 удалён. Проверено на эмуляторе: профиль — `@ubah` + also `@tngnx…`; `tg://resolve?domain=ubah` открывает tangenx; `@ub` подсказывает tangenx; ``@tele `@ubah` @ubah`` уходит как `@teleAppUpdates @ubah @tngnx` с code-entity на `@ubah` (offset 16); `@calc 2+2` → ответ calcmulabot; поиск `ubah` → tangenx, `telebot` → tele Bot; off — сток. Проверено вручную |
| 0108 | бейджи tele на личном канале в профиле | done | depends on 0009; `applyChat` ставит verified/scam/fake для каналов и супергрупп, включая личный канал, при reload |
| 0037 | краш-репорты на tele server | done | `TeleCrash` пишет репорт только при включённом сервере, как `CollectCrashReports` в десктопе (версия, versionCode, сборка tele, устройство); multipart `Android`/versionCode на `/v1/crash.php`, ручная отправка из настроек. `0085-feat-offer-to-send-crash-reports-on-start`: при следующем запуске диалог «tele crashed» (send / don't send), отправка показывает результат тостом. Проверено на эмуляторе: диалог по подложенному репорту, don't send удаляет файл. Проверено вручную |
| infra | tele server client (каркас) | done | `0073-feat-add-a-tele-server-client-skeleton.patch`: TeleConfig `tele_server_url`, TeleServer с HTTPS-фетчем `/v1/badges`, кэш в `tele_badges.json`, `start()`/`clearCachedData()`. Будущие патчи (0009/0012/0081/0091/0108/0037) навесят применение меток, бейджи, usernames, crash reports |
| infra | argon2 helper | done | `0074-feat-add-an-argon2-helper.patch`: pure-JVM `tele.helpers.TeleArgon2` (Argon2Kt 1.6.0, native .so для Android) + self-check против RFC 9106 векторов для `prod:777000` и `prod:-1001234567890`. Основа для протокола бейджей (0009+). Фид применяется в фоновой очереди `TeleServer` (0081): argon2 по всем пирам не блокирует UI, `updateInterfaces` постится на main |

## пачка 9 — апдейтер и what's new

| № | патч | статус | примечание |
|---|---|---|---|
| 0006 | in-app апдейтер с релизов репозитория tele | done | `0086-feat-update-from-the-tele-github-releases`; `tele/helpers/TeleUpdater.kt`: фид `tele-update-android.json` из `releases/latest/download/` репозитория `gettele/android` (`{tag, base, counter, url, apk_sha256}`), новее = `base` > `versionCode/10` или равный `base` и `counter` > `TELE_BUILD`; `url` только внутри `releases/download/<tag>/` и `.apk`. APK качается в `files/cache/tele_update/`, проверяется sha256, ставится системным установщиком (подпись проверяет Android). Проверка через 15 с после старта и каждые 3 ч; локальные сборки (`TELE_BUILD` не задан) не обновляются. Плашка «update tele» внизу главного экрана (`TeleUpdateLayout`, fallback к стоковому `IUpdateLayout`), группа updates в корне настроек tele: «update automatically», «check for updates»/«install update», статус. Проверено на эмуляторе с локальным фидом: скачивание, плашка, статус «ready», системный диалог обновления. Формат релиза — [docs/architecture.md](architecture.md) |
| 0039 | what's new после обновления | done | `0087-feat-show-what-s-new-in-a-local-tele-chat`; `tele/helpers/TeleChangelog.kt`: `tele-changelog.json` из `releases/download/<tag>/` (формат десктопа: `{tag, title, url, categories, items}`) постится один раз на аккаунт после смены `TELE_BUILD` (`changelog_accounts`, тестовый бэкенд отдельно); при первом запуске получают все аккаунты, добавленные позже — нет. Тумблер «show what's new after updates» (вкл.), пункт «what's new» в настройках. Проверено на эмуляторе: пост при старте, повторно не постится, выключенный тумблер не тянет changelog |
| 0074 | what's new как локальный чат (частично) | done | там же; `tele/helpers/TeleChat.kt`: синтетический диалог «tele» (аватар из десктопа, галочка, непрочитанные) только в главном списке «все чаты», после закреплённых по дате; сообщения в `tele.db` (`tele_changelog`, версия БД 6), на сервер ничего не уходит. Экран `TeleChatActivity`: пузыри `ChatMessageCell` с жирными категориями и курсивом «where», кнопки «full changelog» и «new settings». Долгий тап — about tele / delete chat, свайп отключён. Проверено на эмуляторе |
| 0109 | объяснение отсутствующего changelog | done | там же; «what's new» без заметок показывает причину: релиз не опубликован, локальная сборка или ошибка загрузки + кнопка «full changelog». Проверено на эмуляторе (локальная сборка) |
| 0110 | новые настройки после апдейта (бейджи «new») | done | `0088-feat-show-new-settings-after-an-update`; `tele/helpers/TeleNewSettings.kt`: список известных ключей настроек и страниц в `known_settings`, новые после обновления — пункт «new in tele N» с бейджем NEW в корне настроек tele (пропадает после открытия) и экран `MODE_NEW` (новые страницы + тумблеры по секциям). При первом запуске всё считается известным. Проверено на эмуляторе: бейдж, экран, кнопка «new settings» в чате tele |

## пачка 10 — спецфичи

| № | патч | статус | примечание |
|---|---|---|---|
| 0045, 0080 | вычисление «= выражение» (calcmula) + живое превью | done | `0091-feat-compute-messages-starting-with-via-calcmula`: текст или подпись, начинающиеся с `= `, уходят на `GET https://calcmula.app/api/calc?q=…` и отправляются как цитата с запросом + `= ответ`; ошибка (тело 400) — буллетин, текст возвращается в поле. Хук — первая строка `SendMessagesHelper.sendMessage(SendMessageParams)` и обёртка очереди в `prepareSendingMedia` (подписи медиа). `0092-feat-preview-calcmula-results-while-typing`: карточка над полем (`tele/ui/CalcmulaPreview.kt`, задержка 350 мс, кэш 32 результата на 5 мин), тап — отправка. Тумблеры в sending, выкл.; превью создаётся при открытии чата. Подписи из выбора документов не считаются. Проверено на эмуляторе: выкл. — литерал, вкл. — `= 2+2` → цитата + `= 4`, ошибка, превью, тап; подпись к фото не проверена |
| 0087, 0105, 0112 | шоты: сообщение как картинка (1x–4x, что показывать) | done | `0093-feat-save-messages-as-a-picture`: пункт «shot» в меню сообщения и кнопка в панели выделения (`ChatActivity`, id 130/131) → экран `TeleShotActivity`: настоящие `ShotCell` раскладываются как в сетке чата (альбомы по span) и рисуются в Bitmap поверх обоев; масштаб 1x–4x, «мои как входящие», что показывать (кнопки, превью ссылок, реакции, ответы, пересылки, время, имена/аватары, даты, фон/прозрачность); copy / save (Pictures/Telegram) / send / share. Настройки вида — `shot_view`. Тумблер в interface, выкл. Проверено на эмуляторе: текст, несколько сообщений, фото, пост канала, альбом из 3 фото, 1x/3x, сохранение/копирование/шаринг; не проверены 4x, send to chat, темы с градиентом |
| 0060 | пипетка в фоторедакторе | done | `0095-feat-pick-brush-colors-from-the-image`: в стоке пипетка уже есть, но в трёх тапах (кружок → «+» → пипетка); по решению мейнтейнера — кнопка в один тап у палитры (`tele/helpers/TeleEyedropper.kt`), открывает стоковую лупу `PipettePickerView` над сведённой картинкой (фото + штрихи + стикеры/текст), цвет ставится стоковым путём. Тумблер в interface → editor, выкл. Проверено на эмуляторе: цвет с фото и со штриха; поворот/кроп/зум не проверены |
| 0083 | цена коллекционного подарка на дату покупки | done | `0089-feat-show-collectible-prices-at-the-purchase-date`: на самом деле это карточка коллекционного юзернейма/номера (`FragmentUsernameBottomSheet`), не подарка: цена в USD по курсу TON на дату покупки (`GET https://gram.rin.ms/v1/ton/price?at=…`, кэш), подменяет фиатную цену Fragment после ответа. Тумблер в interface, выкл., без него запроса нет. Проверено на эмуляторе: `@rove` у @durov — $26,938.46 → $44,200.00 |
| 0048 | коллекционные подарки в see.tg | done | `0090-feat-open-collectible-gifts-in-see.tg`: ссылка «open in see.tg» под таблицей уникального подарка (`StarGiftSheet`), открывает `https://t.me/seetgbot/nft?startapp=<slug>`; у обычных подарков скрыта. Тумблер в ids, выкл. Проверено на эмуляторе: мини-приложение see.tg открылось с нужным `start_param` |
| 0107 | docked media над полем ввода (частично) | done | `0096-feat-attach-media-above-the-field` (beta): при включённом тумблере обычная отправка из меню вложений пристыковывает фото/видео полосой над полем (`tele/ui/TeleDockedStrip.kt`), текст поля — подпись, кнопка отправки (и её меню silent/schedule/draft) шлёт один альбом; × на плитке и на панели, спойлер; хранится по чату в `tele_docked` (tele.db v7), строка чата показывает «Draft: 2 photos». Пропущено: сетка, перестановка, документы/вставка/шаринг, отложенные и quick replies, платные чаты, HQ после перезапуска. Тумблер в sending, выкл. Проверено на эмуляторе: стыковка, подпись, альбом, ответ, восстановление после выхода и перезапуска |
| 0009 | фикс: падение на старте из-за меток | done | `0094-fix-avoid-badge-crash-on-startup`: `TeleBadges.scopeFor` брал `ConnectionsManager.getInstance` внутри конструктора `MessagesController` (putUser support-юзера) → бесконечная рекурсия и SIGSEGV при холодном старте, если `ConnectionsManager` ещё не создан; теперь статический `native_isTestBackend`. Найдено при тестах шотов; после фикса холодные старты без падений |
| 0040 | брендинг «tele» во внутренних строках | done | `0038-feat-call-the-app-tele-in-its-own-texts` + `0097-fix-finish-tele-branding-and-settings`: app-level strings перекрывают стоковые упоминания приложения; onboarding показывает `tele` и объясняет, что это fork; permission prompts для контактов, уведомлений и автозаполнения кода тоже называют tele. сервисные упоминания (Premium, модераторы, FAQ) и имена папок на диске оставлены как есть |
| 0042 | секции и поиск настроек tele | done | `0040-feat-split-tele-settings-into-sections-and-add-them-.patch` + `0097-fix-finish-tele-branding-and-settings.patch`; `TeleSettingsActivity(mode)` — корень открывает interface, privacy, ids, sending, your data и server; названия и обычные line-иконки секций сохранены; корневые секции и группы настроек оформлены штатным `UniversalRecyclerView.setSections()`; большинство переключателей имеют описания на английском; `TeleSearch.kt` добавляет секции и настройки в `ProfileActivity.SearchAdapter` (guid 950+, хлебные крошки tele > секция). редактор rewrite: компактные кликабельные Telegram-style чекбоксы |

## пачка 11 — база приватности

игнор-лист, per-chat ghost и ghost-schedule — база приватности по решению мейнтейнера, поэтому она теперь первая после уже завершённых пачек.

ворота: debug-apk; с опциями on/off проверить локальные фильтры, уведомления, ghost-отправку и обязательное восстановление privacy rule после force-stop.

после ревью мейнтейнера (`0108-fix-apply-the-privacy-review-feedback`): пикер переделан на стоковый `SearchField` (был прозрачный и наезжал на список) и показывает только людей; в профиле появилась кнопка «Ignore messages» с тумблером; слова по умолчанию гасят сообщение, полное скрытие — отдельный тумблер; ghost-переключатели собраны под общим «Ghost mode» (в android нет мастер-тумблера, как в десктопе) и не работают, пока он выключен; в меню сообщения появился пункт «Read», когда включён ghost read.

после второго ревью (`0109-fix-second-privacy-review-round`): пикер игнора и ghost-исключений переписан на стоковый экран пересылки (`DialogsActivity`, `DIALOGS_TYPE_FORWARD` + `selectAlertString`) — список чатов с галочками, счётчик получателей и нижняя панель, как при пересылке нескольким людям; в режиме игнора отмечаются только люди, группы и каналы — нет; в разделе ghost появилось живое превью (карточка «you / what they see»: заголовки — системные сообщения, строки — плашки профиля из заголовка диалога с настоящей аватаркой и бейджем stealth, «On my way…» — поле ввода, «See you tomorrow?» — пузыри сообщений (наш с одной галочкой), «Their story» — кружок истории с буквенной аватаркой и текстом справа, «12 views» — стоковая иконка «Hide My View» (`msg_stories_stealth2`) из premium-режима историй), клик по строке переключает тумблер, как в десктопном патче 0244; исправлен краш в профиле: `TeleHooks.onPrivacyRulesChanged` слал `messagesDidLoad` без аргументов, из-за чего `ChatActivity` падал с AIOOBE на `args[10]` — теперь ячейки чата перебиндовываются по счётчику ревизии, а список чатов обновляется через `dialogsNeedReload`; peek last seen грузит правила приватности с сервера, если их ещё нет в кэше, вместо отказа «the privacy rules are not loaded yet».

отдельно (`0110-fix-capitalize-the-tele-strings`): сплошная вычитка строк форка — экраны, пункты меню, диалоги, тосты и подписи в поиске переведены в верхний регистр (в десктопе всё в нижнем, в android — как в телеграме). слово «tele» остаётся строчным везде, включая «tele server URL», «tele · Privacy» и «New in tele». технические строки (sql, регулярки, ключи конфига, коды ошибок ленты) не тронуты; статусы в превью ghost («online», «recently», «typing…») оставлены строчными, как в шапке чата.

отдельно (`0111-fix-hide-phones-in-streamer-mode`): в streamer mode номер больше не показывается в заголовке чата — раньше для пользователя без контакта телеграм подставлял туда телефон. телефон скрыт и в имени, если у пользователя нет имени (вместо номера — «Unknown»), и в своём профиле (строка «Mobile»). в списке чатов, в профиле и в заголовке имя берётся из `UserObject.getUserName`, который в режиме стримера не откатывается на номер.

отдельно (`0112-feat-search-jumps-to-the-setting`): результат поиска открывает нужную страницу tele и проматывает её к нужному тумблеру, подсвечивая его — как это делают настройки самого телеграма. сделано штатным механизмом (`SearchResult.rowName` + `AndroidUtilities.scrollToFragmentRow`), поэтому подсветка и прокрутка совпадают со стоковыми.

отдельно (`0113-fix-improve-the-link-rewrite`): в окнах «Domain rule» / «Pattern rule» добавлены боковые отступы (20 dp) и промежутки между полями и чекбоксами. вместо системного тоаста показывается телеграмный баултин со строкой «домен_до -> домен_после» (например `x.com -> fxtwitter.com`), чтобы было видно, что поменялось именно в ссылке. «Pick a random target» больше не выбирает цель по хешу ссылки (из-за чего один и тот же домен заменялся всегда на один и тот же) — теперь случайный выбор на каждую перезапись.

| № | патч | статус | примечание |
|---|---|---|---|
| 0016, 0073 | игнор-лист (скрыть/затухание) с пикером как в privacy | built | `0099-feat-ignore-users-by-hiding-or-fading-their-messages`: `tele/helpers/PrivacyRules.kt` (список `privacy_ignore:<account>` в `tele_kv`, account-scoped) + форк-пикер `tele/ui/settings/TelePeersActivity.kt` (после ревью — стоковый экран пересылки с галочками, только люди; режим `hide`/`fade` на peer); фильтр в `DialogCell` (превью скрывается или гаснет) и `ChatMessageCell` (строка сообщения схлопывается в 0 высоты или рисуется с alpha 35%). Проверено на эмуляторе: `hide` убирает превью и сообщения, `fade` гасит строку. Отклонение от десктопа: режим (`hide`/`fade`) задаётся на каждого peer, а не одним глобальным тумблером |
| 0032, 0073 | per-chat ghost: исключения и ghost по чатам | built | `0100-feat-add-per-chat-ghost-mode-exceptions`: тот же пикер, список `privacy_ghost:<account>` (`always`/`never`); гейты `GHOST_TYPING`/`GHOST_READ`/`GHOST_CONTENTS_READ` в `MessagesController` и `LocationController` стали per-chat (`PrivacyRules.ghostTyping/ghostRead/ghostContentsRead`). Онлайн-статус остаётся глобальным, как в десктопе: per-peer онлайн технически невозможен |
| 0032, 0064 | ghost-schedule и offline-after-send | built | `0101-feat-send-ghost-messages-as-scheduled-and-go-offline`: в `SendMessagesHelper.sendMessage` дата отправки = now+12s, если включён `ghost_schedule` и чат в ghost-списке; после принятия запроса — `TL_account.updateStatus(offline=true)`, если включён `ghost_online`. Проверено на эмуляторе: сообщение уходит как «Scheduled for …». Включённый `ghost_schedule` считается признаком ghost-режима вместе с глобальными ghost-переключателями (в android нет мастер-тумблера, как в десктопе). После второго ревью добавлено живое превью ghost (карточка «you / what they see», клик по строке переключает тумблер) — `0109-fix-second-privacy-review-round` |
| 0166 | скрытие по слову/regex | built | `0102-feat-hide-messages-by-keyword-or-regex`: правила в `tele_kv` (`privacy_hidden_words:<account>` для глобальных и `…:<dialogId>` для чата), по одному в строке, обычный текст или `/regex/` и `/regex/i` (java regex, case-insensitive); редактор `tele/ui/settings/TeleWordsActivity.kt` (глобальный из privacy, per-chat — из меню чата); битый regex не применяется и показывается ошибкой. Проверено на эмуляторе: `/.*/` скрывает все входящие текстовые сообщения, медиа без текста остаются (как в десктопе) |
| 0228 | ignored/hidden words молчат | built | `0103-feat-keep-ignored-and-hidden-messages-silent`: в `NotificationsController.processNewMessages` сообщения, попавшие под игнор-лист или под слова, не создают уведомление (`PrivacyRules.isMuted`); серверные счётчики не меняются, история и превью — как в обычном режиме |
| 0227 | показ ghost-scheduled сообщений | built | `0104-feat-show-pending-ghost-scheduled-messages`: пока `ghost_scheduled_messages` включён, локальная копия ghost-scheduled сообщения хранится в чате (`mode = 0` вместо `MODE_SCHEDULED`), а не в списке отложенных; при доставке сервером сообщение с тем же id обновляет строку, дубля нет |
| 0229 | невидимые сторис и per-chat ghost | built | `0105-fix-make-invisible-stories-follow-the-ghost-list`: `StoriesController.markStoryAsRead` не отправляет `TL_stories_readStories`, если чат в ghost-списке; живые сторис такого чата не открываются (`StoryViewer`). Локальный `max_read_id` пишется как раньше (`storiesStorage.updateMaxReadId`) — переживает перезапуск |
| 0282 | подсмотреть скрытый last seen | built | `0106-feat-peek-at-a-hidden-last-seen`: `tele/helpers/LastSeenPeek.kt` — правило last seen временно меняется на allow-users, статус читается и показывается тостом, исходное правило восстанавливается (до 5 попыток, 2 с) и лежит в `tele_kv`, поэтому восстанавливается и после перезапуска (`restorePending` в `TeleHooks.init`); пункт «peek last seen» в меню чата. Тумблер выключен по умолчанию, в описании есть предупреждение. После второго ревью правила приватности подгружаются с сервера, если их ещё нет в кэше (`0109-fix-second-privacy-review-round`) |
| 0160 | streamer mode (частично) | built | `0107-feat-add-a-streamer-mode`: `FlagSecureReason` всегда ставит `FLAG_SECURE` (приоритет над `never block screenshots`), окна photo/secret/story/call/bubble/external — тоже; превью уведомлений заменяется пустым, телефон в профиле скрывается. Проверено на эмуляторе: `adb screencap` возвращает пустой файл, пока режим включён. Заголовок окна и трей — desktop-only, не переносились |

## пачка 12 — доработки перенесённого и быстрые тумблеры

пять исправлений уже перенесённых фич и семь небольших тумблеров; это первая пачка после privacy base. effort: S×10, M×2.

ворота: debug-apk; докачка, scheduled retries, link migration и каждый новый тумблер проверены on/off.

| № | патч | статус | примечание |
|---|---|---|---|
| 0017 (доработка) | время у сервисных сообщений при включённых секундах | todo | android 0008 покрывает только формат `HH:mm:ss`; дописывать « · HH:mm:ss» к тексту `TL_messageService` (`MessageObject.messageText`, `ChatActionCell`), время по `messageOwner.date` тем же `formatterDay`, гейт `SHOW_SECONDS`, пересчёт через `TeleHooks.onConfigChanged`; обновить описание опции в `TeleSettingsActivity` («service messages also show their time»); влитый бывший 0043; S |
| 0077 (доработка) | пресеты перезаписи ссылок: TikTok → tnktok.com, samekosabax.com | todo | доработка android 0051/0052: `LinkRewrites.presets()` — TikTok только `tnktok.com`, к X добавить `samekosabax.com`; `rules()` мигрирует сохранённые цели `vxtiktok.com → tnktok.com` с дедупликацией; `Tracking.kt` — `samekosabax\.com` в regex twitter/x; S |
| 0095 (доработка) | отложенные вовремя: ретраи и уведомление | todo | доработка android 0064: сейчас `PunctualScheduled.sendNow` игнорирует ошибку и перебирает сообщение каждые 20 с; добавить учёт попыток по (account, dialogId, mid), `FLOOD_WAIT_N`/`SLOWMODE_WAIT_N` → ждать N+1 с, `code <= 0 \|\| >= 500 \|\| TIMEOUT` → лестница 5 с / 15 с / 1 / 5 / 15 мин, максимум 5 попыток, по исчерпании — уведомление на своём канале и тост «couldn't send a scheduled message on time: <причина>»; пачку при неповторяемой ошибке не дробить; архивные чаты; M |
| 0006 (доработка) | апдейтер: докачка и лестница повторов | todo | доработка android 0086 (`TeleUpdater.kt`): `.part` не удалять при сетевой ошибке, повторный `download` с `Range: bytes=<size>-`, 206 с корректным `Content-Range`, 200 → с нуля, 416 при `size>0` → сразу sha256; sha256 по готовому файлу, при несовпадении удалить; при сетевых ошибках следующая проверка по лестнице 1 / 5 / 15 / 60 мин (сейчас всегда `CHECK_INTERVAL` 3 ч); прогресс от `offset + ready`; M |
| 0253 (доработка) | копировать peer id голыми цифрами | todo | fix-коммит к android 0025: пункт Copy в `ProfileActivity` копирует `PeerId.rowText(...)` (с разделителями и `(DC…)`); добавить `PeerId.copyText(account, userId, chatId)` = `botApiAdjusted(...).toString()`; S |
| 0125 | скрыть кнопку подарка в поле | todo | `ChatActivityEnterView`, ChatActivity (канал); S; по умолч. (тумблер выкл); личные чаты и каналы |
| 0132 | скрыть похожие каналы | todo | `MessageObject`, `MessagesController`, `ProfileActivity`; S; гейт запроса рекомендаций |
| 0143 | скрыть тултип коллекционного статуса | todo | `ProfileActivity`; S; ранний return |
| 0154 | reduce motion | todo | `LiteMode`; S; сохранение и восстановление флагов |
| 0172 | скрыть телефон в профилях | todo | `ProfileActivity.phoneRow`; S; зависит от android 0075; только phoneRow |
| 0233 | нет метки «изменено» у ботов | todo | `ChatMessageCell`, `TeleHooks`; S; `bot` или `via_bot_id` |
| 0231 | параметр старта на кнопке Start | todo | `ChatActivity`; S; тултип по long-click |

## пачка 13 — структура настроек и редактор меню

копия новой структуры настроек tele с десктопа (0169) — основа для новых страниц («new settings», живые превью), затем редактор меню (0171: все меню, пресеты, текстовый экспорт/импорт, миграция hidden+order из android 0047/0057) и мелкие пункты меню на нём. effort: S×7, M×2, L×1.

ворота: debug-apk, на устройстве: все страницы настроек открываются, поиск находит тумблеры; сохранённые скрытие/порядок меню сообщений мигрировали; пресеты и экспорт/импорт меню работают; пункты 0255/0295/0266/0179 появляются только при включённых фичах.

| № | патч | статус | примечание |
|---|---|---|---|
| 0169 | перегруппировка страниц настроек | todo | `TeleSettingsActivity`, `TeleSearch`; M; реш.: 0169 структура десктопа; база для 0170 и новых страниц |
| 0170 | сворачиваемые под-тумблеры | todo | `TeleSettingsActivity`; S; зависит от 0169; новый тип строки |
| 0171 | редактор меню: группы, подменю | todo | `MessageMenu`, `TeleMenuActivity`, 7 меню; L; зависит от android 0047, android 0057, android 0058; реш.: 0171 все меню, пресеты, экспорт; по видам меню, миграция hidden+order |
| 0167 | пункты меню по включённой фиче (частично) | todo | меню чата/профиля; S; зависит от 0171; по умолч.; под-тумблеры *_menu пропущены, только аудит |
| 0179 | copy/delete алиаса из меню | todo | `ChatActivity`, `ProfileActivity`; S; зависит от android 0030, android 0035; long-click по ссылке/строке |
| 0200 | выделять сервисные сообщения | todo | `ChatActivity`, `ChatActionCell`; M; исключить из copy/forward |
| 0255 | копировать путь файла из меню | todo | `ChatActivity`, `MessageMenu`, `FileLoader`; S; зависит от 0171 меню, android 0047, android 0057; только скачанные файлы |
| 0266 | копировать id владельца набора | todo | `StickersAlert`, `EmojiPacksAlert`, `PeerId.kt`; S; формула эмпирическая |
| 0295 | копировать текст сервисных сообщений | todo | `ChatActivity.fillMessageMenu`, `MessageMenu.ALL`; S; зависит от меню-редактор; default off, проверить wallet-карту |
| 0149 | view as TL в приложении | todo | `ViewAsTl`, `ui/web`; S; зависит от android 0059; проверить большие #data |

## пачка 14 — хранилище tele.db: удалённые, закладки, лимиты gif

всё, что держит локальные данные в `tele.db`: срок хранения удалённых и защита kept-медиа, удалённые чаты/топики, закладки, время прочтения, gif и избранное сверх лимита. effort: S×2, M×5, L×2.

ворота: debug-apk, на устройстве: удалённые сообщения/чаты/топики остаются после перезапуска, срок 1/7/30/навсегда соблюдается, kept-медиа переживает очистку кэша; откат метки при неудачном серверном удалении; закладки и точка возврата; «удалить все мои сообщения» в тестовом чате.

| № | патч | статус | примечание |
|---|---|---|---|
| 0151 | какие удалённые хранить | todo | `DeletedMessages.shouldArchive`; S; зависит от android 0068; боты и избранное |
| 0219 | откат неудавшегося удаления | todo | `MessagesController.deleteMessages`, `DeletedMessages.kt`; M; зависит от android 0068; различать FLOOD/сеть и жёсткие ошибки |
| 0182 | хранение удалённых после рестарта | todo | `DeletedMessages`, `MessageHistory`; S; зависит от android 0068, android 0069, 0151; реш.: 0182 срок 1/7/30/навсегда; остаток: срок + защита kept-медиа |
| 0283 | сохранять удалённые чаты и топики | todo | `MessagesController`, `TopicsController`, `DialogCell`; L; зависит от 0019, 0151, 0256, android 0068, 0182; реш.: 0283 как desktop; все пути удаления |
| 0321 | восстановить пост канала из форварда | todo | `DeletedMessages.kt`, `ChatMessageCell`; M; зависит от 0019, android 0068; маркер в fork-таблице |
| 0301 | удалить все мои сообщения из чата | todo | `RemoveMine.kt`, `ChatActivity`, `DialogsActivity`, `TopicsFragment`; M; зависит от 0019, android 0068; FLOOD_WAIT, пропуск kept deleted |
| 0126 | закладки и точка возврата | todo | `ChatActivity`, `ChatMessageCell`, `tele.db`; L; зависит от android 0047; реш.: 0126 tele.db; два тумблера, можно разделить на два патча |
| 0147 | время прочтения ваших сообщений | todo | `MessagesController`, `MessageSeenView`, `tele.db`; M; по умолч.: тумблер выкл; лимиты как у десктопа |
| 0164 | gif и избранное сверх лимита | todo | `MediaDataController`, `tele.db`; M; file_reference refresh |

## пачка 15 — списки: пины, папки и лимиты

прежняя пачка 11 («списки и лимиты»): локальные пины и папки сверх серверного лимита (одна модель хранения и общий порядок), unsorted-папка на том же механизме, скрытие сообществ и мелочи списка. effort: S×3, M×1, L×3.

ворота: debug-apk, на устройстве: закрепление сверх лимита и перетаскивание вперемешку, пины в архиве/папках/топиках/Saved; папки сверх лимита, unsorted; скрытие сообществ; переход к первому сообщению; мьют папок.

| № | патч | статус | примечание |
|---|---|---|---|
| 0123 | пины чатов сверх лимита (локальные) | todo | модель десктопа после переработки: у каждого пина флаг `local`, в `tele_kv` список `{id, hash?, local}` на каждый список (основной/архив/фильтр/топики форума/Saved), один общий порядок серверных и локальных пинов (серверные вливаются в локальный список), перетаскивание вперемешку — серверу уходит только его часть; снятие пина у серверного+локального оставляет серверный; закрепление сверх лимита создаёт `local = true`; точки хука [INFERENCE, не проверены]: ошибка лимита в пути `TL_messages_toggleDialogPin`, сортировка локальных в `MessagesController.sortDialogs`; L |
| 0124 | папки сверх лимита (локальные) | todo | fork-фильтры вне серверной синхронизации; тот же механизм у 0162 (unsorted); L |
| 0162 | папка «unsorted» | todo | `getDialogFilters`, `FilterTabsView`; L; зависит от локальные папки (0124); по умолч.: 0162; один механизм с локальными папками |
| 0117 | скрывать сообщества | todo | образец `debloat/community-dialogs`; S |
| 0031 | перейти к первому сообщению | todo | образец `feature/jump-to-beginning`; S |
| 0082 | мгновенное перемещение чатов (частично) | todo | без десктопного freeze — только идея; S |
| 0156 | мьют папок и «глушить полностью» | todo | `isDialogMuted`, `NotificationsController`, `FilterTabsView`; M; по умолч.: 0156 выкл; tele_kv |

## пачка 16 — внешний вид списка, профиля и пузырей

компактный список чатов, режим «только иконки» у папок, фон шапки профиля, пузыри, строчный интерфейс. горячие файлы (`DialogCell`, `ChatMessageCell`, `ProfileActivity`) — проверять рендер на устройстве. effort: S×1, M×7, L×3.

ворота: debug-apk, на устройстве: компактные строки и режим иконок на разных размерах шрифта, профиль с размытым фоном и заливкой цветом, пузыри без хвостиков, бейджи в reply/forward; lowercase не ломает локали; off = сток.

| № | патч | статус | примечание |
|---|---|---|---|
| 0129 | компактный список чатов | todo | `DialogCell`, `DialogsAdapter`; L; реш.: 0129 compact L; малые аватары, одна строка |
| 0133 | скрыть счётчики непрочитанного | todo | `FilterTabsView`, `NotificationsController`, `Drawer*Cell`; M; четыре под-тумблера |
| 0300 | компактные папки «только иконки» (частично) | todo | `FilterTabsView`, `DialogsActivity`; L; по умолч.: новая фича; нет режима иконок в стоке |
| 0279 | скрыть дни рождения | todo | `BirthdayController`, `DialogsActivity`, `ProfileBirthdayEffect`; S; зависит от 0125; без рестарта через onConfigChanged |
| 0299 | размытое фото как фон шапки профиля | todo | `ProfileActivity.TopView`; M; MODE_IDS или interface |
| 0304 | залить профиль цветом фото (частично) | todo | `ProfileActivity`, `ResourcesProvider`; L; зависит от 0299; реш.: 0304 полный override; регрессионно хрупко |
| 0267 | убрать хвостики пузырей | todo | `ChatMessageCell`, `Theme.MessageDrawable`; M; форсировать drawPinnedBottom; проверка на устройстве |
| 0276 | бейджи в «Переслано» и reply | todo | `ChatMessageCell`, `TeleNameBadges`; M; зависит от 0012, android 0077, android 0083; горячий файл, проверка на устройстве |
| 0022, 0035 | lowercase всего интерфейса | todo | перехват `LocaleController.getString` (+ строки `strings_tele.xml`); тумблер выкл.; M |
| 0010, 0041 | шаблон заголовка экрана диалогов (частично) | todo | движок переменных на базе шапки чатов; сейчас `TeleBuild.label()` «tele N»/«tele dev»; 0150 («#» в метке) пропущен, 0258 (строчная метка) уже есть; по умолчанию: без шаблона заголовка окна; M |
| 0068 | локальные фоны чатов (частично) | todo | per-chat обои уже в стоке; добавить форс-локальность (не отправлять `setChatWallPaper` на сервер) и удаление навязанного; M |

## пачка 17 — отправка

подтверждение отправки вторым тапом, тишина по умолчанию, форматы и ретраи отправки/загрузки. effort: S×5, M×5, L×1.

ворота: debug-apk, на устройстве: второй тап подтверждает стикеры/гифки/голосовые; silent по умолчанию и по чату (`silent_<dialogId>`); аудиофайл как голосовое; пересылка по одному; ретрай упавшего чанка загрузки и «retry all»; сообщение за очередью можно отпустить; выделение >100 сообщений.

| № | патч | статус | примечание |
|---|---|---|---|
| 0128 | отправка без звука по умолчанию | todo | `SendMessagesHelper`, ChatActivity меню; M; по умолч.: 0128 silent_<id>; меню отправки «со звуком» |
| 0130 | подтверждение отправки вторым тапом | todo | `EmojiView`, `ChatActivityEnterView`, `MentionsAdapter`; M; по умолч.: 0130 как десктоп; второй тап 5 с; голосовые — в превью |
| 0318 | подтверждение стикеров из бокса набора | todo | `StickersAlert`; S; зависит от 0130; по умолч.: 0130/0318 по десктопу; общий `TeleSendConfirm` |
| 0153 | .mkv как видео (частично) | todo | `SendMessagesHelper`; S; по умолч.: 0153 частично; нужна проверка на устройстве |
| 0157 | аудиофайл как голосовое | todo | `MediaController`, `ChatAttachAlertAudioLayout`; L; зависит от android 0096; по умолч.: 0157 нативный энкодер; блокирует запись на время конвертации |
| 0259 | пересылка по одному сообщению | todo | `SendMessagesHelper`; S; альбомы вместе; flood wait |
| 0254 | быстрый ответ по точному /имени | todo | `ChatActivityEnterView`, `QuickRepliesController`; S; зависит от android 0065; не боты/stars/scheduled |
| 0215 | ретрай упавших кусков загрузки | todo | `FileUploadOperation`; M; в секретных чатах не ретраить |
| 0220 | отправить все неудавшиеся | todo | `ChatActivity.fillMessageMenu`, `MessageMenu.kt`; S; «Retry all» |
| 0226 | очередь за загрузкой: видно и отпустить | todo | `SendOrder.kt`, `MessageMenu.kt`, `ChatMessageCell`; M; зависит от android 0066; под тумблером queue_behind_media |
| 0269 | выделять больше 100 сообщений | todo | `ChatActivity`, `MessagesController.deleteMessages`; M; зависит от 0259; реш.: 0269 chunked; нарезка по 100 |

## пачка 18 — поле ввода, текст и цитаты

живой markdown, подписи к стикерам (показ везде), цитаты, calcmula, копирование текста. effort: S×4, M×5, L×2.

ворота: debug-apk, на устройстве: markdown как декор при наборе и entities при отправке; подпись стикера в пузыре/списке/уведомлении; несколько цитат в одном ответе; чип calcmula над полем; copy как Markdown/HTML.

| № | патч | статус | примечание |
|---|---|---|---|
| 0245 | живой markdown при наборе | todo | поле ввода, подписи, `getEntities`; L; реш.: 0245 декор-спаны + подтумблер `>`; цитаты `>`/`>!` отдельным подтумблером |
| 0175 | подписи к стикерам | todo | `ChatMessageCell`, `DialogCell`, уведомления; L; реш.: 0175 отправка+рендер везде; сток не рисует подпись стикера |
| 0210 | несколько цитат в одном ответе | todo | `ChatActivity`, `ChatActivityEnterView`; M; общий код с 0211 |
| 0211 | цитата из расшифровки голосового | todo | `ChatActivity.canShowQuote`; S; зависит от 0210; реш.: 0137 транскрипция остаётся; вставка блок-цитатой в поле |
| 0148 | подсказки calcmula | todo | `Calcmula.kt`, `CalcmulaPreview.kt`; M; зависит от android 0091, android 0092; send without calculating |
| 0176 | calcmula-результат после = | todo | `ChatActivityEnterView`; M; зависит от android 0092; реш.: 0176 чип; тап вставляет |
| 0144 | перезапись ссылки только для превью | todo | `EditTextCaption`, `ChatActivity`; S; зависит от android 0051, android 0052, android 0062; неактивно при no_link_previews |
| 0141 | набранные эмодзи в «недавние» | todo | `Emoji`, `SendMessagesHelper`; S; тумблер выкл (fix) |
| 0139 | копировать как Markdown/HTML | todo | `MessageMenu`, `ChatActivity`; M; зависит от android 0047; Writer entity→MD/HTML |
| 0142 | нумерация строк code-блоков | todo | `ChatMessageCell`, `MessageObject`; M; rich-IV отдельно |
| 0146 | шот → docked-лента (частично) | todo | `TeleShotActivity`, `DockedMedia`; S; зависит от android 0093, android 0096; только отправка в docked |

## пачка 19 — поиск и чат

regex-поиск, фильтры поиска, упоминания и мелкие правки чата. effort: S×4, M×6.

ворота: debug-apk, на устройстве: regex в чате и в списке, ряд чипов по типу (GIF/кружки), поиск по человеку + типу; упоминание нескольких подряд (долгий тап); онлайн в больших группах; закреплённый стикер-набор; лента реакций; mini app не на весь экран.

| № | патч | статус | примечание |
|---|---|---|---|
| 0168 | regex-поиск по истории | todo | поиск в чате и чат-листе; M; по умолч.; только память, не SQLite |
| 0281 | фильтр поиска в чате по типу | todo | `MediaDataController.searchMessagesInChat`, `ChatActivity`; M; зависит от 0168; реш.: 0281 chip row (по умолч.); включая GIF/кружки |
| 0306 | поиск по человеку + типу | todo | `MediaDataController.searchMessagesInChat`; M; зависит от 0281; по умолч.: 0281 чипы; вердикт изменён с ❌, релевантен после 0281 |
| 0280 | упоминать нескольких подряд | todo | ChatActivity mentionContainer; S; реш.: 0280 long-press; не для inline-ботов |
| 0268 | онлайн участников в больших группах (частично) | todo | `MessagesController`, `ChatAvatarContainer`; S; реш.: 0268 край скрытых ≤200; в стоке; доделываем край |
| 0134 | панель закрепа из меню чата | todo | `ChatActivity`; S; по умолч.: 0134 выкл; пункт при !allowPin |
| 0235 | своя полоса реакций | todo | `ReactionsContainerLayout`, `TeleSettingsActivity`; M; drag-reorder; кастомные реакции через `MediaDataController` |
| 0127 | закрепить наборы стикеров/эмодзи | todo | `EmojiView`; M; локально в tele_kv |
| 0322 | фильтр стикеров и эмодзи по формату | todo | `StickersActivity`, `EmojiView`; M; формат по mime документов |
| 0249 | мини-аппы никогда на весь экран | todo | `BotWebViewContainer/Sheet`; S; UNSUPPORTED на fullscreen |

## пачка 20 — имена, id и история версий

невидимые имена и скрытые символы, DC/ID/дата загрузки, история версий в APK и живые превью настроек (0244 — последним: опирается на ghost, 0208/0209, 0169). effort: S×3, M×5, L×1.

ворота: debug-apk, на устройстве: невидимые имена пользователей и чатов заменены `@username` (только в памяти, БД не меняется); скрытые символы подсвечены; DC по первому фото; история версий открывается офлайн из `res/raw`; живые превью в настройках.

| № | патч | статус | примечание |
|---|---|---|---|
| 0208 | @username вместо невидимых имён | todo | `UserObject`, `putChat`, `DialogCell`, `ChatMessageCell`; M; зависит от android 0029 (LocalNames); реш.: 0208 users+chats, в памяти; чаты только в памяти, не в БД |
| 0209 | показ скрытых символов | todo | `ProfileActivity`, `MessageObject`; M; зависит от 0208; общая таблица кодпоинтов с 0208 |
| 0189 | DC чата по первому фото | todo | `PeerId`, `ProfileActivity`; M; зависит от android 0025; по умолч.: «uncertain»; async строка |
| 0196 | DC медиа в просмотрщике | todo | `PhotoViewer`, `StoryViewer`; S; зависит от 0189, android 0025; тумблер SHOW_DC |
| 0265 | дата загрузки медиа во вьюере | todo | `PhotoViewer`; S; зависит от 0196 (опц.); с DC через « · » при 0196 |
| 0173 | подпись имени в цитате удалённого | todo | `DeletedReply`; S; зависит от android 0071; mention/ссылка, без превью |
| 0237 | история изменений всех версий | todo | `TeleChangelog.kt`, `res/raw`; M; зависит от android 0087, android 0088; реш.: 0237/0241 в APK, CI; `changelog_history.json` генерирует CI |
| 0241 | what's new с живыми тумблерами | todo | `TeleSettingsActivity(MODE_NEW)`, `TeleSearch.kt`; M; зависит от 0237, android 0088; реш.: 0169 структура настроек, 0237/0241; после 0237 |
| 0244 | живые превью в настройках | todo | `TeleSettingsActivity` (`TYPE_PREVIEW`); L; зависит от 0208, 0209, ghost, android 0025; реш.: 0169; делать последним |

## пачка 21 — уведомления, загрузки и система

разное, что трогает сервисы и систему: «пришёл в онлайн» со службой keep-alive, папки загрузок, веб-карты, «без AI», test-аккаунты. effort: S×3, M×4.

ворота: debug-apk, на устройстве: уведомление «пришёл в онлайн» (живой keep-alive); сохранение в `Telegram/<чат>`; выбор веб-карты; AI-функции отключены, расшифровка голосовых осталась; тонкая кисть; test-аккаунт добавляется long-press.

| № | патч | статус | примечание |
|---|---|---|---|
| 0155 | уведомление «пришёл в онлайн» | todo | `MessagesController`, свой канал, `keep-alive`; M; реш.: 0155 keep-alive; без FCM нужен сервис |
| 0158 | папка загрузок на чат (частично) | todo | `MediaController.saveFile`; M; реш.: 0158 подпапка Telegram/<чат>; без SAF |
| 0138 | выбор веб-карт для локаций | todo | `LocationActivity`; S; реш.: 0138 веб-карты; Яндекс/2ГИС/OSM/Google |
| 0137 | выключить AI-функции | todo | `AIEditorAlert`, `TranslateController`, `AiTonesController`; M; реш.: 0137 транскрипция остаётся; расшифровка голосовых не гасится |
| 0262 | тонкая кисть в редакторе | todo | `Paint/RenderView`; S; формула веса кисти |
| 0222 | журнал звонков: ретрай загрузки | todo | `CallLogActivity`; S; только ретрай |
| 0070 | аккаунты test-сервера (частично) | todo | нужен нативный per-account флаг `isTestBackend` (JNI tgnet); жест — long-press; M |

## пачка 22 — центр уведомлений

первый хунк форка в `jni/` (tgnet, flood wait) и экран центра с бейджем в настройках tele; затем зависимые патчи. нативная сборка под все ABI. 0206 требует решения на стороне tele-server (платформа `android`). effort: S×4, M×2, L×1.

ворота: debug-apk, на устройстве: нативный хук тестируется искусственным `FLOOD_WAIT`; выключен — tgnet идёт как сток; центр показывает flood wait/slowmode, упоминания и ответы, записи целиком («show more»), скопированные значения; сборка на всех ABI.

| № | патч | статус | примечание |
|---|---|---|---|
| 0205 | центр уведомлений | todo | `tgnet/jni`, `TeleNotices`, `tele_notices`, `TeleSettingsActivity`, `DialogsHintCell`; L; зависит от JNI-хук tgnet, android 0073; реш.: центр уведомлений + JNI-хук, вход — строка с бейджем в tele; первый hunk форка в `jni/` |
| 0212 | лимиты slowmode и throttling | todo | tgnet-хук, `TeleNotices`; S; зависит от 0205, центр уведомлений; реш.: центр уведомлений; тип ошибки в общем колбэке |
| 0232 | упоминания и ответы в центре | todo | `NotificationCenter.didReceiveNewMessages`, `LaunchActivity`; M; зависит от 0205, центр уведомлений; реш.: центр уведомлений; не через `processNewMessages` |
| 0239 | центр: записи целиком, «Show more» | todo | ячейка центра; S; зависит от 0205, центр уведомлений; реш.: центр уведомлений; делать сразу в ячейке |
| 0240 | центр: скопированные значения | todo | `TeleNotices.copied`, `Bulletin`; S; зависит от 0205, центр уведомлений; реш.: центр уведомлений; только fork-копирования |
| 0246 | бейдж «ответ/@» в центре уведомлений | todo | ячейка центра уведомлений; S; зависит от 0205, 0232, центр уведомлений; реш.: центр уведомлений портируется; косметика, после 0205/0232 |
| 0206 | серверные notices в центре | todo | `TeleServer.kt`, `TeleBadges.kt`; M; зависит от 0205, android 0073, android 0074, центр уведомлений; по умолч.: фид принимает platform android; открытый вопрос к серверу |

## пачка 23 — подарки: пароль и массовые действия

локальный пароль для звёзд и подарков стоит первым (гейтит остальное), затем массовые отправки/действия, поиск, фильтры и раннер, переживающий flood wait (0213 — после центра уведомлений). effort: S×3, M×7, L×1.

ворота: debug-apk, на устройстве: пароль + биометрия запрашиваются перед платежами; несколько подарков сразу, мультивыбор и дим скрытых; поиск и CSV-экспорт транзакций; фильтр по дате; пачка подарков переживает flood wait; на тестовом аккаунте.

| № | патч | статус | примечание |
|---|---|---|---|
| 0187 | локальный пароль для звёзд/подарков | todo | `StarsController`, `StarGiftSheet`; M; реш.: 0187 свой пароль+биометрия; гейтит 0184–0198, 0195 |
| 0217 | локальный пароль для платежей | todo | `PaymentFormActivity`, `AlertsCreator`; S; зависит от 0187; реш.: локальный пароль 0187+0217; свой пароль + биометрия |
| 0213 | пачки подарков переживают flood-wait | todo | `StarsController`, `ProfileGiftsContainer`; M; зависит от 0184–0186, 0190, 0192, 0193, 0205, студия подарков; реш.: mass actions + runner 0213; Kotlin-раннер с пропуском плохих |
| 0184 | несколько подарков сразу | todo | `SendGiftSheet`; M; зависит от 0187; реш.: массовые подарки; клампить по per_user_remains |
| 0185 | приглушить скрытые подарки + мультивыбор | todo | `ProfileGiftsContainer`; L; зависит от 0187; реш.: массовые подарки; сначала S-часть (dim) |
| 0186 | поиск по подаркам | todo | `ProfileGiftsContainer`, `GiftsList`; M; зависит от 0185; реш.: массовые подарки; чипы как ResaleGiftsFragment |
| 0190 | ещё массовые действия с подарками | todo | `GiftBatch`, `TL_stars`; M; зависит от 0185, 0187, 0213; реш.: массовые подарки; раннер общий с 0213 |
| 0192 | поиск/экспорт транзакций звёзд | todo | `StarsIntroActivity`; M; зависит от 0187; по умолч.: CSV share; догрузка всей истории |
| 0193 | фильтр списков по дате | todo | `SharedMedia`, подарки, транзакции; M; зависит от 0186, 0192; по умолч.: все списки; CalendarActivity диапазон |
| 0207 | копировать ссылку на коллекцию подарков | todo | `ProfileGiftsContainer`; S; рядом со стоковым Share |
| 0224 | ретрай загрузки коллекций подарков | todo | `StarsController.GiftsCollections`; S; повтор через 3 с |

## пачка 24 — студия подарков

конструктор и экспорт (видео/GIF/TGS — тяжёлая часть), fake-апгрейд с ролл-анимацией, gift grid любого пира. запросы к api.changes.tg — за тумблером, по умолчанию выкл. effort: S×2, M×2, L×3.

ворота: debug-apk, на устройстве: студия строит и экспортирует; fake-апгрейд с роллом и скрытым номером/моделью до конца; рарити; без тумблера нет запросов к третьей стороне.

| № | патч | статус | примечание |
|---|---|---|---|
| 0197 | gift studio | todo | `GiftCell`, `StarGiftPatterns`, `MediaCodec`; L; зависит от 0198, 0204, 0234; реш.: студия; по умолч.: api.changes.tg off; экспорт видео/GIF/TGS — тяжёлая часть |
| 0204 | gift grid builder | todo | экран-конструктор, `GiftCell`; L; зависит от 0197, 0185, 0186; реш.: студия; по умолч.: api.changes.tg off; рендер общий с 0197 |
| 0234 | больше подарков в студии | todo | студия подарков; L; зависит от 0197, 0198, 0204, студия подарков; реш.: gift studio; по умолч.: api.changes.tg за тумблером; третьесторонний запрос, off |
| 0198 | fake-апгрейд подарка | todo | `StarGiftSheet.doUpgrade`; M; зависит от 0201; реш.: fake upgrade с ролл-анимацией; нужна новая ролл-анимация |
| 0201 | прятать номер/модель до конца ролла | todo | `StarGiftSheet`; S; зависит от 0198; реш.: 0201 ролл; вместе с 0198 |
| 0247 | подарки любого пира в gift grid | todo | `StarsController`, `ProfileGiftsContainer`; M; зависит от 0204, студия подарков; реш.: студия подарков; надстройка над grid-билдером |
| 0248 | ранги редкости в студии подарков | todo | студия подарков, TL rarity; S; зависит от 0197, 0234, студия подарков; реш.: студия подарков; только рендер списка частей |

## пачка 25 — MTProto: инспектор, консоль, диагностика

инспектор и консоль (TL-схема в комплекте), подтверждение опасных методов, отчёты о крашах и зависаниях (0202/0203 — за серверным тумблером, нужна поддержка в tele-server). опирается на пароль из пачки 23. effort: S×3, M×1, L×2.

ворота: debug-apk, на устройстве: консоль отправляет запросы и показывает ответы; опасные методы спрашивают подтверждение; отчёты без дампа и о зависаниях уходят только при включённом сервере.

| № | патч | статус | примечание |
|---|---|---|---|
| 0088 | debug-логи и mtproto-инспектор (частично) | todo | лог/JSON-вьюер; полнота упирается в JNI tgnet; в новой очереди инспектор разросся (консоль 0195, подтверждения 0218, панели 0298) — делается вместе с ними, TL-схема в комплекте; решение мейнтейнера: инспектор и консоль; L |
| 0195 | MTProto-консоль | todo | `WebView`, `ConnectionsManager`; L; зависит от android 0088 (инспектор), android 0059, 0187, 0218, 0298; реш.: инспектор+консоль; TL-схема в комплекте |
| 0218 | консоль mtproto: опасные методы | todo | консоль mtproto; S; зависит от 0195; реш.: инспектор + консоль; список переносится как есть |
| 0298 | инспектор/консоль как панели (частично) | todo | консоль MTProto, полноэкранный фрагмент; S; зависит от 0195, 0218, android 0090; реш.: инспектор+консоль порт; идёт в составе 0195/0218 |
| 0202 | отчёты о крашах без дампа | todo | `TeleCrash`, `ApplicationExitInfo`; S; зависит от android 0037, android 0085; по умолч.: серверный тумблер; нужна поддержка tele-server |
| 0203 | отчёты о зависаниях | todo | ApplicationLoader watchdog, `TeleCrash`; M; зависит от 0202; по умолч.: серверный тумблер; нужна поддержка tele-server |

## пачка 26 — деньги: движок и ключи

wallet-engine из gettele/money: дифф переносится на ревизию Android, Rust пересобирается (NDK, все ABI), импорт по приватному ключу. страница настроек `MODE_MONEY`; флаг `walletAvailable` (0278) — первым, от него зависят остальные. безопасность критична. effort: S×3, M×1, L×2.

ворота: debug-apk, на устройстве: сборка Rust на всех ABI; импорт кошелька приватным ключом и смена секретной фразы на тестовом кошельке; квота комиссии смены ключа; копирование слов, буфер очищается через 60 с.

| № | патч | статус | примечание |
|---|---|---|---|
| 0278 | кошелёк до включения Telegram | todo | `AppGlobalConfig.walletAvailable`; S; зависит от деньги; реш.: деньги портируются; один хунк, нужен рестарт |
| 0310 | wallet-engine из gettele/money | todo | `jni/wallet-engine`, `jni/gram-wallet`, `Rust/NDK`; L; зависит от деньги; реш.: re-port diff + пересборка Rust; ревизия отличается от десктопа |
| 0311 | импорт кошельков по приватному ключу | todo | `WalletImportFragment`, `GramWalletStorage`, `WalletEngine2`; L; зависит от 0310, 0278, деньги; реш.: включая приватные ключи; безопасность критична |
| 0285 | секретная фраза кошелька без бэкапа | todo | деньги: `GramWallet`, `WalletKeysBackupFragment`; M; зависит от 0278; реш.: 0285 порт+тест-кошелёк; проверять на тестовом кошельке; MODE_MONEY |
| 0309 | квота комиссии смены ключа (BoC) (частично) | todo | Rust `gram-wallet`; S; зависит от 0285, 0310, деньги; реш.: money порт всё; проверка движка после 0310 |
| 0312 | копировать секретные слова без ожидания | todo | `WalletKeysBackupFragment`, `WalletSecretPhraseFragment`; S; зависит от деньги; default off, очистка буфера 60 с |

## пачка 27 — деньги: интерфейс и карта

отключение money, тусклые группы адреса, ссылки на транзакции (tonscan.org), 2D и 3D-шейдер карты. effort: S×5, L×2.

ворота: debug-apk, на устройстве: money выключается целиком (нужен рестарт); ссылки на транзакции открываются; карта 2D и 3D, подарки стикерами на карте; на тестовом кошельке.

| № | патч | статус | примечание |
|---|---|---|---|
| 0288 | выключить money целиком | todo | `AppGlobalConfig.walletAvailable`, `MessageObject`, `ChatActionCell`; S; зависит от деньги; override флага + ранние возвраты |
| 0290 | тусклые группы адреса | todo | `WalletActivity.formatTransactionAddress`; S; зависит от деньги; раскомментировать диммирование |
| 0313 | скрыть «you also have …» над картой | todo | `WalletActivity.updateWalletTopPanel`; S; зависит от деньги; под тумблер MODE_MONEY |
| 0286 | копировать ссылки на транзакции | todo | деньги: `WalletActivity.openTransactionSheet`; S; зависит от деньги; реш.: 0286/0296 tonscan.org; tonscan вместо серверного explorer |
| 0296 | ссылка на транзакцию из перевода | todo | `ChatActivity.fillMessageMenu`; S; зависит от 0286, деньги; реш.: 0286/0296 tonscan.org; пункт только при найденной транзакции |
| 0307 | дизайн карточки money подарком (частично) | todo | `WalletCardComponent`, `WalletCard3D`, `WalletCard2DView`; L; зависит от 0278, деньги; реш.: 0307/0317 2D+3D; 3D-шейдер включён |
| 0317 | подарки стикерами на карте money (частично) | todo | `WalletActivity`, `WalletCardView`; L; зависит от 0307, деньги, студия подарков; реш.: 0307/0317 2D+3D; драг и анимации |

## пачка 28 — скриптинг

quickjs-ng через NDK, grants, web-платформа; папка скриптов — external files dir + импорт через SAF; отдельный поток скриптов. без виджет-слоя Qt и Monaco. effort: M×1, L×2.

ворота: debug-apk, на устройстве: скрипт из папки запускается, grant «display» спрашивает согласие, TL-вызовы работают; остановка скрипта; off = сток.

| № | патч | статус | примечание |
|---|---|---|---|
| 0302 | скриптинг (QuickJS, grants, TL) (частично) | todo | `ConnectionsManager`, `MessagesController`, NDK quickjs-ng; L; зависит от 0088, скриптинг; реш.: скриптинг порт всё; по умолч.: папка + SAF; без виджет-слоя и Monaco |
| 0303 | grant «display» для скриптов (частично) | todo | `tele/scripting` consent; M; зависит от 0302, скриптинг; реш.: скриптинг порт всё; делается вместе с 0302 |
| 0320 | веб-платформа и API для скриптов (частично) | todo | `tele_script_*` JNI/Kotlin, `OkHttp`; L; зависит от 0302, скриптинг; реш.: 0320 порт включая веб-платформу; UI-поверхности по необходимости |

## пачка 29 — html-пузыри .tgw

litehtml через NDK (сборка), карточки в `ChatMessageCell` через Canvas JNI, playground-чат. зависит от скриптинга (0302) и litehtml (0314). effort: M×1, L×2.

ворота: debug-apk, на устройстве: litehtml собирается на всех ABI; .tgw-карточка рисуется в пузыре со скриптом; playground-чат открывается.

| № | патч | статус | примечание |
|---|---|---|---|
| 0314 | сборка litehtml | todo | CMake/NDK `jni`; M; зависит от litehtml; реш.: litehtml через NDK; только сборка |
| 0315 | HTML-карточки litehtml + QuickJS (частично) | todo | `ChatMessageCell`, Canvas JNI; L; зависит от 0302, 0314, litehtml; реш.: .tgw порт; перенос ~2.2k строк `tele_html.cpp` |
| 0316 | playground-чат и .tgw карточки (частично) | todo | локальный чат, `ChatMessageCell`; L; зависит от 0315, android 0087, litehtml; реш.: .tgw порт; носитель по образцу android 0087 |

## пачка 30 — низкий приоритет

патчи, которые в плане, но не горят (решение по умолчанию): подписанные стикеры в docked, беззвучное видео как GIF, починка gzip-заголовка .tgs. effort: S×2, M×1.

ворота: debug-apk, на устройстве: каждый тумблер on/off.

| № | патч | статус | примечание |
|---|---|---|---|
| 0236 | подписанные стикеры в docked-медиа | todo | `DockedMedia.kt`, `TeleDockedStrip.kt`, `EmojiView`; M; зависит от 0175, android 0096; по умолч.: поздний батч, низкий приоритет; реш.: 0175; `sendMedia` с caption |
| 0242 | беззвучное видео как gif | todo | `SendMessagesHelper`, `VideoEditedInfo.muted`; S; по умолч.: поздний батч, низкий приоритет; нужна только обратная опция |
| 0230 | починка gzip-заголовка .tgs | todo | `SendMessagesHelper`; S; зависит от студия подарков; по умолч.: поздний батч, низкий приоритет; полезно при отправке .tgs файлом |

---

## вне плана (skip)

| № | патч | причина |
|---|---|---|
| 0020 | fade опций Experimental | страницы Experimental на android нет |
| 0036 | фикс дрожания окон (win) | win32/qt оконная подсистема |
| 0043 | параллельная загрузка медиа | уже сток android (uploads независимы) |
| 0044 | таймстампы реплаев к IV-медиа | IV на android — webview; ценность сомнительна, пересмотреть |
| 0049 | двигать поздно отправленные вниз | android упорядочивает по mid — проблема не существует |
| 0051 | открывать ссылки в приложениях | системные App Links/Intent делают это сами |
| 0056 | скорость вместо перетаскивания media viewer | qt mouse-хак; у android свои жесты |
| 0067 | отключить rich-paste промпт | rich-сообщения tele на android нет |
| 0076 | панели только по клику | hover нет — на android уже только тап |
| 0079 | launch flags для сети tele | эквивалент — тумблеры инфраструктуры, отдельный патч не нужен |
| 0084 | произвольные иконки из картинки | android: наборы через activity-alias (набор иконок tele — в пачке 0); трей n/a |
| 0097 | редактор шаблона заголовка окна | объект — заголовок окна десктопа |
| 0104 | выбор приложения для сервисов | решается системно (App Links / «открывать по умолчанию») |
| 0115 | видео останавливается на конце | баг ffmpeg-стриминга tdesktop; android — exoplayer |
| 0131 | отключить жесты | ❌ десктоп-тачпад, вне плана; реш.: 0131 не портировать |
| 0135 | запись голоса без fade-in | ❌ на Android такой обработки нет |
| 0136 | фикс карточки профиля tele-чата | ❌ десктопный ресайз окна |
| 0140 | цикл видео в просмотрщике | 🟢 в стоке (`PhotoViewer`): `gallery_menu_loop` |
| 0145 | меню сообщения по ПКМ | ❌ нужна мышь |
| 0150 | {build} голое число | ❌ шаблонов заголовка нет; реш.: 0150 пропуск |
| 0152 | масштаб интерфейса 1% | ❌ слайдера масштаба нет |
| 0159 | ресайз поля ввода | ❌ drag конфликтует со скроллом |
| 0161 | перевод перед отправкой | 🟢 в стоке (`AIEditorAlert`); по умолч.: 0161 сток |
| 0163 | тайминг gif и имена загрузок | ❌ уже решено стоком |
| 0165 | выбор нескольких чатов в списке | 🟢 в стоке: long-press в списке чатов (action mode) |
| 0174 | точка посадки анимации отправки | ❌ баг десктопной анимации |
| 0177 | не перерисовывать чат-лист в простое | ❌ Qt-специфика |
| 0178 | большие crash-дампы в zip | ❌ нет minidump |
| 0180 | юзерпики в компактных строках | ❌ Qt-кэш |
| 0181 | предпросмотр чата | 🟢 в стоке: чат-пик в списке (long-press, `DialogsActivity.showChatPreview`) |
| 0183 | список «кто отреагировал» | ❌ кэш tdesktop |
| 0188 | список «кто прочитал» | ❌ кэш tdesktop |
| 0191 | pageUp/PageDown/Home/End | ❌ клавиатура/мышь |
| 0194 | oversized-стикеры как файлы | 🟢 в стоке (`MessageObject`) |
| 0199 | цитирование rich-сообщений | ❌ rich-редактора нет |
| 0214 | причина неудачного сохранения загрузки | ❌ сбрасывать нечего; реш.: 0158 подпапка Telegram/<chat> без SAF |
| 0216 | -teleoffline не глушит локальное | ❌ offline-флага на Android нет |
| 0221 | поиск любого участника при @ | 🟢 в стоке (`MentionsAdapter`) |
| 0223 | архивные стикеры per-account | 🟢 в стоке (`MediaDataController`): бага на Android нет |
| 0225 | календарь медиа в саблисте | 🟢 в стоке (`CalendarActivity`) |
| 0238 | реальное время поздней отправки | 🟢 в стоке (`SendMessagesHelper`, `ChatActivity`): сток подменяет сообщение серверным |
| 0243 | пропуск terms для mini app | 🟢 в стоке (`LaunchActivity`) |
| 0250 | невидимые символы выталкивают текст | ❌ баг движка текста tdesktop |
| 0251 | бейдж неудачной отправки как часы | ❌ стоковая «!» на Android |
| 0252 | зависание от относительных дат | ❌ баг tdesktop, у Android свой FormattedDateSpan |
| 0256 | сохранённые удалённые вне списков | 🔁 уже перенесено (`DeletedMessages`), решено android 0068 по построению |
| 0257 | линия под группой настроек | ❌ вёрстка desktop |
| 0258 | заголовок `tele #N` строчными | 🔁 уже перенесено (`TeleBuild.label()`), android 0005: метка уже `tele N` |
| 0260 | голос 128 кбит/с | 🟢 в стоке (`jni/audio.c`, `OPUS_BITRATE_MAX`) |
| 0261 | фото сжимать слабее | 🟢 в стоке (`generatePhotoSizes`): закрыто HD-фото; реш.: 0261 → android 0063 |
| 0263 | экспорт чата крупнее | ❌ экспорта нет на Android |
| 0264 | меньше минимальный размер окна | ❌ окна нет |
| 0270 | без обводки у крупного эмодзи | ❌ на Android обводки нет |
| 0271 | tele в меню «Пуск» | ❌ Windows |
| 0272 | классические отступы текста | ❌ стиль desktop |
| 0273 | починка шрифтов чата | ❌ Windows/DirectWrite |
| 0274 | чёткие иконки в shot | ❌ артефакт растеризации desktop |
| 0275 | плавная прокрутка колесом | ❌ нет мыши |
| 0277 | выделение ячеек таблиц | ❌ rich-таблиц нет |
| 0284 | прототип секретных чатов | 🟢 в стоке (`SecretChatHelper`): секретные чаты уже есть; android 0021–0024 |
| 0287 | отправка при старом кошельке | 🟢 в стоке (`GramWallet.previousWallets`): в Android нет конфликта кастоди |
| 0289 | текст «пароль money = пароль tele» | 🟢 в стоке (`PasscodeActivity`): wallet-строки уже в экране пароля |
| 0291 | клик по коллажу переключает viewer | ❌ viewer модальный (`PhotoViewer`) |
| 0292 | двойной клик выделяет слова | 🟢 в стоке (`WalletActivity`, `ChatActionCell`): комментарий уже selectable |
| 0293 | rich-редактор оставляет черновики локально | 🔁 уже перенесено (`MediaDataController.saveDraft`), гейт `TeleConfig.LOCAL_DRAFTS` в android 0021 |
| 0294 | бокс «сохранить черновик» не блокирует | ❌ нет бокса ожидания облака (`RichEditor`) |
| 0297 | ресайз окна money | ❌ оконная фича Qt; реш.: money «порт всё», но окна нет |
| 0305 | zoom колесом в viewer | ❌ колесо мыши (`PhotoViewer`) |
| 0308 | плавные глайды колеса | ❌ колесо мыши |
| 0319 | β убрана с blurred-profile-bg | ❌ только имя опции |
| lib_ui 0001 | fullscreen mini apps (Qt<6) | ❌ геометрия окна Qt |
| lib_ui 0002 | неразрывные символы не скроллят поле | 🟢 в стоке (`EditText`): multiline уже переносит по символам |
| lib_ui 0003 | метрики шрифтов на Windows | ❌ только Windows |
| lib_ui 0004 | чёткие иконки-эмодзи при большом ratio | ❌ проверить шоты 3–4× вручную (`ShotFrame.kt`) |
| lib_ui 0005 | мягкие шаги колеса | ❌ колесо мыши |
| lib_ui 0006 | кнопка maximize по состоянию окна | ❌ тайтлбар окна |
| lib_ui 0007 | exchangeText/rowSpans для скриптов | ❌ API Qt-виджетов |
| lib_ui 0008 | глайд с частотой экрана | ❌ Choreographer родной |

## решения мейнтейнера

полный список — [docs/decisions.md](decisions.md); пометка «реш.» в примечаниях — решение мейнтейнера, «по умолч.» — решение лида (мейнтейнер может переиграть).

решено мейнтейнером:

- портируем целые подсистемы: деньги (с приватными ключами 0310/0311, страница `MODE_MONEY`), скриптинг (quickjs-ng через NDK, включая веб-платформу 0320), html-пузыри `.tgw` (litehtml через NDK), центр уведомлений (JNI-хук в tgnet), mtproto-инспектор и консоль, подарки (массовые действия, локальный пароль, студия, fake-апгрейд);
- приватность — база первой: игнор-лист, ghost по чатам, ghost-schedule, затем 0166, 0227, 0228, 0229 (пачка 12);
- 0131 (отключение жестов) не портируем; 0137 — расшифровка голосовых остаётся; 0126 — закладки в `tele.db`; 0129 — полноценные компактные строки; 0138 — веб-карты; 0155 — со службой keep-alive; 0158 — подпапка `Telegram/<чат>`; 0169, 0171 — структура настроек и меню как на десктопе; 0175, 0176, 0182, 0208, 0237/0241, 0245, 0268, 0269, 0280–0283, 0300, 0304 — как записано в decisions.md.

решено лидом по умолчанию:

- 0128 (стоковый `silent_<dialogId>`), 0130/0318, 0134/0147/0156 (тумблеры по умолчанию выкл.), 0150 (пропуск), 0153, 0157, 0161 и 0261 (уже в стоке), 0162, 0166, 0167, 0168, 0189, 0192, 0193, 0197/0204 (api.changes.tg за тумблером), 0230/0236/0242 (поздний батч), 0285, 0286/0296, 0302 — см. decisions.md;
- **открытые пункты для мейнтейнера сервера:** 0202/0203 (отчёты о зависаниях и Tele-Note за серверным тумблером) и 0206 (общий фид должен принимать платформу `android` и номера сборок Android) требуют поддержки в tele-server.

## сводка

- пачек: 31 (0–30): 0–11 собраны (в них остаются отдельные `queued`), 12–30 — план, все строки `todo`
- строк в плане (пачки 12–30): 150 — 142 новых патча десктопа (0125–0322), 4 строки по прежним номерам (остатки старых пачек 11–12: пины, папки, сообщества, первое сообщение, мгновенные перемещения, lowercase, шаблон заголовка, фоны чатов, test-аккаунты, mtproto-инспектор) и 4 доработки перенесённого (0017, 0077, 0095, 0006)
- вне плана: 78 (14 прежних + 64 новых: ❌ нет аналога или десктопная специфика, 🟢 уже в стоке, 🔁 уже перенесено; см. skip)
- порядок реализации строго по пачкам; зависимости: игнор-лист, per-chat ghost и ghost-schedule (пачка 11) → 0166, 0227, 0228, 0229 — сделаны; 0169 (пачка 13) → 0170, 0241, 0244; 0171 → 0255, 0295; 0187 (пачка 23) → 0184–0193, 0217, подарочные платежи, консоль 0195; 0205 (пачка 22) → 0206, 0212, 0213, 0232, 0239, 0240, 0246; 0175 → 0236; 0197/0204 → 0198, 0201, 0234, 0247, 0248, 0230; 0310 → 0311, 0309, 0285, затем 0278 → карта 0307 → 0317; 0302 → 0303, 0320, 0315; 0314 → 0315 → 0316; 0195 → 0218, 0298 (прежние: 0101/0121 → 0071; 0012/0081/0108 → 0009; 0080 → 0045; 0118/0119 → 0050)
- нативная работа (NDK/CMake, все ABI): 0205 (jni tgnet), 0310/0311 (Rust wallet-engine), 0302 (quickjs-ng), 0314 (litehtml) — каждая в своей пачке, сборка проверяется на всех ABI
