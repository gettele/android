# Пачка 12 — доработки перенесённого и быстрые тумблеры

## Статус и границы

1. Это подробное рабочее руководство для **текущей пачки 12**.
2. Приватность уже перенесена в пачку 11; её prerequisites считаются landed.
3. Не возвращать в эту пачку строки приватности из batch 11.
4. В пачке ровно 12 строк PATCHLIST.
5. Пять строк — follow-up к уже перенесённым Android-патчам.
6. Семь строк — независимые быстрые тумблеры.
7. Порядок ниже является порядком реализации.
8. Не добавлять в batch 12 строки из соседних пачек.
9. Desktop-номер всегда означает текущую очередь `tdesktop`.
10. Старый номер приводится только для объяснения влитого патча.
11. Desktop source читать через `git show origin/main:patches/tdesktop/...`.
12. Android source читать через `git show tele:...`.
13. C++/Qt код не копировать.
14. `[INFERENCE]` означает, что anchor не подтверждён чтением исходника.
15. Не выдавать оценку за подтверждённый hook.
16. Все новые настройки default off, если ниже явно не указано иное.
17. Off обязан быть неотличим от stock.
18. Privacy prerequisites batch 11 не являются зависимостью для семи toggles, но уже доступны как общий слой.
19. Не менять схему stock database и `LAST_DB_VERSION`.
20. Не редактировать `.patch` вручную.

## Назначение

Batch 12 закрывает расхождения, появившиеся после переноса старых Android-фич.

Десктопная очередь изменила поведение пяти уже реализованных функций.

Android должен получить именно новый контракт, а не старую реализацию.

Одновременно семь небольших функций дают быструю проверку settings и hooks.

Пачка не является новой архитектурой настроек.

Она использует существующие `TeleConfig`, `TeleHooks`, `tele_kv` и экспорт.

Она не добавляет tele-server endpoint.

Все Telegram network requests остаются запросами Telegram API.

## Состав и порядок

| Шаг | Desktop | Android parent | Batch row | Effort | Зависимость |
|---:|---:|---|---|---|---|
| 1 | 0017 (+ бывший 0043) | 0008 | service seconds | S | `SHOW_SECONDS` |
| 2 | 0077 (+ бывший 0079) | 0051/0052 | link presets | S | `LinkRewrites` |
| 3 | 0095 | 0064 | punctual retry | M | `PunctualScheduled` |
| 4 | 0006 | 0086 | updater resume | M | `TeleUpdater` |
| 5 | 0253 | 0025 | peer-id bare copy | S | `PeerId` |
| 6 | 0125 | none | hide gift button | S | stock gift buttons |
| 7 | 0132 | none | hide similar channels | S | recommendation request |
| 8 | 0143 | none | hide collectible hint | S | profile hint |
| 9 | 0154 | none | reduce motion | S | `LiteMode` |
| 10 | 0172 | none | hide phone in profiles | S | profile phone row |
| 11 | 0233 | none | hide edited label for bots | S | message rendering |
| 12 | 0231 | none | start parameter on Start | S | bot start button |

Итого: `S×10`, `M×2`.

Реализовать строки строго сверху вниз.

Следующий шаг не начинается до проверки предыдущего API.

Каждая строка остаётся отдельным Android commit.

Если строка делится, сначала обновить PATCHLIST.

## Уже существующие parent patches

### Android 0008 — seconds

Parent добавляет формат `HH:mm:ss` через `TeleHooks.secondsFormatterFormat`.

Он покрывает обычные message times.

Он не добавляет время к тексту service message.

Follow-up не должен дублировать formatter.

Использовать тот же `SHOW_SECONDS`.

### Android 0046/0047 — link rewrites

`LinkRewrites` уже читает JSON из `tele_kv`.

`presets()` возвращает доменные правила.

`rules()` читает сохранённые пользовательские правила.

Follow-up обязан мигрировать данные при чтении.

Нельзя терять enabled, random и pattern fields.

### Android 0056 — punctual scheduled

`PunctualScheduled` сканирует `scheduled_messages_v2`.

Сейчас due rows группируются по dialog.

`sendNow` создаёт `TL_messages_sendScheduledMessages`.

Callback сейчас игнорирует error.

Retry state должен быть account-scoped.

### Android 0076 — updater

`TeleUpdater` использует `tele-update-android.json`.

APK сейчас пишется в `.part`.

Текущий `get` ожидает HTTP 200.

`download` удаляет `.part` в finally.

