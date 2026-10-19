# releasing

for maintainers. releases are built and published by github actions and need the repository's secrets, so contributors never release anything themselves. this page explains how it works, so everyone knows what a release is made of and how to check one. the model is [tele desktop's](https://github.com/nitreojs/tele/blob/main/docs/releasing.md), cut down to one platform.

## versions

- a release is tagged `v<APP_VERSION_NAME>-tele.<N>`, for example `v13.0.2-tele.1`, and titled `tele N · <APP_VERSION_NAME>`. `APP_VERSION_NAME` and `APP_VERSION_CODE` come from `gradle.properties` of the patched telegram tree, so they follow `UPSTREAM`.
- `N` is one above the highest existing `v*-tele.*` release or tag, whatever upstream it was built on: numbers go on across upstream bumps, because the app compares build numbers. build.yml picks it, or takes the `number` input when it's above every existing one.
- `N` is compiled in as `TELE_BUILD` (`local.properties` of the build, read by `TMessagesProj/build.gradle`). the app shows it as the build number and builds without it (`TELE_BUILD` unset, so local and dev builds) never update themselves.
- the self-updater orders builds by `APP_VERSION_CODE` first and `N` second, so a release on a newer upstream always wins.

## before a release

1. **patches.** the queue is exported and committed on `main`, and applies to a fresh clone of `UPSTREAM` (see [development](development.md#checking-the-queue-applies)). every patch of the batch was tested on a device, a ci run takes about an hour and a broken release reaches every user through the updater.
2. **changelog.** write what's new into `ci/changelog.json`, replacing the previous release's text:

   ```json
   {
     "categories": ["interface", "chats"],
     "items": [
       {"text": "scroll to zoom in the photo viewer", "where": "settings → tele → interface", "category": "interface"}
     ]
   }
   ```

   `categories` is the order of the groups in the app and in the release notes, and every item's `category` has to be listed. `where` is where to find it and may be empty. one sentence per item, plain text. the limits are the app's (100 items, 16 categories, 64 characters in a category, 1024 in an item), `python3 ci/changelog.py ci/changelog.json --tag v1-tele.1 --repo gettele/android` validates the file. publishing fails while the items equal the previous release's.

## building and publishing

build.yml runs in two ways:

- **a push to `main`** that touches `UPSTREAM`, `patches/`, `ci/` or the workflow builds and checks everything, and keeps the apk as an artifact for 7 days. it never publishes.
- **a manual run** (`gh workflow run build.yml --ref main -f publish=true`, optionally `-f number=<N>`) builds the same and publishes the release. it's refused on any branch but `main`. `publish=false` is the same build without the release.

the run:

1. fetches [DrKLO/Telegram](https://github.com/DrKLO/Telegram) at the `UPSTREAM` commit and the submodules, and applies `patches/android/*.patch` with `git am` as `github-actions[bot]`.
2. picks `N`, builds the tag, and checks `ci/changelog.json` before the long part starts.
3. installs the sdk packages pinned in `TMessagesProj/build.gradle` (platform, build tools, ndk, cmake) and builds `:TMessagesProj_App:assembleAfatRelease`: the universal apk (`afat` flavor, all four abis, `minApi` 23), release build type, minified and signed.
4. checks that the apk verifies and is signed by the certificate pinned in `ci/release-cert-sha256.txt`: a build signed by any other key fails here, before anything is published.
5. writes the update feed and the changelog, attests the apk, uploads everything as the `release` artifact.
6. the `publish` job (only for a manual run with `publish=true`) is the only one with write access. it re-checks the feed against the apk, creates the release as a draft with every asset, then publishes it and marks it the latest release, so a client never sees a release without its files.

runs on one branch queue one after another, so two releases never pick the same number.

## what gets published

| file | what it is |
|---|---|
| `tele-<tag>.apk` | the universal apk, signed with the release key |
| `tele-update-android.json` | the update feed: `{"tag", "base", "counter", "url", "apk_sha256"}`, where `base` is `APP_VERSION_CODE` (without the abi digit), `counter` is `N`, `url` points at the apk in this release |
| `tele-changelog.json` | what's new, for the in-app chat: `{"tag", "title", "url", "categories", "items"}`, made from `ci/changelog.json` |

the release notes are made from the same changelog: the items by category, and the download.

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

| variable | what it is |
|---|---|
| `KEY_ALIAS` | the alias of the release key (`tele`). a variable, not a secret: github masks every secret value in logs and outputs, and a secret `tele` would mask the release tag itself |

every run needs all of them, including pushes: the signature check compares with the pinned certificate.

## new upstream releases

sync.yml checks [DrKLO/Telegram](https://github.com/DrKLO/Telegram) every 6 hours. upstream commits a release as `update to <version> (<code>)` on `gradle.properties`; when its code is above the one in `UPSTREAM`, it opens a `new-upstream` issue with the version, the commit and the commands to rebase. it never rebases or bumps `UPSTREAM` on its own: conflicts are resolved locally, as described in [development](development.md#syncing-with-a-new-upstream-release), and the result goes in as `chore: rebase patches onto <version>`. when `UPSTREAM` has caught up, the next run closes the issue.

## ci notes

- the first build compiles the natives for four abis (ffmpeg, tgnet, voip, ...) and takes a long time; the gradle cache of `main` speeds up later ones, the natives are rebuilt each time. the runner's disk is tight, so the job removes the preinstalled dotnet, ghc and codeql first.
- the build needs the sdk packages that `TMessagesProj/build.gradle` pins; a bump there (new ndk or cmake) is picked up on its own.
