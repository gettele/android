# development

how to set up the tree, build a debug apk, make a change and turn it into a patch. read [architecture.md](architecture.md) first for how the queue works, and [../AGENTS.md](../AGENTS.md) for the rules.

## prerequisites (windows)

- jdk 17 (gradle and agp requirement), on `PATH` or via `org.gradle.java.home`.
- android sdk with: platform `android-36`, build-tools `36.0.0`, ndk `27.2.12479018`, cmake `3.22.1` (all pinned in `TMessagesProj/build.gradle`).
- git; enough disk for the sdk, gradle caches and native build artifacts (tens of gb).
- the first build compiles natives (ffmpeg stack, tgnet, voip) — expect a long, slow build. later java-side rebuilds are fast.
- **disk space:** the sdk drive needs several gb free for the pinned ndk `27.2.12479018` and cmake `3.22.1` (gradle installs them automatically if the sdk license is accepted). a full c: drive fails the build with `InstallFailedException` / "insufficient disk space" during configuration.

## layout

```
<build path>/
  Telegram/    DrKLO/Telegram checkout, branch `tele` — the code tree
  main/        this repository — queue, docs, patches
```

the checkout already exists at `G:\CodeProjects\tele_android\Telegram` at the `UPSTREAM` commit.

## preparing the code tree

```bash
cd ../Telegram
git checkout master                       # or fetch if needed
git branch -f tele <UPSTREAM commit>      # see UPSTREAM
git checkout tele
```

from here every patch is a commit on top of `<UPSTREAM>`: `git log <UPSTREAM>..tele` is the applied queue.

## sdk wiring

point gradle at the sdk once — `local.properties` in the **checkout root** (`Telegram/local.properties`, gitignored; the same file carries the api credentials below). use forward slashes — a properties file with windows backslashes needs `\\` escaping and one missed escape fails the build with a cryptic sdk-path error:

```
sdk.dir=C:/Users/<user>/AppData/Local/Android/Sdk
```

## submodules

the checkout has 15 submodules; two are required even to configure the build (`TMessagesProj_Modules/media` — androidx media3 fork wired from `settings.gradle`, and `TMessagesProj/lib/jlatexmath`), the `jni/*` ones are required for the native part:

```bash
cd ../Telegram
git submodule update --init --depth 1 TMessagesProj_Modules/media TMessagesProj/lib/jlatexmath   # configure
git submodule update --init --depth 1                                                           # everything, for natives
```

the first full init downloads gigabytes; it is a one-time cost.

## api credentials

**the stock `APP_ID`/`APP_HASH` shipped in the telegram repo are flagged as spam — logging in with them does not work.** a fork must use its own pair from [my.telegram.org](https://my.telegram.org).

the pair is read from `local.properties` in the **checkout root** (`Telegram/local.properties`) by the first queue patch (`misc: support custom api credentials`) and baked into `BuildConfig`:

```
sdk.dir=C:/Users/<user>/AppData/Local/Android/Sdk
TELE_API_ID=12345
TELE_API_HASH=abcdef0123456789abcdef0123456789
```

- `local.properties` is gitignored in the checkout: the values never enter the queue, patches or commits. never put the real pair anywhere tracked, and never send it to anyone.
- with no pair set, the build falls back to the stock constants (compiles fine, login will not work) and gradle prints a `tele:` warning.
- a custom api id is not an official one, so `BuildVars.SUPPORTS_PASSKEYS` is disabled automatically when the pair is set.

## building

```bash
cd ../Telegram
./gradlew :TMessagesProj_App:assembleDebug
```

- the apk lands in `TMessagesProj_App/build/outputs/apk/debug/`; gradle splits by abi — install `arm64` on anything modern:
  `adb install -r TMessagesProj_App/build/outputs/apk/debug/*.arm64.apk`
- a debug build is a real client on a real account: prefer a secondary account or telegram's test servers for testing.
- `APP_PACKAGE`, `APP_VERSION_NAME`/`APP_VERSION_CODE` live in `gradle.properties`; the branding patch changes them.

## making a change

all work happens in the telegram tree, as commits on `tele`.

1. **edit** in the checkout. follow [../AGENTS.md](../AGENTS.md): fork code in `tele/`, stock files get gated hunks only.
2. **build and run.** exercise the change by hand with the option on and off. off has to behave exactly like stock.
3. **commit.**
   - a new feature is one new commit at the end of the queue: `feat: <what it does>`.
   - a fix to a patch that isn't released yet goes into that patch's commit: `git commit --fixup <commit>`, then `git rebase -i --autosquash <UPSTREAM>`.
   - one line, lowercase, imperative, no attribution.
4. **export** into this repository:

   ```bash
   cd ../Telegram
   git format-patch <UPSTREAM> -o ../main/patches/android/ --zero-commit --no-signature
   ```

   this rewrites the numbered patch files from the commits. `git status` in `main/` shows exactly which patches changed.

5. **update `PATCHLIST.md`** (statuses, new rows) and commit here, one commit per patch:

   ```bash
   cd ../main
   git add patches/android PATCHLIST.md
   git commit -m "feat: <what it does>"
   ```

## the batch gate

patches are shipped in batches (see `PATCHLIST.md`). when the last patch of a batch is committed and exported:

1. `./gradlew :TMessagesProj_App:assembleDebug` with every batch toggle exercised in at least one of: on, off, default state.
2. hand the apk over for manual testing (device or avd). state plainly what to test and how.
3. after human verification, mark the batch `done` in `PATCHLIST.md`.

a feature is never claimed working because it compiles.

## checking the queue applies

the export is only trustworthy if the queue applies to a pristine base:

```bash
git -C ../Telegram checkout -b scratch <UPSTREAM>
git -C ../Telegram am ../main/patches/android/*.patch   # or format-patch round-trip via git am --3way
git -C ../Telegram branch -D scratch
```

if a patch fails to apply outside your tree, a commit wasn't exported or a patch was edited by hand.

## syncing with a new upstream release

```bash
cd ../Telegram
git fetch origin
git rebase --onto <new release commit> <UPSTREAM> tele
```

- a conflict points at exactly one patch; fix it in that patch's commit (`git rebase --continue`).
- rebuild and test the patches whose conflicts were resolved.
- re-export the queue, update `UPSTREAM`, and commit here: `chore: rebase patches onto <version>`.

syncing is its own change — never mix it with a feature change.
