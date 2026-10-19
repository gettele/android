# Пачка 30 — низкий приоритет

## Назначение и границы

1. Этот документ описывает только текущие строки пачки 30 в `docs/PATCHLIST.md`: 0236, 0242 и 0230. Номера — текущая нумерация очереди desktop; Android-файлы после реализации получат номера очереди, а не номера desktop.
2. Здесь создаётся только guide. Код должен сначала появиться отдельными коммитами в checkout `Telegram` на ветке `tele`, затем экспортироваться обычным `git format-patch`; `.patch` вручную не редактировать.
3. Desktop-патчи были прочитаны через `git show origin/main:patches/tdesktop/...`; Android-якоря — через `git show tele:...`. Desktop C++/Qt не копируется в Kotlin/Java.
4. Решение из `decisions.md` и PATCHLIST: все три строки остаются в плане, но идут поздно и имеют низкий приоритет. Оценка пачки — S×2, M×1. Ворота: debug APK и ручная проверка каждого фактического тумблера on/off.
5. При выключенном новом или существующем тумблере поведение должно быть ровно stock Android. Не менять `TLRPC.java`, stock-схему БД или `LAST_DB_VERSION`; fork-состояние — только через уже существующие tele-хранилища.

## Доказанная зависимость и намеренно неполный объём

6. **0236 → Android 0175 обязательно.** 0175 (план пачки 18) должен сначала дать единый caption path для отправки/правки стикера и показ подписи в `ChatMessageCell`, `DialogCell` и уведомлениях. 0236 не должен заново изобретать подписи или обходить этот path. Сейчас 0175 в PATCHLIST `todo`.
7. **0236 → Android 0096 обязательно.** Реальный docked-media код находится в экспортированном Android 0096 (`tele/helpers/DockedMedia.kt`, `DockedStore.kt`, `tele/ui/TeleDockedStrip.kt`). Документ `batch-15.md` описывает списки, а не docked media; поэтому формулировка «batch 15 docked» неточна: доказанная зависимость — именно Android 0096 (строка desktop 0107), не batch-15 guide. [INFERENCE] Если нумерация пачек у мейнтейнера означает иной внутренний план, её нужно уточнить до кода.
8. **0242 зависит только от существующего video-send path.** Он не зависит от 0175 или 0096. Android 0095 (GIF/video direction) ещё не завершён, поэтому портируется только обратная опция «беззвучное видео как GIF», без обещания полного desktop GIF/video parity.
9. **0230 имеет частичную зависимость от gift studio.** Desktop-половина, которая исправляет gzip при экспорте studio, ждёт desktop/Android gift studio 0197/0204; текущего Android studio нет. Полезная самостоятельная половина — исправление заголовка у пользовательского `.tgs` перед upload. Нельзя выдавать upload-половину за порт всей studio-фичи. [INFERENCE] Нужно решить перед коммитом, принимать ли этот частичный scope сейчас или ждать 0197/0204.

## Desktop-контракт

### 0236 — `captioned stickers go to the docked media`

10. `patches/tdesktop/0236-feat-captioned-stickers-go-to-the-docked-media.patch` добавляет в контекстные меню sticker/GIF панелей действие **Attach**. В `stickers_list_widget.cpp` и `gifs_list_widget.cpp` выбранный документ помечается `needsCaption=true` и `teleAttach=true`; обычное мгновенное Send остаётся отдельным действием.
11. `history_widget.cpp` и `history_view_compose_controls.cpp` направляют такой выбор в `ComposeDockedAddSticker`. Для sticker/GIF с подписью это должно добавить элемент над полем, а не открыть обычный `SendGifWithCaption`. Callback `sendSticker` передаёт документ, send options и текст подписи; при отправке документ уходит существующим media API с caption.
12. Docked store desktop держит отдельный sticker/GIF item в tray, показывает его первым, получает кадр из TGS/WebM/WebP, считает его в заголовке и не позволяет перетаскивать/открывать обычное `more`-меню для этого item. Остальные media items продолжают жить в существующем tray.
13. При send сначала проверяется лимит подписи sticker, затем sticker item удаляется из tray и отправляется с текстом поля; если вместе лежат обычные файлы, они отправляются своим прежним bundle path. Подпись должна сохранить обычные caption entities, reply и send options. Scheduled path в desktop специально не открывает дополнительное schedule box.
14. Android-перевод не обязан повторять desktop `FileChosen`/Qt-типы. Нужен account/dialog/thread-bound fork item, persistence и UI-представление, совместимые с существующим 0096. Не разрешать sticker через старую ветку `PhotoEntry` только ради переиспользования.