`finish` планирует фиксированные 3 часа.

Follow-up меняет только resume и network retry.

### Android 0024 — peer id

`ProfileActivity` показывает `PeerId.rowText`.

`rowText` может иметь grouping spaces.

При merge DC он может иметь `(DC...)`.

Copy должен быть независим от отображаемой строки.

## Exact verified parent snippets

Ниже приведены anchors, проверенные через `git show tele`.

```kotlin
fun rules(): List<Rule> {
    val raw = TeleDatabaseHelper.get(KEY) ?: return emptyList()
    val out = ArrayList<Rule>()
```

Это подтверждает JSON read path для rewrite migration.

```kotlin
fun presets(): List<Rule> = listOf(
    Rule(TYPE_DOMAIN, listOf("x.com", "twitter.com"),
        listOf("fixupx.com", "fxtwitter.com", "vxtwitter.com", "fixvx.com"), random = true),
```

Текущий X preset содержит четыре target domains.

```kotlin
Rule(TYPE_DOMAIN, listOf("tiktok.com"),
    listOf("vxtiktok.com", "tnktok.com")),
```

Текущий TikTok preset ещё содержит закрытый `vxtiktok.com`.

```kotlin
ConnectionsManager.getInstance(account).sendRequest(request) { _, _ -> }
```

Этот callback подтверждает место обработки scheduled error.

```kotlin
val temp = File(target.parentFile, target.name + ".part")
try {
    temp.outputStream().use { out ->
        get(release.url, MAX_APK_SIZE, out) { ready, total ->
```

Это подтверждает текущую updater модель без resume.

```kotlin
fun rowText(account: Int, userId: Long, chatId: Long): String {
    val id = format(account, userId, chatId)
```

Copy must not call `rowText` after this follow-up.

```kotlin
private fun botApiAdjusted(account: Int, userId: Long, chatId: Long): Long {
```

Новый public helper должен переиспользовать этот calculation.

## 1. Service seconds — desktop 0017

### Цель

При включённых секундах service message получает `text · HH:mm:ss`.

Примеры: `Alice joined · 14:03:21` и `Pinned a message · 09:01:02`.

Обычные сообщения сохраняют parent behavior.

При выключении текст и layout полностью stock.

### Implementation

Проверить `MessageObject.messageText` для `TL_messageService`.

Проверить путь `isDialogs` и центрированных action cells.

Взять секунды из `messageOwner.date`.

Использовать тот же `formatterDay`, что и parent.

Не форматировать `System.currentTimeMillis()`.

Не менять `messageOwner.message` на сервере.

Добавить маленький helper в `tele/helpers` или `TeleHooks`.

Гейт должен быть самым ранним и читать `SHOW_SECONDS`.

Не добавлять второй глобальный formatter.

`TeleHooks.onConfigChanged` должен обновлять уже созданные cells.

Пересобрать text/layout после toggle.

Обновить описание существующей строки settings.

Текст описания: service messages also show their time.

### Anchor status

`LocaleController` seconds formatter подтверждён parent patch.

`MessageObject.messageText` service anchor описан assessment.

Точный текущий overload проверить через `git show tele`.

Если overload не найден, пометить точку `[INFERENCE]`.

Не утверждать `ChatActionCell` hook без проверки.

### Acceptance

On: открыть join service message.

On: открыть pin/unpin service message.

On: проверить time zone и полночь.

On: проверить list preview.

On: переключить off без restart.

Off: сравнить text, height и wrapping со stock.

Logcat tag: `TeleSeconds`.

Logcat допускает account и mid, не текст сообщения.

## 2. Link rewrite presets — desktop 0077

### Цель

TikTok preset должен содержать только `tnktok.com`.

X/Twitter preset должен дополнительно содержать `samekosabax.com`.

Tracking regex должен распознавать `samekosabax.com`.

Старые saved targets `vxtiktok.com` мигрируют молча.

Миграция дедуплицирует одинаковые targets.

### Implementation

В `presets()` заменить TikTok list на `listOf("tnktok.com")`.

В X list добавить `samekosabax.com`.

В `Tracking.kt` добавить escaped domain в twitter/x regex.

В `rules()` нормализовать только domain rule targets.

Заменять `vxtiktok.com` на `tnktok.com`.

Сохранять порядок первого появления.

Удалять duplicate target after replacement.

Не менять pattern rule `replace` text.

Не мигрировать `from` domains.

Не перезаписывать database до необходимости.

