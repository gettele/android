# architecture

how tele (android) is put together: the patch queue, where fork code lives, the config and settings systems, and how batches and builds gate the work. for day-to-day recipes see [development.md](development.md); the rules are in [AGENTS.md](../AGENTS.md).

## the patch queue

tele is not a git fork of telegram android. this repository holds the queue; the code lives in a telegram checkout next to it.

why a queue and not a fork:

- every change is a separate, reviewable commit with a one-line subject. the queue is the changelog.
- moving to a new upstream release means replaying the queue; a conflict points at exactly one patch.
- the diff against stock stays visible and small. nothing drifts silently.

rules that follow from this:

- one feature per patch. fixes to an unreleased patch are folded into its commit.
- fork code lives in new files. stock files only get small, gated hunks.

the model is inherited from [nitreojs/tele](https://github.com/nitreojs/tele) (patch queue over telegram desktop — the source of the features being ported) and [teidesu/inugram](https://github.com/teidesu/inugram) (patch queue over telegram android — the model for android-side layout). both are credited here; all fork code is original.

## repository layout

```
tele_android/
  main/                  this repository (branch: lord, local-only)
    README.md            what tele is, how to install it, network and privacy notes
    features.md          every user-facing patch, by settings page (english)
    AGENTS.md            rules for coding agents
    UPSTREAM             the base version and commit of DrKLO/Telegram
    patches/android/     exported queue, one file per commit (appears as work lands)
    .github/workflows/   build.yml (build and publish the apk), sync.yml (watch for new upstream releases)
    ci/                  release helpers and the next release's changelog (see releasing.md)
    docs/
      PATCHLIST.md       the plan: batches, patches, statuses (planning file for agents)
      architecture.md    this file
      development.md     setup, building, the edit→test→export loop
      releasing.md       versions, building and publishing releases, secrets, signing
      portability.md     snapshot of the 127-patch portability analysis
  Telegram/              DrKLO/Telegram checkout, branch `tele` — the code tree
```

`UPSTREAM` holds the exact base commit (for 13.0.2 (7175): `commit`). every patch is a commit on top of it; `git log <UPSTREAM>..tele` in the checkout is the applied queue.

never bump `UPSTREAM` in a feature change: syncing to a new release is its own change, after which every patch is rebased and re-exported.

## fork code in the telegram tree

everything below lives inside the telegram checkout, under `TMessagesProj/src/main/`.

### where code lives

- `java/tele/` — all fork code, root package `tele`:
  - `TeleConfig.kt` — every toggle and option, loaded once at startup;
  - `TeleHooks.kt` — the central lifecycle bus: one static entry point per stock call site (`init`, `onResume`, `onNewMessage`, `onDeepLink`, `onMessagesControllerCreated`, …). stock patches call `TeleHooks`; everything else is dispatched from it;
  - `helpers/` — feature coordinators (`ChatHelper`, `ProfileHelper`, …), one per feature area;
  - `ui/settings/` — the fork settings pages;
  - `db/TeleDatabaseHelper.kt` — fork storage.
- `res/values/strings_tele.xml` — fork strings, keys prefixed `Tele` (`TeleHideStories`), accessed via `LocaleController.getString(R.string.TeleXxx)`.
- stock files get gated calls into `TeleHooks`/helpers — nothing else.

kotlin is the fork language; stock is java. the infra patch enables kotlin for the project (stock only ships the stdlib dependency). tiny stock-class fixes stay inline in java.

### TeleConfig pattern

```kotlin
object TeleConfig {
    @JvmField val HIDE_STORIES = BoolItem("hide_stories", false)
    @JvmField val MAX_ACCOUNTS  = IntItem("max_accounts", 8)
}
```

- pref key = snake_case of the name, storage in the fork's own `SharedPreferences` (`tele`), loaded once from `TeleHooks.init`.
- types: `BoolItem`, `IntItem`, `FloatItem`, `StringItem`; subclass for enums.
- from java: `TeleConfig.HIDE_STORIES.getValue()` — never `.value`.
- default off must equal stock behaviour. every call site is gated: with the toggle off, no fork code may run and nothing may change on screen or on the network.

### settings section

settings → tele: own pages in `tele/ui/settings/` (appearance / chats / messages / privacy / profiles / bots / debug), each a fragment in the style of stock settings lists, split into groups, registered in the fork search and reachable via `tg://settings/tele/<slug>` deeplinks. a row that only matters while another toggle is on stays hidden until the parent is on.

fork state export/import (json) mirrors tele's settings backup: the spec table in the settings io helper decides what is exported; unknown settings are skipped with a log line.

### database

- stock schema and `LAST_DB_VERSION` are off-limits.
- fork versioning lives in `tele_kv`; fork tables are `tele_*`, created and migrated in `TeleDatabaseHelper`.
- fork fields are populated by hooking stock load/save calls.

### update feed and the tele server

- the in-app updater (tele 0006) reads the github releases of [gettele/android](https://github.com/gettele/android); off for local/dev builds (`TELE_BUILD` unset), toggleable. every release tag is `v<APP_VERSION_NAME>-tele.<TELE_BUILD>` and carries:
  - `tele-update-android.json` — `{"tag", "base", "counter", "url", "apk_sha256"}`: `base` is `APP_VERSION_CODE` (the installed version code without the abi digit), `counter` is `TELE_BUILD`, `url` points into `releases/download/<tag>/` and ends with `.apk`. the client fetches it from `releases/latest/download/`, updates when `(base, counter)` is newer than the running build, checks the sha256 and hands the apk to the system installer; android itself rejects an apk signed with another key.
  - `tele-changelog.json` — `{"tag", "title", "url", "categories": [...], "items": [{"text", "where", "category"}]}`, the same format as tele desktop. after an update every account gets it once in the local tele chat (0075); a missing file is explained instead (0111).
- the tele server client (patches 0009/0093/…) downloads a public, hashed list over https and matches locally; it never uploads account data. the protocol is defined by tele desktop's readme and is platform-neutral.
- how a release is built, signed and published (and what the secrets are) is in [releasing.md](releasing.md).
- crash reports (0037) leave the device only after the user taps send, and the text is shown first.

## batches and build gates

work is delivered in batches — see [PATCHLIST.md](PATCHLIST.md) (`docs/PATCHLIST.md`) for the current plan. rules:

- a batch is an ordered set of patches that can be built and tested together; infra first, dependent patches after their dependencies.
- when every patch of a batch is committed (telegram tree) and exported (here), a debug apk is assembled and handed over for manual testing on a device or emulator.
- a batch is done only after a human verified it. `docs/PATCHLIST.md` statuses: `todo` → `wip` → `built` (batch gate passed) → `done` (manually verified).

## patch files

- patches live in `patches/android/NNNN-<subject>.patch`, numbered in queue order, exported with `git format-patch <UPSTREAM> -o patches/android/ --zero-commit --no-signature --no-numbered` (`--no-numbered` keeps patch subjects stable across exports).
- a commit inserted in the middle renumbers every later patch — new features go at the end.
- never edit a `.patch` by hand; change the commit and export again.
- `.gitattributes` pins `*.patch` as binary (`-text`) so git never rewrites line endings inside patches.

## syncing with a new upstream release

1. fetch the new release commit in the telegram checkout.
2. rebase the `tele` branch onto it; a conflict points at exactly one patch — fix it in that patch's commit.
3. rebuild, exercise the patches whose conflicts were resolved.
4. re-export the queue, update `UPSTREAM`, commit `chore: rebase patches onto <version>` here.

## credits

- [nitreojs/tele](https://github.com/nitreojs/tele) — the desktop fork whose features this project ports; its docs are the model for ours.
- [teidesu/inugram](https://github.com/teidesu/inugram) — android patchset whose layout and conventions informed ours (config pattern, hooks bus, db rules).
- through inugram, prior art also originates from [Nekogram](https://github.com/Nekogram/Nekogram) and [NagramX](https://github.com/risin42/NagramX); credit them again in the readme wherever their approach is followed.
