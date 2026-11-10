# tele 11 · 13.2.1 — preview

Unpublished draft, generated from `ci/changelog.json`. Download and release-tag links become available only after publication. This preview does not mark manual release gates as passed.

telegram android [13.2.1](https://github.com/DrKLO/Telegram) with 333 patches.

## new

### sending

- preview attached photos and videos as an album or a strip, with a compact header, grouping and file controls ([0333](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0333-docked-complete-media-composer.patch), settings → tele → sending → attach media above the field, off)
- pasted media, keyboard images and single-chat shares wait above the field; scheduled messages, quick replies and paid chats use the dock too ([0333](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0333-docked-complete-media-composer.patch), settings → tele → sending → attach media above the field, with docked media)

### scripts

- scripts can run on a schedule, switch day and night mode and add their own settings pages ([0310](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0310-feat-add-schedules-the-theme-and-settings-pages-to-s.patch), settings → tele → scripts, off)
- scripts can clean or replace opened links, silence notifications and reject files shared into the app, with your permission ([0311](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0311-feat-let-scripts-intercept-links.patch), [0312](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0312-feat-let-scripts-hide-notifications.patch), [0313](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0313-feat-let-scripts-keep-shared-files-away.patch), settings → tele → scripts, off)
- scripts can expand text in the message field, follow the player and calls, and add actions to message menus ([0314](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0314-feat-let-scripts-rewrite-the-message-field.patch), [0315](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0315-feat-let-scripts-follow-the-player.patch), [0316](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0316-feat-let-scripts-follow-calls.patch), [0317](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0317-feat-let-scripts-add-message-actions.patch), settings → tele → scripts, off)
- script logs support selection across entries and precise timestamps; installed scripts share one settings group ([0328](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0328-feat-group-installed-scripts-together.patch), [0329](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0329-fix-make-script-logs-selectable.patch), settings → tele → scripts, with scripting)

## fixes

### sending

- mixed attached files and media keep their order and one caption; cancelling scheduling or payment keeps the tray ([0333](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0333-docked-complete-media-composer.patch), docked media tray, with docked media)

### scripts

- network requests and message decorators no longer block script timers or message rendering ([0327](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0327-fix-run-fetch-and-message-decorators-asynchronously.patch), settings → tele → scripts, with scripting)
- local script translations stay out of the message editor; editing the message or stopping its script clears stale decorations ([0324](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0324-fix-refresh-script-translations-and-show-text-dialog.patch), [0326](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0326-fix-keep-script-decorations-out-of-message-edits.patch), message menu, message editor, with scripting)
- scripting stays enabled after a restart, profile changes refresh on screen and optional request fields reach Telegram ([0318](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0318-fix-keep-scripting-on-after-a-restart.patch), [0322](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0322-fix-refresh-the-profile-a-script-wrote.patch), [0323](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0323-fix-send-optional-script-request-fields.patch), settings → tele → scripts, with scripting)
- scripts cannot read another account's notifications or answer another script's pending interceptor requests ([0325](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0325-fix-isolate-scripts-and-enforce-runtime-permissions.patch), [0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), settings → tele → scripts, always on)
- importing, replacing or changing a script revokes its old permissions; the first update to this build resets script permissions and script storage ([0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), settings → tele → scripts, always on)

### privacy

- streamer mode blocks capture of disappearing media even when screenshots are otherwise allowed ([0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), settings → tele → privacy → streamer mode, with streamer mode)
- peeking at last seen restores every privacy exception, and local-password recovery checks the account that owns the lock ([0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), settings → tele → privacy, always on)
- a legacy local password must be entered once before recovery can be attached to its owner ([0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), settings → tele → privacy → local password, with a local password)
- hidden-word patterns, server images and update filenames are bounded to protect responsiveness, memory and local files ([0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), privacy, notifications, updates, always on)

### your data

- signing out clears the account's locally kept deleted messages, saved drafts and script state so another login cannot inherit them ([0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), account logout, always on)

### interface

- the Other changes section keeps its notes inside one card, and long translated script-import notices wrap in full ([0330](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0330-fix-keep-other-changes-inside-their-settings-group.patch), [0332](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0332-security-harden-fork-boundaries.patch), settings → tele → what's new, scripts, always on)

### debug

- freeze reports count only foreground stalls while the phone is awake; background time and sleep no longer trigger them ([0331](https://github.com/gettele/android/blob/v13.2.1-tele.11/patches/android/0331-fix-limit-freeze-reports-to-foreground-stalls.patch), settings → tele → debug → report freezes, off)

## download

[tele-v13.2.1-tele.11.apk](https://github.com/gettele/android/releases/download/v13.2.1-tele.11/tele-v13.2.1-tele.11.apk): install it over your tele. a running tele finds this release within 3 hours, or right away with settings → tele → check for updates.
