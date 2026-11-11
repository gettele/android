# releasing

for maintainers. releases are built and published by github actions and need the repository's secrets, so contributors never release anything themselves. this page explains how it works, so everyone knows what a release is made of and how to check one. the model is [tele desktop's](https://github.com/nitreojs/tele/blob/main/docs/releasing.md), cut down to one platform.

## versions

- a release is tagged `v<APP_VERSION_NAME>-tele.<N>`, for example `v13.0.3-tele.1`, and titled `tele N · <APP_VERSION_NAME>`. `APP_VERSION_NAME` and `APP_VERSION_CODE` come from `gradle.properties` of the patched telegram tree, so they follow `UPSTREAM`.
- `N` is one above the highest existing `v*-tele.*` release or tag, whatever upstream it was built on: numbers go on across upstream bumps, because the app compares build numbers. build.yml picks it, or takes the `number` input when it's above every existing one.
- `N` is compiled in as `TELE_BUILD` (`local.properties` of the build, read by `TMessagesProj/build.gradle`). the app shows it as the build number and builds without it (`TELE_BUILD` unset, so local and dev builds) never update themselves.
- the self-updater orders builds by `APP_VERSION_CODE` first and `N` second, so a release on a newer upstream always wins.
- every published release is listed in [releases](releases.md), with its base and patch count; the page keeps the same history that `ci/changelog.json` and the published `tele-changelog.json` assets hold.

## before a release

1. **patches.** the queue is exported and committed on `main`, and applies to a fresh clone of `UPSTREAM` (see [development](development.md#checking-the-queue-applies)). every patch of the batch was tested on a device, a ci run takes about an hour and a broken release reaches every user through the updater.
2. **changelog.** replace `ci/changelog.json` with the changes since the latest **published** release, not since the last editing session. Read that release's `tele-changelog.json`, compare its tag/commit with the current patch queue, and remove everything already shipped. Do not publish or edit an existing GitHub release unless explicitly asked.

   ```json
   {
     "categories": ["sending", "scripts", "privacy"],
     "items": [
       {
         "text": "preview attached photos and videos as an album or a strip",
         "where": "settings → tele → sending → attach media above the field",
         "category": "sending",
         "kind": "new",
         "default": "off",
         "options": ["tele-docked-media", "tele-docked-grid"],
         "patches": ["0333-docked-complete-media-composer.patch"],
         "android_ids": ["A014"]
       }
     ]
   }
   ```

   The release body follows [tele desktop 23](https://github.com/nitreojs/tele/releases/tag/v7.3.3-tele.23): a linked Telegram base and queue count, optional upstream changes, `## new`, `## fixes`, then `## download`. Keep settings-area categories one level lower as `### sending`, `### scripts`, `### privacy`; do not use `fixes` as a category for new notes. Empty sections/categories are omitted. The channel announcement uses the same grouping; the app continues to receive ordinary `categories`/`items` and ignores release-only metadata.

   Each item describes a user-visible change in plain lowercase English, without a trailing period. Give enough detail to understand its effect; do not enumerate implementation details or every edge case. `kind` is `new` or `fix`, independently of the patch subject; extending an existing feature is new, repairing existing behavior is a fix. Link the actual Android patch filenames through `patches`; use `default` for the option's initial state (`off`, `on`, `with scripting`) or `always on` for an unconditional fix. `where` is the real UI path and may be empty. `options` are real `tele-…` setting IDs for live toggles in the app. Never invent a setting path, patch number, upstream feature or verification result.

   `android_ids` names the stable Android identities from [android-patches.md](android-patches.md), backed by `ci/android-patches.json`. It supplements, rather than replaces, `patches`: use only IDs relevant to that release item and the exact queue files changed in this release. A new docked follow-up stays `A014` even if its queue position changes; do not list every historical file of the identity as new. GitHub notes and channel posts link A-IDs to stable registry anchors and queue numbers to the exact patch artifacts at the build revision. The app ignores the extra identity metadata. Unknown, removed or unrelated IDs fail validation.

   **Telegram changes:** compare the base in the new tag with the latest published tag, not with an older local summary. If it changed, add an `upstream` object with `version`, `previous`, `url` (official Android release/source notes) and `changes` (a list of verified client changes across the complete version range). The generator renders `## telegram android <version>` with “new since <previous>”. Distinguish stock additions from tele patches, and exclude desktop/iOS-only features or server rollouts not supported by this Android base. Cite the official source in `url`; use source/release diffs when no official user-facing notes exist. If the base is unchanged, omit `upstream` entirely—do not repeat previous Telegram news. With `--previous`, validation rejects missing upstream notes for a base change or stale upstream notes for an unchanged base.

   Before delivery, generate both the JSON and Markdown against the previous published asset, inspect the rendered notes and run the announcement with `--dry-run`. Example for the upcoming tele 11:

   ```bash
   python3 ci/changelog.py ci/changelog.json --tag v13.2.1-tele.11 --repo gettele/android --previous /path/to/tele10-changelog.json --json /tmp/tele11-changelog.json --notes /tmp/tele11-notes.md
   python3 ci/announce.py /tmp/tele11-changelog.json --repo gettele/android --dry-run
   ```

   tele 10 already uses Telegram 13.2.1, so tele 11 on the same base has **no upstream-news section**. Generate unpublished previews outside the tracked repository; never add them to published history before the release exists. Generated notes do not imply manual release gates have passed.

   `categories` controls group order; every item's category must be listed. The app limits remain 100 items, 16 categories, 64 characters per category and 1024 per item text. `python3 ci/changelog.py ci/changelog.json --tag v13.2.1-tele.11 --repo gettele/android` validates without writing or publishing. Publishing refuses unchanged previous items. The optional `header` and `footer` remain single lines up to 64 characters, before/after the notes and channel post; the app ignores them.

## building and publishing

build.yml runs in two ways:

- **a push to `main`** that touches `UPSTREAM`, `patches/`, `ci/` or the workflow builds and checks everything, and keeps the apk as an artifact for 7 days. it never publishes.
- **a manual run** (`gh workflow run build.yml --ref main -f publish=true`, optionally `-f number=<N>`) builds the same and publishes the release. it's refused on any branch but `main`. `publish=false` is the same build without the release.

the run:

1. fetches [DrKLO/Telegram](https://github.com/DrKLO/Telegram) at the `UPSTREAM` commit and the submodules, and applies `patches/android/*.patch` with `git am` as `github-actions[bot]`.
2. picks `N`, builds the tag, and checks `ci/changelog.json` before the long part starts. it then runs `ci/changelog_history.py`, which merges the `tele-changelog.json` of every published release with this one into `res/raw/changelog_history.json` of the build, so the app lists every version offline, and after the build checks that the apk carries it.
3. installs the sdk packages pinned in `TMessagesProj/build.gradle` (platform, build tools, ndk, cmake) and builds `:TMessagesProj_App:assembleAfatRelease`: the universal apk (`afat` flavor, all four abis, `minApi` 23), release build type, minified and signed.
4. checks that the apk verifies and is signed by the certificate pinned in `ci/release-cert-sha256.txt`: a build signed by any other key fails here, before anything is published.
5. writes the update feed and the changelog, attests the apk, uploads everything as the `release` artifact.
6. the `publish` job (only for a manual run with `publish=true`) is the only one with write access. it re-checks the feed against the apk, creates the release as a draft with every asset, then publishes it and marks it the latest release, so a client never sees a release without its files.
7. the `announce` job posts the release to the telegram channel with `ci/announce.py`, made from the release's `tele-changelog.json`. the channel also gets tele desktop's releases, so the post is titled `tele for android N · <APP_VERSION_NAME>` and ends with a `#android` footer. without the `TELE_BOT_TOKEN` and `TELE_CHANNEL` secrets it posts nothing. a failed post doesn't touch the release: re-run the job, or post any published release with `gh workflow run announce.yml -f tag=<tag>`.
8. add the release to [releases](releases.md) from its published `tele-changelog.json`, with the base version, the date and the patch count at its tag.

runs on one branch queue one after another, so two releases never pick the same number.

## what gets published

| file | what it is |
|---|---|
| `tele-<tag>.apk` | the universal apk, signed with the release key |
| `tele-update-android.json` | the update feed: `{"tag", "base", "counter", "url", "apk_sha256"}`, where `base` is `APP_VERSION_CODE` (without the abi digit), `counter` is `N`, `url` points at the apk in this release |
| `tele-changelog.json` | what's new, for the in-app chat: `{"tag", "title", "url", "categories", "items"}`, made from `ci/changelog.json` |

the release notes use the same changelog: Telegram base and patch count, upstream news only for a base change, new features and fixes with categories one heading level below, linked patch references, option locations/defaults, and the Android download. CI pins patch links to the build's commit through `--revision "$GITHUB_SHA"`.

the app reads `releases/latest/download/tele-update-android.json`, updates when `(base, counter)` is newer than its own, checks the sha256 of the download and hands the apk to the system installer. it only accepts urls under `https://github.com/gettele/android/releases/download/<tag>/` ending in `.apk`. after an update it reads `tele-changelog.json` of its own tag once per account. both formats are described in [architecture](architecture.md#update-feed-and-the-tele-server).

## signing

- **the release key** is a keystore on the maintainer's machine: `~/.tele/tele-release.jks`. **back it up, together with its passwords, somewhere other than that machine.** android only installs an update signed with the same key as the installed app, so a lost key means every user has to uninstall and lose local data to get any later release, and nothing in this repository can bring it back.
- the workflow gets it from repository secrets and writes it to `TMessagesProj/config/release.keystore` of the build checkout. the passwords go to gradle as `-PRELEASE_STORE_PASSWORD`, `-PRELEASE_KEY_ALIAS` and `-PRELEASE_KEY_PASSWORD`, and the files are deleted when the build ends. the secrets are masked in logs, and nothing echoes them.
- **the pinned certificate** `ci/release-cert-sha256.txt` is the sha256 of the release key's certificate. changing it is changing who can update the installed apps, so it takes a deliberate change of its own.
- **build provenance.** the apk of a published release is attested with `actions/attest`. anyone can check a download:

  ```
  gh attestation verify tele-<tag>.apk --repo gettele/android
  ```

## repository secrets

set under settings → secrets and variables → actions.

| secret | what it is |
|---|---|
| `TELE_API_ID`, `TELE_API_HASH` | the api pair from [my.telegram.org](https://my.telegram.org), written to `local.properties` of the build (see [development](development.md#api-credentials)) |
| `KEYSTORE_BASE64` | the release keystore, base64 on one line: `base64 -i ~/.tele/tele-release.jks \| tr -d '\n'` |
| `KEYSTORE_PASSWORD` | the keystore password |
| `KEY_PASSWORD` | the key password |
| `TELE_BOT_TOKEN` | token of the bot that posts announcements, an admin of the channel that may post messages |
| `TELE_CHANNEL` | the channel's chat id (`-100…`) |
| `GOOGLE_SERVICES_JSON` | optional: the `google-services.json` of tele's firebase project, with the `org.telegram.messenger.tele` and `org.telegram.messenger.tele.dev` apps. the build writes it to `TMessagesProj_App/google-services.json`, which turns on the google services plugin and fcm pushes. telegram only sends pushes to it when the firebase project's credentials are set for tele's api id on [my.telegram.org](https://my.telegram.org); the service account key never goes into the repository or its secrets |

| variable | what it is |
|---|---|
| `KEY_ALIAS` | the alias of the release key (`tele`). a variable, not a secret: github masks every secret value in logs and outputs, and a secret `tele` would mask the release tag itself |

every run needs all of them except the two announcement secrets and `GOOGLE_SERVICES_JSON`, including pushes: the signature check compares with the pinned certificate.

## new upstream releases

sync.yml checks [DrKLO/Telegram](https://github.com/DrKLO/Telegram) every 6 hours. upstream commits a release as `update to <version> (<code>)` on `gradle.properties`; when its code is above the one in `UPSTREAM`, it opens a `new-upstream` issue with the version, the commit and the commands to rebase. it never rebases or bumps `UPSTREAM` on its own: conflicts are resolved locally, as described in [development](development.md#syncing-with-a-new-upstream-release), and the result goes in as `chore: rebase patches onto <version>`. when `UPSTREAM` has caught up, the next run closes the issue.

## ci notes

- the first build compiles the natives for four abis (ffmpeg, tgnet, voip, ...) and takes a long time; the gradle cache of `main` speeds up later ones, the natives are rebuilt each time. the runner's disk is tight, so the job removes the preinstalled dotnet, ghc and codeql first.
- the build needs the sdk packages that `TMessagesProj/build.gradle` pins; a bump there (new ndk or cmake) is picked up on its own.
