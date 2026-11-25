# Testing the desktop tele 29 ports

This is the manual test plan for Android patches `0371`–`0380`. Use a secondary account; wallet and on-chain tests can spend real funds.

## Build and install

```bash
cd Telegram
./gradlew :TMessagesProj_App:assembleDebug --offline
adb install -r TMessagesProj_App/build/outputs/apk/afat/debug/app.apk
adb logcat -c
adb logcat | grep -E 'FATAL EXCEPTION|AndroidRuntime|MTP Info|tele'
```

For every toggle, test **off**, **on**, and **default after a fresh install**. Off must match stock Telegram Android exactly.

## Patch-by-patch checks

### 0371 — member ranks load early

1. Open a megagroup that has custom member ranks.
2. Make sure the cached recent-participant rows fill the members viewport.
3. Open **Members** without scrolling.
4. Verify ranks are present on the first visible rows.
5. Scroll and verify pagination still works and does not duplicate rows.

Expected: the first full participants page is fetched even when cached rows already fill the screen.

### 0372 — stalled media download fallback

This needs a controlled network lab; a normal phone/emulator cannot reliably reproduce it.

1. Use a test DC or proxy where regular endpoints are reachable and `media_only` endpoints blackhole TCP connects.
2. Start a file download on a known download slot.
3. Let the media route time out twice before any bytes arrive.
4. Verify logcat contains `download slot … timed out twice on media route, trying regular DC …`.
5. Verify the same request completes through the regular route.
6. Start a second download on another slot and verify it can remain on the media route.
7. Check logcat for decrypt, bad-salt, `-404`, or retry-limit errors.

Expected: same DC, same slot, same request token and chunk offset; only address/key/salt/session change. CDN, uploads and established transfers must not switch.

### 0373 — hide story posting

1. Enable **tele → privacy → Hide stories**.
2. Verify other people's stories disappear while the chat-list story camera button and posting entry points still follow the nested **Hide story posting** sub-toggle (`off` by default if toggled off explicitly, `on` by default when turning **Hide stories** on with no child set).
3. Expand **Hide stories**, toggle **Hide story posting** off then back on, and verify the chat-list story camera button, share-to-story, profile bottom post button, `StoryRecorder`, `StarGiftSheet`, and `tg://post` disappear and return live.
4. Search settings for `story camera`, `post stories`, and `Hide story posting` with the group collapsed and verify all three open and highlight **Hide story posting**.
5. Disable **Hide stories** and verify viewing and stock story posting both return.

### 0374 — hide bot previews

1. Open a bot profile that has preview media.
2. Enable **tele → bots → Hide bot previews**.
3. Verify the preview tab and its media-count contribution disappear.
4. Disable it and verify the tab returns without an app restart.

### 0375 — plain search calendar

1. Open a chat/search calendar that has photo and video days.
2. Enable **tele → interface → lists → Plain search calendar**.
3. Verify day thumbnails disappear while day numbers, message marks and selection remain.
4. Disable it and verify thumbnails return.

### 0376 — matching blockquotes in reply headers

1. Create an ordinary text source message with formatted text (bold, emoji, custom emoji, formatted date, or plain text in the middle) and reply with a leading blockquote matching a unique substring anywhere in that source, followed by reply text.
2. Repeat against a rich message (`TYPE_ARTICLE`) source with an unambiguous mid-message blockquote match.
3. Enable **tele → messages → quotes → Show matching blockquotes as reply quotes**.
4. Verify both reply headers show the source quote with quote chrome and inline formatting.
5. Tap each header and verify the source is scrolled to and the matched offset (not only offset 0) is highlighted.
6. Disable the toggle and verify headers return to stock.
7. Repeat with duplicate/ambiguous substrings, mismatched entities, media, an album, and an existing manual quote; all must stay stock.

### 0377 — hide incoming gift offers

1. Receive an incoming on-chain gift offer.
2. Enable **tele → profiles and ids → Hide gift offers**.
3. Verify the offer bubble and its notification disappear.
4. Send an outgoing offer and verify it remains visible.
5. Disable the toggle and verify incoming offers return.

### 0378 — no Money also hides gift offers

1. Enable **tele → money → Turn off Money**.
2. Verify the gift-offer action is absent from a collectible gift menu.
3. Verify incoming gift offers are hidden even if **Hide gift offers** is off.
4. Disable **Turn off Money** and verify both return.

### 0379 — incoming Money notices and badge

1. Use a wallet-enabled test account. Leave both new toggles off and receive a transfer; establish the baseline.
2. Enable **tele → money → transactions → Incoming transfers in notifications**.
3. Receive a transfer and verify a tele notice appears with the amount and sender.
4. Enable **New transfers badge** and receive another transfer.
5. Verify `+N` appears next to Money in the chat menu and does not change Telegram unread counters.
6. Open Money and verify the badge clears.
7. Restart the app and verify old transfers are not announced again.
8. Enable **Turn off Money** and verify tracking, notices and badge stop.

### 0380 — on-chain gift password guards

1. Set a local password in **tele → privacy → local password** and enable the relevant buy/sell actions.
2. Try to make a purchase offer, buy a resale gift, list/change the price of a gift, accept an incoming offer, and bulk-unlist gifts.
3. Verify the password prompt appears before the action sheet or network request.
4. Cancel and verify nothing happens; enter a wrong password and verify nothing happens.
5. Unlock and verify the same action resumes once.
6. Disable the corresponding password option and verify the action no longer asks.

## Reporting

For each patch record: account/device, Android version, toggle state, steps, expected/actual result, and relevant logcat lines. A patch is `done` only after the maintainer verifies both on and off states.
