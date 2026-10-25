# tele for android

a telegram android fork: a queue of patches applied on top of a [telegram for android](https://github.com/DrKLO/Telegram) release. it ports the features of [tele](https://github.com/nitreojs/tele), the telegram desktop fork.

## download

grab the latest build from [releases](https://github.com/gettele/android/releases/latest). it's one universal apk, `tele-<tag>.apk`, for all cpu types.

- android 6.0 or newer.
- open the apk and let your browser or file manager install apps when android asks.
- tele is installed as `org.telegram.messenger.tele`, next to the official telegram. builds from source are `org.telegram.messenger.tele.dev`, so they don't clash with a release.
- release builds get fcm push notifications on phones with google play services. without them, notifications come over tele's own background connection while android keeps the app running; turn on settings → notifications and sounds → keep-alive service and let tele run unrestricted in the battery settings to keep it running.

tele updates itself: it checks these releases 15 seconds after start and every 3 hours, downloads new builds in the background and offers to install them with the system installer. the feed carries a sha256 that is checked before installing, and android itself refuses an apk signed with another key. turn it off in settings → tele → update automatically. builds from source that have no tele build number never update.

every apk of a published release has a [build provenance attestation](https://github.com/gettele/android/attestations). check a download with the [github cli](https://cli.github.com):

```
gh attestation verify tele-<tag>.apk --repo gettele/android
```

## highlights

everything tele adds lives in settings → tele, grouped into pages.

- [ghost mode](features.md#privacy): no read receipts, typing, online status or story views, each switchable.
- [kept deleted messages](features.md#your-data): messages deleted by others stay in the chat, marked, even after a restart. with the edit history of messages next to them.
- [username aliases](features.md#your-data): your own @alias for any chat, and local names for people, only for you.
- [docked media](features.md#sending): attach media above the field, with a caption, and keep it per chat.
- [shots](features.md#interface): save messages as a picture, 1x to 4x, with or without the chat background.
- [link cleaner and rewrites](features.md#links): tracking parameters removed from links you open and send, pasted links rewritten by your own rules, and control over link previews.
- [calcmula](features.md#sending): messages starting with `= ` are computed and sent with the answer.
- [message menu editor](features.md#interface): hide and reorder the items of the message menu.
- [ids](features.md#ids): peer ids and data centers in profiles, message, gift and emoji ids.
- [tele server badges](features.md#server): checkmarks and custom verification from the tele server.
- [self-updater](features.md#updates): updates from these releases, and what's new in a local tele chat.

## more

- [all features](features.md), grouped by settings page.
- [docs/PATCHLIST.md](docs/PATCHLIST.md): the plan, patch by patch, what's done and what isn't.
- [docs/portability.md](docs/portability.md): which desktop features make sense on android and which don't.
- [docs/releasing.md](docs/releasing.md): how releases are built, signed and published.

## network and privacy

tele only talks to a few places besides telegram itself, and only with the switches that cover them:

- the **tele server** (settings → tele → server, `https://tele.starkow.dev` by default): tele downloads one public, hashed list with checkmarks, custom verification and extra usernames, and matches it on your device. it never sends the server your account, ids, usernames, contacts or messages. clear the url to turn it off. the same server takes crash reports, but only after a crash and your tap on send. how it works and how to run your own: the [desktop docs](https://github.com/nitreojs/tele/blob/main/docs/server.md).
- **github releases** of [gettele/android](https://github.com/gettele/android/releases): the update check, on by default, turned off with update automatically.
- **calcmula.app**: only when you turn on a calcmula switch in sending.
- **gram.rin.ms**: only when you turn on collectible prices at the purchase date.
- **schema.jppgr.am**: only when you use view as TL, and it opens in your browser.

everything else tele adds works on your device. every switch is off by default unless [features.md](features.md) says on, and a switch that is off behaves exactly like stock telegram.

## build from source

tele is built from this repository's patch queue and a telegram android checkout. [docs/development.md](docs/development.md) has the sdk, your own api credentials (telegram's stock pair doesn't work for forks), the build and how to make a change.

## how it works

tele isn't a git fork of telegram. `patches/android/` holds the queue, one patch per commit, and `UPSTREAM` names the telegram android release it applies on. fork code lives in new files in a `tele` package, and stock files only get small gated hunks, so moving to a new telegram release means replaying the queue and fixing the one patch that conflicts. [docs/architecture.md](docs/architecture.md) has the details.

## contributing

changes to tele go through the patch queue. read these first:

- [docs/architecture.md](docs/architecture.md): the patch queue, where the fork code lives and how batches and builds gate the work.
- [docs/development.md](docs/development.md): building, running a dev build and making a change.
- [AGENTS.md](AGENTS.md): the rules for coding agents, which are the rules for patches too: fork code in new files, minimal stock hunks, off means stock.

## credits

- [Telegram for Android](https://github.com/DrKLO/Telegram) by DrKLO, which every tele build is made from.
- [tele](https://github.com/nitreojs/tele) by nitreojs, the desktop fork whose features this ports. its docs are the model for ours.
- [inugram](https://github.com/teidesu/inugram) by teidesu, a patch queue over telegram android. its layout and conventions informed ours: the config, the hooks bus and the database rules. through it, prior art also comes from [Nekogram](https://github.com/Nekogram/Nekogram) and [NagramX](https://github.com/risin42/NagramX).

all fork code here is written from scratch.

## license

telegram for android is free software under the [GNU GPL version 2](https://github.com/DrKLO/Telegram/blob/master/LICENSE). tele builds include its code and are distributed under the same license.
