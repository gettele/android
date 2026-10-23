# AGENTS.md

instructions for ai coding agents working on tele (android). humans: start with [docs/architecture.md](docs/architecture.md) and [docs/PATCHLIST.md](docs/PATCHLIST.md).

tele is telegram android kept as a patch queue: this repository holds `UPSTREAM` (the base version of [DrKLO/Telegram](https://github.com/DrKLO/Telegram)), `patches/android/*.patch` and the docs. the code you edit lives in a separate telegram checkout (`../Telegram` by default) on a branch called `tele`, where the queue is applied as one commit per patch on top of the `UPSTREAM` commit. you change that tree with commits, then export them back into patches here.

the architecture is modelled on [nitreojs/tele](https://github.com/nitreojs/tele) (the desktop patch queue this project ports) and [teidesu/inugram](https://github.com/teidesu/inugram) (an android patchset). both are references, not sources to copy from: fork code is written here, from scratch, with `tele` naming — and both get credited in the readme.

## hard rules

1. **fork code goes into new files.** package `tele` under `TMessagesProj/src/main/java/tele/` (kotlin): `TeleConfig.kt` (toggles), `TeleHooks.kt` (lifecycle bus), `helpers/`, `ui/settings/`, `db/`. fork strings go into `TMessagesProj/src/main/res/values/strings_tele.xml`, keys prefixed `Tele` (like `TeleHideStories`).
2. **minimal stock hunks.** in stock files only add a gated call into `Tele`: an early return before the stock block or a fork call after it. no re-indentation of stock code, no renames, no removing stock imports (except to replace with a `tele` import). prefer early returns and add-after-stock so rebases stay trivial.
3. **never edit `TLRPC.java`.** it is generated; read it as much as you like, edit never. new tl fields that a feature needs are read from the parsed objects; if something is genuinely missing, surface it to the maintainer instead of patching the generator output.
4. **never touch the stock db schema or `LAST_DB_VERSION`.** fork state lives in `tele_*` tables / `tele_kv` via `TeleDatabaseHelper`. populate fork fields by hooking the stock load/save calls, not by editing stock sql.
5. **every setting is a `TeleConfig` item.** a new setting touches: `TeleConfig.kt` (an item, default off), a settings page row in `tele/ui/settings/` (inside a group, with search keywords where the name doesn't cover what people search for), and the export/import spec table. toggles default to **off**, and off must behave exactly like stock — verify every call site is gated.
6. **check if stock already does it** before implementing a toggle (per-chat wallpapers, lite mode, notification settings often have it). tell the maintainer instead of re-implementing.
7. **expose, don't duplicate.** a `private` field/method needed from fork code becomes `public` — that is the whole hunk. new members/methods/overloads added to stock classes are prefixed `tele_` (java fields too). look for an existing extension point before adding anything to a base class.
8. **prefer data-layer hooks over ui-layer.** one hook in `MessagesController` / `SendMessagesHelper` beats fifteen hooks in views and cells.
9. **a bug in a stock class is fixed in that class.** `EditTextBoldCursor` bugs get fixed in `EditTextBoldCursor.java`, not in a helper.
10. **no code comments.** names and small functions carry the meaning; the one exception is a short note on a real trap the code can't express.
11. **hot files.** `ChatActivity.java` (46k lines), `ChatMessageCell.java` (29k), `PhotoViewer.java` (24k), `MessagesController.java` (24k), `ProfileActivity.java` (17k), `ChatActivityEnterView.java` (15k): `rg` for the exact symbol, then read a small window with offset. never read them top-to-bottom.
12. **network and privacy.** no third-party network request without a setting that controls it, default off. never send account data to the tele server (ids, usernames, contacts, messages) — the client downloads public data and matches locally. every request the fork adds checks the fork's own offline switches at the lowest level.
13. **line endings.** keep the endings of the file you edit; a file must never mix crlf and lf.
14. **commits** are one line: `feat: …` / `fix: …` / `debloat: …` / `misc: …` in the telegram tree; `docs:` / `chore:` / `feat:` also here. lowercase, imperative, what the user gets. no body, no trailers, no co-author lines, no tool or ai attribution. the subject becomes the patch file name.
15. **never edit `.patch` files by hand.** change the commits in the telegram tree and export (see [docs/development.md](docs/development.md)).
16. **never bump `UPSTREAM` in a feature change.** moving to a new upstream release is its own change (`chore: rebase patches onto <version>`).
17. **don't run `git push` or network git commands** in this repository unless asked. the remote is github.com/gettele/android (`main` there = local `lord`); pushing to `main` starts a ci build (see [docs/releasing.md](docs/releasing.md)).
18. **every user-facing patch also updates [features.md](features.md).** one row per feature, in english, in the section of the settings page that holds its switch: what it does in one plain sentence, where to find it, the default, the patch file in `patches/android/` and the desktop patch it comes from (by its number in the current desktop queue). it goes into the same commit as the patch export, never later.
19. **[docs/PATCHLIST.md](docs/PATCHLIST.md) is the planning file for agents.** the batch plan, statuses and per-patch notes live there (in russian, by the current desktop numbering — see [docs/desktop-numbers.md](docs/desktop-numbers.md) for old numbers); the maintainer's decisions are in [docs/decisions.md](docs/decisions.md) and the step-by-step guide for every planned batch is in [docs/batches/](docs/batches/). read them before picking up work and keep statuses true. [features.md](features.md) is what users read, so don't put plans or implementation notes in it.

## workflow

1. **prepare the tree.** in the telegram checkout: `git checkout -b tele <UPSTREAM commit>` (see the `UPSTREAM` file). one branch, the queue as commits.
2. **edit and commit there.** one feature = one commit at the end of the queue (`feat: …`). a fix or follow-up to an existing patch goes into that patch's commit, released or not (`git commit --fixup <commit>`, `git rebase -i --autosquash <UPSTREAM commit>`); it stays a separate commit only when it can't be squashed without conflicts or touches several patches at once.
3. **build.** `./gradlew :TMessagesProj_App:assembleDebug` in the telegram checkout (see [docs/development.md](docs/development.md) for sdk setup). the first build compiles natives and is slow.
4. **run and test.** install on a device or emulator and exercise the feature by hand with the option on and off. if you can't run the app, say so plainly and hand over exact steps to test; never claim a feature works because it compiles.
   - driving the emulator/device ui (taps, gestures, typing) is the maintainer's job. hand over a numbered step list and wait; the assistant does code, builds, installs, logcat and screenshots.
   - when a ui detail or behavior is unclear, ask the maintainer directly instead of inferring; two minutes of questions beats half an hour of reasoning.
5. **export** into this repository: `git format-patch <UPSTREAM commit> -o patches/android/ --zero-commit --no-signature` (from `../Telegram`, see [docs/development.md](docs/development.md)), then update `docs/PATCHLIST.md` statuses and, for a user-facing patch, add its row to `features.md`.
6. **batch gate.** patches are delivered in batches (see `docs/PATCHLIST.md`). when every patch of a batch is committed and exported, assemble a debug apk and hand it over for manual testing. a batch is done only after that build is verified by a human.
7. **commit here.** `git add patches docs/PATCHLIST.md features.md && git commit -m "feat: <what it does>"` (one commit per patch; docs and infra changes use their prefixes).

## known pitfalls

- **everything ui must run on the main thread.** data arrives on background threads (`ConnectionsManager` callbacks, `MessagesStorage`); hop with `AndroidUtilities.runOnUIThread` or the fragment's `runOnUIThread` before touching views.
- **per-account state is keyed by `currentAccount`.** `MessagesController.getInstance(currentAccount)`, `UserConfig.getInstance(currentAccount)` — a singleton cached for account 0 breaks multi-account (the fork raises the account limit on purpose).
- **recycler views recycle holders.** a menu item or cell tweak must re-apply its state in bind, not only on creation.
- **`LiteMode` and performance class gate animations.** respect them; a fork animation that ignores power saving is a bug.
- **notification channels are immutable after creation.** a fork notification needs its own channel id, never a reused stock one.
- **`FLAG_SECURE` is per-window.** "never block screenshots" style toggles must cover every window that sets it (photo viewer, secret chats, stories), not one.
- **stock strings are off-limits.** never edit `strings.xml`; fork strings go to `strings_tele.xml`. formats differ between languages — keep arguments in order or use positional ones.
- **`TLRPC` fields are `public` and nullable.** tl responses are hand-parsed: check for null before dereferencing anything that came from the network.
- **gradle splits by abi.** the debug task builds all splits; pick the apk for the device (`arm64` on everything modern) when installing by hand.
- **the first build compiles natives** (cmake + ndk 27.2): tens of minutes. incremental java builds after that are fast; a `git clean` in `TMessagesProj` resets that.

## definition of done

- it builds, and the dev build runs.
- the feature was exercised by hand, with the option on and off.
- off by default, and off is exactly stock's behaviour.
- the option is in `TeleConfig`, on a settings page in a group, has search keywords where useful, and is in the export/import spec.
- network use respects the offline switches.
- exported into `patches/android/`, `docs/PATCHLIST.md` updated, and `features.md` updated for a user-facing patch, committed per the rules.
- a batch, when complete: debug apk assembled and handed over for manual testing.
