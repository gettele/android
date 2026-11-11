# Android patch registry

This is the public, human-readable registry of tele changes whose design or implementation originates on Android rather than being a direct port of the desktop queue. The canonical machine-readable copy is [`ci/android-patches.json`](../ci/android-patches.json); keep both in sync.

The registry is curated, not exhaustive. It groups follow-up patches into logical changes rather than indexing every file in [`patches/android`](../patches/android). Absence from the registry does not imply a pure desktop port.

## Schema

The JSON file is an object with one top-level `entries` array; each array element is one logical entry.

| field | type | meaning |
|---|---|---|
| `id` | string | stable logical identifier (`A001`, `A002`, ...). IDs are never renumbered or reused; see [lifecycle](#lifecycle). |
| `title` | string | short public name of the logical change. |
| `type` | `original` \| `adaptation` | `original` means Android-only design and implementation with no desktop feature equivalent; `adaptation` means a substantial Android implementation or extension of a desktop feature. The value describes the entry as a whole. |
| `status` | `active` \| `removed` | `removed` is a tombstone: the entry stays in the registry so its ID cannot be reused. |
| `desktop` | array of strings | desktop feature titles this entry adapts or relates to. Titles are used instead of queue numbers because the desktop queue renumbers. The array is required and may be empty. An `original` entry may cite related desktop work, but the reference does not turn it into an adaptation; both current originals use an empty array. |
| `description` | string | concise scope and the split between ported feature and Android-native work. |
| `patches` | array of strings | exact filenames under `patches/android/`, including follow-ups and fixes that belong to the same logical change. Required; must be empty for a `removed` tombstone. |
| `reason` | string, optional for `active` | required on a `removed` tombstone; explains why the logical change was withdrawn. |

## Classification

- `original` is reserved for changes whose problem, design and implementation are Android-only. A non-empty `desktop` list may still explain related work, but no desktop feature is being adapted wholesale.
- `adaptation` covers Android-native reimplementation of a desktop feature, including substantial new UI, storage, JNI/NDK or platform integration. It does **not** claim the whole feature as an Android original.
- Desktop references are feature titles from the desktop queue, not queue positions. Numbers in old plans were unstable across renumbering, so they are deliberately not used here.
- Fixes and follow-ups are folded into the logical entry they serve. Small cross-cutting technical fixes that do not represent an original or adaptation are left to the maintainer and are outside this registry.
- Entry-level `type` describes the logical change as a whole. A group can contain Android-only fixes around a ported feature; the description says which part is native.

## Lifecycle

- **Allocation.** A new logical change gets the next free identifier after the current maximum numeric value (`max + 1`). Numbers below the maximum are never allocated, even if an entry was removed.
- **Never recycle.** A removed entry keeps its `id` forever. Deleting or reusing an ID would silently repoint external links, release notes and historical diffs.
- **Removal.** Withdraw a change by setting `status` to `removed`, keeping the `id` and `title`, adding a short `reason`, and setting `patches` to an empty array. Stable history lives in git, not in stale filename references; consumers must not require a removed tombstone to reference files that still exist.
- **Rebase and renames.** When a rebase renames a patch file or changes its content, update the filename in the existing entry. Do not allocate a new ID or a new entry for the renamed patch. `id` tracks the logical change, not the filename.
- **Many-to-many.** One entry may list many patches and one patch may legitimately belong to more than one logical entry. Consumers must not assume patch filenames are unique across entries. The current registry has multiple files per entry but no filename shared between entries.
- **Grouping.** Add a genuinely independent logical change as a new entry; do not split or merge existing IDs merely to match a new patch layout. Follow-up fixes stay in the entry they serve.

## Entries

| id | title | type | status | patches |
|---|---|---|---|---|
| [A001](#a001) | Android build credentials and runtime skeleton | original | active | 2 |
| [A002](#a002) | Android packaging, branding and launcher icons | adaptation | active | 8 |
| [A003](#a003) | Native tele settings, navigation and search | adaptation | active | 16 |
| [A004](#a004) | Local names and aliases with shared native editors | adaptation | active | 3 |
| [A005](#a005) | Retained deleted messages, edit history and saved drafts | adaptation | active | 7 |
| [A006](#a006) | Public tele server, Argon2 and crash bridge | adaptation | active | 11 |
| [A007](#a007) | Android updater, release notes and local tele chat | adaptation | active | 7 |
| [A008](#a008) | Message shots and render pipeline | adaptation | active | 5 |
| [A009](#a009) | Notification center, presence and service notices | adaptation | active | 9 |
| [A010](#a010) | Diagnostics, MTProto tools and memory reports | adaptation | active | 6 |
| [A011](#a011) | Wallet engine Android integration | adaptation | active | 5 |
| [A012](#a012) | Android scripting host and native scripting UIs | adaptation | active | 23 |
| [A013](#a013) | Cross-cutting fork security boundaries | original | active | 1 |
| [A014](#a014) | Docked media composer | adaptation | active | 22 |
| [A015](#a015) | Round video recording controls | original | active | 1 |

<a id="a001"></a>

## A001 — Android build credentials and runtime skeleton

**Type:** `original` · **Status:** `active`

**Desktop references:** none (Android-only change).

Adds fork-specific API credentials from local.properties and the Kotlin/tele runtime skeleton (TeleConfig, TeleHooks, tele.db) that later Android changes build on. This is Android-only build and storage foundation.

| patch |
|---|
| [`0001-misc-support-custom-api-credentials.patch`](../patches/android/0001-misc-support-custom-api-credentials.patch) |
| [`0002-misc-enable-kotlin-and-add-the-tele-skeleton.patch`](../patches/android/0002-misc-enable-kotlin-and-add-the-tele-skeleton.patch) |

<a id="a002"></a>

## A002 — Android packaging, branding and launcher icons

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *rename the app to tele*; *call the app tele everywhere*; *new tele app and tray icons*

Renames the app and fork packages, disables stock Google services, overrides user-visible app names, and ships the Android adaptive launcher, notification and settings icons. The packaging, string overrides and generated icon assets are Android-specific work; the naming and icon feature follows the desktop.

| patch |
|---|
| [`0004-misc-call-the-app-tele.patch`](../patches/android/0004-misc-call-the-app-tele.patch) |
| [`0006-misc-use-fork-package-names.patch`](../patches/android/0006-misc-use-fork-package-names.patch) |
| [`0007-misc-disable-google-services-integration.patch`](../patches/android/0007-misc-disable-google-services-integration.patch) |
| [`0034-feat-call-the-app-tele-in-its-own-texts.patch`](../patches/android/0034-feat-call-the-app-tele-in-its-own-texts.patch) |
| [`0035-feat-tele-launcher-and-settings-icons.patch`](../patches/android/0035-feat-tele-launcher-and-settings-icons.patch) |
| [`0041-feat-apply-the-generated-icon-set.patch`](../patches/android/0041-feat-apply-the-generated-icon-set.patch) |
| [`0087-fix-finish-tele-branding-and-settings.patch`](../patches/android/0087-fix-finish-tele-branding-and-settings.patch) |
| [`0277-fix-call-the-app-tele-in-unsupported-messages.patch`](../patches/android/0277-fix-call-the-app-tele-in-unsupported-messages.patch) |

<a id="a003"></a>

## A003 — Native tele settings, navigation and search

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *add a tele section to the settings*; *group and search tele settings*; *regroup tele settings pages*; *collapsible sub-toggles in tele settings*; *trim settings descriptions*

Builds the Android tele settings tree: section pages, grouped rows, collapsible sub-options, and stock settings-search integration that opens and highlights the matching row. Includes Android-side fixes for search results and rows; the settings architecture is native Android work around the desktop settings feature.

| patch |
|---|
| [`0003-feat-add-the-tele-settings-section.patch`](../patches/android/0003-feat-add-the-tele-settings-section.patch) |
| [`0019-fix-apply-interface-toggles-without-restart.patch`](../patches/android/0019-fix-apply-interface-toggles-without-restart.patch) |
| [`0036-feat-split-tele-settings-into-sections-and-add-them-.patch`](../patches/android/0036-feat-split-tele-settings-into-sections-and-add-them-.patch) |
| [`0039-feat-icon-rows-for-tele-settings-sections.patch`](../patches/android/0039-feat-icon-rows-for-tele-settings-sections.patch) |
| [`0088-fix-polish-the-tele-settings-labels.patch`](../patches/android/0088-fix-polish-the-tele-settings-labels.patch) |
| [`0101-feat-search-jumps-to-the-setting.patch`](../patches/android/0101-feat-search-jumps-to-the-setting.patch) |
| [`0108-feat-use-the-chat-list-search.patch`](../patches/android/0108-feat-use-the-chat-list-search.patch) |
| [`0119-feat-regroup-tele-settings.patch`](../patches/android/0119-feat-regroup-tele-settings.patch) |
| [`0120-feat-collapse-tele-setting-suboptions.patch`](../patches/android/0120-feat-collapse-tele-setting-suboptions.patch) |
| [`0144-fix-shorten-setting-descriptions.patch`](../patches/android/0144-fix-shorten-setting-descriptions.patch) |
| [`0261-fix-restore-lost-settings-search-results.patch`](../patches/android/0261-fix-restore-lost-settings-search-results.patch) |
| [`0262-fix-restore-three-missing-tele-settings-rows.patch`](../patches/android/0262-fix-restore-three-missing-tele-settings-rows.patch) |
| [`0266-fix-make-settings-search-case-insensitive.patch`](../patches/android/0266-fix-make-settings-search-case-insensitive.patch) |
| [`0303-fix-open-the-tele-submenus-at-their-item.patch`](../patches/android/0303-fix-open-the-tele-submenus-at-their-item.patch) |
| [`0306-fix-point-the-settings-search-at-real-rows.patch`](../patches/android/0306-fix-point-the-settings-search-at-real-rows.patch) |
| [`0330-fix-keep-other-changes-inside-their-settings-group.patch`](../patches/android/0330-fix-keep-other-changes-inside-their-settings-group.patch) |

<a id="a004"></a>

## A004 — Local names and aliases with shared native editors

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *name people only for you*; *link usernames to profiles locally*

Adds Android editors for per-account local names and usernames: themed inline fields with delete, management screens in tele settings, and one shared alias dialog used by chat and profile menus. The feature follows desktop local names and aliases; the editor flow is native Android.

| patch |
|---|
| [`0031-feat-dim-the-name-and-alias-fields-and-allow-deletin.patch`](../patches/android/0031-feat-dim-the-name-and-alias-fields-and-allow-deletin.patch) |
| [`0032-feat-manage-local-names-and-aliases-from-tele-settin.patch`](../patches/android/0032-feat-manage-local-names-and-aliases-from-tele-settin.patch) |
| [`0033-feat-one-shared-alias-dialog-with-a-title-that-names.patch`](../patches/android/0033-feat-one-shared-alias-dialog-with-a-title-that-names.patch) |

<a id="a005"></a>

## A005 — Retained deleted messages, edit history and saved drafts

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *keep deleted messages*; *keep messages you delete yourself*; *keep the edit history of messages*; *show edit history as a chat*; *keep drafts on this device*; *save drafts for later*

Stores kept deleted messages, message edits and draft snapshots in tele.db and adds native screens for drafts and deleted messages. The desktop retention and draft features are reimplemented for Android storage and UI; the Android design is substantial, but the feature concept is not claimed as original.

| patch |
|---|
| [`0060-feat-keep-deleted-messages.patch`](../patches/android/0060-feat-keep-deleted-messages.patch) |
| [`0061-feat-keep-the-edit-history-of-messages.patch`](../patches/android/0061-feat-keep-the-edit-history-of-messages.patch) |
| [`0062-feat-save-drafts-for-later.patch`](../patches/android/0062-feat-save-drafts-for-later.patch) |
| [`0064-fix-saved-drafts-and-deleted-replies.patch`](../patches/android/0064-fix-saved-drafts-and-deleted-replies.patch) |
| [`0131-feat-redesign-saved-drafts.patch`](../patches/android/0131-feat-redesign-saved-drafts.patch) |
| [`0132-feat-redesign-deleted-messages.patch`](../patches/android/0132-feat-redesign-deleted-messages.patch) |
| [`0143-fix-protect-all-kept-media.patch`](../patches/android/0143-fix-protect-all-kept-media.patch) |

<a id="a006"></a>

## A006 — Public tele server, Argon2 and crash bridge

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *apply verification and marks from the tele server*; *show checkmarks and custom verification everywhere*; *clear server data and explain custom verifications*; *usernames from the tele server*; *send crash reports to the tele server*

Adds the Android client for the public tele server: hashed badge feed, Argon2 helper, server usernames, badge rendering hooks, refresh and clear, and the crash-report upload bridge. It only downloads public data and sends no account data, matching the desktop server feature.

| patch |
|---|
| [`0065-feat-add-a-tele-server-client-skeleton.patch`](../patches/android/0065-feat-add-a-tele-server-client-skeleton.patch) |
| [`0066-feat-add-an-argon2-helper.patch`](../patches/android/0066-feat-add-an-argon2-helper.patch) |
| [`0067-feat-add-a-tele-crash-reporter-skeleton.patch`](../patches/android/0067-feat-add-a-tele-crash-reporter-skeleton.patch) |
| [`0068-feat-show-server-verification-badge-in-profiles.patch`](../patches/android/0068-feat-show-server-verification-badge-in-profiles.patch) |
| [`0069-feat-show-tele-custom-badges-everywhere.patch`](../patches/android/0069-feat-show-tele-custom-badges-everywhere.patch) |
| [`0070-feat-show-tele-server-usernames.patch`](../patches/android/0070-feat-show-tele-server-usernames.patch) |
| [`0071-feat-keep-tele-server-data-fresh.patch`](../patches/android/0071-feat-keep-tele-server-data-fresh.patch) |
| [`0072-feat-explain-tele-badges-in-profiles.patch`](../patches/android/0072-feat-explain-tele-badges-in-profiles.patch) |
| [`0073-feat-show-tele-badges-in-bubbles-and-settings.patch`](../patches/android/0073-feat-show-tele-badges-in-bubbles-and-settings.patch) |
| [`0074-feat-find-chats-by-server-aliases.patch`](../patches/android/0074-feat-find-chats-by-server-aliases.patch) |
| [`0075-feat-offer-to-send-crash-reports-on-start.patch`](../patches/android/0075-feat-offer-to-send-crash-reports-on-start.patch) |

<a id="a007"></a>

## A007 — Android updater, release notes and local tele chat

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *update from the tele github releases*; *show what's new in tele after an update*; *show new settings after an update*; *browse every tele version's changes*; *what's new as a settings page with live toggles*

Implements the Android in-app updater (APK feed, SHA-256, resume and retry), a local "tele" changelog chat, per-version history and live new-settings toggles. The update flow is Android-specific; the release-notes and what's-new behavior follows the desktop.

| patch |
|---|
| [`0076-feat-update-from-the-tele-github-releases.patch`](../patches/android/0076-feat-update-from-the-tele-github-releases.patch) |
| [`0077-feat-show-what-s-new-in-a-local-tele-chat.patch`](../patches/android/0077-feat-show-what-s-new-in-a-local-tele-chat.patch) |
| [`0078-feat-show-new-settings-after-an-update.patch`](../patches/android/0078-feat-show-new-settings-after-an-update.patch) |
| [`0110-fix-resume-an-interrupted-update-download.patch`](../patches/android/0110-fix-resume-an-interrupted-update-download.patch) |
| [`0201-feat-every-version-s-changes.patch`](../patches/android/0201-feat-every-version-s-changes.patch) |
| [`0202-feat-what-s-new-with-live-toggles.patch`](../patches/android/0202-feat-what-s-new-with-live-toggles.patch) |
| [`0203-fix-retry-dropped-update-downloads.patch`](../patches/android/0203-fix-retry-dropped-update-downloads.patch) |

<a id="a008"></a>

## A008 — Message shots and render pipeline

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *save messages as a picture*; *scale shots up to 4x and show your messages as incoming*; *choose what shots show*; *show skipped messages in shots*

Renders selected messages into a bitmap on Android with 1x-4x scale, incoming-style own messages, configurable visibility and skipped-message markers; fixes sender and badge rendering and normalizes docked-shot sending. The rendering code is Android-native work around the desktop shot feature.

| patch |
|---|
| [`0083-feat-save-messages-as-a-picture.patch`](../patches/android/0083-feat-save-messages-as-a-picture.patch) |
| [`0259-feat-show-skipped-messages-in-shots.patch`](../patches/android/0259-feat-show-skipped-messages-in-shots.patch) |
| [`0269-fix-keep-the-sender-of-my-messages-in-shots.patch`](../patches/android/0269-fix-keep-the-sender-of-my-messages-in-shots.patch) |
| [`0270-fix-keep-badges-clear-of-names-and-restore-shot-tags.patch`](../patches/android/0270-fix-keep-badges-clear-of-names-and-restore-shot-tags.patch) |
| [`0271-fix-send-docked-shots-like-normal-shots.patch`](../patches/android/0271-fix-send-docked-shots-like-normal-shots.patch) |

<a id="a009"></a>

## A009 — Notification center, presence and service notices

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *notify when people come online*; *notification centre*; *rate-limit notices for slowmode and download throttling*; *mentions and replies in the notification centre*; *reply and mention badges in the notification centre*; *notification centre shows whole entries*; *copied values in the notification centre*; *server notices*

Adds the on-device notification center and its Android integrations: tgnet flood-wait hook, presence notifications, mention and reply entries, badges, full entries, copied-value logging, tele toasts and server notices. The subsystem is ported, with the JNI hook and Android UI written here.

| patch |
|---|
| [`0204-feat-notify-when-people-come-online.patch`](../patches/android/0204-feat-notify-when-people-come-online.patch) |
| [`0210-feat-notifications-center.patch`](../patches/android/0210-feat-notifications-center.patch) |
| [`0211-feat-rate-limit-notice-filters.patch`](../patches/android/0211-feat-rate-limit-notice-filters.patch) |
| [`0212-feat-mentions-and-replies-in-center.patch`](../patches/android/0212-feat-mentions-and-replies-in-center.patch) |
| [`0213-feat-reply-and-mention-badges.patch`](../patches/android/0213-feat-reply-and-mention-badges.patch) |
| [`0214-feat-full-center-entries.patch`](../patches/android/0214-feat-full-center-entries.patch) |
| [`0215-feat-copied-values-in-center.patch`](../patches/android/0215-feat-copied-values-in-center.patch) |
| [`0216-feat-server-notices.patch`](../patches/android/0216-feat-server-notices.patch) |
| [`0217-feat-log-tele-toasts.patch`](../patches/android/0217-feat-log-tele-toasts.patch) |

<a id="a010"></a>

## A010 — Diagnostics, MTProto tools and memory reports

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *capture and inspect mtproto*; *add the mtproto console*; *send crash reports to the tele server*; *send crash reports without a dump*; *report freezes*

Adds Android diagnostics: memory data in crash reports, OOM heap snapshots, Java-side MTProto capture and inspection, a schema-driven MTProto console, no-dump and freeze reports, and foreground-only freeze gating. The Android tooling and crash surfaces are native work; capture and console behavior follows the desktop.

| patch |
|---|
| [`0240-feat-memory-in-crash-reports.patch`](../patches/android/0240-feat-memory-in-crash-reports.patch) |
| [`0241-feat-memory-snapshot-on-out-of-memory.patch`](../patches/android/0241-feat-memory-snapshot-on-out-of-memory.patch) |
| [`0242-feat-capture-and-inspect-mtproto.patch`](../patches/android/0242-feat-capture-and-inspect-mtproto.patch) |
| [`0243-feat-add-the-mtproto-console.patch`](../patches/android/0243-feat-add-the-mtproto-console.patch) |
| [`0244-feat-add-diagnostic-reports.patch`](../patches/android/0244-feat-add-diagnostic-reports.patch) |
| [`0331-fix-limit-freeze-reports-to-foreground-stalls.patch`](../patches/android/0331-fix-limit-freeze-reports-to-foreground-stalls.patch) |

<a id="a011"></a>

## A011 — Wallet engine Android integration

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *take wallet-engine from gettele/money for private keys*; *import wallets from private keys*; *copy secret words without waiting*; *turn on the wallet before telegram does*

Builds the Android wallet engine with private-key support, key rotation and backup, import and recovery screens, pasted-word handling and phrase-sheet scrolling. The engine integration and NDK bridge are Android work built on the desktop wallet-engine feature.

| patch |
|---|
| [`0245-build-wallet-engine-with-private-keys.patch`](../patches/android/0245-build-wallet-engine-with-private-keys.patch) |
| [`0246-feat-wallet-keys.patch`](../patches/android/0246-feat-wallet-keys.patch) |
| [`0247-fix-spread-pasted-wallet-words.patch`](../patches/android/0247-fix-spread-pasted-wallet-words.patch) |
| [`0248-fix-scroll-the-wallet-phrase-sheet.patch`](../patches/android/0248-fix-scroll-the-wallet-phrase-sheet.patch) |
| [`0278-feat-recover-wallets-from-an-address-and-12-words.patch`](../patches/android/0278-feat-recover-wallets-from-an-address-and-12-words.patch) |

<a id="a012"></a>

## A012 — Android scripting host and native scripting UIs

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *scripting prototype*; *let scripts give their menu items icons*

Adds the QuickJS-ng JNI host, per-account script runtimes, grants and sandboxing, and native Android surfaces for menus, links, notifications, shared files, compose, player, calls, message actions, script text and logs. The host and UI are Android-native implementations of the desktop scripting prototype.

| patch |
|---|
| [`0254-feat-add-android-scripting-runtime.patch`](../patches/android/0254-feat-add-android-scripting-runtime.patch) |
| [`0255-feat-give-script-menus-icons.patch`](../patches/android/0255-feat-give-script-menus-icons.patch) |
| [`0298-fix-expose-message-actions-under-both-names.patch`](../patches/android/0298-fix-expose-message-actions-under-both-names.patch) |
| [`0310-feat-add-schedules-the-theme-and-settings-pages-to-s.patch`](../patches/android/0310-feat-add-schedules-the-theme-and-settings-pages-to-s.patch) |
| [`0311-feat-let-scripts-intercept-links.patch`](../patches/android/0311-feat-let-scripts-intercept-links.patch) |
| [`0312-feat-let-scripts-hide-notifications.patch`](../patches/android/0312-feat-let-scripts-hide-notifications.patch) |
| [`0313-feat-let-scripts-keep-shared-files-away.patch`](../patches/android/0313-feat-let-scripts-keep-shared-files-away.patch) |
| [`0314-feat-let-scripts-rewrite-the-message-field.patch`](../patches/android/0314-feat-let-scripts-rewrite-the-message-field.patch) |
| [`0315-feat-let-scripts-follow-the-player.patch`](../patches/android/0315-feat-let-scripts-follow-the-player.patch) |
| [`0316-feat-let-scripts-follow-calls.patch`](../patches/android/0316-feat-let-scripts-follow-calls.patch) |
| [`0317-feat-let-scripts-add-message-actions.patch`](../patches/android/0317-feat-let-scripts-add-message-actions.patch) |
| [`0318-fix-keep-scripting-on-after-a-restart.patch`](../patches/android/0318-fix-keep-scripting-on-after-a-restart.patch) |
| [`0319-fix-let-scripts-reach-the-player-and-the-message-men.patch`](../patches/android/0319-fix-let-scripts-reach-the-player-and-the-message-men.patch) |
| [`0320-fix-follow-the-player-without-events-and-show-script.patch`](../patches/android/0320-fix-follow-the-player-without-events-and-show-script.patch) |
| [`0321-feat-show-a-script-text-on-its-own-screen.patch`](../patches/android/0321-feat-show-a-script-text-on-its-own-screen.patch) |
| [`0322-fix-refresh-the-profile-a-script-wrote.patch`](../patches/android/0322-fix-refresh-the-profile-a-script-wrote.patch) |
| [`0323-fix-send-optional-script-request-fields.patch`](../patches/android/0323-fix-send-optional-script-request-fields.patch) |
| [`0324-fix-refresh-script-translations-and-show-text-dialog.patch`](../patches/android/0324-fix-refresh-script-translations-and-show-text-dialog.patch) |
| [`0325-fix-isolate-scripts-and-enforce-runtime-permissions.patch`](../patches/android/0325-fix-isolate-scripts-and-enforce-runtime-permissions.patch) |
| [`0326-fix-keep-script-decorations-out-of-message-edits.patch`](../patches/android/0326-fix-keep-script-decorations-out-of-message-edits.patch) |
| [`0327-fix-run-fetch-and-message-decorators-asynchronously.patch`](../patches/android/0327-fix-run-fetch-and-message-decorators-asynchronously.patch) |
| [`0328-feat-group-installed-scripts-together.patch`](../patches/android/0328-feat-group-installed-scripts-together.patch) |
| [`0329-fix-make-script-logs-selectable.patch`](../patches/android/0329-fix-make-script-logs-selectable.patch) |

<a id="a013"></a>

## A013 — Cross-cutting fork security boundaries

**Type:** `original` · **Status:** `active`

**Desktop references:** none (Android-only change).

Hardens fork boundaries that stock Android does not cover: per-account script isolation and approvals, pending-reply ownership, streamer-mode secret windows, last-seen restoration, local-password recovery ownership, and bounded regex, notice and update paths. Android-specific audit work.

| patch |
|---|
| [`0332-security-harden-fork-boundaries.patch`](../patches/android/0332-security-harden-fork-boundaries.patch) |

<a id="a014"></a>

## A014 — Docked media composer

**Type:** `adaptation` · **Status:** `active`

**Desktop references:** *attach media above the field (docked media)*; *caption docked media and bring it to parity with the send box*

Implements the Android media composer above the message field: docked photos, video, documents, shots and captioned stickers, per-chat and per-topic drafts, reordering, spoiler previews, drag animation, removal and send integration. The composer is a substantial native Android implementation of the desktop docked-media feature.

| patch |
|---|
| [`0086-feat-attach-media-above-the-field.patch`](../patches/android/0086-feat-attach-media-above-the-field.patch) |
| [`0173-feat-dock-shots-above-the-field.patch`](../patches/android/0173-feat-dock-shots-above-the-field.patch) |
| [`0258-feat-dock-captioned-stickers.patch`](../patches/android/0258-feat-dock-captioned-stickers.patch) |
| [`0264-fix-keep-docked-drafts-in-their-topic.patch`](../patches/android/0264-fix-keep-docked-drafts-in-their-topic.patch) |
| [`0279-feat-reorder-docked-media-dock-documents-and-keep-hq.patch`](../patches/android/0279-feat-reorder-docked-media-dock-documents-and-keep-hq.patch) |
| [`0280-fix-polish-docked-media-tiles.patch`](../patches/android/0280-fix-polish-docked-media-tiles.patch) |
| [`0281-fix-docked-media-previews-drag-and-spoiler-clipping.patch`](../patches/android/0281-fix-docked-media-previews-drag-and-spoiler-clipping.patch) |
| [`0282-fix-dock-internal-storage-files-and-restore-document.patch`](../patches/android/0282-fix-dock-internal-storage-files-and-restore-document.patch) |
| [`0283-fix-dock-internal-storage-files-and-keep-files-in-th.patch`](../patches/android/0283-fix-dock-internal-storage-files-and-keep-files-in-th.patch) |
| [`0284-fix-open-docked-media-viewer-with-files-in-the-tray.patch`](../patches/android/0284-fix-open-docked-media-viewer-with-files-in-the-tray.patch) |
| [`0285-fix-keep-spoiler-media-proportions-in-docked-preview.patch`](../patches/android/0285-fix-keep-spoiler-media-proportions-in-docked-preview.patch) |
| [`0286-fix-cover-docked-spoiler-previews.patch`](../patches/android/0286-fix-cover-docked-spoiler-previews.patch) |
| [`0287-fix-round-docked-media-corners-with-cover-crop.patch`](../patches/android/0287-fix-round-docked-media-corners-with-cover-crop.patch) |
| [`0288-feat-delay-docked-media-menu-and-keep-drag-priority.patch`](../patches/android/0288-feat-delay-docked-media-menu-and-keep-drag-priority.patch) |
| [`0289-feat-animate-docked-media-drag-and-removal.patch`](../patches/android/0289-feat-animate-docked-media-drag-and-removal.patch) |
| [`0290-feat-start-docked-drag-after-150ms.patch`](../patches/android/0290-feat-start-docked-drag-after-150ms.patch) |
| [`0291-feat-open-docked-media-menu-500ms-after-drag-readine.patch`](../patches/android/0291-feat-open-docked-media-menu-500ms-after-drag-readine.patch) |
| [`0292-refactor-one-long-press-for-the-docked-media-menu-an.patch`](../patches/android/0292-refactor-one-long-press-for-the-docked-media-menu-an.patch) |
| [`0293-fix-keep-docked-drag-working-while-the-long-press-me.patch`](../patches/android/0293-fix-keep-docked-drag-working-while-the-long-press-me.patch) |
| [`0294-fix-show-docked-media-menu-on-release-so-drag-stays-.patch`](../patches/android/0294-fix-show-docked-media-menu-on-release-so-drag-stays-.patch) |
| [`0295-fix-keep-docked-spoilers-after-leaving-the-media-edi.patch`](../patches/android/0295-fix-keep-docked-spoilers-after-leaving-the-media-edi.patch) |
| [`0333-docked-complete-media-composer.patch`](../patches/android/0333-docked-complete-media-composer.patch) |

<a id="a015"></a>

## A015 — Round video recording controls

**Type:** `original` · **Status:** `active`

**Desktop references:** none (Android-only change).

Adds optional manual recording start and camera zoom controls to the Android round-video recorder. Round glass controls sit below the centered camera preview; holding a control opens a scrolling zoom ruler with a fixed pointer, glass zoom label and lens checkpoints, preserving the selected zoom. Preset changes animate the zoom. Lens discovery accounts for sensor size as well as focal length, rather than treating digital zoom values as separate cameras.

Rear controls always include wide/minimum, main 1× and telephoto/2× presets; additional accessible lenses add buttons. Digital fallbacks do not claim extra physical lenses, and zoom-out is limited to the camera's actual minimum. The active interval's button shows the current zoom. The ruler targets 5×, or the longest native telephoto above 5× plus 3×, clamped to hardware limits.
The ruler's actual maximum is also labeled and provides checkpoint haptics, without adding another preset button.
With a reply panel, pause and resume controls retain the same vertical position throughout the transition to the recorded-video preview.

| patch |
|---|
| [`0334-feat-improve-round-video-controls.patch`](../patches/android/0334-feat-improve-round-video-controls.patch) |
