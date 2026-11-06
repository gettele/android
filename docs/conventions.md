# conventions

how fork code, commits and patches should look. the goal is a queue that reads well, reviews quickly and survives every upstream release with as few conflicts as possible.

the hard rules are in [../AGENTS.md](../AGENTS.md). this file is the short reference for the choices those rules leave open. existing code is brought in line as it is touched; don't mass-rewrite unrelated files just to satisfy this page.

## code

### where code goes

- new code goes into `TMessagesProj/src/main/java/tele/`, package `tele`, in kotlin. the exceptions are small fixes that belong inside a stock java class.
- the layout is:

  - `TeleConfig.kt` — every setting;
  - `TeleHooks.kt` — the lifecycle bus for stock call sites;
  - `helpers/` — feature coordinators, one area per file;
  - `ui/` — fork screens, views and dialogs;
  - `ui/settings/` — settings pages, search entries and deeplink handlers;
  - `db/TeleDatabaseHelper.kt` — fork storage.

- name screens and views `Tele<Feature>` (`TeleDockedStrip`, `TeleGiftStudioActivity`), helpers after the feature (`DockedMedia`, `GiftGrid`), and settings pages after the page (`TeleSettingsActivity`, `TeleSearch`).
- stock files only get hunks that hook into the fork: an import, a gated call, an early return, a changed argument. a typical hunk:

  ```java
  if (tele.TeleConfig.TELE_FEATURE.getValue()) {
      tele.TeleHooks.onFeature(...);
  }
  ```

- prefer a hook over a copy. call the stock function and adjust its input or result from `tele`, or use an existing extension point. a copy silently misses every upstream fix.
- expose, don't duplicate. a stock field or method needed from fork code becomes `public`; new members and methods added to stock classes are prefixed `tele_` (`tele_setTopViewHeight`, `tele_setDockedMedia`).
- never edit `TLRPC.java` (generated) and never touch the stock database schema or `LAST_DB_VERSION`. fork state lives in `tele_*` tables and `tele_kv` through `TeleDatabaseHelper`.
- a bug in a stock class is fixed in that class, not in a helper.
- a submodule change is its own change. never commit a moved submodule pointer in a feature patch.

### style

follow the style around the code:

- kotlin, four spaces, no semicolons, explicit imports and no wildcard imports.
- types and functions in `PascalCase`, locals in `camelCase`, constants in `SCREAMING_SNAKE_CASE`.
- `@JvmField` on every `TeleConfig` item and any other field read from stock java; `@JvmStatic` on object functions called from stock java; `@JvmOverloads` when java needs constructor defaults.
- `runCatching` and `FileLog` for failures that must not crash a screen; network work off the main thread, view work back on it with `AndroidUtilities.runOnUIThread`.
- state that belongs to an account is keyed by `currentAccount`; never cache account 0 in a singleton.
- recycler cells re-apply fork state in bind, not only on creation.
- respect `LiteMode` and the performance class before adding animations.
- **no code comments.** names and small functions carry the meaning; the only exception is a short note on a real trap the code cannot express.

### options

every tele setting is a `TeleConfig` item. adding a switch touches:

1. `TeleConfig.kt`: declare the item and give it a snake_case key.

   ```kotlin
   @JvmField
   val HIDE_DOCKED_TILES = BoolItem("hide_docked_tiles", false)
   ```

   types are `BoolItem`, `IntItem`, `FloatItem`, `StringItem`; enums and multi-choice values use `StringItem` and are parsed at the call site.

2. `ui/settings/TeleSettingsActivity.kt`: add a row to the page and the group it belongs to. never append a loose row at the end of a page.

   ```kotlin
   toggle("Hide docked tiles", TeleConfig.HIDE_DOCKED_TILES)
   ```

   a child row goes into `GROUPS` under its parent and stays hidden until the parent is on. descriptions and search keywords follow the rules below.

3. `ui/settings/TeleSearch.kt`: add the search entry when the name and the description do not already cover what people would search for. new GUIDs go at the end; never reuse one.