Если read migration сохраняет, сделать atomic `TeleDatabaseHelper.put`.

Сохранить enabled и random.

Не показывать пользователю warning о закрытом домене.

### Acceptance

Preset TikTok: ровно `tnktok.com`.

Saved `vxtiktok.com`: becomes `tnktok.com`.

Saved both values: one `tnktok.com` remains.

X preset contains `samekosabax.com`.

Tracking URL on samekosabax is cleaned.

Pattern rule remains byte-for-byte equivalent.

Off: paste path is stock.

On: paste path rewrites once.

Logcat tag: `TeleLinkRewrite`.

Never log complete URLs.

## 3. Punctual retry — desktop 0095

### Цель

Отложенное сообщение отправляется вовремя, но не долбит сервер.

Текущий infinite 20-second retry должен исчезнуть.

Ошибки callback становятся retry decisions.

### Retry key and state

Ключ: `(account, dialogId, mid)`.

State: `retryAt`, `failures`, `lastReason`, terminal flag.

State may live in memory for this feature.

Do not persist message body.

Clear state on success.

Clear stale state after message is no longer scheduled.

Do not use account 0 fallback.

### Error classes

`FLOOD_WAIT_N` waits `N + 1` seconds.

`SLOWMODE_WAIT_N` waits `N + 1` seconds.

Network/timeout/code `<= 0` waits 5 seconds first.

Server code `>= 500` uses 5 seconds first.

Then 15 seconds, 1 minute, 5 minutes, 15 minutes.

Maximum five attempts.

Non-repeatable error becomes terminal immediately.

Terminal message must include safe reason.

### UX and notification

On exhaustion show toast: `couldn't send a scheduled message on time: <reason>`.

Also post a notification on a dedicated `tele_*` channel.

Do not use a stock notification channel.

Do not split a repeatable batch into single requests.

Archive chats remain included by existing scan semantics.

Avoid notification storm after terminal state.

UI work runs on main thread.

### Acceptance

FLOOD_WAIT waits server-provided seconds plus one.

SLOWMODE_WAIT behaves identically.

Timeout follows ladder.

Sixth attempt never occurs.

Permanent error does not retry.

Success clears state.

Process remains quiet between retryAt and due check.

Off: existing scheduled behavior is unchanged.

Logcat tag: `TelePunctualScheduled`.

Log only account/dialog/mid/status; never message text.

## 4. Updater resume — desktop 0006

### Download protocol

Keep `.part` after IOException or network HTTP failure.

On next download, read current part length as offset.

Send `Range: bytes=<size>-`.

Accept 206 only when Content-Range starts at offset.

For valid 206 append bytes.

HTTP 200 means server ignored Range: truncate and restart.

HTTP 416 with size > 0 triggers immediate sha256 check.

Do not treat arbitrary 416 as success.

Hash the completed APK, not the stale target.

On hash mismatch delete `.part` and report failure.

Rename only after hash success.

Progress is `offset + ready`.

### Retry schedule

Network failures schedule 1 minute.

Second network failure schedules 5 minutes.

Third schedules 15 minutes.

Fourth and later schedules 60 minutes.

Reset network failure counter on success.

Reset on non-network terminal response.

Keep ordinary 3-hour check after a clean latest check.

Local builds remain disabled.

### Acceptance

Kill network during download.

Restart/check and verify Range header.

Validate Content-Range mismatch falls back safely.

Return 200 and verify clean restart.

Return 416 with complete part and verify hash.

Corrupt part is deleted after mismatch.

Progress never jumps backwards.

1/5/15/60 schedule is observable in debug log.

Off: updater behavior outside feature remains unchanged.

Logcat tag: `TeleUpdater`.

Never log URL query secrets or full release payload.

## 5. Bare peer-id copy — desktop 0253

### Цель

Copy action copies bare Bot API digits, independent of display formatting.

A user copying a channel receives `-100...`, not spaces or `(DC...)`.

### Implementation

Add `PeerId.copyText(account, userId, chatId)`.

Return `botApiAdjusted(account, userId, chatId).toString()`.

Make only the necessary helper visibility change.

Use this helper in `ProfileActivity` Copy action.

Keep `rowText` for visible row.

Respect account argument explicitly.

Do not change ID display preferences.

Do not log copied IDs.

### Acceptance

User id copies plain decimal digits.

Group id copies negative plain decimal.

Channel id copies `-100...` when bot API toggle is on.