### 0242 — `choose how silent videos are sent`

15. Desktop 0242 (`settings/settings_tele.cpp`, `storage/storage_media_prepare.cpp`, `tele_gif_video.cpp`) добавляет выбор под опцией GIF/video: значение по умолчанию — GIF, второе значение — Video. Для беззвучного видео `ApplySilentVideoDefault` выбирает GIF только когда GIF/video feature включена и у файла нет audio; пользовательский выбор отдельного файла может это изменить.
16. Для preview/send-with-caption и protected-forward desktop повторно вызывает `KeepSendingAsGif`, чтобы беззвучная animation не потеряла тип при подготовке. Настройка экспортируется/importируется как choice с пустым значением и `video`.
17. На текущем Android сток уже отправляет обычное беззвучное видео как video. В `SendMessagesHelper` `prepareSendingVideo` строит `VideoEditedInfo`, на worker-пути учитывает `videoEditedInfo.muted`, а при `muted` добавляет `TL_documentAttributeAnimated` (около текущего блока `12120–12343`). Поэтому Android добавляет только default-off switch, который для видео без audio выставляет тот же muted/GIF результат в **initial preparation**, не меняя явный выбор пользователя в редакторе. Точная точка установки должна быть подтверждена по текущему `ChatAttachAlert`/`VideoEditedInfo` path перед кодом. [INFERENCE]
18. Не определять наличие звука по расширению. Использовать уже вычисленные MediaCodec/metadata-поля либо существующий `VideoEditedInfo`; не превращать round video, encrypted/TTL video или файл с аудиодорожкой в GIF без подтверждения desktop-семантики. [INFERENCE] Границы для round/TTL/encrypted требуют решения и device test.

### 0230 — `tgs stickers telegram would reject`

19. Desktop 0230 делает три связанных вещи. `tele_tgs_rules.cpp::RepairTgsHeader` принимает только gzip с magic `1f 8b`, длиной больше девятого байта, без `FHCRC` (`flags & 0x02 == 0`) и с byte 9 `OS=10` (TOPS-20), затем меняет только byte 9 на Unix `3`.
20. `tele_sticker_truth.cpp::RepairTgsUpload` сначала проверяет расширение `.tgs` без учёта регистра; если content уже есть — чинит его in-memory, иначе читает файл только в установленном `kMaxTgsBytes` и заменяет upload content при успешной починке. Оригинальный файл не переписывается. `localimageloader.cpp` вызывает это перед загрузкой. `ReadStickerThumbnail` также чинит bytes перед разбором.
21. Отдельно studio exporter задаёт `gz_header.os=3`; это часть, отложенная до gift studio на Android. Для Android 0230 сначала покрыть только upload bytes, включая путь выбора через `Uri` после того, как stock скопировал его в cache.
22. Текущий Android anchor для определения имени/расширения — `SendMessagesHelper.prepareSendingDocumentInternal` (`git show tele:.../SendMessagesHelper.java`, около `9537–9548`); публичные входы — `prepareSendingDocument(s)` около `10017–10242`. Однако desktop mutates content, а Android upload может читать файл чанками. [INFERENCE] Перед реализацией нужно открыть фактический `FileUploadOperation` source и выбрать существующий content hook; если его нет, сделать bounded temp copy только для повреждённого `.tgs`, не менять исходный файл и не читать файл целиком сверх лимита.
23. Не чинить любой gzip, не менять OS byte у корректного Unix/другого OS, не игнорировать `FHCRC`, не делать fallback на произвольное распаковывание и не отправлять исправленные bytes на tele-server. Это локальная нормализация upload.