4. `TeleBackup.kt`: no per-setting entry is needed — every `TeleConfig` item is exported automatically. add internal keys (passwords, server url, internal counters) to `SKIPPED` instead.

- toggles default to off unless the desktop patch or the maintainer says otherwise. off must mean exactly stock behavior: no fork code runs, nothing changes on screen and nothing changes on the network.
- changing a setting calls `TeleHooks.onConfigChanged(item)` when the ui has to react immediately.
- from java use `TeleConfig.ITEM.getValue()`, never the kotlin property.

### ui strings

- fork strings are hardcoded english in sentence case. call the app `tele` and the service `telegram`; `tele` stays lowercase everywhere.
- strings that stock code resolves through `LocaleController` go into `res/values/strings_tele.xml`, keyed `Tele<PascalCase>` (`TeleHideStories`). never edit the stock `strings.xml`.
- literal texts shown by fork menus, dialogs, bulletins and toasts go through `TeleLowercase.lc(...)`, so the lowercase-interface switch covers them. don't lower dynamic data, names or message text.
- descriptions only when the name cannot fully explain the row. one short sentence with the missing fact (a side effect, a condition, what leaves the device). no filler and no restating the name.
- stock strings are off-limits. language formats differ; keep arguments positional when the text is translated.

## commits

- one line, conventional prefix, lowercase, imperative, no trailing period: `feat: send photos in hd by default`, `fix: ignore reply counters on scheduled messages`.
- in the telegram tree use `feat:`, `fix:`, `debloat:` and `misc:`. in this repository use `docs:`, `chore:`, `feat:` and `fix:`.
- no body, no trailers, no co-author lines, no tool or ai attribution.
- the subject becomes the patch subject and its file name. describe what the user gets, and don't rename a released patch without a reason: a new subject shows up as one dropped and one new patch in the release notes.
- a fix or follow-up to an unreleased patch goes into that patch's commit (`git commit --fixup`, `git rebase -i --autosquash`). keep it separate only when it cannot be squashed without conflicts or touches several patches at once.

## patch hygiene

- one feature per patch. small hunks survive upstream syncs; every extra context line is a chance to conflict.
- don't reformat, reorder or rename stock code, and don't fix stock whitespace in passing.
- keep the line endings of the file you edit; a file must never mix crlf and lf. `.gitattributes` pins `*.patch` as binary.
- never edit a `.patch` by hand. change the commit in the telegram tree and export:

  ```bash
  cd ../Telegram
  git format-patch <UPSTREAM> -o ../main/patches/android/ --zero-commit --no-signature --no-numbered
  ```

- new features go at the end of the queue. a commit inserted in the middle renumbers every later patch and breaks their links.
- never bump `UPSTREAM` in a feature change. moving to a new upstream release is its own change (`chore: rebase patches onto <version>`).
- every user-facing patch updates [features.md](../features.md) in the same commit as the patch export; [PATCHLIST.md](PATCHLIST.md) keeps the batch plan and statuses true.

## privacy rules for features

tele is a client for people who care what leaves their device.

- no new third-party network request without a setting that controls it, default off. the setting is checked at the lowest level of the request, before the connection is created.
- the existing network entry points follow the same rule: `CALCMULA` for calcmula, `PURCHASE_PRICE` for the ton price, `GIFT_STUDIO` for the gift catalog, `AUTO_UPDATE` for github updates, `SHOW_CHANGELOG` for the changelog, `SEND_CRASH_REPORTS` for crash reports, `TELE_SERVER_URL` for the tele server.
- never send account data to the tele server: no ids, usernames, contacts or messages. the client downloads public data and does the matching locally. the only exception is a crash report, which leaves only after the user taps send, shows its text first and lets the user untick their username.
- the tele server protocol is public in the desktop [server documentation](https://github.com/nitreojs/tele/blob/main/docs/server.md). a change to it is a documented, backwards compatible change there, not a hidden one in the code.