DC suffix never enters clipboard.

Grouping spaces never enter clipboard.

Off: visible row and existing Copy behavior otherwise remain stock.

Logcat: no clipboard content.

## Seven quick toggles

All seven follow the same contract.

Each gets a `TeleConfig` item.

Each item is default off.

Each gets settings row and export/import entry.

Each gets a search record in IDs 1120–1139.

Each has English feature row in `features.md`.

Each applies without restart through `TeleHooks.onConfigChanged`.

Each gates every relevant call site.

### Toggle table

| Desktop | Suggested key | Search ID | Default | Main Android anchors |
|---|---|---:|---|---|
| 0125 | `HIDE_GIFT_BUTTON` | 1120 | off | `ChatActivityEnterView`, channel buttons |
| 0132 | `HIDE_SIMILAR_CHANNELS` | 1121 | off | `MessageObject`, `MessagesController`, `ProfileActivity` |
| 0143 | `HIDE_COLLECTIBLE_HINT` | 1122 | off | `ProfileActivity` collectible hint |
| 0154 | `REDUCE_MOTION` | 1123 | off | `LiteMode` flags |
| 0172 | `HIDE_PHONE_IN_PROFILES` | 1124 | off | `ProfileActivity.phoneRow` |
| 0233 | `HIDE_BOT_EDITED_LABEL` | 1125 | off | `ChatMessageCell`, bot/via_bot_id |
| 0231 | `SHOW_START_PARAMETER` | 1126 | off | `ChatActivity` Start button |

Reserved 1127–1139 are not to be occupied by unrelated settings.

### 0125 gift button

Hide private-chat gift button at creation/update.

Hide channel gift entry in `ChatActivityChannelButtonsLayout`.

Reset recycled visibility when off.

Refresh existing input view on config change.

On test private chat and channel.

Off test gift button exactly as stock.

### 0132 similar channels

Gate recommendation request, not only its rendering.

Cover joined-channel message recommendation.

Cover profile recommendation surface.

Do not delete existing server data.

On verify no recommendation request and no row.

Off verify stock request and row.

### 0143 collectible hint

Early-return from collectible status tooltip.

Do not disable collectible status itself.

Do not suppress profile rows or prices.

On long-open profile and verify no tooltip.

Off verify tooltip stock.

### 0154 reduce motion

Use existing `LiteMode` flags.

Save prior flags in account-scoped tele state.

Restore prior values when toggled off.

Respect call animation exception.

Do not invent a second animation engine.

On test stickers, emoji, particles and chat effects.

Off verify user’s previous LiteMode state returns.

### 0172 hide phone

Gate only `ProfileActivity.phoneRow`.

Use shared helper if one exists.

Do not mutate contacts or server privacy.

Cover own profile and another user profile.

On verify no phone row.

Off verify stock phone row.

### 0233 bot edited label

Suppress edited marker only for bots or `via_bot_id` semantics.

Do not suppress edited marker for human messages.

Apply to text and media captions where stock label appears.

On test bot edit and human edit.

Off test both stock.

### 0231 Start parameter

Expose the parameter on Start button.

Use long press for tooltip/copy only if stock action allows it.

Do not alter bot command payload.

Handle empty parameter without an empty tooltip.

On test deep link with parameter.

Off verify Start action is stock.

## Settings, defaults and search

Settings page must use existing group names.

No new top-level page is needed.

Follow-up rows belong beside their parent setting.

Quick toggles use interface, sending or ids groups as appropriate.

`REDUCE_MOTION` belongs to interface.

`HIDE_PHONE_IN_PROFILES` belongs to privacy/profile group.

`SHOW_START_PARAMETER` belongs to interface or chats group.

Search titles and descriptions are in `strings_tele.xml`.

Search keywords include gift, recommendations, collectible, motion, phone, bot, edited, start parameter.

IDs 1120–1126 must be unique.

IDs 1127–1139 remain reserved.

Search results open Tele page, not stock privacy page.

Search rows are registry-static; values remain account-scoped.

## Migration and retry state

No stock migration version is allowed.

Existing `link_rewrite_rules` is read compatibly.

`vxtiktok.com` migration is idempotent.

No migration is needed for service seconds.

No migration is needed for peer copy.

Updater `.part` is intentionally preserved only for the matching release target.

A part from a different tag must be discarded.

Punctual retry memory is keyed by account/dialog/mid.

Retry entries must expire after terminal success or stale schedule removal.

Do not persist message body or peer names.