## Android anchors и реализация

24. Для 0236 базовый data hook — `tele/helpers/DockedMedia.kt`: `dock(...)` около 156 сейчас отвергает `sticker` около 169–170; `send(...)` около 257 работает только с `tray.items`; `toInfo(...)` около 232 формирует `SendingMediaInfo`, а отправка идёт через `SendMessagesHelper.prepareSendingMedia(...)` около 304. Расширить fork-модель отдельным sticker item, а не менять stock `MediaController.PhotoEntry` и не добавлять поля в TL.
25. Точки интеграции UI 0096: `ChatActivity` attach selection около `12797` вызывает `DockedMedia.dock`; top view подключается около `8263`; `ChatActivityEnterView` вызывает `DockedMedia.send` около `7550`; `tele_setDockedMedia` управляет send button. 0236 должен сохранить этот порядок: docked send перехватывает send раньше обычного text path, очищает caption только после успешного consume и не отправляет sticker второй раз.
26. Для sticker/GIF picker найти фактические callback-ы в текущем `EmojiView`/`StickersAlert`/`ChatActivityEnterView` по symbol search, не по старым line numbers. В существующем callback добавить отдельное long-press/context-menu действие `Attach`, gated `TeleConfig.DOCKED_MEDIA`; обычный tap и OFF остаются stock. `TeleDockedStrip` должен bind/rebind sticker state на каждом recycle и не держать Activity/static View.
27. Для отправки после 0175 переиспользовать его caption/entity helper и существующий `SendMessagesHelper.sendSticker(... CharSequence caption ...)` overload либо подтверждённый общий `sendMedia` path. Не вызывать private stock API дублированием; если нужен доступ — сделать минимальный `public`/`tele_` seam. Caption limit проверять до удаления tray, ошибку показывать на UI thread.
28. Sticker state ключуется `currentAccount + dialogId + threadId`; persistence использует существующий `TeleDatabaseHelper`/`DockedStore` формат 0096, без stock DB migration. После process death, account switch, topic switch и config OFF не допускается показать item другого key. Если текущий 0096 формат не умеет документ reference/thumbnail, сначала определить безопасный локальный snapshot и download lifecycle. [INFERENCE]
29. Для 0242 новый helper может быть `tele/helpers/SilentVideo.kt`, но не дублировать VideoEditedInfo. Hook должен быть в самом общем текущем preparation path до worker/send, с явной проверкой `TeleConfig.SILENT_VIDEO_AS_GIF`; обычный `SendMessagesHelper` stock path при OFF не должен создавать helper work. `videoEditedInfo.muted` и animated attribute должны оставаться согласованными с уже существующим conversion code.
30. Для 0230 helper в `tele/helpers/TgsUpload.kt` должен быть чистым bounded byte/file transform. Hook — на confirmed document upload path после расширения/URI resolution и до `FileUploadOperation`; если фактический upload API не допускает bytes, зафиксировать это как blocker, а не менять `TLRPC.java` или подменять MIME. Проверить также path, где `.tgs` приходит из content URI.
31. Все фоновые callbacks для thumbnail/download/upload имеют account и generation; View/strip/field меняются только через main dispatcher. `LiteMode` учитывать для любой новой frame/animation работы; для низкоприоритетной sticker tile допустим статический thumbnail/frame, если exact animated behavior не подтверждён. [INFERENCE]

## TeleConfig, настройки и search IDs

