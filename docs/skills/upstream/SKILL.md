---
name: upstream
description: >
  Use when moving the tele (android) patch queue to a new Telegram Android release: the
  sync job opens an issue "telegram android <version> is out", or the maintainer says
  "update UPSTREAM", "rebase the patches onto <version>", "fix the rebase conflicts".
  Covers fetching the release, diffing it against the current base, finding the fixes that
  became obsolete in stock, the rebase loop and the conflict policy, the build and smoke
  test, the export, the UPSTREAM and docs updates, and the finishing checks. NOT for
  adding a feature or fixing a bug on the current base (that is `AGENTS.md` + every
  feature guide in `docs/`).
---

# moving the queue to a new upstream release

tele is a patch queue, not a fork: `UPSTREAM` names the Telegram Android commit, every
patch is one commit on top of it in `../Telegram` on branch `tele`. A new upstream
release is its own change (`chore: rebase patches onto <version>`), never mixed with
features. What follows is the whole procedure; the rules behind it are in
[AGENTS.md](../../../AGENTS.md) and [architecture.md](../../architecture.md).

## 0. what a new release means

`sync.yml` opens an issue `telegram android <version> (<code>) is out` with the commit
hash. It never rebases: conflicts are resolved locally, by an agent or the maintainer.
Read the issue, take the commit from it, and check whether the release has a `13.x.y`
`update to <version> (<code>)` commit plus a `1266006d8 update submodules`-style commit.

## 1. fetch and size the change

```bash
cd ../Telegram
git fetch origin
git log --oneline <old-base>..<new-base>            # how many commits, what they are
git log --no-merges --oneline <old-base>..<new-base>
git diff --stat <old-base>..<new-base> | tail -5
```

Work out what the rebase will hit: the files our queue touches against the files upstream
changed.

```bash
git diff --name-only <old-base>..<new-base> > /tmp/up.txt
git diff --name-only <old-base>..tele        > /tmp/ours.txt
comm -12 <(sort /tmp/up.txt) <(sort /tmp/ours.txt)
```

Dozen files = a quick rebase; a few hundred = expect a day of conflict work and read
section 3 before starting. Always back the queue up first:

```bash
git branch -f tele-before-<version> tele
```

## 2. find the fixes that stock now does itself

Before the rebase, look for our own `fix:` patches that upstream wrote too. Two probes:

- search the upstream commits for the feature: `git log --oneline <old>..<new> -i
  --grep='location\|menu\|scheduled\|badge\|photo\|story'`, and read the bodies of the
  suspicious ones;
- diff the file a fix patch touches and compare with our hunk:
  `git diff <old>..<new> -- <file>`. A fix is obsolete when upstream now does the same
  thing (not merely nearby edits).

If it is obsolete:

```bash
# during the rebase this is a conflict, or the commit applies as a no-op
git rebase --skip
cd ../main
git rm patches/android/<NNNN>-<subject>.patch
# drop its row from features.md, note it in the 13.x section of docs/PATCHLIST.md
```

13.2.1 did this to `0304` (live location kept the gps request alive): the new
`GoogleLocationProvider` keeps the `LocationCallback` per listener, so the patch went
away. Keeping it would have applied a worse variant of stock code.

## 3. rebase

```bash
cd ../Telegram
git rebase --onto <new-base> <old-base> tele --autostash
```

`--autostash` matters: a local wallet-engine rebuild leaves `TMessagesProj/jni/prebuild/*`
and three submodule pointers dirty, and they must survive the rebase untouched. Never
commit them into a patch.

On a conflict git stops at one patch. For each one:

1. read both sides (`git diff --name-only --diff-filter=U`, then the conflict block);
2. decide by category (below), edit the file, `git add <file>`;
3. `git rebase --continue` (use `GIT_EDITOR=true` so it does not open an editor);
4. `git rebase --abort` is always available — the backup branch is the fallback.

### conflict categories

- **upstream added lines next to ours.** keep both: upstream's lines, then our addition.
  Most conflicts are this.
- **upstream refactored the code our hook lived in.** take upstream's side, then re-attach
  the fork hook to the new shape: a `TeleConfig` gate, a helper call, a changed argument.
  Never keep the old stock body our patch carried as context; it would resurrect dead
  code. 13.2.1 turned `ProfileActivity.nameTextView[]` into one `nameTextView`, moved the
  shared media menus into `fillOptions`, and gave stars a `RecyclerPagerView`; the hooks
  were re-pointed, not re-added.
- **constant id collision.** both sides declare `private final static int` menu ids. Keep
  upstream's values and move ours: check the whole set with
  `grep -o 'static final int [a-z_0-9]* = [0-9]*'` and look for duplicates (message menu
  ids and chat menu ids are different dispatchers, so numbers may repeat there).
- **stock fix replaced ours.** drop our hunk, let upstream's code stand (see 2).
- **functionally contradictory.** upstream changed the behaviour our patch depended on:
  stop, decide whether the feature still makes sense, and if not, skip the patch and put
  it in the PATCHLIST section for the rebase.

Never hand-edit anything under `main/patches/`; the tree is the source.

## 4. build

```bash
cd ../Telegram
git submodule update --init            # first, always: upstream bumps submodules
./gradlew :TMessagesProj_App:assembleDebug
```

**submodules come first.** an `update to <version>` commit usually moves
`jni/tgcalls`, `jni/third_party/ffmpeg`, `libprisma`, `libvpx` and friends; the old
checkouts then fail the native build with C++ errors that look like a bad patch
(`no matching constructor for initialization of 'TokenList'` in libprisma, for example).
`git submodule status` marks every out-of-sync checkout with `+`; update those, then build.
a new ffmpeg commit means the natives are rebuilt, which is slow.