Account switch must not reuse retry state from another account.

## Threading and account rules

Settings changes arrive on the lifecycle bus.

View changes run on Android main thread.

Storage reads run on storage/database queue.

ConnectionsManager callbacks hop to UI before touching views.

Updater runs on its `DispatchQueue`.

Punctual scan reads storage queue and sends on UI/network path.

Every controller call carries `account`.

Never use `UserConfig.selectedAccount` as implicit feature state.

Never cache mutable rule lists across accounts.

Recycler/list rows reset all visibility and alpha on bind.

## User-visible UX and errors

Descriptions must explain what is hidden, not implementation.

Default-off settings must not surprise existing users.

Network failures use short local errors.

Do not expose message text, phone, username or complete URL in logs.

Updater error offers retry through existing check action.

Scheduled terminal failure offers toast plus tele notification.

Link migration is silent and does not alter pasted text retroactively.

Peer copy has no confirmation dialog beyond stock clipboard behavior.

Toggles apply immediately without restart.

## features.md rows

Add one English row per user-facing quick toggle.

The five follow-ups update the parent row only where behavior description changes.

Service seconds row says service messages also show time.

Link row says TikTok target is `tnktok.com` and X includes samekosabax.

Scheduled row mentions bounded retries and failure notification.

Updater row mentions resume after network interruption.

Peer row says copy is plain digits independent of display.

Every row includes settings section, default, Android patch file and desktop number.

Follow-up may use the parent patch filename plus a fix patch once exported.

Do not document unimplemented future IDs.

## Logcat checklist

`TeleSeconds`: account/mid/status only.

`TeleLinkRewrite`: rule type and migration count, no URL.

`TelePunctualScheduled`: account/dialog/mid/retry status.

`TeleUpdater`: state, tag, offset, HTTP class; no full URL.

`TelePrivacy`: only if shared privacy helper is touched.

`TeleToggle`: key and state, no personal data.

Debug logs must be disabled or reduced in release builds.

Errors must not include message bodies.

## Acceptance matrix

| Area | On | Off |
|---|---|---|
| service seconds | service text has time | byte/visual stock |
| link presets | targets and regex updated | rewrite gate stock |
| scheduled | bounded classified retries | parent behavior |
| updater | range resume and ladder | existing updater semantics |
| peer copy | bare Bot API digits | existing row copy semantics |
| gifts | gift controls hidden | gift controls stock |
| similar channels | request/row suppressed | recommendations stock |
| collectible hint | tooltip absent | tooltip stock |
| reduce motion | LiteMode restrictions | prior flags restored |
| phone | phone row absent | phone row stock |
| bot edited | bot marker absent | all markers stock |
| Start parameter | parameter visible/action works | Start stock |

## Batch gate

After all 12 commits are exported, run the documented debug build.

Command: `./gradlew :TMessagesProj_App:assembleDebug`.

Exercise every toggle in default, on and off states where practical.

Install the ABI matching the test device.

Manually test all five follow-ups on a real account.

Verify two accounts for scheduled and settings state.

Verify process restart for updater part and settings.

Verify network interruption for updater and scheduled retry.

Verify archive chat and channel paths.

Inspect logcat for privacy-safe output.

Only a human can mark the batch `done`.

Until then PATCHLIST status remains truthful.

The batch gate is not satisfied by compilation alone.

## Handoff checklist

1. Confirm batch 11 privacy prerequisites are landed.
2. Confirm parent Android patches exist in `git show tele`.
3. Confirm desktop anchors exist in `git show origin/main`.
4. Implement rows in the twelve-step order.
5. Add config, settings, search and export for seven toggles.
6. Update parent feature rows and add follow-up wording.
7. Export patches from the Android checkout.
8. Update PATCHLIST statuses only after export.
9. Assemble debug APK.
10. Hand APK and numbered manual tests to maintainer.
11. Wait for human on/off verification.
12. Mark batch done only after the batch gate.

## Explicit non-goals

Do not implement bookmarks, folders, privacy picker or ghost schedule here.

Do not redesign TeleSettingsActivity.

Do not add a new database schema.

Do not add a tele-server API.

Do not edit generated `TLRPC.java`.

Do not change unrelated parent behavior.

Do not broaden retry policy beyond the stated error classes.

Do not log sensitive user data.

Do not claim a desktop anchor that was not verified.

Пачка 12 начинается после уже landed privacy batch 11 и заканчивается только после полного batch gate.