32. 0230 — bug-fix без пользовательского выбора, поэтому отдельный TeleConfig item не добавлять: корректные файлы не меняются, повреждённые TOPS-20 `.tgs` исправляются всегда. Это решение нужно явно подтвердить, если мейнтейнер требует выключаемый fix.
33. 0236 — отдельный switch не добавлять: он следует существующему `TeleConfig.DOCKED_MEDIA = BoolItem("docked_media", false)` и существующей строке «attach media above the field (beta)» в `TeleSettingsActivity.MODE_SENDING`. Включение/выключение должно включать/выключать и Attach для sticker/GIF; 0175 caption switches не должны автоматически включать docked.
34. 0242 добавить `TeleConfig.SILENT_VIDEO_AS_GIF = BoolItem("silent_video_as_gif", false)`. Row — в `TeleSettingsActivity` в `MODE_SENDING`; export/import spec и `strings_tele.xml` обязательны. Android default **off**, хотя desktop default GIF: правило AGENTS о stock-compatible off имеет приоритет.
35. Текущий `TeleSearch.kt` имеет старые tele IDs 950–1109; записей 1480–1499 в этом registry нет. Перед кодом проверить collision также со stock `ProfileActivity.SearchAdapter`, затем зарезервировать только нужные IDs:
   - `1480` — canonical «send silent videos as GIF», mode `sending`, item `silent_video_as_gif`; keywords `silent`, `silent video`, `gif`, `беззвучное видео`, `гиф`.
   - `1481` — alias «silent video format», ведёт на 1480, не новый config item.
   - `1482` — alias «captioned stickers in docked media», ведёт на существующий `DOCKED_MEDIA`/sending row, не новый config item.
   - `1483–1499` оставить свободными до подтверждённых будущих settings; не заполнять догадками. IDs — navigation identifiers, не Telegram dialog IDs и не export keys.
36. `settingIds()` получит только фактический `silent_video_as_gif`; существующий `docked_media` уже участвует в new-settings machinery. Если для 0230 нужен поиск без settings row, сначала получить решение мейнтейнера; не маскировать help alias под отдельный toggle.

## Порядок коммитов и effort

37. Один desktop row — один Android commit; не объединять три фичи в «media improvements». Предлагаемый порядок:
   1. `fix: repair tgs upload headers` — 0230, S. Выполнить upload-only scope; studio exporter явно оставить за 0197/0204 либо остановиться до решения о зависимости.
   2. `feat: send silent videos as gifs` — 0242, S. Новый off-by-default switch, settings/search/export и общий video preparation hook.
   3. `feat: dock captioned stickers` — 0236, M. Выполнять только после Android 0175 и подтверждения/стабилизации 0096 API; расширяет `DockedMedia` и picker callbacks, не переписывает queue.
38. [INFERENCE] Если мейнтейнер требует строгого порядка строк PATCHLIST, поменять 0230 на третью позицию, но 0236 всё равно нельзя начинать до 0175/0096. Каждый commit должен собираться поверх предыдущего и экспортироваться отдельно.
39. Рекомендуемые subjects — план, не готовый commit: перед commit сверить с фактическим diff и лимитом 5 слов. Не делать fixup опубликованных patch-файлов; не менять PATCHLIST status до реальной стадии `wip/queued/built/done`.

## Планируемые строки `features.md`

40. После каждого user-facing export добавить английскую строку в секцию `sending`; этот guide не редактирует `features.md`:
   - `captioned stickers in docked media` — «stickers and GIFs from the picker can be attached above the field, captioned there and sent through the docked media strip»; where `tele → sending → attach media above the field`; default `with attach media above the field (off)`; Android `[<exported 0236 patch filename>]`; desktop link `[236](https://github.com/nitreojs/tele/blob/main/patches/tdesktop/0236-feat-captioned-stickers-go-to-the-docked-media.patch)`.
   - `send silent videos as GIFs` — «when enabled, videos without an audio track are sent as GIFs instead of videos; videos with sound keep their normal type»; where `tele → sending`; default `off`; Android `[<exported 0242 patch filename>]`; desktop link `[242](https://github.com/nitreojs/tele/blob/main/patches/tdesktop/0242-feat-choose-how-silent-videos-are-sent.patch)`.
   - `repair rejected .tgs uploads` — «repairs the TOPS-20 gzip OS byte in `.tgs` files immediately before upload without changing the original file»; where `sending`; default `always on`; Android `[<exported 0230 patch filename>]`; desktop link `[230](https://github.com/nitreojs/tele/blob/main/patches/tdesktop/0230-fix-tgs-stickers-telegram-would-reject.patch)`. Не описывать в этой строке studio export, пока 0197/0204 не портированы.
