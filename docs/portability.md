# Патчи tele → Telegram Android: карта переносимости

## Что это

[tele](https://github.com/nitreojs/tele/) — патч-очередь для **Telegram Desktop** (tdesktop v7.2.9): исходный разбор — 127 патчей, каждый — отдельная фича или фикс. Вопрос: какие из этих фич можно перенести на **Telegram Android**? Номера патчей в этом документе — **текущие номера очереди десктопа** (очередь была перенумерована, три патча влиты в соседние); карта старый → новый — [desktop-numbers.md](desktop-numbers.md).

Объект переноса:

- [Telegram Android](https://github.com/drklo/telegram) — локальный чекаут **12.10.6 (7112)**, папка `Telegram/` (TMessagesProj).
- Образец патч-культуры Android-форков — [inugram](https://github.com/teidesu/inugram) (stgit-патчсет поверх свежего Telegram Android). Его правила задают то, *как* патч должен выглядеть на Android:
  - минимальный хук в stock-коде + ранняя проверка тумблера (`InuConfig.*.getValue()`) + вся логика в Kotlin-хелперах (`src/kotlin/helpers/`);
  - default off = поведение стока один в один;
  - **не трогать `TLRPC.java`** (автогенерат) и **не менять схему stock-БД** — форк-состояние живёт в `inu_*`-таблицах / `inu_kv`;
  - форк-код — в новых файлах, new API — с префиксом `inu_`, `private → public` вместо дублирования;
  - настройки форка — страницы `SettingsPageActivity` + поиск/deeplinks (`SearchRegistry`), строки в `strings_inu.xml`.

> **Важно:** делаем **свой** форк tele для Telegram Android. Inugram — архитектурный ориентир, не источник для копирования кода: свои классы (`TeleConfig`, `tele_*`-хелперы), свои ресурсы (`strings_tele.xml`), свои тумблеры. Там, где подход или код вдохновлены inugram (а через него — Nekogram, NagramX и др.), указываем кредиты.

## Методика

Каждый из 127 патчей прочитан; оценивалась переносимость **фичи** (не кода — C++/Qt-реализация tele не переиспользуется), с проверкой:

1. Какие системы tdesktop задействует патч и есть ли Android-эквиваленты (точки внедрения в `MessagesController`, `SendMessagesHelper`, `ChatActivity`, `PhotoViewer`, `MessagesStorage`, `StoriesController`, tgnet и т.д.). Все названные классы сверены по исходникам 12.10.6.
2. Есть ли уже готовый аналог в inugram (по `series` и `FEATURES.md`) — такие патчи «переносить не нужно», но указание на аналог даёт готовый каркас.
3. Desktop-специфика (окна, тайтлбар, трей, мышь, self-update, launch flags) — есть ли осмысленный мобильный эквивалент.

## Легенда

| Вердикт | Значение |
|---|---|
| ✅ **переносим** | фича реализуема на Android напрямую; указаны точки внедрения и/или готовый аналог inugram |
| ⚠️ **частично** | ядро переносимо, но часть функциональности десктоп-специфична либо висит на отсутствующих подсистемах tele |
| ❌ **не переносим** | фича принципиально десктопная, либо проблема, которую она решает, на Android отсутствует по построению |
| 🏗 **инфраструктура** | патч чинит/строит собственную инфраструктуру tele (секция настроек, опции, экспорт); на Android её роль уже играет инфраструктура inugram — переносить нечего, фичи вешаются на неё |

## Сводка

**98 переносимы · 20 частично · 9 не переносимы** (из 127 исходных патчей; в текущей нумерации это 124 номера — старые 0043, 0079 и 0118 влиты в 0017, 0077 и 0107).

Из 98 «переносимых» **около 40 имеют готовый аналог или готовую базу в inugram** (полное покрытие — hide-stories, show-seconds, strip-tracking, message-menu, cloud-drafts, community-dialogs, id-in-profile, jump-to-beginning, multi-account, hide-call-action, call-confirmation, disable-chat-title-phone, folders-display-mode, branding, settings-ui; остальные — смежная поверхность для расширения), ещё 2 — фактически стоковое поведение Android (0043, 0051). Паттерн реализации — «как у inugram, но своё» (см. раздел «Как переносить»).

Типичные причины «не переносим» (все 9):

| Категория | Патчи |
|---|---|
| Оконная подсистема Windows/Qt (рамки, развёрнутые окна, mouse-drag) | 0036, 0056 |
| Заголовок окна / тайтлбар как объект | 0097 |
| Проблема отсутствует: Android хранит сообщения по mid — «позднее» сообщение само встаёт вниз | 0049 |
| Проблема решена ОС: App Links / Intent сами открывают ссылки в нативных приложениях | 0051 |
| Нет объекта: на мобильном нет hover-поведения мыши | 0076 |
| Фича о несуществующем на Android объекте (страница Experimental настроек tdesktop) | 0020 |
| Баг десктопного ffmpeg-стримингового движка (Android — ExoPlayer/MediaCodec) | 0115 |
| Фича о rich-сообщениях tele, которых на Android нет | 0067 |

Смежные, но обязательные оговорки для «частично»: системный трей не имеет мобильного аналога (0084, 0089 — остаётся иконка приложения/уведомлений, в inugram уже покрыто `hooks/icon-replacement`), launch flags заменяются тумблерами (0079), docked media (0107) и очередь отправки tele (0118, 0119) висят на tele-подсистемах, которых на Android нет и которые пришлось бы портировать отдельно.

---

## Сводная таблица (исходные 127 патчей, текущие номера)

Названия патчей — по именам файлов в `tele/patches/tdesktop/`.

| № | Фича | Вердикт | Ключевая причина / точка внедрения / аналог inugram |
|---|---|---|---|
| 0001 | build number в тайтлбаре | ✅ | шапка списка чатов «Telegram» (`DialogsActivity`, `actionBar.setTitle(AppName)`) + рядом с версией в настройках (0047) |
| 0002 | секция tele в настройках | ✅🏗 | своя инфраструктура в духе InuConfig (кредиты inugram): TeleConfig + страницы настроек |
| 0003 | скрыть сторис | ✅ | `StoriesController`; аналог `debloat/hide-stories` |
| 0004 | смотреть сторис незаметно | ✅ | подавление `StoriesController.markStoryAsRead`/просмотров |
| 0005 | пейлоады кнопок ботов в тултипах | ✅ | тултип/поповер при зажатии кнопки; парсинг `TL_keyboardButton*` (связан с 0028) |
| 0006 | self-update из GitHub релизов | ✅ | свой in-app updater с релизов репозитория tele (будет выложен позже); подход — как in-app апдейтер inugram (порт Nekogram) |
| 0007 | переименовать приложение в tele | ✅ | manifest/strings + лончер-иконка (связан с 0089); ориентир `misc/branding` |
| 0008 | quick replies в группах/каналах | ✅ | отправка шортката как обычных сообщений (`SendMessagesHelper`) |
| 0009 | метки с tele-сервера (verified/scam/fake) | ✅ | HTTP-фетч + перезапись флагов в `MessagesController.putUser/processChat` |
| 0010 | живой шаблон тайтлбара | ⚠️ | шаблонизатор → кастомный заголовок списка чатов (inugram уже имеет базу) |
| 0011 | снять лимит аккаунтов | ✅ | `UserConfig.MAX_ACCOUNT_COUNT`; аналог `feature/multi-account` |
| 0012 | verified-бейджи везде | ⚠️ | точки UI есть; рендер кастомных бейджей зависит от 0009 |
| 0013 | id подарков | ✅ | `TL_starGiftUnique` в гифт-шитах (`ui/Stars`, `ui/Gifts`) |
| 0014 | id пира в профиле | ✅ | `ProfileActivity`; аналог `feature/id-in-profile` |
| 0015 | deeplink-ссылки на настройки tele | ✅🏗 | уже есть: SearchRegistry/deeplinks inugram |
| 0016 | игнор-лист: скрыть/затухание | ✅ | data-layer фильтр; близко `feature/hide-blocked-messages` (без fade) |
| 0017 | секунды во времени сообщений (+ время в сервисных сообщениях, влит бывший 0043) | ✅ | `LocaleController`; к тексту `TL_messageService` в `MessageObject` дописывается « · HH:mm:ss»; аналог `feature/show-seconds` |
| 0018 | история правок сообщения | ✅ | хук `updateMessageEdited` + `inu_`-таблица версий |
| 0019 | хранить удалённые сообщения | ✅ | хук `deleteMessages`/`processDeleteMessages` + `inu_`-таблица |
| 0020 | fade недоступных опций Experimental | ❌ | страницы Experimental на Android нет |
| 0021 | скрыть кнопки звонков | ✅ | `ChatActivity`/`ProfileActivity`; аналог `feature/hide-call-action` |
| 0022 | lowercase всего UI | ✅ | единая точка `LocaleController.getString` |
| 0023 | DC в профиле | ✅ | `TLRPC.FileLocation.dc_id` → строка в `ProfileActivity` |
| 0024 | скрыть спонсорские сообщения | ✅ | гейт sponsored-блока в `MessagesController` (+`ChatActivity`) |
| 0025 | открывать ссылки без подтверждения | ✅ | ранний return в `AlertsCreator.showOpenUrlAlert` |
| 0026 | исчезающие медиа без сжигания | ✅ | подавление `markMessagesContentAsRead` + пункт «mark as viewed» |
| 0027 | скриншоты исчезающих медиа | ✅ | снятие `FLAG_SECURE` в `PhotoViewer` |
| 0028 | копировать callback-данные кнопок | ✅ | данные в `TL_keyboardButton*`, пункт в меню сообщения |
| 0029 | id сообщения в меню | ✅ | хук меню `ChatActivity.createMenu` |
| 0030 | скрыть папку «Все чаты» | ✅ | `FilterTabsView`; аналог `feature/folders-display-mode` |
| 0031 | перейти к первому сообщению | ✅ | `ChatActivity` + подгрузка истории; аналог `feature/jump-to-beginning` |
| 0032 | ghost mode | ✅ | подавление receipts/typing/online/сторис-просмотров в `MessagesController` (+schedule-трюк) |
| 0033 | view as TL (schema.jppgr.am) | ✅ | `ConnectionsManager` + сериализация TLRPC; inugram уже показывает JSON |
| 0034 | скрыть спонсорский канал MTProxy | ✅ | гейт промо-диалога в `MessagesController` (`TL_help_promoData`) |
| 0035 | lowercase текстов tele | ✅ | стилистика строк самого форка; аналог `misc/branding` |
| 0036 | фикс дрожания развёрнутых окон (Win) | ❌ | Win32/Qt-оконный фикс |
| 0037 | краш-репорты на tele-сервер | ✅ | UncaughtExceptionHandler + HTTPS; база (crash sheet) уже есть в inugram |
| 0038 | статичные видео-аватары | ✅ | гейт в `ImageReceiver` при установке аватара |
| 0039 | what's new после обновления | ✅ | сверка версии + JSON по HTTPS; вешается на готовый updater inugram |
| 0040 | звать приложение tele везде | ✅ | ресурсы/лейбл; аналог `misc/branding` |
| 0041 | шаблоны заголовка окна | ⚠️ | системного заголовка нет; шаблон → заголовок экрана диалогов |
| 0042 | группировка+поиск настроек tele | ✅🏗 | уже есть в инфраструктуре inugram |
| 0043 | параллельная загрузка медиа в чаты | ✅ | фактически сток Android (uploads независимы) |
| 0044 | таймстампы реплаев к IV-медиа | ⚠️ | для обычных медиа уже есть; IV-часть привязана к десктопному рендереру |
| 0045 | вычисление «= выражение» (calcmula) | ✅ | перехват отправки → HTTP → пересборка текста |
| 0046 | show peer ids в настройки tele | ✅🏗 | аналог `feature/id-in-profile` |
| 0047 | build в главном меню | ✅ | `SettingsActivity` versionView / шапка fork-дровера |
| 0048 | коллекционные подарки в see.tg | ✅ | кнопка + deep link в `StarGiftSheet`/`GiftSheet` |
| 0049 | двигать поздно отправленные вниз | ❌ | Android упорядочивает по mid — проблема не существует |
| 0050 | очередь за загружающимся медиа | ✅ | hold текста до конца upload; состояние уже трекается в `SendMessagesHelper` |
| 0051 | открывать ссылки в десктоп-приложениях | ❌ | App Links/Intent делают это системно |
| 0052 | чистка трекинг-параметров | ✅ | аналог `feature/strip-tracking` (правила AdGuard) |
| 0053 | спойлеры раскрыты всегда | ✅ | глобальный гейт в `MessageObject`/`SpoilerEffect` |
| 0054 | tele-пункты внизу меню сообщения | ✅ | покрыто кастомизируемым меню inugram (`feature/message-menu`) |
| 0055 | копировать id кастомного эмодзи | ✅ | hit-test спанов в `ChatMessageCell` + пункт меню |
| 0056 | скорость вместо перетаскивания в media viewer | ❌ | Qt mouse-хак; у Android PhotoViewer свои жесты |
| 0057 | переупорядочить/скрыть пункты меню сообщения | ✅ | уже есть: `feature/message-menu` (порт NagramX) |
| 0058 | хранить и самоудалённые сообщения | ✅ | развитие 0019 |
| 0059 | server/updates на странице tele | ✅🏗 | инфраструктура inugram |
| 0060 | пипетка в фоторедакторе | ✅ | в стоке пипетка есть в `ColorPickerBottomSheet` (три тапа); порт — кнопка в один тап у палитры `LPhotoPaintView` со стоковой лупой |
| 0061 | история правок как чат | ✅ | снапшоты версий + фрагмент с ячейками чата |
| 0062 | скрыть/подтвердить кнопки звонков | ✅ | аналоги `feature/hide-call-action` + `feature/call-confirmation` |
| 0063 | группировка настроек tele | ✅🏗 | инфраструктура inugram |
| 0064 | больше ghost-опций | ✅ | подавление `TL_account.updateStatus`/readReactions после действий |
| 0065 | id обычных подарков | ✅ | данные есть, строка в карточке подарка |
| 0066 | инлайн-результаты без via | ✅ | вместо `TL_messages_sendInlineBotResult` собрать обычное сообщение |
| 0067 | отключить rich-paste промпт | ❌ | rich-сообщения — фича tele, на Android промпта нет |
| 0068 | локальные фоны чатов | ⚠️ | per-chat обои уже в стоке; добавка — форс-локальность и удаление навязанного |
| 0069 | реплай на удалённое: скип/цитата | ✅ | фильтрация `reply_to` при отправке |
| 0070 | аккаунты test-сервера | ⚠️ | нужен нативный per-account флаг `isTestBackend` (JNI), жест → long-press |
| 0071 | username-алиасы | ✅ | `inu_kv`-маппинг + `MentionsAdapter` + подстановка при отправке |
| 0072 | скрыть кнопки упоминаний/реакций | ✅ | гейт `showButton` в `ChatActivitySideControlsButtonsLayout` |
| 0073 | пикеры для игнора/ghost-чатов | ✅ | стандартный пикер пиров; аналоги `hide-blocked-messages`/`paranoia` |
| 0074 | what's new как локальный чат | ⚠️ | реализуемо (синтетический чат или экран в стиле чата); решение требует обдумывания |
| 0075 | имена вместо номеров в шапке | ✅ | аналог `debloat/disable-chat-title-phone` |
| 0076 | панели только по клику (без hover) | ❌ | hover нет, на мобильном уже только тап |
| 0077 | перезапись вставляемых ссылок + редактор правил и пресетов (влит бывший 0079) | ✅ | хук вставки; база — `feature/strip-tracking`/`web-preview`; страница редактора на инфраструктуре форка |
| 0078 | локальные имена людей | ✅ | подмена на слое `putUser`/`UserObject.getUserName` |
| 0079 | launch flags для сети tele | ⚠️ | нет launch flags; эквивалент — тумблеры; вешается на updater inugram |
| 0080 | превью calcmula над полем | ✅ | переносится вместе с 0045 (calcmula) |
| 0081 | очистка кэша бейджей tele | ✅ | кнопка + тултипы на инфраструктуре настроек |
| 0082 | мгновенное перемещение чатов | ⚠️ | freeze-механика десктопная; переносима только идея без анимации |
| 0083 | цена коллекционного юзернейма/номера на дату покупки | ✅ | HTTPS (курс TON) + кэш; карточка `FragmentUsernameBottomSheet`, не подарки |
| 0084 | свои иконки приложения и трея | ⚠️ | иконки приложения/уведомлений — есть (`hooks/icon-replacement`); трея нет |
| 0085 | управление превью ссылок | ⚠️ | выбор/отключение — есть (web-preview); форс чужого превью — доработка |
| 0086 | @username → t.me в окне ссылки | ✅ | regex в `showInputDialog` создания ссылки |
| 0087 | сообщение как картинка (shot) | ✅ | офф-скрин рендер `ChatMessageCell` в Canvas |
| 0088 | debug-логи + MTProto-инспектор | ⚠️ | лог/JSON-вьюер переносим; полнота инспектора упирается в JNI tgnet |
| 0089 | иконки приложения и трея tele | ⚠️ | лончер-иконки — есть; трей — нет |
| 0090 | имя пункта «Copy Callback Data» | ✅ | покрыто `feature/message-menu` (long-tap кнопки бота) |
| 0091 | юзернеймы с tele-сервера | ✅ | HTTP-фетч + встройка в список юзернеймов профиля |
| 0092 | кликабельные кастом-эмодзи в эмодзи-only | ✅ | хендлеры в `ChatMessageCell` (AnimatedEmojiSpan) |
| 0093 | GIF как видео и видео как GIF | ✅ | подмена атрибутов документа при отправке; близко `feature/send-mp4-as-video` |
| 0094 | черновики только на устройстве | ✅ | аналог `debloat/cloud-drafts` |
| 0095 | отложенные отправляются вовремя | ✅ | локальный планировщик + «send now» |
| 0096 | id и DC в одной строке | ✅ | компоновка строк профиля; база `feature/id-in-profile` |
| 0097 | редактор шаблона заголовка окна | ❌ | объект фичи — заголовок окна |
| 0098 | не применять replies-счётчики к отложенным | ✅ | guard в `MessageObject` (replies) |
| 0099 | сохранённые черновики (много на чат) | ⚠️ | ядро реализуемо; rich-IV-черновики и Ctrl+S — десктоп |
| 0100 | фото в HD по умолчанию | ✅ | форс `photoEntry.highQuality` в `PhotoViewer`/attach-панели |
| 0101 | поиск чатов по алиасам | ✅ | встройка в `DialogsSearchAdapter` из `inu_`-таблицы (зависит от 0071) |
| 0102 | seen/reacted счётчики раздельно | ✅ | `MessageSeenView` |
| 0103 | отправить inline-запрос как текст | ✅ | пункт при активном inline-боте → обычный sendMessage |
| 0104 | какое приложение открывает сервис | ⚠️ | технически Intent с setPackage; но это уже делают App Links/chooser ОС |
| 0105 | шоты 1x–4x, свои сообщения как входящие | ✅ | масштабированный офф-скрин рендер (зависит от 0087) |
| 0106 | экспорт/импорт настроек tele | ✅🏗 | уже есть: export/import JSON в inugram |
| 0107 | docked media над полем ввода + подписи и паритет с send-боксом (влит бывший 0118) | ⚠️ | концепт переносим; висит на tele-инфраструктуре черновиков/очереди |
| 0108 | бейджи tele на личном канале в профиле | ✅ | строка личного канала; база `feature/linked-channel-in-profile` |
| 0109 | объяснение отсутствующего changelog | ⚠️ | UX-идея → в готовый updater inugram |
| 0110 | новые настройки после апдейта | ✅🏗 | бейджи «new» поверх SettingsPageActivity |
| 0111 | никогда не блокировать скриншоты | ✅ | не ставить `FLAG_SECURE` (в т.ч. secret chats/PhotoViewer) |
| 0112 | что показывать в шотах | ✅ | флаги офф-скрин рендера (зависит от 0087) |
| 0113 | короткие описания настроек | ✅🏗 | строки форка в ресурсах; принцип уже соблюдён |
| 0114 | пересылка защищённых как копии | ✅ | перехват форварда → пересборка/перекачка в `SendMessagesHelper` |
| 0115 | видео останавливается на конце | ❌ | баг десктопного AudioTrack/миксера ffmpeg |
| 0116 | скрывать настройки до включения родителя | ✅🏗 | уже есть: условные секции/ExpandableBoolGroup inugram |
| 0117 | скрывать сообщества | ✅ | аналог `debloat/community-dialogs` (display modes) |
| 0118 | ответы мимо очереди за медиа | ⚠️ | логика есть, носитель (очередь tele 0050) надо портировать |
| 0119 | отправить сейчас по двойному Enter | ⚠️ | Enter нет; нужен другой триггер + очередь 0050 |
| 0120 | перегруппировка настроек отправки | ✅🏗 | страницы инфраструктуры inugram |
| 0121 | алиасы для inline-ботов | ✅ | подстановка перед resolve (зависит от 0071) |
| 0122 | скрыть бейджи упоминаний/реакций в списке | ✅ | гейт отрисовки в `DialogCell` (расширение 0072) |
| 0123 | пины чатов сверх лимита (локальные) | ✅ | fork-хранилище пинов + перехват ошибки лимита |
| 0124 | папки сверх лимита (локальные) | ✅ | fork-хранилище фильтров вне серверной синхронизации |

---

## Детальный разбор

### 0001–0032

#### 0001 — show the tele build number in the title bar
- **Суть:** новое ядро `tele_build` (номер релиза из CMake-переменной TELE_BUILD), метка «TELE #N / TELE DEV» рисуется в тайтлбаре окна.
- **Вердикт:** ✅ переносим — на Android есть эквивалент «тайтлбара»: шапка списка чатов с надписью «Telegram» (крупный сворачивающийся заголовок в стиле SliverAppBar).
- **Android:** номер сборки рядом с «Telegram» в шапке списка чатов — `DialogsActivity` (`actionBar.setTitle(getString(R.string.AppName))`, ~строка 3517, внутренний хедер-класс) — плюс рядом с версией в настройках (0047).

#### 0002 — add a tele section to the settings
- **Суть:** инфраструктура — новая секция настроек `settings_tele` с кнопкой в главном меню настроек.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — делаем свою по образцу InuConfig (кредиты inugram), не копию.
- **Android:** `TeleConfig` (тумблеры, default off = сток) + свои страницы настроек в духе `SettingsPageActivity`; строки `strings_tele.xml`, deeplinks `tg://settings/tele/...`.

#### 0003 — add an option to hide stories everywhere
- **Суть:** тумблер «hide stories»: сторис считаются истёкшими, исчезают из профиля/бара/визуализатора, ссылки на сторис не открываются; плюс каркас опций `tele_options`.
- **Вердикт:** ✅ переносим — чистые серверные/UI-фильтры, десктоп-специфики нет.
- **Android:** `org.telegram.ui.Stories.StoriesController` (списки/кольца), `StoryViewer`, `DialogsActivity` (бар сторис); аналог в inugram: `debloat/hide-stories`.

#### 0004 — add an option to watch stories invisibly
- **Суть:** тумблер «watch stories invisibly»: не отправлять серверу markAsRead/просмотры (кроме лайв-сторис).
- **Вердикт:** ✅ переносим — вся механика — подавление исходящих API-запросов.
- **Android:** `StoriesController.markStoryAsRead` и инкремент просмотров (StoriesController/StoryViewer); аналога в inugram нет.

#### 0005 — show bot button payloads in tooltips
- **Суть:** наведение на кнопку бота показывает тултип с её содержимым (callback-данные, URL, inline-запросы, request peer и т.д.).
- **Вердикт:** ✅ переносим — парсинг пейлоада (`HistoryMessageMarkupButton`) переносим полностью; вместо ховера — тултип/поповер при зажатии кнопки бота.
- **Android:** `org.telegram.tgnet.tl.TL_keyboard` (`TL_keyboardButtonCallback` и др.) + long-press-поповер над кнопкой в `ChatMessageCell`/`ChatActivity`; связан с 0028 (копирование пейлоада).

#### 0006 — update from the tele github releases
- **Суть:** self-updater: проверка GitHub-релизов, скачивание, «restart to update», тумблер автообновления. Докачка (`.part`, `Range: bytes=N-`, проверка `Content-Range`, 416 = уже скачано, 200 вместо 206 = с нуля), sha256 по готовому файлу, при сетевых ошибках повтор по лестнице 1 / 5 / 15 / 60 мин.
- **Вердикт:** ✅ переносим — свой in-app updater с релизов репозитория tele (репозиторий будет выложен позже): проверка последнего релиза → скачивание APK → установка.
- **Android:** свой хелпер в духе UpdateHelper inugram (порт Nekogram, с кредитами): `SharedConfig` (сохранённая версия) + `LaunchActivity` (проверка при старте) + скачивание/установка APK.

#### 0007 — rename the app to tele
- **Суть:** брендинг: имя, bundle id, ресурсы, «Telegram Desktop» → «tele» во всех строках.
- **Вердикт:** ✅ переносим — текстовые/ресурсные замены, механика один в один.
- **Android:** applicationId/label (build.gradle, strings.xml, LaunchActivity, уведомления) **+ лончер-иконка tele** (связан с 0089); ориентир: `misc/branding` inugram.

#### 0008 — send quick replies in groups and channels
- **Суть:** Business quick replies предлагаются в автокомплите групп/каналов и отправляются как обычные сообщения (сервер шорткаты туда не принимает).
- **Вердикт:** ✅ переносим — Android полноценно поддерживает quick replies; механика «отправить как обычные» переносится на слой отправки.
- **Android:** `org.telegram.ui.QuickRepliesSettingsActivity` + хранение в MessagesController/MessagesStorage; отправка — `SendMessagesHelper`/`ChatActivity`.

#### 0009 — apply verification and marks from the tele server
- **Суть:** клиент тянет с tele-сервера список меток (verified/scam/fake, «support text») и накладывает их на пиров.
- **Вердикт:** ✅ переносим — HTTPS-фетч + перезапись флагов; UI-бейджи уже рисуются из этих флагов.
- **Android:** перехват в `MessagesController.putUser/processUser/processChat` (перезапись `user.verified/scam/fake`), далее отрисовка работает штатно (`ChatActivity` заголовок, `DialogCell` verifiedDrawable); HTTP — OkHttp/ConnectionsManager. Аналога в inugram нет.

#### 0010 — make the title bar label a live template
- **Суть:** шаблонизатор тайтлбара: переменные `{build}`, `{time}`, `{unread}`, `{chat}`, условия `[ ... ]`, живой предпросмотр.
- **Вердикт:** ⚠️ частично — «титул окна» десктопен; переносима идея шаблона на заголовок списка чатов.
- **Android:** движок шаблонов (Kotlin-хелпер) + подстановка в заголовок `DialogsActivity`; база — «custom title text» inugram.

#### 0011 — remove the account limit
- **Суть:** константы kMaxAccounts 3→1536, kPremiumMaxAccounts 6→1536.
- **Вердикт:** ✅ переносим — та же константа существует на Android.
- **Android:** `UserConfig.MAX_ACCOUNT_COUNT` (сейчас 4) + интерфейс добавления аккаунта; аналог в inugram: `feature/multi-account` (до 8, снятие premium-ограничений).

#### 0012 — show checkmarks and custom verification everywhere
- **Суть:** verified-бейдж во всех местах: превью чата, сендер-неймы в пузырях, главное меню, настройки; рендер кастомных меток.
- **Вердикт:** ⚠️ частично — все точки отображения на Android существуют; рендер кастомных бейджей зависит от 0009.
- **Android:** `DialogCell` (drawVerified), `ChatActivity` (заголовок чата), `ProfileActivity`; рендер кастомных бейджей — хелпер поверх флагов из 0009.

#### 0013 — show gift ids
- **Суть:** строка «Gift ID» в карточке уникального подарка, клик копирует id.
- **Вердикт:** ✅ переносим — id есть в данных (`TL_starGiftUnique`), одна строка + копирование.
- **Android:** `org.telegram.ui.Stars` (ProfileGiftsView, StarGiftSheet), `org.telegram.ui.Gifts.GiftSheet`; копирование — Bulletin/ClipboardHelper.

#### 0014 — show the peer id as its own profile row
- **Суть:** id пира отдельной строкой в профиле (варианты формата: без пробелов, Bot API стиль с -100), клик копирует.
- **Вердикт:** ✅ переносим — чистая фича профиля; готовое соответствие в inugram.
- **Android:** `ProfileActivity`; аналог в inugram: `feature/id-in-profile` (туда же можно взять варианты форматирования tele).

#### 0015 — copy links to tele settings
- **Суть:** контекстное меню «копировать deep link» на каждом тумблере секции настроек.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — на Android аналогичная система deeplink/поиска по настройкам форка уже реализована.
- **Android:** аналог в inugram: SearchRegistry + deeplinks `tg://settings/inu/...`.

#### 0016 — ignore users by hiding or fading their messages
- **Суть:** локальный список игнора: сообщения пользователя скрываются полностью или «затухают» (fade); меню игнора на юзерпике.
- **Вердикт:** ✅ переносим — data-layer фильтрация по локальному списку; fade — чуть больше UI-работы.
- **Android:** хук выборки сообщений в `ChatActivity`/`MessageObject`, список в `inu_`-таблице; близкий аналог в inugram: `feature/hide-blocked-messages` (без режима fade).

#### 0017 — show seconds in message times
- **Суть:** опция добавляет секунды к времени у сообщений и «edited at»; сервисные сообщения (вход, пин и т.п.) тоже получают время («user joined · 14:03:21») по той же опции (влит бывший 0043); при смене опции у сервисных сообщений принудительное обновление текста.
- **Вердикт:** ✅ переносим — формат времени плюс расширение текста сервисного сообщения при рендере.
- **Android:** `LocaleController.formattingChatTimestamp`/`formatterDay`, ячейки; для сервисных — композиция `messageText` у `TL_messageService` в `MessageObject.generateLayout` + `ChatMessageCell`; аналог в inugram: `feature/show-seconds`.

#### 0018 — keep the edit history of messages
- **Суть:** перехват applyEdition, версии текста/медиа сохраняются в памяти; пункт меню «Edit history» показывает список версий.
- **Вердикт:** ✅ переносим — точка перехвата есть, хранение локальное; UI просмотра — боттомшит.
- **Android:** `MessagesController` (обработка `updateMessageEdited`) + `inu_`-таблица версий, пункт меню через хук `ChatActivity.createMenu`.

#### 0019 — keep deleted messages
- **Суть:** удалённые сообщения сохраняются: не удаляются с сервера при собственном удалении, копия держится при серверном удалении, помечаются иконкой, отдельная секция просмотра.
- **Вердикт:** ✅ переносим — два механизма (подавление исходящего delete, кэширование входящего) доступны; объём большой, но десктоп-специфики нет.
- **Android:** хук `MessagesController.deleteMessages` (не отправлять запрос) и `processDeleteMessages` (копии `TLRPC.Message` в `inu_`-таблицы); отображение — отдельный экран. Частичный аналог в inugram: `feature/show-deleted-replies` (только заглушка).

#### 0020 — fade every unsupported experimental option
- **Суть:** фикс отрисовки: заголовки недоступных опций на странице Experimental настроек тоже серые.
- **Вердикт:** ❌ не переносим — страницы Experimental (settings_experimental) на Android нет, чинить нечего.
- **Android:** — (гипотетически — серый стиль для тумблеров с рестартом в SettingsPageActivity, косметика).

#### 0021 — hide call buttons
- **Суть:** тумблер прячет кнопку звонка из топбара чата и профиля.
- **Вердикт:** ✅ переносим — стандартный debloat.
- **Android:** `ChatActivity` (ActionBar) и `ProfileActivity`; аналог в inugram: `feature/hide-call-action`.

#### 0022 — lowercase every interface text
- **Суть:** опция пропускает каждую строку локализации через lowercase (с сохранением lang-тегов и ссылок).
- **Вердикт:** ✅ переносим — единая точка выдачи строк.
- **Android:** `org.telegram.messenger.LocaleController.getString/getStringInternal` (центральный перехват).

#### 0023 — show the data center in profiles
- **Суть:** строка «DC» в профиле: DC из file location аватара (или mainDcId для себя), города, копирование.
- **Вердикт:** ✅ переносим — dc_id присутствует в Android-модели, строка — тривиальная вставка.
- **Android:** `TLRPC.FileLocation.dc_id`, `MessagesController.getMainDcId` → строка в `ProfileActivity`; связанный патч inugram: `bugfix/profile-photo-location-dc-id`.

#### 0024 — hide sponsored messages
- **Суть:** тумблер: не запрашивать и не показывать sponsored messages (каналы, боты, поиск).
- **Вердикт:** ✅ переносим — подавление запроса/инъекции спонсорских блоков.
- **Android:** гейт sponsored-блока в `MessagesController` + панель в `ChatActivity`; близкий (не равный) патч inugram: `debloat/sponsored-data-saver`.

#### 0025 — open links without confirmation
- **Суть:** опция пропускает диалог «открыть ссылку?» для ссылок с кастомным текстом.
- **Вердикт:** ✅ переносим — точный эквивалент диалога существует.
- **Android:** ранний return в `AlertsCreator.showOpenUrlAlert` (вызовы в ChatActivity и др.); связанный патч inugram: `feature/confirm-internal-links` (наоборот — общая точка).

#### 0026 — open disappearing media without burning it
- **Суть:** открытие view-once/TTL-медиа не отправляет «просмотрено» серверу; пункт меню «Mark as viewed» сжигает вручную.
- **Вердикт:** ✅ переносим — подавление отметки прочтения + ручной триггер.
- **Android:** `MessagesStorage.markMessagesContentAsRead`/`MessagesController` (хук для TTL-медиа), пункт «пометить просмотренным» в меню `ChatActivity`.

#### 0027 — allow screenshots of disappearing media
- **Суть:** опция отключает screenshot protection для view-once/TTL-медиа в просмотрщике.
- **Вердикт:** ✅ переносим — точка прямо существует (оговорка: сознательное ослабление приватности).
- **Android:** управление `FLAG_SECURE` в `PhotoViewer` (+ SecretMediaViewer).

#### 0028 — copy the callback data of bot buttons
- **Суть:** пункт меню «copy payload» на кнопках бота: callback-данные (текст или hex), URL, inline-запрос.
- **Вердикт:** ✅ переносим — данные доступны в модели.
- **Android:** `TL_keyboardButtonCallback.data`, пункт в меню сообщения/обработчике ботов; inugram уже покрывает long-tap inline-кнопок в `feature/message-menu`.

#### 0029 — show the message id in the message menu
- **Суть:** пункт меню сообщения показывает его id (с копированием).
- **Вердикт:** ✅ переносим — одна строка меню.
- **Android:** хук `ChatActivity.createMenu` + Bulletin; расширение `feature/id-in-profile`/`feature/message-menu` inugram.

#### 0030 — hide the all chats folder
- **Суть:** тумблер убирает таб/папку «All chats» из полосы фильтров.
- **Вердикт:** ✅ переносим — готовый аналог уже есть.
- **Android:** `FilterTabsView` в `DialogsActivity`; аналог в inugram: `feature/folders-display-mode` (hide "all chats" tab).

#### 0031 — jump to the first message of a chat
- **Суть:** пункт меню «jump to first message»: загрузка истории сверху и переход к первому сообщению чата/топика.
- **Вердикт:** ✅ переносим — механика загрузки «от начала» существует.
- **Android:** `ChatActivity` + `MessagesController.loadMessages`; аналог в inugram: `feature/jump-to-beginning`.

#### 0032 — add ghost mode
- **Суть:** набор тумблеров: не отправлять read-receipts (опционально читать при ответе), typing/запись/загрузку, не показывать онлайн, отправка «как запланированные» с отложенной рассылкой, незаметный просмотр сторис; scopes по чатам.
- **Вердикт:** ✅ переносим — вся механика — подавление исходящих API-вызовов и schedule-трюк; полностью data-layer.
- **Android:** `MessagesController.markDialogAsRead` (receipts), `sendTyping`, `TL_account.updateStatus` (онлайн), `StoriesController.markStoryAsRead`, schedule-отправка через `sendMessage`; тумблеры InuConfig. Прямого аналога в inugram нет (`feature/paranoia` — про скрытие/маскировку чатов, другую семантику).

### 0033–0057

#### 0033 — view messages and telegram objects as TL
- **Суть:** пункты «View as TL» в меню сообщений, чатов, профилей, стикеров, эмодзи, подарков, историй и папок: TL-объект дозапрашивается с сервера, сериализуется и открывается на schema.jppgr.am.
- **Вердикт:** ✅ переносим — MTProto-запросы (ConnectionsManager), сериализация TLRPC-объектов и открытие URL; десктоп-специфики нет.
- **Android:** `org.telegram.tgnet.TLRPC` + `ConnectionsManager`; inugram уже показывает JSON сообщения/пользователя (`feature/message-menu`, `feature/id-in-profile`) — та же база.

#### 0034 — hide the mtproxy sponsor channel
- **Суть:** тумблер: при подключении через MTProxy спонсорский канал не показывается закреплённым в списке чатов.
- **Вердикт:** ✅ переносим — промо-данные прокси обрабатываются в MessagesController (`TL_help_getPromoData`, `PROMO_TYPE_PROXY`, promoDialogId).
- **Android:** `MessagesController` (обработка promoData / hidePromoData) + `DialogsActivity`/пиннинг; аналога в inugram нет (близко по духу к debloat-патчам sponsored-*).

#### 0035 — lowercase tele's own texts too
- **Суть:** косметика — собственные строки форка приводятся к нижнему регистру через хелпер Tele::Lower.
- **Вердикт:** ✅ переносим — стилистическое соглашение по строкам самого форка, не платформенная работа.
- **Android:** строки форка в ресурсах и Kotlin-хелперах; аналог в inugram: `misc/branding`.

#### 0036 — stop maximized windows jittering on monitors without a taskbar
- **Суть:** виндо-специфичный фикс: `QWindowsWindowFunctions::setHasBorderInFullScreenDefault(true)` для Qt < 6.0.
- **Вердикт:** ❌ не переносим — патч целиком в platform/win/integration_win.cpp; на Android ни окон, ни этого API нет.
- **Android:** —

#### 0037 — send crash reports to the tele server
- **Суть:** отчёты о крашах (Breakpad-минидампы) отправляются на настраиваемый tele server (/v1/crash.php).
- **Вердикт:** ✅ переносим — POST лога краша на настраиваемый HTTP-endpoint; десктопные части (минидампы) заменяются механизмами логов Android.
- **Android:** UncaughtExceptionHandler + HTTPS; в inugram уже есть crash report sheet (ловит необработанные исключения, предлагает шарить лог) — туда и вешается.

#### 0038 — turn off animated userpics
- **Суть:** два тумблера: статичные аватары в списке чатов и в чатах/профилях — video-аватары не проигрываются; открытие фото всё равно проигрывает видео.
- **Вердикт:** ✅ переносим — решение о проигрывании видео-аватара принимается в одной точке ImageReceiver.
- **Android:** `messenger/ImageReceiver.java` (гейт при setImage: has_video + premium), `ui/Components/AvatarDrawable.java`; аналога в inugram нет.

#### 0039 — show what's new in tele after an update
- **Суть:** после обновления форк тянет changelog (JSON по HTTPS) и показывает «what's new»; тумблер.
- **Вердикт:** ✅ переносим — чистая логика «сравнить версию → скачать JSON → показать».
- **Android:** `SharedConfig` (сохранённая версия) + `LaunchActivity` (проверка при старте) + Bulletin/AlertDialog; вешается на готовый updater inugram.

#### 0040 — call the app tele everywhere
- **Суть:** ребрендинг: «tele» вместо «Telegram» во всех внутренних строках.
- **Вердикт:** ✅ переносим — на Android даже проще: имя задаётся лейблом и строковыми ресурсами.
- **Android:** app label (AndroidManifest/strings.xml) + строки форка; аналог в inugram: `misc/branding`.

#### 0041 — customize the window title and format template
- **Суть:** два настраиваемых шаблона с переменными — для лейбла над чатом и для системного заголовка окна.
- **Вердикт:** ⚠️ частично — движок шаблонов переносим; системный заголовок окна на Android бессмыслен; осмысленный эквивалент — шаблонный заголовок экрана диалогов.
- **Android:** `ui/ActionBar/ActionBar.java` (setTitle) + `DialogsActivity`; база — «custom title text» inugram, расширение до шаблонов с переменными.

#### 0042 — group and search tele settings
- **Суть:** реорганизация секции настроек tele: группировка по страницам/подгруппам и поиск по настройкам.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — роль секции tele на Android играет инфраструктура inugram, где группировка и поиск уже есть.
- **Android:** аналог в inugram: `misc/settings-ui` (+ «search and deeplinks for fork settings»).

#### 0043 — upload media in several chats at once
- **Суть:** тумблер параллельных загрузок: планировщик выбирает следующий файл из другого чата.
- **Вердикт:** ✅ переносим — по большей части уже есть: на Android каждый файл грузится своим `FileUploadOperation`, несколько загрузок уже идут параллельно; желаемое поведение — по сути сток.
- **Android:** `SendMessagesHelper` (uploadMessages) + `FileUploadOperation`; аналога в inugram нет и не требуется.

#### 0044 — reply timestamps for media in rich messages
- **Суть:** если реплай цитирует Instant View-страницу с видео/документом, таймстампы в реплае становятся рабочими (перемотка).
- **Вердикт:** ⚠️ частично — «таймстамп → перемотка» для обычных медиа Android уже умеет; IV-часть привязана к десктопному рендереру (на Android IV — webview), ценность сомнительна.
- **Android:** `ui/web/WebInstantView.java`, обработка timestamp-ссылок в `ChatMessageCell`; аналога нет.

#### 0045 — compute messages starting with = via calcmula
- **Суть:** сообщение с «= » вычисляется через HTTP-API calcmula.app и отправляется как «запрос в цитате + ответ».
- **Вердикт:** ✅ переносим — механика полностью сетевая: перехват отправки → HTTP → пересборка текста с Blockquote → отправка.
- **Android:** перехват в `ChatActivity`/`SendMessagesHelper` (sendMessage), HTTP стандартными средствами; аналога нет.

#### 0046 — move show peer ids into tele settings
- **Суть:** перенос тумблера «show peer id» из экспериментальных настроек tdesktop в секцию tele.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — перекладывание опции между меню; фича «ID в профиле» в inugram уже реализована.
- **Android:** аналог в inugram: `feature/id-in-profile` (+ InuConfig как место тумблера).

#### 0047 — show the tele build in the main menu
- **Суть:** к строке версии в главном меню добавляется «build #N» / «dev build».
- **Вердикт:** ✅ переносим — тривиальная правка отображения версии.
- **Android:** `ui/SettingsActivity.java` (versionView) либо шапка fork-дровера inugram.

#### 0048 — open collectible gifts in see.tg
- **Суть:** кнопка «Open in see.tg» в окне коллекционного подарка: мини-приложение t.me/seetgbot/nft?startapp=<slug>; тумблер.
- **Вердикт:** ✅ переносим — добавление ссылки/кнопки в UI подарка и открытие deep link.
- **Android:** `ui/Stars/StarGiftSheet.java` / `ui/Stars/ProfileGiftsView.java` / `ui/Gifts/GiftSheet.java`; аналога нет.

#### 0049 — move late sent messages to the bottom
- **Суть:** если медленная загрузка завершилась позже отправки более новых сообщений, элемент переносится в низ истории.
- **Вердикт:** ❌ не переносим — проблема десктопная: tdesktop держит элементы в порядке дат/блоков. Android хранит и отображает сообщения строго по mid (`MessagesStorage`: ORDER BY mid), «позднее» сообщение получает больший mid и само встаёт вниз.
- **Android:** —

#### 0050 — queue messages behind an uploading media
- **Суть:** тумблер: текстовые сообщения, отправленные во время загрузки медиа в тот же чат, удерживаются и уходят строго после медиа.
- **Вердикт:** ✅ переносим — проблема существует и на Android (текст уходит сразу), состояние «в этом диалоге идёт загрузка» уже трекается.
- **Android:** `SendMessagesHelper` (uploadMessages/uploadingMessagesIdDialogs как источник состояния) + перехват отправки текста; аналога нет.

#### 0051 — open links in their desktop apps
- **Суть:** клик по ссылке открывает нативное десктоп-приложение (spotify:, steam://, discord:// и т.п.).
- **Вердикт:** ❌ не переносим — патч закрывает десктопный пробел «браузер не умеет открывать в приложениях». Android делает это системно: ACTION_VIEW с https-URL резолвится через App Links/Intent-резолвер.
- **Android:** — (стоковое поведение Intent/App Links).

#### 0052 — clean tracking parameters from links
- **Суть:** чистка трекинг-параметров (utm_*, fbclid, si, …) из ссылок при отправке и при открытии, с набором правил.
- **Вердикт:** ✅ переносим — чистая строковая обработка URL в двух точках.
- **Android:** аналог в inugram: `feature/strip-tracking` («strip tracking params from links before opening and/or when pasting — rules from AdGuard»).

#### 0053 — reveal spoilers automatically
- **Суть:** глобальный тумблер: спойлеры (текст, превью диалогов, реплаи, медиа) рендерятся раскрытыми.
- **Вердикт:** ✅ переносим — глобальный гейт «не считать контент спойлерным» на уровне данных/отрисовки.
- **Android:** `MessageObject`, `ChatMessageCell`, `ui/Components/spoilers/SpoilerEffect`; аналога нет (inugram `hide-spoiler-pending`/`better-spoilers` — другое).

#### 0054 — move tele tools to the bottom of the message menu
- **Суть:** перестановка: собственные пункты tele вставляются в самый низ контекстного меню сообщения.
- **Вердикт:** ✅ переносим — расстановка пунктов самого форка; inugram имеет полностью настраиваемое меню, пункты встают куда нужно.
- **Android:** аналог в inugram: `feature/message-menu`.

#### 0055 — copy custom emoji ids from the message menu
- **Суть:** «Copy emoji ID» при правом клике по кастомному эмодзи в сообщении; тумблер.
- **Вердикт:** ✅ переносим — hit-test кастомного эмодзи по координатам долгого тапа + пункт меню.
- **Android:** `ChatMessageCell` (textLayoutBlocks/AnimatedEmojiSpan, hit-test), пункт в меню `ChatActivity`; аналога нет (смежное — «Save to Downloads for stickers»).

#### 0056 — change the speed instead of moving the media viewer window
- **Суть:** однострочный фикс десктопного просмотрщика: при speed boost перетаскивание мышью меняет скорость, а не двигает окно.
- **Вердикт:** ❌ не переносим — фикс различения mouse-drag и удержания в Qt-виджете; у Android PhotoViewer своя touch-механика — ситуация не существует.
- **Android:** —

#### 0057 — reorder and hide message menu items
- **Суть:** фреймворк: порядок/видимость пунктов контекстного меню сообщения, редактор в настройках.
- **Вердикт:** ✅ переносим — точно такая же фича уже есть в inugram (порт NagramX).
- **Android:** аналог в inugram: `feature/message-menu` (переупорядочивание, скрытие, long-tap-варианты, quick actions).

### 0058–0088

#### 0058 — keep messages you delete yourself
- **Суть:** расширяет «хранить удалённые»: локально сохраняются и самоудалённые сообщения (до перезапуска).
- **Вердикт:** ✅ переносим — перехват удаления на слое данных, ничего десктопного.
- **Android:** путь удаления в `MessagesController`, снапшоты `MessageObject` в памяти, рендер в `ChatMessageCell`; смежный аналог: `feature/show-deleted-replies`.

#### 0059 — show server and updates on the tele settings page
- **Суть:** секции «Server» и «Updates» переносятся на корневую страницу настроек tele.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — внутренняя страница настроек форка; переносить не нужно.
- **Android:** InuConfig + SettingsPageActivity inugram.

#### 0060 — pick brush colors from the image
- **Суть:** пипетка в палитре кисти фоторедактора: увеличительный фрагмент, тап — цвет применяется.
- **Вердикт:** ✅ переносим — сэмпл пикселя из битмапа и запись в палитру.
- **Android:** `ui/Components/Paint/Views/LPhotoPaintView.java`, `ColorPickerBottomSheet.java`; аналога нет.

#### 0061 — show edit history as a chat
- **Суть:** локальные снапшоты сообщения перед каждой правкой; история правок открывается как чат с пузырями.
- **Вердикт:** ✅ переносим — точка захвата есть (`TL_updateEditMessage`), рендер версий существующими ячейками; трудозатратно, но без десктоп-специфики.
- **Android:** `MessagesController` (updateEditMessage), `MessageObject` (хранение версий), фрагмент с `ChatMessageCell`.

#### 0062 — hide or confirm call and voice chat buttons
- **Суть:** кнопки звонков: показ/скрытие/подтверждение; подтверждение перед групповым звонком/стримом.
- **Вердикт:** ✅ переносим — обе части напрямую реализуемы.
- **Android:** аналоги в inugram: `feature/call-confirmation` + `feature/hide-call-action`; точки: `ChatActivity`, `ProfileActivity`, `VoIPService`, `VoIPFragment`.

#### 0063 — group the tele interface and profile settings
- **Суть:** группировка опций на страницах настроек tele.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — косметика; на Android есть готовый фреймворк.
- **Android:** InuConfig + SettingsPageActivity inugram.

#### 0064 — more ghost mode options
- **Суть:** «offline после отправки», не подтверждать прочтение реакций, переключатель ghost в меню чата.
- **Вердикт:** ✅ переносим — не-отправка API-запросов (`TL_account.updateStatus(false)` после отправки, локальная пометка реакций).
- **Android:** `MessagesController` (`TL_account.updateStatus`, путь чтения реакций); аналога нет.

#### 0065 — show ids on regular gifts
- **Суть:** строка «Gift ID» с копированием в карточке обычного (не коллекционного) подарка.
- **Вердикт:** ✅ переносим — id приходит в TLRPC-объектах, чистый UI; TLRPC.java не трогается (данные только читаются).
- **Android:** `ui/Gifts/GiftSheet.java`, `ui/Stars/StarGiftSheet.java`; аналога нет.

#### 0066 — send inline results without via
- **Суть:** инлайн-результаты ботов отправляются как собственные сообщения пользователя, без `via @bot`.
- **Вердикт:** ✅ переносим — вместо `TL_messages_sendInlineBotResult` собирается обычное `TL_message` из контента результата.
- **Android:** `SendMessagesHelper` (путь sendInlineBotResult), `MessagesController`, `ChatActivity`; аналога нет.

#### 0067 — skip the rich message prompt on paste
- **Суть:** отключение тоста «отправить как rich message» при вставке форматированного текста.
- **Вердикт:** ❌ не переносим — rich-сообщения — десктопная фича самого tele; на Android этого промпта не существует.
- **Android:** смежное в inugram: `debloat/hide-rich-editor-button` (другая механика).

#### 0068 — set or remove chat backgrounds only for you
- **Суть:** установка/удаление фонов чатов «только для себя» — локально, без серверной синхронизации.
- **Вердикт:** ⚠️ частично — сток Android уже умеет per-chat обои; портабельна только добавка: форс-локальное применение и удаление навязанного собеседником фона без серверного запроса.
- **Android:** `ThemeActivity`, `WallpapersListActivity`, `MessagesController.setWallpaperToPeer`; аналог в inugram: `debloat/disable-chat-themes`.

#### 0069 — skip or quote deleted messages when replying
- **Суть:** при ответе на удалённое сообщение — вырезать reply или процитировать текст удалённого.
- **Вердикт:** ✅ переносим — фильтрация `reply_to` при отправке + подстановка цитаты; данные локального сообщения доступны.
- **Android:** `SendMessagesHelper` (препроцессинг reply_to), `ChatActivity`; смежный аналог: `feature/show-deleted-replies`.

#### 0070 — add test server accounts with a plain right click
- **Суть:** правый клик по «добавить аккаунт» предлагает аккаунт на test-сервере.
- **Вердикт:** ⚠️ частично — ядро портабельно (`isTestBackend` в tgnet), но установка флага для нового аккаунта требует нативного/JNI-дополнения (Java-сеттера нет); жест — long-press.
- **Android:** `tgnet/ConnectionsManager` (`isTestBackend`, нативный бэкенд в `jni/tgnet/`), переключатель аккаунтов; аналога нет.

#### 0071 — link usernames to profiles locally
- **Суть:** локальные алиасы «@имя → профиль»: подстановка при отправке, автодополнение упоминаний, переход по клику.
- **Вердикт:** ✅ переносим — хранилище маппинга (`inu_kv`), препроцессинг исходящего текста, дополнение в поле ввода.
- **Android:** `MentionsAdapter` (автодополнение), `SendMessagesHelper`/`MessagesController` (замена), путь `getUserByName` для перехода; аналога нет.

#### 0072 — hide the mentions and reactions buttons
- **Суть:** опции скрывают кнопки «непрочитанные упоминания» и «непрочитанные реакции» над полем ввода.
- **Вердикт:** ✅ переносим — скрытие — гейт на одном вызове.
- **Android:** `ui/Components/chat/layouts/ChatActivitySideControlsButtonsLayout.java` (BUTTON_MENTION/BUTTON_REACTIONS, `showButton`) + `ChatActivity`; аналога нет.

#### 0073 — pick ignored users and ghost chats like privacy exceptions
- **Суть:** списки игнорируемых и ghost-чатов через универсальный пикер контактов/чатов.
- **Вердикт:** ✅ переносим — стандартный механизм выбора пиров уже используется в privacy-настройках и форк-списках.
- **Android:** аналоги в inugram: `feature/hide-blocked-messages`, `feature/paranoia` (пикеры списков пиров).

#### 0074 — show what's new in a local tele chat
- **Суть:** «What's New» как настоящий локальный чат с аватаркой, бейджем и историей.
- **Вердикт:** ⚠️ частично — но не так страшно, как казалось: запрет на «синтетический чат» — это правило inugram, а не платформенное ограничение; у нас свои правила. Варианты: синтетический диалог в списке либо отдельный экран в стиле чата. Требует обдумывания.
- **Android:** синтетика в `DialogsActivity`/`MessagesStorage`/fork-БД (обдумать атомарность, сортировку и поведение в поиске) либо экран в стиле чата на форк-инфраструктуре; база — свой updater (0006).

#### 0075 — show names instead of phone numbers in chat headers
- **Суть:** люди, не внесённые в контакты, показываются именем, а не номером в шапке чата.
- **Вердикт:** ✅ переносим — один хук формирования подзаголовка; фича уже есть в inugram почти дословно.
- **Android:** аналог в inugram: `debloat/disable-chat-title-phone`; точки: `ChatActivity`, `UserObject.formatName`.

#### 0076 — open the emoji panel and attach menu by click only
- **Суть:** панели открываются только по клику, отменяется открытие при наведении мыши.
- **Вердикт:** ❌ не переносим — компенсация десктопного hover; на Android панели уже открываются только тапом.
- **Android:** — (нечего отключать).

#### 0077 — rewrite pasted links with your own rules
- **Суть:** пользовательские правила перезаписывают вставляемые ссылки (twitter→fixupx и т.п.): домены и regex; редактор правил с пресетами (влит бывший 0079). При чтении правил цель `vxtiktok.com` (сервис закрылся) молча заменяется на `tnktok.com`; пресет TikTok — только `tnktok.com`, к пресету X/Twitter добавлен `samekosabax.com` (и в regex правила трекинга).
- **Вердикт:** ✅ переносим (🏗 редактор — страница настроек на инфраструктуре форка) — обработка текста при вставке; inugram уже перехватывает вставку для strip-tracking.
- **Android:** база — `feature/strip-tracking`/`feature/web-preview`; точки: `ChatActivity`, `EditTextCaption`.

#### 0078 — name people only for you
- **Суть:** локальные имена людей: подменяют имя во всём интерфейсе.
- **Вердикт:** ✅ переносим — подмена на слое данных пользователя; хранилище — `inu_kv`.
- **Android:** `MessagesController.putUser`, `UserObject.getUserName` (через это проходит отображение любого пира); аналога нет.

#### 0079 — add launch flags to turn off tele's own network
- **Суть:** флаги запуска `-noteleserver/-noteleupdate/-teleoffline` гейтят сетевые активности самого tele.
- **Вердикт:** ⚠️ частично — ядро (гейтинг исходящих запросов форка) портабельно, но launch flags на Android нет — эквивалент тумблеры; updater-платформа десктопна.
- **Android:** тумблеры InuConfig + хуки вокруг updater inugram.

#### 0080 — preview calcmula results while typing
- **Суть:** живое превью результата calcmula над полем ввода при наборе.
- **Вердикт:** ✅ переносим — переносится вместе с 0045 (calcmula): панель-превью над полем ввода, отправка по кнопке.
- **Android:** `ChatActivityEnterView` + `ChatActivity` (панель над полем — как reply/attach-панели); аналога нет.

#### 0081 — clear server data and explain custom verification
- **Суть:** кнопка очистки кэша бейджей tele-сервера и объясняющие тултипы кастомной верификации.
- **Вердикт:** ✅ переносим — HTTP-фетч + локальный кэш (`inu_kv`) + тривиальные UI-дополнения.
- **Android:** `ProfileActivity` (бот-верификация), кнопка в настройках форка; аналога нет.

#### 0082 — move chats instantly in the chat list
- **Суть:** отключение «заморозки» списка на время переупорядочивания.
- **Вердикт:** ⚠️ частично — freeze-механика (`skipChatsListFreeze`, движение мыши) десктопна; на Android при drag-переупорядочивании её нет. Портабельна только идея «мгновенного перемещения без анимации».
- **Android:** `DialogsActivity` (drag-реордер, movingDialogFilters), отключение move-анимации; аналога нет.

#### 0083 — show collectible prices at the purchase date
- **Суть:** цена покупки коллекционного подарка на дату приобретения: запрос истории курса TON + локальный кэш.
- **Вердикт:** ✅ переносим — HTTPS-запрос с кэшем + строка в карточке.
- **Android:** `ui/Gifts/GiftSheet.java`, `ui/Stars/StarGiftSheet.java`, `ResaleGiftsFragment`; аналога нет.

#### 0084 — set your own app and tray icons
- **Суть:** пользовательские иконки приложения и трея из любого изображения.
- **Вердикт:** ⚠️ частично — иконка приложения через activity-alias уже реализована в inugram; трей — десктопная концепция (максимум — иконка уведомления, покрыта).
- **Android:** аналог в inugram: `hooks/icon-replacement` (+ тумблер иконки уведомления).

#### 0085 — choose when links get previews and set your own
- **Суть:** управление превью ссылок: когда показывать, и задание собственного превью любой ссылки.
- **Вердикт:** ⚠️ частично — выбор/отключение превью переносимо (инфраструктура web preview у inugram есть); форс «чужой ссылки как превью» требует дописывания webpage-черновика в отправку.
- **Android:** аналоги в inugram: `feature/web-preview`, `bugfix/web-preview-refetch`, `feature/web-preview-spoiler`; точки: `ChatActivity`, `SendMessagesHelper`, `MessageObject`.

#### 0086 — turn username into a t.me link in the link box
- **Суть:** в диалоге «создать ссылку» `@username` превращается в `https://t.me/username`.
- **Вердикт:** ✅ переносим — одна regex-подстановка в валидации.
- **Android:** `EditTextCaption` (`showInputDialog`, вызывается из `ChatActivity` по R.id.menu_link); аналога нет.

#### 0087 — save messages as a picture
- **Суть:** пункт «Shot»: рендер выбранных сообщений в PNG с опциями.
- **Вердикт:** ✅ переносим — ячейки умеют рисоваться в произвольный Canvas; офф-скрин Bitmap + сохранение.
- **Android:** `ChatMessageCell` (отрисовка), меню `ChatActivity`, сохранение через MediaController/FileProvider; аналога нет.

#### 0088 — debug logs and an mtproto inspector
- **Суть:** просмотрщик логов + MTProto-инспектор: перехват TL-запросов/ответов и просмотр в HTML/JS-вьюере.
- **Вердикт:** ⚠️ частично — лог/JSON-вьюер переносим (inugram уже показывает JSON); полнота инспектора упирается в JNI (`ConnectionsManager.sendRequest` — native), покрытие ниже, чем в tdesktop.
- **Android:** `tgnet/ConnectionsManager` (обёртки sendRequest), точки `TLdeserialize`; отображение — WebView/SettingsPageActivity; смежное: JSON-показ inugram, NotificationDebugHelper.

### 0089–0124

#### 0089 — new tele app and tray icons
- **Суть:** замена бинарных ассетов: иконки приложения и системного трея.
- **Вердикт:** ⚠️ частично — лончер-иконки переносятся; иконки трея — чистый десктоп (на мобильном аналог — иконка уведомлений).
- **Android:** mipmap/launcher-иконки, иконка уведомлений; аналог в inugram: `hooks/icon-replacement` (+ тумблер notification icon).

#### 0090 — name the item Copy Callback Data like telegram does
- **Суть:** косметика — пункты «Copy callback data» переименованы для унификации.
- **Вердикт:** ✅ переносим — правка строки форк-меню; покрыто готовым патчем.
- **Android:** аналог в inugram: `feature/message-menu` (long-tap inline callback button → copy callback data).

#### 0091 — usernames from the tele server
- **Суть:** фид бейджей расширяется секцией «usernames» (алиас→username, позиция); подмешиваются к реальным в профиле.
- **Вердикт:** ✅ переносим — HTTP-фетч + парсинг JSON + встройка в список юзернеймов профиля.
- **Android:** HTTP + Kotlin-хелпер, встройка в `ProfileActivity` (список юзернеймов); аналога нет.

#### 0092 — open custom emoji in rich and emoji-only messages
- **Суть:** фикс: кастомные эмодзи в эмоби-only/развёрнутых сообщениях открывают набор по клику.
- **Вердикт:** ✅ переносим — хендлеры на каждую позицию эмодзи в ячейке.
- **Android:** `ChatMessageCell` (pressedLink/AnimatedEmojiSpan) + открытие сета через стикер-шит; аналога нет.

#### 0093 — send gifs as videos and videos as gifs
- **Суть:** пункты «отправить как GIF/как видео»: переключение атрибутов документа при отправке.
- **Вердикт:** ✅ переносим — подмена `TL_documentAttributeVideo/Animated` перед отправкой + пункт меню.
- **Android:** `SendMessagesHelper` (атрибуты документа), меню `ChatActivity`; ближайший аналог в inugram: `feature/send-mp4-as-video`.

#### 0094 — keep drafts on this device
- **Суть:** тумблер «локальные черновики»: не выгружать черновики в облако, кнопка очистки облачных.
- **Вердикт:** ✅ переносим — готовая фича в inugram.
- **Android:** аналог в inugram: `debloat/cloud-drafts` (disable cloud drafts upload); точки: `MediaDataController`/drafts.

#### 0095 — send scheduled messages on time
- **Суть:** тумблер: клиент сам отправляет отложенные в назначенную минуту, пока онлайн. Ошибка отправки не глотается: `FLOOD_WAIT`/`SLOWMODE_WAIT` → повтор через N+1 с; сетевые ошибки и 5xx → лестница 5 с / 15 с / 1 / 5 / 15 мин, максимум 5 попыток на сообщение; при неудаче уведомление «couldn't send a scheduled message on time» и тост; сканируются и архивные чаты.
- **Вердикт:** ✅ переносим — планировщик над локальными отложенными + «send now».
- **Android:** `MessagesController`/`SendMessagesHelper` (отправка отложенных), выборка по scheduleDate из `MessagesStorage`, Handler/AlarmManager; аналога нет.

#### 0096 — show id and dc in one row
- **Суть:** ID и DC показываются в одной строке профиля.
- **Вердикт:** ✅ переносим — компоновка строк; обе фичи-базы уже есть.
- **Android:** `ProfileActivity`; база — `feature/id-in-profile` (+ DC-строка из 0023).

#### 0097 — redesign the title template editor
- **Суть:** редактор шаблона заголовка окна (подсветка переменных, превью, чипы).
- **Вердикт:** ❌ не переносим — объект фичи — заголовок окна/тайтлбар; на мобильном не к чему вешать.
- **Android:** — (кастомный заголовок списка чатов inugram — другая фича).

#### 0098 — ignore reply counters on scheduled messages
- **Суть:** фикс: не применять replies-данные (счётчик комментариев) к отложенным сообщениям.
- **Вердикт:** ✅ переносим — guard в одной точке.
- **Android:** `MessageObject` (обработка `message.replies`).

#### 0099 — save drafts for later
- **Суть:** подсистема «сохранённых черновиков»: снапшот состояния поля (текст, медиа, reply, опции), браузер черновиков, восстановление.
- **Вердикт:** ⚠️ частично — ядро (несколько черновиков на чат: текст+медиа+reply) реализуемо; rich-IV-черновики и хоткей Ctrl+S — десктоп.
- **Android:** `ChatActivityEnterView`/`ChatActivity` (снимок/восстановление), `SendMessagesHelper` (сериализация медиа), fork DB; аналога нет.

#### 0100 — send photos in hd by default
- **Суть:** тумблер: каждый send-бокс стартует с включенным HD.
- **Вердикт:** ✅ переносим — форс начального состояния флага.
- **Android:** `PhotoViewer` (photoEntry.highQuality), `ChatAttachAlertPhotoLayout`; тумблер InuConfig; аналога нет.

#### 0101 — find chats by their aliases
- **Суть:** поиск чатов по tele-алиасам: совпадения поднимаются в выдачу поиска.
- **Вердикт:** ✅ переносим — поиск по собственной таблице + вставка результатов; зависит от 0072.
- **Android:** `DialogsActivity`/`DialogsSearchAdapter`, `MessagesStorage`, fork DB; аналога нет.

#### 0102 — show seen and reacted counts separately
- **Суть:** счётчики читателей и реагировавших показываются раздельно («Seen 5 · Reacted 3»).
- **Вердикт:** ✅ переносим — правка текста/подсчёта в UI «who read».
- **Android:** `MessageSeenView` + меню просмотров в `ChatActivity`; смежное: seen-by inugram.

#### 0103 — send an inline bot query as text
- **Суть:** при активном inline-боте в меню отправки появляется «отправить запрос как текст».
- **Вердикт:** ✅ переносим — детект inline-режима + альтернативный обычный sendMessage.
- **Android:** `ChatActivity` (onTextChanged, inline-бот), `ChatActivityEnterView` (меню отправки), `SendMessagesHelper`; аналога нет.

#### 0104 — choose which app opens each service
- **Суть:** настройка «какое приложение открывает каждый сервис» (spotify/discord/steam/zoom…).
- **Вердикт:** ⚠️ частично — технически воспроизводимо (Intent с setPackage), но системные App Links/«Открывать по умолчанию» уже решают это на уровне ОС; ценность на мобильном близка к нулю.
- **Android:** открытие ссылок в `ChatActivity`/`LaunchActivity`; системный аналог существует.

#### 0105 — scale shots up to 4x and show your messages as incoming
- **Суть:** развитие «шотов»: рендер 1x–4x с острым ре-рендером, опция «мои как входящие».
- **Вердикт:** ✅ переносим — офф-скрин рендер с масштабом; трудоёмко, но реализуемо; зависит от 0089.
- **Android:** `ChatMessageCell` (офф-скрин Canvas), сборка bitmap + FileProvider; аналога нет.

#### 0106 — export and import tele settings
- **Суть:** экспорт/импорт всех настроек tele в JSON с превью.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — на Android уже есть и работает; новые фичи вешаются на готовый экспорт/импорт.
- **Android:** аналог в inugram: `misc/settings-ui` (export/import JSON).

#### 0107 — attach media above the field
- **Суть:** «пристыкованные медиа»: постоянная панель над полем ввода с готовящимся медиа/черновиком (можно листать чат и писать дальше); подписи, паритет с send-боксом (цена paid media, TTL, invert caption, large photos, scheduled; влит бывший 0118), нарезка >N файлов на альбомы при отправке из черновика. На десктопе docked вышел из беты.
- **Вердикт:** ⚠️ частично — концепт переносим (панель над `ChatActivityEnterView`), но фича построена на tele-инфраструктуре очередей отправки и локальных черновиков, которой на Android нет; перестройка layout'а чата. Переносимы подписи и паритет состояния.
- **Android:** `ChatActivity` + `ChatActivityEnterView` (кастомный докед-вид), `ChatAttachAlert` (подписи), метка в `DialogCell`; аналога нет.

#### 0108 — show server badges on the personal channel in profile
- **Суть:** серверные бейджи tele отрисовываются на строке личного канала в профиле.
- **Вердикт:** ✅ переносим — HTTP-фид (как 0009/0093) + отрисовка рядом с текстом.
- **Android:** строка личного канала в `ProfileActivity`; поверхность совпадает с `feature/linked-channel-in-profile` inugram.

#### 0109 — explain a missing changelog instead of doing nothing
- **Суть:** когда заметки о релизе не найдены, показывается объяснение вместо молчания.
- **Вердикт:** ⚠️ частично — подсистема changelog tele напрямую не переносится; UX-идея переносится во встроенный обновлятор, который в inugram уже есть.
- **Android:** показ в обновляторе форка (UpdateHelper inugram).

#### 0110 — show new settings after an update
- **Суть:** после апдейта новые пункты настроек помечаются «new», появляется категория с непросмотренными.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — вешается на готовый фреймворк настроек форка.
- **Android:** SettingsPageActivity + SearchRegistry inugram (бейджи «new» поверх).

#### 0111 — never block screen capture
- **Суть:** тумблер «никогда не блокировать скриншоты»: перехват включения защиты экрана, защищённые чаты включительно.
- **Вердикт:** ✅ переносим — мобильный эквивалент: не ставить `FLAG_SECURE` на окнах; известная фича форков.
- **Android:** точки установки FLAG_SECURE (`PhotoViewer`, `SecretMediaViewer`, окна secret-чатов и др.); аналога в inugram нет.

#### 0112 — choose what shots show
- **Суть:** опции шота: скрыть inline-кнопки, нижнюю инфу, превью ссылок, реакции при рендере в картинку.
- **Вердикт:** ✅ переносим — флаги офф-скрин отрисовки; внутри будущей фичи «сообщение как картинка» (0087/0107).
- **Android:** `ChatMessageCell` (условия отрисовки при офф-скрин-рендере); аналога нет.

#### 0113 — trim settings descriptions
- **Суть:** копирайтинг: сокращены описания, расширены ключевые слова поиска настроек.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — строки форка в ресурсах; принцип уже соблюдён.
- **Android:** strings_inu.xml + SearchRegistry inugram.

#### 0114 — forward protected messages as copies
- **Суть:** тумблер: контент из чатов с запретом пересылки отправляется заново (текст + перекачанные медиа) вместо настоящего форварда.
- **Вердикт:** ✅ переносим — перехват форварда и пересборка сообщений как новых; весь конвейер отправки доступен.
- **Android:** `SendMessagesHelper` (отправка копий), пункты меню/снятие блокировок в `ChatActivity`/`PhotoViewer`; аналога нет (inugram `forward-options`/`cycle-forward-mode` — про другое).

#### 0115 — stop videos at their end
- **Суть:** фикс стриминга tdesktop: аудиомиксер сбросил трек → playPosition возвращает завершение, чтобы видео корректно останавливалось.
- **Вердикт:** ❌ не переносим — баг собственного ffmpeg-стримингового движка десктопа (AudioTrack/миксер); медиастек Android другой (ExoPlayer/MediaCodec), класс бага отсутствует.
- **Android:** нет соответствия.

#### 0116 — hide settings until their parent is on
- **Суть:** фреймворк зависимостей в настройках: пункт скрыт, пока не включен родительский тумблер.
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — аналогичная возможность уже есть в фреймворке настроек форка.
- **Android:** аналог в inugram: SettingsPageActivity + ExpandableBoolGroup/условные секции.

#### 0117 — hide communities
- **Суть:** тумблер: связанные группы/комьюнити не показываются в списке чатов, профилях, подсказках.
- **Вердикт:** ✅ переносим — в inugram уже есть режимы отображения сообществ.
- **Android:** аналог в inugram: `debloat/community-dialogs` (regular / open on avatar long-tap / invisible); точки: `DialogsActivity`, `DialogCell`, `ProfileActivity`.

#### 0118 — send replies to older messages past the queue
- **Суть:** опция к очереди tele: ответы на сообщения старше грузящегося медиа уходят сразу, минуя очередь.
- **Вердикт:** ⚠️ частично — логика внепорядковой отправки переносима, но вшита в очередь tele (0050), которой на Android нет; без порта очереди фича без носителя.
- **Android:** `SendMessagesHelper` (delayedMessages/очередь отправки); аналога нет.

#### 0119 — send right away on double enter
- **Суть:** опция к очереди tele: двойной Enter отправляет удержанные сообщения немедленно.
- **Вердикт:** ⚠️ частично — логика форсирования переносима; клавиатурного жеста нет (нужен эквивалент, напр. двойной тап по кнопке отправки), плюс зависимость от очереди 0051.
- **Android:** `ChatActivityEnterView` (кнопка отправки/IME-экшен); аналога нет.

#### 0120 — regroup the sending settings
- **Суть:** перегруппировка секций страницы настроек tele (sending order, uploads, message field, scheduled).
- **Вердикт:** ✅ переносим (🏗 инфраструктура) — компоновка на готовом фреймворке.
- **Android:** аналог в inugram: BehaviorSettingsActivity / MessagesSettingsActivity.

#### 0121 — use aliases for inline bots
- **Суть:** inline-запрос «@алиас …» резолвится через tele-алиасы в реальный username бота.
- **Вердикт:** ✅ переносим — подстановка в двух точках (детект inline-бота, resolveUsername); зависит от 0072.
- **Android:** `ChatActivity` (детект inline), `MessagesController` (resolveUsername); аналога нет.

#### 0122 — hide mention and reaction badges in the chat list
- **Суть:** тумблы 0072 расширены: скрытие кнопок также убирает бейджи @ и ❤️ из строк списка чатов и табов.
- **Вердикт:** ✅ переносим — фильтрация состояния бейджей при отрисовке строки чата.
- **Android:** `DialogCell` (отрисовка mention/reaction-бейджей), `DialogsActivity`; аналога нет (`feature/old-mention-indicator` — про стиль).

#### 0123 — pin chats past the limit
- **Суть:** «локальные пины»: чаты сверх серверного лимита хранятся локально, hollow-иконка пина, аккуратный фолбэк при ошибке сервера. У каждого пина флаг `local`, **один общий порядок** серверных и локальных пинов (серверные вливаются в локальный список), перетаскивание вперемешку (серверу уходит только его часть); те же списки для топиков форума, Saved Messages, папок и Archive; снятие пина у серверного+локального оставляет серверный.
- **Вердикт:** ✅ переносим — fork-хранилище пинов + перехват ошибок лимита + правки реордера/отрисовки; в рамках правил форка.
- **Android:** `MessagesController` (pinned dialogs/ошибки лимита), `DialogsActivity` (реордер), `DialogCell` (иконка), InuDatabaseHelper; аналога нет (есть только багфиксы пинов inugram).

#### 0124 — folders past the limit
- **Суть:** папки сверх серверного лимита, живущие только на клиенте (не синхронизируются), с редактором и лимитами чатов «без лимита».
- **Вердикт:** ✅ переносим — локальное хранилище фильтров вне серверной синхронизации; объём большой, но десктоп-специфики нет.
- **Android:** `MediaDataController` (dialogFilters), `FilterTabsView`, `DialogsActivity`, InuDatabaseHelper; аналога нет (смежные `folders-display-mode`, `chats-long-tap-folders`).

---

## Готовые аналоги в inugram (ориентир, не источник)

Эти патчи tele имеют готовые аналоги в патч-сете inugram (имена — по `series`). Берём их как ориентир — доказательство, что фича жизнеспособна на Android, — но реализации делаем свои (см. раздел ниже), с указанием кредитов:

| Патчи tele | Аналог inugram |
|---|---|
| 0003 | `debloat/hide-stories` |
| 0007, 0035, 0040 | `misc/branding` |
| 0011 | `feature/multi-account` |
| 0014, 0046, 0096 | `feature/id-in-profile` |
| 0016 (без fade), 0073 | `feature/hide-blocked-messages`, `feature/paranoia` |
| 0017 | `feature/show-seconds` |
| 0021, 0062 | `feature/hide-call-action`, `feature/call-confirmation` |
| 0028, 0054, 0057, 0090 | `feature/message-menu` |
| 0030 | `feature/folders-display-mode` |
| 0031 | `feature/jump-to-beginning` |
| 0037 (база), 0039, 0109 | in-app updater + crash report sheet (порт Nekogram) |
| 0042, 0059, 0063, 0077, 0106, 0110, 0113, 0116, 0120 | `misc/settings-ui` (InuConfig/SettingsPageActivity/SearchRegistry) |
| 0052, 0077 | `feature/strip-tracking` (+ `feature/web-preview`) |
| 0068 (частично) | `debloat/disable-chat-themes` |
| 0075 | `debloat/disable-chat-title-phone` |
| 0084, 0089 (иконки) | `hooks/icon-replacement` |
| 0094 | `debloat/cloud-drafts` |
| 0108 (поверхность) | `feature/linked-channel-in-profile` |
| 0117 | `debloat/community-dialogs` |
| 0043, 0051 | стоковое поведение Android / системные App Links |

## Как переносить (свой форк, паттерн по inugram)

Инфраструктуру строим свою, по образцу inugram (с кредитами): свои имена и свой код — не копия `inu_*`.

1. **Stock-патч минимальный:** ранний `if (TeleConfig.FEATURE.getValue()) { TeleHelper.handle(...); return; }` или вызов форк-логики *после* stock-блока; без реиндентации stock-кода.
2. **Логика — в Kotlin-хелперах** (`tele_*`/`Tele*Helper`), тумблер — `@JvmField val FEATURE = BoolItem("feature_name", false)` в `TeleConfig` (default off = поведение стока один в один).
3. **Хранилище форка:** `tele_*`-таблицы / `tele_kv` через `TeleDatabaseHelper`; **не трогать** `TLRPC.java` и схему stock-БД.
4. **UI настроек:** своя секция «tele» со страницами в духе `SettingsPageActivity` (+ строки в `strings_tele.xml`, ключи `Tele*`), поиск и deeplinks `tg://settings/tele/...`.
5. **Data-layer вместо UI-layer:** один хук в `MessagesController`/`SendMessagesHelper` дешевле пятнадцати хуков во вьюхах — большинство ✅-патчей tele (ghost mode, удалённые, алиасы, лимиты) реализуются именно так.
6. **Осторожно с «горячими» файлами** (`ChatActivity.java` 46k строк, `ChatMessageCell.java` 29k, `MessagesController.java` 24k) — только точечные правки по `rg`-найденному символу.
7. **Кредиты:** в README и/или «О программе» указать inugram как архитектурный ориентир и упомянуть порты, восходящие к Nekogram/NagramX (монет-тема, апдейтер, кастомное меню и т.п.).

### Типичные ловушки при переносе конкретных групп

- **Подавление серверных вызовов** (ghost 0032/0065, сторис 0004, исчезающие медиа 0026): гейтить надо *все* пути отправки, включая difference/catch-up (`onNewMessage` у inugram уже ловит все пути прихода).
- **Хранение локальных списков** (алиасы 0071/0103/0124, игнор 0016, имена 0078, пины 0123, папки 0124, версии правок 0018/0062): только fork-хранилище + хуки на stock load/save.
- **Офф-скрин рендер** (шоты 0087/0107/0114): `ChatMessageCell` умеет рисовать в произвольный Canvas, но потребуется собрать «виртуальный» чат (фон, пузыри, тема) — самая трудоёмкая из переносимых фич.
- **tele-server фичи** (0009, 0037, 0091, 0108): перезапись флагов пира в `MessagesController.putUser/processChat` + один HTTPS-фетч; архитектура сервера описана в README tele и платформенно-нейтральна.

## Источники

- tele: `tele/AGENTS.md`, `tele/README.md` (таблица всех 127 патчей), `tele/docs/architecture.md`, патчи в `tele/patches/tdesktop/`
- Telegram Android 12.10.6 (7112): `Telegram/TMessagesProj/`
- Образец: inugram `AGENTS.md`, `FEATURES.md`, `series`, патчи `inugram/patches/{bugfix,feature,debloat,hooks,misc}`