- the first build after an upstream bump recompiles natives (cmake + ndk): tens of
  minutes. A `git clean` in `TMessagesProj` resets that cost.
- **sandbox without Google Maven.** `dl.google.com` (and therefore `maven.google.com`) is
  blocked in some environments: new plugin versions (`com.google.gms:google-services`)
  and new dependencies (`firebase-bom`, mlkit, `firebase-pnv`) cannot be resolved, and the
  build fails at configuration or `resolveDependencies`. `repo.maven.apache.org` does not
  carry them either (the android firebase/androidx artifacts live only on Google Maven).
  do not commit version pins and do not commit repository changes; add a local init script
  instead and delete it afterwards:

  ```groovy
  // ~/.gradle/init.d/tele-mirrors.gradle — local only
  def mirrors = [
      'https://maven.aliyun.com/repository/google',
      'https://maven.aliyun.com/repository/public',
  ]
  settingsEvaluated { settings ->
      settings.pluginManagement.repositories {
          maven { url 'https://maven.aliyun.com/repository/gradle-plugin' }
          maven { url 'https://maven.aliyun.com/repository/google' }
          maven { url 'https://maven.aliyun.com/repository/public' }
          gradlePluginPortal()
          google()
          mavenCentral()
      }
  }
  gradle.projectsLoaded {
      gradle.rootProject.buildscript.repositories { mirrors.each { m -> maven { url m } } }
      gradle.rootProject.allprojects { repositories { mirrors.each { m -> maven { url m } } } }
  }
  ```

  aliyun's `google` mirror carries the firebase bom, `firebase-pnv`, `google-services`
  and the crashlytics plugin. do not add `repo.huaweicloud.com` — it hangs on
  `com.huawei.agconnect:agcp`; the project's own `developer.huawei.com/repo` serves it and
  is already in `build.gradle`.
- compile errors after a big refactor are the compiler pointing at the stock api our
  patches still use. Search the new class (`grep -n 'nameTextView'`) and fix the call,
  not the whole patch.

## 5. run and smoke test

Install the apk and walk the basics with every toggle at its default first:
open a chat, the message menu incl. `tele`/`Tools` submenus, send text/photo/sticker, the
profile (badges, id row), settings → tele (every page opens, search finds a setting), the
chat list title, the folder tabs. Then the areas the rebase touched by hand, from the
PATCHLIST section of this release. Hand the android-testing part to the maintainer when
it needs their device or account.

## 6. export and docs

```bash
cd ../Telegram
git format-patch <new-base> -o ../main/patches/android/ --zero-commit --no-signature --no-numbered
```

then in `main`:

- `UPSTREAM`: version, full commit, repo (three lines).
- `docs/PATCHLIST.md`: a `## перенос на <version>` section: what upstream changed that hit
  our patches, which fix patches were dropped as obsolete, which features were re-pointed
  and need a device check. Keep it short; the skill and the patches hold the details.
- `features.md`: drop the rows of dropped patches; every row links a patch file by number,
  and a dropped patch leaves a dead link.
- `docs/architecture.md`: the `UPSTREAM` example line holds the current base commit.
- `docs/releases.md`: the queue count in the header ("the queue now has N patches").
- `ci/changelog.json`: the release notes are written for the *next* release; mention the
  rebase and the features that arrived with it there, not in `releases.md`.

## 7. commit and verify

```bash
cd ../main
git add UPSTREAM patches docs/PATCHLIST.md features.md docs/architecture.md docs/releases.md
git commit -m "chore: rebase patches onto <version>"
```

the subject goes into the queue history and the next release notes: `chore: rebase patches
onto 13.2.1`, no body. Do not push unless asked; a push to `main` starts a ci build.

finishing checks:

- the queue applies to a pristine base and reproduces the tree:

```bash
cd ../Telegram
export GIT_INDEX_FILE=$(mktemp -u)
git read-tree <new-base>
for p in ../main/patches/android/*.patch; do git apply --cached "$p" || echo "FAIL $p"; done
[ "$(git write-tree)" = "$(git rev-parse HEAD^{tree})" ] && echo replay ok
unset GIT_INDEX_FILE
```

- `git rev-list --count <new-base>..tele` equals the number of patch files;
- no conflict marker survived a resolution, committed or not:

```bash
grep -rn '^<<<<<<< \|^>>>>>>> ' --include=*.java --include=*.kt --include=*.xml TMessagesProj
```

  a marker left in a tree that `git am`/rebase accepted only fails at the java compile,
  often hundreds of lines away from the rebase;

- the working tree has no source changes left (`git status --short -- 'TMessagesProj/src'`
  is empty; the wallet prebuilt files and submodule pointers stay as they were);
- `main` has no dead links: `grep -o 'patches/android/[0-9]\{4\}-[^)]*' features.md
  docs/PATCHLIST.md` against `ls patches/android`.

## recurring shapes

| symptom | fix |
|---|---|
| `nameTextView[a]` does not compile | upstream has one `nameTextView`: drop the index and the `copyFromChatActivity` second-view branch |
| an old stock body reappears inside our patch | the patch carried it as context; take upstream's new body and re-add only our lines |
| `Could not find com.google.gms:google-services:<version>` | sandbox without Google Maven: local temporary pin or build elsewhere; never commit it |
| every patch changed after the export | expected: `index` hashes and hunk offsets move with the base; only content changes matter |
| `git rebase` refuses: "unstaged changes" | wallet prebuilt artifacts: `--autostash`, never `--force` |
| native build fails in `libprisma`/`jni` with implausible C++ errors | submodules are at the old commits: `git submodule update --init` |
| `Could not find com.google.firebase:firebase-pnv` | Google Maven is blocked: local mirror init script (section 4), never a committed version pin |