41. Фактическое имя Android patch-файла нельзя угадывать до commit/export: оно зависит от subject и очереди. Не добавлять placeholder в `features.md`; заменить `<...>` только при экспорте.

## Тесты, ручная проверка и OFF

42. Автоматические unit/instrumentation targets для этих helper-ов в прочитанном checkout не подтверждены; не создавать новый тестовый каркас без существующего harness. Минимум — чистые тесты transform-а 0230, если проектный target уже есть, плюс обязательная ручная проверка batch gate.
43. 0230: fixtures для gzip OS=10 должны стать OS=3; OS=3 и другие OS не менять; короткий/non-gzip input, `FHCRC`, upper-case `.TGS`, URI/cache path, отсутствующий/слишком большой файл и корректный upload проверить. Сравнить hash исходного файла до/после. В OFF сценария нет для always-on fix; stock-поведение для всех уже корректных и неподдержанных файлов должно остаться тем же.
44. 0242 OFF/default: обычное видео без audio остаётся Telegram video, видео с audio не меняется. ON: беззвучное video действительно уходит GIF/animated; video со звуком остаётся video; explicit editor choice не затирается; caption, album, retry, draft, round video, secret/TTL проверяются отдельно и не считаются покрытыми без наблюдения. Проверить restart/config change и запись choice в export/import.
45. 0236 OFF: picker tap и long-press имеют stock behavior, sticker/GIF не попадает в strip. ON: attach action для sticker и GIF, caption вводится над полем, item переживает close/reopen/restart, отправляется с caption/entity, обычные media и смешанный tray не ломаются, remove/reorder/send/cancel работают. Проверить account 0/другой account, topic, caption limit, empty caption, slow mode, schedule/paid media restrictions. 0175 display/render в bubble/list/notification проверяется отдельно.
46. Для каждого toggle проверить initial default, включение без restart, выключение с уже сохранённым state, повторное включение, recycled strip/cell и отсутствие второго send. Сборка сама по себе не доказывает UX.

## Pitfalls, вопросы и gate

47. Не считать расширение `mp4`/`.tgs` достаточным доказательством media type; не читать network bytes или message caption как local file; не держать `Activity`, `View`, `Bitmap` или account-0 singleton в долгоживущем helper. Проверять nullable TL fields и upload failures.
48. Для 0236 главный риск — старый `DockedMedia.dock` прямо отвергает `sticker`, а `send`/`toInfo` знают только `tray.items`; нельзя просто снять `sticker` guard и потерять caption/persistence. Для 0242 главный риск — выставить `muted` после worker уже построил document; hook должен быть до этого момента. Для 0230 главный риск — переписать пользовательский файл или обойти `FHCRC`/size checks.
49. Открытые вопросы до кода: (a) принимать ли 0230 upload-only до 0197/0204 или ждать studio; (b) точный Android API для explicit «send as video» и аудио-метаданных в 0242; (c) допустимы ли scheduled/paid/secret/TTL sticker items в 0236, поскольку текущий 0096 их ограничивает; (d) нужен ли отдельный setting для 0236 вместо наследования `docked_media`; (e) действительно ли batch-15 в запросе означает иной план, поскольку `docs/batches/batch-15.md` — списки.
50. Gate пачки: все три commits закоммичены и экспортированы; `./gradlew :TMessagesProj_App:assembleDebug`; APK передан человеку; на устройстве проверены 0230 fixtures/upload, 0242 on/off/default и 0236 on/off при наличии 0175/0096; только после человеческой проверки строки PATCHLIST переводятся в `done`. До этого оставить `todo`/фактический промежуточный статус.
