# PATCHLIST

план переноса фич [tele](https://github.com/nitreojs/tele) (telegram desktop) на telegram android. основа — [docs/portability.md](docs/portability.md): из 127 патчей tele 98 переносимы, 20 частично, 9 не переносимы. здесь они разбиты на **пачки** (batches): порядок реализации, зависимости и статусы.

анализ исходных патчей: [nitreojs/tele](https://github.com/nitreojs/tele) v7.2.9, патчи 0001–0127. колонка «№» указывает исходный патч tele (`tele/patches/tdesktop/NNNN-*.patch`); файлы в `patches/android/` нумеруются **по позиции в очереди** (`git format-patch`), соответствие наш→исходный — в таблицах ниже.

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

порядок пачек = порядок сборки. пачка закрывается только через **ворота сборки**: все её патчи закоммичены и экспортированы → `./gradlew :TMessagesProj_App:assembleDebug` → apk передан на ручное тестирование → человеческая верификация → статусы `done`. правило подробнее: [AGENTS.md](AGENTS.md), [docs/development.md](docs/development.md#the-batch-gate).

инфраструктурные патчи (без номера tele) помечены `infra` и реализуют сразу пачку настроек tele: `0002`, `0015`, `0060`, `0064`, `0079` (редактор), `0108`, `0112`, `0115`, `0119`, `0123`.

---

## пачка 0 — фундамент: инфраструктура, брендинг, сборка

всё, без чего не работает ничего: конфиг, секция настроек, брендинг, номер сборки. ворота пачки 0 — первая сборка дебаг-релиза всего проекта.

| № | патч | статус | примечание |
|---|---|---|---|
| misc | свои api-креденциалы (`TELE_API_ID`/`TELE_API_HASH` из local.properties) | done | `0001-misc-support-custom-api-credentials` |
| infra | kotlin-плагин + скелет `tele/` (TeleConfig, TeleHooks, db) | done | `0002-misc-enable-kotlin-and-add-the-tele-skeleton` |
| infra | секция настроек «tele» (страница, строка в главных настройках, deeplinks позже) | done | `0003-feat-add-the-tele-settings-section` |
| 0007, 0091 | переименовать приложение в tele + иконка | done | `0004-misc-call-the-app-tele`; оба debug-оверлея манифеста. иконки — `0039-...`, `0043-...` и финально `0046-feat-apply-the-generated-icon-set`: актив из `android_icons/` (генерился студийным тулом) — лаунчер + round + foreground + monochrome-слой + градиентный фон, иконка уведомлений `tele_stat_notification` (4 места `setSmallIcon`), иконка секции tele — белый пузырь на `IconBackgroundColors.BLUE` (уменьшена до 17dp). строки корня tele-настроек — на `TextCell` с линейными `msg2_*`-иконками, как на внутренних экранах настроек. package rename — позже |
| misc | свой package-суффикс debug-сборок (`.tele` вместо `.beta`) | done | `0006-misc-use-a-fork-package-suffix-for-debug-builds`; не конфликтует с Telegram/Beta на устройстве |
| misc | отключение google-services (чужой firebase) | done | `0007-misc-disable-google-services-integration`; fcm-push не работает до своей конфигурации |
| 0001, 0048 | номер сборки tele в шапке списка чатов и рядом с версией в настройках | done | `0005-feat-show-the-tele-build-number`; `TELE_BUILD` из local.properties, 0 = dev |

## пачка 1 — быстрые тумблеры интерфейса

маленькие независимые фичи: каждая — один-два хука. назначение пачки — обкатать очередь и ворота сборки.

| № | патч | статус | примечание |
|---|---|---|---|
| 0017, 0043 | секунды во времени сообщений (+ время в сервисных сообщениях) | done | `0008-feat-show-seconds-in-message-times`; хук `formatterDay` в `LocaleController` |
| 0030 | скрыть папку «Все чаты» | done | `0009-debloat-hide-the-all-chats-folder`; гейт в `getDialogFilters()` |
| 0021, 0063 | скрыть кнопки звонков + подтверждение перед звонком | done | `0010-debloat-hide-call-buttons` (гейт по `phone_calls_available` в ChatActivity+ProfileActivity), `0011-feat-confirm-calls-before-starting` (VoIPHelper) |
| 0025 | открывать ссылки без подтверждения | done | `0012-feat-open-links-without-confirmation`; условие в `showOpenUrlAlert` |
| 0076 | имена вместо номеров в шапке чата | done | `0013-feat-show-names-instead-of-phone-numbers-in-chat-hea` |
| 0011 | поднять лимит аккаунтов (4→8) | done | `0014-feat-remove-the-account-limit`; always on |
| 0054 | спойлеры раскрыты всегда | done | `0015-feat-reveal-spoilers-automatically`; текст+медиа в `MessageObject` |
| 0073, 0125 | скрыть кнопки упоминаний/реакций и их бейджи в списке | done | `0016-debloat-hide-mention-and-reaction-badges`; гейт на `mentionString`/`drawMention` в `DialogCell` |
| 0038 | статичные видео-аватары | done | `0017-feat-turn-off-animated-userpics`; гейт в `ImageReceiver` + ветка видео в `ProfileActivity`; проверено только отсутствие анимации у статичных аватаров — аккаунта с видео-аватаром нет |
| 0100 | не применять счётчики replies к отложенным | done | `0018-fix-ignore-reply-counters-on-scheduled-messages`; always on |
| infra | применение тумблеров без перезапуска | done | `0019-fix-apply-interface-toggles-without-restart`; `TeleHooks.onConfigChanged`: пересоздание форматтеров + оповещение UI |
| 0001 | надпись сборки tele в шапке списка чатов при наличии истории | queued | `0020-fix-show-the-tele-build-label-in-the-chats-header`; вордмарк `telegram_logo_2` — вектор, строками не меняется; заголовок берётся из `TeleHooks.storiesHeaderTitle`. фикс регресса: emoji-статус рядом с заголовком гасился (альфа статуса была привязана к логотипу, который в текстовом режиме скрыт) — теперь статус виден и позиционируется за текстом заголовка |

## пачка 2 — приватность

| № | патч | статус | примечание |
|---|---|---|---|
| 0003 | скрыть сторис везде | queued | `0021-feat-add-privacy-toggles-for-stories-ghost-mode-scre`; гейт в `StoriesController.hasStories()` (обе перегрузки) + репост в сторис |
| 0004 | смотреть сторис незаметно | queued | тот же патч; подавлен `TL_stories_readStories` в `markStoryAsRead`, живые сторис блокируются в `StoryViewer.open` |
| 0032, 0065 | ghost mode + расширенные опции | queued | online/typing/read; contents-read глушится на сетевом слое — `0023-fix-hide-viewed-receipts-at-the-network-layer` (4 точки `readMessageContents`). **не сделано:** offline-after-send, schedule-трюк |
| 0026 | исчезающие медиа без сжигания (+ «mark as viewed») | queued | `0022-...` (гейт) + `0024-feat-add-mark-as-viewed-action-for-disappearing-medi`; пункт «mark as viewed» в меню сообщения через `TeleHooks.forceMarkViewed`. ttl-фото открываются не в `PhotoViewer`, а в `SecretMediaViewer`; сжигание идёт через `ChatActivity.sendSecretMessageRead` → `markMessageAsRead2` → `createTaskForMid` + `readMessageContents` — гейт стоит там (`sendSecretMessageRead`/`sendSecretMediaDelete`). **не покрывается:** view-once в стиле extended-media-preview — сервер сжигает их при загрузке `getExtendedMedia`, подавлять нечем |
| 0027 | скриншоты исчезающих медиа | queued | тот же патч; `FLAG_SECURE` снимается в `PhotoViewer` (per-open) и в `SecretMediaViewer` (per-open, до `addView`) при `ttl_seconds != 0`; условие — `TeleHooks.isDisappearing` (любая media с `ttl_seconds != 0`, не только документы) |
| 0113 | никогда не блокировать скриншоты | queued | гейты в `PhotoViewer`, `SecretMediaViewer` (перенесён из конструктора в `openMedia` — иначе тумблер замораживается на первом открытии), `SecretVoicePlayer`, `StoryViewer.allowScreenshots` + choke в `FlagSecureReason.updateWindowSecure` (12.x ведёт FLAG_SECURE «по причинам»: секретные чаты, noforwards, voice-once в чате, экран пароля) |
| 0016, 0074 | игнор-лист (скрыть/затухание) с пикером как в privacy | todo | не начат. разведка: хранилище готово — `tele_kv` в `TeleDatabaseHelper` (набор id через запятую, новая таблица не нужна); стоковый `PrivacyUsersActivity` **не переиспользуем** — он жёстко зашит на `TYPE_BLOCKED` и читает блок-лист `ContactsController`, нужен форк пикера; фильтр в `DialogCell` (список) и `ChatMessageCell` (в чате) |
| 0096 | черновики только на устройстве | queued | тот же патч; гейт `TL_messages_saveDraft` в `MediaDataController` |

**отложенный баг (разбор после):** после холодного старта на аккаунте с активными историями строка историй не показывается (шапка падает в режим «без историй»: заголовок сборки + emoji-статус от actionBar). Данные в базе есть; `updateStoriesVisibility` «залипает» в скрытом состоянии после старта — цикл любого тумблера (постит `storiesUpdated`) возвращает строку. Воспроизводится холодным перезапуском. Не связано с правками заголовка 0020 — на предыдущем билде пачки 2 старт в это же состояние не попадал (возможно, гонка старта, требуется разбор).

## пачка 3 — профиль и ID

| № | патч | статус | примечание |
|---|---|---|---|
| 0014, 0047, 0098, 0023 | id пира и DC в профиле (варианты формата, одна строка) | queued | `0025-feat-show-the-peer-id-and-data-center-in-the-profile`; хелпер `tele/helpers/PeerId.kt` (bot api: чат −id, канал/супергрупп −100…; dc из `photo.dc_id` → `photo_small/big.dc_id`, свой профиль — `getCurrentDatacenterId()`; города: 1,3 Miami; 2,4 Amsterdam; 5 Singapore); строки в `ProfileActivity` после username (юзер, чат) и bio (карточка юзера), у чатов — вне блока about/public, чтобы показывались всем; клик — меню копирования. строки форка в `strings_tele.xml` включены в генерацию локали (`TelegramBuildAppPlugin.kt`, `stringsXml`) — иначе `LocaleController.getString` даёт `LOC_ERR:null`. 0047 впитан: тумблеры сразу в настройках tele |
| 0013, 0066 | id подарков (обычных и коллекционных) | todo | `TL_starGiftUnique`, гифт-шиты |
| 0029 | id сообщения в меню сообщения | queued | `0026-feat-show-the-message-id-in-the-message-menu`; пункт «ID: N» первым в меню сообщения через `fillMessageMenu` (option 118), копирует bare id |
| 0056 | копировать id кастомного эмодзи | queued | `0028-...`; long-press на эмодзи → пункт «copy emoji ID» первым в меню; hit-test — `ChatMessageCell.tele_emojiIdAt` (текст + подпись), id живёт в `ChatActivity.tele_pressedEmojiId`/`tele_menuEmojiId` |
| 0080 | локальные имена людей | queued | `0029-...`; хранилище — `tele_kv` ключ `local_names` (JSON), `tele/helpers/LocalNames.kt`; подмена в `UserObject.getUserName/getFirstName`; пункт «set a name for me» в меню профиля («…»); тумблер `local_names` |
| 0072 | username-алиасы | queued | `0030-feat-link-your-own-usernames-to-chats-locally`; `tele/helpers/Aliases.kt` (`tele_kv`, ключ на аккаунт: алиас → dialogId); пункт «set an alias for me» в меню профиля рядом с локальным именем; резолв — перехват в `LaunchActivity.runLinkRequest`: `@алиас` открывает чат напрямую. автодополнение — `MentionsAdapter.showUsersResult` (алиасы первыми в результатах; `0033` — при полностью введённом алиасе подсказка не пропадает); подмена при отправке — `MediaDataController.getEntities` (`Aliases.mentionFor`): текст алиаса **не уходит на сервер** — при наличии публичного username подставляется `@username` + `TL_messageEntityMention`, без него — реальное имя (из `first_name`/`last_name`, не локальное) + `inputMessageEntityMentionName` с `InputUser`; чат — `@username`; строка `alias` в профиле; пункт «open the real @X» в контекстном меню тега (`ChatActivity.didLongPressUsername`); тап по `@алиас` открывает чат; инлайн-боты — `MentionsAdapter.searchForContextBot`: алиас резолвится в бота и уходит в inline-запрос. |
| 0013, 0066 | id подарков (обычных и коллекционных) | queued | `0027-...`; строка «Gift ID» в `StarGiftSheet` после `tableView.clear()` (3 пути: уникальный — `gift_id`, сохранённый — `savedStarGift.gift.id`, из сообщения — `stargift.id`); `tele/helpers/Gifts.kt`; тумблеры `show_gift_ids`/`show_regular_gift_ids` |

## пачка 4 — меню сообщения и боты

| № | патч | статус | примечание |
|---|---|---|---|
| 0058, 0055, 0092 | настраиваемое меню сообщения (порядок/скрытие) | queued | `0047-feat-hide-message-menu-items`; скрытие готово: `tele/helpers/MessageMenu.kt` — реестр код→имя, хранение скрытых кодов в `tele_kv`, фильтр в конце `fillMessageMenu` (все три вызова), редактор `tele/ui/settings/TeleMenuActivity.kt` из tele > interface > editor. **порядок (0055) готов** — `0057-feat-reorder-message-menu-items`: сохранённый порядок кодов применяется стабильной сортировкой в том же фильтре (коды вне списка — после, в стоковом порядке), в редакторе строки тянутся долгим тапом (ItemTouchHelper), каждое перемещение персистится. **видимая ручка (0058)** — stock `list_reorder` слева от каждой строки, касание ручки запускает drag; фикс открытия редактора: `HeaderCell`/`TextInfoPrivacyCell` больше не ошибочно unwrap-ятся как drag-wrapper. **порядок и ручка не проверены на девайсе** |
| 0028, 0005 | пейлоады кнопок ботов: поповер при зажатии + копирование | queued | `0042-feat-show-bot-button-payloads-on-long-press`; зажатие callback/switch-inline/webview-кнопки открывает диалог с пейлоадом и Copy (непечатаемые байты — hex). слот — существующий `ChatActivity.didLongPressBotButton`, где url/copy уже обрабатывались, а остальные типы молчали; тумблер `bot_button_payloads` (интерфейс, по умолчанию вкл) — `0045` |
| 0033 | view as TL (schema.jppgr.am) | queued | `0059-feat-view-messages-and-peers-as-tl`: default-off тумблер `view_as_tl`, свежий `messages.getMessages`/`channels.getMessages` для меню сообщений и full-запросы user/group/channel из профиля; бинарная TL-сериализация → URL-safe Base64/raw-deflate → schema.jppgr.am, длинные ссылки открываются через временный FileProvider redirect. **не подключены:** story/topic/sticker/gift/folder контекстные меню; ручное открытие ссылки не проверено |
| 0094 | кликабельные кастом-эмодзи в эмодзи-only сообщениях | n/a | на Android путь уже есть: `checkTextBlockMotionEvent` принимает `TYPE_EMOJIS`, тап по спану вызывает `didPressAnimatedEmoji` → `EmojiPacksAlert` с превью; десктопу патч был нужен потому, что там эмодзи-only рендерится как unwrapped media без ссылок. проверить тапом по большому кастом-эмодзи |
| 0104 | seen/reacted счётчики раздельно | n/a | на Android уже раздельно: `MessageSeenView` строится из `TL_messages_getMessageReadParticipants` (только прочтения), реакции идут через пилл (`ReactedUsersListView`) — смешения, которое чинит десктопный патч, нет |
| 0105 | отправить inline-запрос как текст | n/a | на Android кнопка отправки уже шлёт текст поля (`processSendingText`), панель инлайна — отдельный тап по результату; десктопный пункт нужен был потому, что Enter отправлял подсвеченный результат |
| 0067 | инлайн-результаты без via | queued | `0041-feat-send-inline-results-without-via`; тумблер `inline_no_via` (секция privacy + поиск): `via_bot_id` не ставится ни при отправке (`params.containsKey("bot")`), ни в ретрае (ветка `replyMarkup`), локальная отрисовка честная. **не проверено на девайсе**; игры/webview-результаты могут требовать via — поэтому тумблер по умолчанию выключен |
| 0103 | поиск по алиасам | queued | `0031-feat-search-chats-and-mentions-by-alias`; зависит от 0072. поиск чатов — `DialogsSearchAdapter.searchDialogsInternal` после `MessagesStorage.localSearch`: диалоги, чей алиас содержит запрос, добавляются в выдачу, в ячейке видно `Имя @алиас`; `@` в строке ввода — `MentionsAdapter.showUsersResult` больше не требует непустой серверной выдачи, алиасы подставляются всегда |
| 0105 | управление локальными именами и алиасами | queued | `0035-feat-manage-local-names-and-aliases-from-tele-settin`; зависит от 0072/0029. `tele/ui/settings/TeleNamesActivity.kt` — два экрана из настроек tele («your data»): список «Имя → значение», тап открывает диалог редактирования с кнопкой Delete, долгий тап открывает профиль (`0036` — индекс строки сдвинут на заголовок). Диалоги алиаса и локального имени — один общий в `TeleHooks`: `ChatActivity` и `ProfileActivity` больше не держат свои копии (`0037`), поэтому подпись, линия, отступы и Delete одинаковые везде; тема чата прокидывается через `getResourceProvider()` плейсхолдеры диалогов приглушены, `@` в поле алиаса — приглушённый префикс (`0034`) |
| 0124 | алиасы для inline-ботов | done | покрыто 0030: `MentionsAdapter.teleAliasRealUsername` резолвит алиас в бота до инлайн-запроса (`searchForContextBot`); подтверждено пользователем (memeindexerbot/zaza) |

## пачка 5 — ссылки

| № | патч | статус | примечание |
|---|---|---|---|
| 0053 | чистка трекинг-параметров | queued | `0050-feat-clean-tracking-parameters-from-links`; `tele/helpers/Tracking.kt` — полная таблица правил из tele (глобальная + провайдеры, amazon /ref= в путях, t.me не трогаем). два тумблера в privacy: `clean_opened_links` (хук в `openClickableLink`, одна точка для всех ссылок сообщений) и `clean_sent_links` (в `getEntities` после алиасов, офсеты энтити пересчитываются). **не проверено на девайсе** |
| 0078, 0079 | перезапись вставляемых ссылок по правилам + редактор | queued | `0051-feat-rewrite-pasted-links-by-rules` + `0052-feat-edit-link-rewrite-rules`; `tele/helpers/LinkRewrites.kt` — правила двух типов: домены (from→to, сохраняя www/m/mobile, несколько to — псевдослучайно по url) и regex-паттерн (find → replace с `$1..$9`, `$$` литерально). хук — перехват `android.R.id.paste` в `EditTextCaption`: перезаписанный текст вставляется в курсор, тост перечисляет замены; если правила ничего не изменили — стоковая вставка. тумблер `rewrite_pasted_links` (links-группа privacy, off) + редактор `TeleRulesActivity` (добавить/редактировать/удалить, поиск настроек). `0053-fix-rewrite-pasted-links-before-the-rich-paste-hook`: у поля ввода своя вставка — `handleRichHtmlPaste` перехватывает клипы с text/html до `EditTextCaption`, переписывание вынесено в `teleRewritePaste()` и вызывается раньше; вставка из клавиатуры (Gboard коммитит через `InputConnection.commitText`, минуя paste-механизмы) — `0054-fix-rewrite-links-pasted-from-the-keyboard`: `EditTextCaption` оборачивает InputConnection. подтверждено пользователем на обеих вставках. `0060-feat-add-link-rewrite-presets`: шесть tele presets, enabled-флаг, нормализация доменов и first/random выбор; desktop-совместимые поля читаются с миграцией. **не проверено на девайсе** |
| 0088 | `@username` → t.me в окне создания ссылки | queued | `0049-feat-turn-username-into-a-t.me-link-in-the-link-box`; `EditTextCaption.showInputDialog` OK → `LinkRewrites.usernameToLink` (regex как в tele: `^@([a-zA-Z][a-zA-Z0-9_]{3,31})$`), always on |
| 0087 | контроль превью ссылок (частично) | queued | `0055-feat-disable-link-previews`; тумблер `no_link_previews` (links-группа privacy): гейт в `isMessageWebPageSearchEnabled` — единственная точка, где и запускается поиск превью по тексту, и флаг уходит в черновики (превью не вылезает и при отправке из черновика). ручное добавление превью (`setWebPage` напрямую) работает. `0056-fix-send-with-no_webpage-when-previews-are-disabled`: сток сбрасывает поле `messageWebPageSearch` в true на больших изменениях текста, а send читает поле напрямую — без этого фикса сообщение уходило без `no_webpage` и сервер вешал превью сам. **открыто:** — (0087 закрыт). `0061-feat-skip-link-previews-for-pasted-links`: выбор режима `automatic link previews`, provenance вставки через `EditTextCaption.teleNotifyPastedUrl` (обычная вставка, rich HTML, IME commitText), гейт только на автоматический поиск — явный выбор preview в `MessagePreviewView` не блокируется; при подавлении уходит `searchLinks=false` → `no_webpage`. `0062-feat-add-manual-link-previews`: режим `only the ones you add` + пункт `Add a link preview` в меню выделения поля ввода (URL резолвится существующим `searchLinks`, автопоиск глушится до очистки поля). **не проверено на девайсе** |
| 0024 | скрыть спонсорские сообщения | queued | `0048-feat-hide-sponsored-messages-and-the-proxy-sponsor-c`; тумблер `hide_sponsored`: `getSponsoredMessages` возвращает null — чаты и боты не запрашивают и не рендерят рекламу. **не проверено на девайсе** |
| 0034 | скрыть спонсорский канал MTProxy | queued | тот же патч, тумблер `hide_proxy_sponsor`: proxy-ответ `help.promoData` обнуляет `did` и ставит `noDialog` — стоковый путь сам убирает существующий диалог. PSA не тронуты. **не проверено на девайсе** |

## пачка 6 — отправка

| № | патч | статус | примечание |
|---|---|---|---|
| 0051, 0121, 0122 | очередь текста за загружающимся медиа (+ ответы мимо очереди, форс-отправка) | queued | `0066-feat-queue-text-behind-uploading-media`; тумблеры в sending: `queue_behind_media`, `send_older_replies`, `double_enter_send`. Исправлено после device-теста: delayed upload с уже установленным `sendRequest` больше не исключается; сравнение учитывает отрицательные local IDs (раннее сообщение = больший ID), upload groups и активные sending-media до server ack; flush теперь после финального media RPC success/failure; cancel вызывает `markCancelled` + targeted flush после очистки send/upload state. Вторая причина невыхода из очереди найдена и исправлена: held-текст не регистрируется в `sendingMessages` (это происходит только внутри `performSendMessageRequest`), поэтому existence-check в flush молча выбрасывал held-записи — заменён на явный `cancelled`-флаг; safety recheck повторяется раз в 2с только пока held очередь не опустела. **нужна повторная проверка на девайсе** |
| 0097 | отложенные отправляются вовремя | queued | `0064-feat-send-scheduled-messages-on-time`; тумблер `punctual_scheduled` (секция sending): локальный таймер `tele/helpers/PunctualScheduled.kt` каждые 20с — из `scheduled_messages_v2` берутся server-scheduled (mid>0, не секретные) с `date <= now` и отправляются штатным `TL_messages_sendScheduledMessages` (тот же запрос, что «send now»); работает пока приложение живо и онлайн, при офлайне сервер отсылает сам (может опоздать). старт — `ApplicationLoader` после `checkUnsentMessages`. **не проверено на девайсе** |
| 0102 | фото в HD по умолчанию | queued | `0063-feat-send-photos-in-HD-by-default`; тумблер `hd_photos` (секция sending): один гейт в `MediaController.MediaEditState.isHighQuality()` — при отсутствии per-photo выбора (`highQuality == null`) дефолт HD, покрывает все UI-пути (PhotoViewer, attach-панель, редактор); стоковый пер-photo HD-тоггл и запоминание `photoHighQualityDefault` работают как раньше. **не проверено на девайсе** |
| 0095 | gif как видео и видео как gif | частично n/a | «видео как gif» уже в стоке: mute в PhotoViewer (`videoEditedInfo.muted`) → сток добавляет `TL_documentAttributeAnimated` (`SendMessagesHelper` 11213+) — видео уходит гифкой; «gif как видео» требует транскода gif→mp4 (на desktop `Media::Encode`, на android нет готового пути — длительность gif неоткуда взять), отложено до отдельной проработки |
| 0070 | реплай на удалённое: скип или цитата | todo | зависит от 0019/0059 (хранение удалённых, пачка 7): режим «цитата» без локального текста удалённого невозможен, «скип» без хранилища неотличим от стока (удалённое просто исчезает); переносить вместе с пачкой 7 |
| 0008 | quick replies в группах и каналах | queued | `0065-feat-offer-quick-replies-in-groups`: тумблер `quick_replies_in_groups`; `/` autocomplete показывает Business quick replies в разрешённых группах. Исправлено после device-теста: shortcut content fetch-ится через `messages.getQuickReplyMessages`; IDs больше не уходят в обычный `messages.forwardMessages` (который трактовал shortcut IDs как IDs history и давал чужой текст/стикер). Каждый item отправляется как fresh text/photo/document через `SendMessageParams`, поэтому retry использует send/upload путь; отсутствующий локальный файл у серверного document не считается причиной отказаться от remote media reference. Private-chat replay не менялся. **нужна повторная проверка на девайсе** |
| 0116 | пересылка защищённых как копий | todo | перехват форварда → пересборка/перекачка |

## пачка 7 — локальное хранение истории

| № | патч | статус | примечание |
|---|---|---|---|
| 0019, 0059 | хранить удалённые сообщения (в т.ч. самоудалённые) | todo | хуки `deleteMessages`/`processDeleteMessages` + `tele_*` таблица |
| 0018, 0062 | история правок сообщения (+ просмотр как чат) | todo | хук `updateMessageEdited` + версии в fork-БД |
| 0101 | сохранённые черновики (частично: без rich-IV) | todo | снапшот состояния поля + браузер черновиков |

## пачка 8 — tele server

сервер tele: клиент только скачивает публичный список и матчит локально; аккаунтные данные не отправляются никогда.

| № | патч | статус | примечание |
|---|---|---|---|
| 0009 | метки с tele-сервера (verified/scam/fake/support) | todo | https-фетч + перезапись флагов в `putUser/processChat` |
| 0012 | бейджи верификации везде | todo | зависит от 0009 |
| 0083 | очистка кэша бейджей + тултипы верификации | todo | зависит от 0009 |
| 0093 | юзернеймы с tele-сервера | todo | фид `usernames` → профиль |
| 0110 | бейджи tele на личном канале в профиле | todo | зависит от 0009; база `linked-channel-in-profile` |
| 0037 | краш-репорты на tele server | todo | поверх fork-crash handler; показ текста + ручная отправка |

## пачка 9 — апдейтер и what's new

| № | патч | статус | примечание |
|---|---|---|---|
| 0006 | in-app апдейтер с релизов репозитория tele | todo | свой UpdateHelper; ориентир — порт Nekogram |
| 0039 | what's new после обновления | todo | сверка версии + changelog, поверх апдейтера |
| 0075 | what's new как локальный чат (частично) | todo | синтетический диалог или экран в стиле чата — обдумать |
| 0111 | объяснение отсутствующего changelog | todo | UX вокруг апдейтера |
| 0112 | новые настройки после апдейта (бейджи «new») | todo | поверх инфраструктуры настроек |

## пачка 10 — спецфичи

| № | патч | статус | примечание |
|---|---|---|---|
| 0046, 0082 | вычисление «= выражение» (calcmula) + живое превью | todo | перехват отправки → http → пересборка; панель над полем |
| 0089, 0107, 0114 | шоты: сообщение как картинка (1x–4x, что показывать) | todo | офф-скрин рендер `ChatMessageCell`; самая трудоёмкая |
| 0061 | пипетка в фоторедакторе | todo | `LPhotoPaintView`/палитра |
| 0085 | цена коллекционного подарка на дату покупки | todo | https-курс TON + кэш |
| 0049 | коллекционные подарки в see.tg | todo | кнопка + deep link |
| 0109, 0118 | docked media над полем ввода (частично) | todo | большая перестройка чата; держать в конце |

## пачка 11 — списки и лимиты

| № | патч | статус | примечание |
|---|---|---|---|
| 0126 | пины чатов сверх лимита (локальные) | todo | fork-хранилище + перехват ошибки лимита |
| 0127 | папки сверх лимита (локальные) | todo | fork-фильтры вне серверной синхронизации |
| 0120 | скрывать сообщества | todo | образец `debloat/community-dialogs` |
| 0031 | перейти к первому сообщению | todo | образец `feature/jump-to-beginning` |
| 0084 | мгновенное перемещение чатов (частично) | todo | без десктопного freeze — только идея |

## пачка 12 — прочее и эксперименты

| № | патч | статус | примечание |
|---|---|---|---|
| 0022, 0035 | lowercase всего интерфейса | todo | перехват `LocaleController.getString` |
| 0040 | брендинг «tele» во внутренних строках | done | `0038-feat-call-the-app-tele-in-its-own-texts`: стоковые строки, называющие приложение, перекрываются из `TMessagesProj_App/src/main/res/values/tele_strings.xml` (app-модуль побеждает библиотеку на merge) — стоковые strings.xml не тронуты. сервисные упоминания (Premium, модераторы, FAQ) и имена папок на диске оставлены как есть |
| 0042 | секции и поиск настроек tele | done | `0040-feat-split-tele-settings-into-sections-and-add-them-.patch`; `TeleSettingsActivity(mode)` — корень открывает interface/privacy/ids/your data, каждая секция — свой экран; `tele/ui/settings/TeleSearch.kt` добавляет все секции и тумблеры в массив поиска `ProfileActivity.SearchAdapter` (guid 950+, хлебные крошки tele > секция), хук — оборачивание возвращаемого массива `onCreateSearchArray`. `0044`: строки секций в корне — `SettingsActivity.SettingCell` с цветными иконками и подписями, в одной секции с версией tele |
| 0010, 0041 | шаблон заголовка экрана диалогов (частично) | todo | движок переменных на базе шапки чатов |
| 0069 | локальные фоны чатов (частично) | todo | per-chat обои уже в стоке; добавить форс-локальность |
| 0071 | аккаунты test-сервера (частично) | todo | нужен нативный per-account флаг `isTestBackend` |
| 0090 | debug-логи и mtproto-инспектор (частично) | todo | лог/JSON-вьюер; полнота упирается в JNI tgnet |

---

## вне плана (skip)

| № | патч | причина |
|---|---|---|
| 0020 | fade опций Experimental | страницы Experimental на android нет |
| 0036 | фикс дрожания окон (win) | win32/qt оконная подсистема |
| 0044 | параллельная загрузка медиа | уже сток android (uploads независимы) |
| 0045 | таймстампы реплаев к IV-медиа | IV на android — webview; ценность сомнительна, пересмотреть |
| 0050 | двигать поздно отправленные вниз | android упорядочивает по mid — проблема не существует |
| 0052 | открывать ссылки в приложениях | системные App Links/Intent делают это сами |
| 0057 | скорость вместо перетаскивания media viewer | qt mouse-хак; у android свои жесты |
| 0068 | отключить rich-paste промпт | rich-сообщения tele на android нет |
| 0077 | панели только по клику | hover нет — на android уже только тап |
| 0081 | launch flags для сети tele | эквивалент — тумблеры инфраструктуры, отдельный патч не нужен |
| 0086 | произвольные иконки из картинки | android: наборы через activity-alias (набор иконок tele — в пачке 0); трей n/a |
| 0099 | редактор шаблона заголовка окна | объект — заголовок окна десктопа |
| 0106 | выбор приложения для сервисов | решается системно (App Links / «открывать по умолчанию») |
| 0117 | видео останавливается на конце | баг ffmpeg-стриминга tdesktop; android — exoplayer |

## сводка

- пачек: 13 (0–12); патчей в плане: 98 переносимых + частичные части 20 (0075, 0087, 0090, 0101, 0109+0118, 0121+0122, 0010+0041, 0069, 0071, 0012, 0084) + 2 infra
- вне плана: 14 (см. skip)
- порядок реализации строго по пачкам; зависимости внутри пачек указаны в примечаниях (0103/0124 → 0072; 0012/0083/0110 → 0009; 0082 → 0046; 0121/0122 → 0051)
