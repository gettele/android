# releases

every tele android release, newest first. release notes and the in-app what's new are made from `ci/changelog.json` and the published `tele-changelog.json`; this page keeps the same history readable in the repository. [features](../features.md) groups the same features by settings page. Follow [releasing](releasing.md#before-a-release) when writing the next changelog: new/fix sections keep categories one heading level below, and Telegram news appears only when the base changes from the latest published release.

11 releases, 336 patches at [tele 11](https://github.com/gettele/android/releases/tag/v13.2.1-tele.11). the queue now has 341 patches on telegram 13.2.2. Upcoming changes live in `ci/changelog.json`; only published releases belong in this history.

| release | base | published | patches |
|---|---|---|---|
| [tele 11 · 13.2.1](https://github.com/gettele/android/releases/tag/v13.2.1-tele.11) | 13.2.1 | 2026-11-11 | 336 |
| [tele 10 · 13.2.1](https://github.com/gettele/android/releases/tag/v13.2.1-tele.10) | 13.2.1 | 2026-11-08 | 309 |
| [tele 9 · 13.1.1](https://github.com/gettele/android/releases/tag/v13.1.1-tele.9) | 13.1.1 | 2026-11-07 | 300 |
| [tele 8 · 13.1.1](https://github.com/gettele/android/releases/tag/v13.1.1-tele.8) | 13.1.1 | 2026-11-03 | 244 |
| [tele 7 · 13.1.1](https://github.com/gettele/android/releases/tag/v13.1.1-tele.7) | 13.1.1 | 2026-10-26 | 228 |
| [tele 6 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.6) | 13.0.3 | 2026-10-25 | 202 |
| [tele 5 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.5) | 13.0.3 | 2026-10-23 | 144 |
| [tele 4 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.4) | 13.0.3 | 2026-10-23 | 131 |
| [tele 3 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.3) | 13.0.3 | 2026-10-22 | 141 |
| [tele 2 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.2) | 13.0.3 | 2026-10-21 | 127 |
| [tele 1 · 13.0.2](https://github.com/gettele/android/releases/tag/v13.0.2-tele.1) | 13.0.2 | 2026-10-19 | 96 |

### [tele 10 · 13.2.1](https://github.com/gettele/android/releases/tag/v13.2.1-tele.10)

#### interface

- tele speaks russian and ukrainian: its pages, menus and messages follow the app language (settings → language)
- built on telegram 13.2.1, with its native bot widgets, glass menus and new profile pages

#### chats

- turn off bot widgets: they keep their caption and stop running scripts and asking the network (settings → tele → chats)

#### money

- with money turned off, wallet balances are hidden in profiles too (settings → tele → money)

#### fixes

- the language picked in settings applies to the whole interface again, tele's texts included (settings → language)
- settings search shows every row by its own name and opens it right there (settings search)
- the tele menus stay as wide as their items, and their thin separators match the theme (message menu, chat menu)
- two thin separators that meet when a row hides become one (message menu, chat menu)
- a tele submenu opens where its own item was pressed (message menu, chat menu)
- a diagnostic report is asked about once, and don't send keeps it away for good
- scheduled suggested posts are left to telegram instead of failing with an error

### [tele 9 · 13.1.1](https://github.com/gettele/android/releases/tag/v13.1.1-tele.9)

#### money

- import a wallet from a private key or recover it from its address and 12 words, and rotate or copy its phrase (settings → tele → money)
- turn money off entirely, or dim other address groups and hide their balances (settings → tele → money)
- copy a transaction link or open it in an explorer from a transaction or a transfer message (transaction menu, transfer message menu)
- force the wallet to show even when the server turns money off (settings → tele → money)

#### scripts

- scripts run on the phone with telegram methods, updates, storage, timers and web access, and ask for their permissions before they start (settings → tele → scripts)
- import a script by link or from a folder, and keep it off until you enable it (settings → tele → scripts)
- scripts add their own actions to the message menu, with icons (settings → tele → scripts)

#### sending

- docked media can be reordered, holds documents and keeps HQ photos and captions after a restart (settings → tele → sending → attach media above the field)
- docked tiles get file previews, a real spoiler, drag, rounded corners and an animated removal (settings → tele → sending → attach media above the field)
- silent videos can go as GIFs, and GIFs can go as videos (settings → tele → sending)
- stickers and GIFs from the picker can be attached above the field and sent with a caption (settings → tele → sending → attach media above the field)
- the shot screen shows how many messages the picture leaves out (message menu → shot)

#### profiles

- typing in the chat list and the last activity of a hidden last seen (settings → tele → profiles and ids)

#### interface

- view as TL now covers stories, topics, stickers, gifts and folders (settings → tele → interface)
- the message menu groups the tele tools into Tools, tele and For me submenus with icons and thin or thick separators (message menu, chat menu)
- the menu editor keeps the Tools and tele submenus and shows their items after a layout is saved (settings → tele → interface → message menu → editor)

#### links

- the link cleaner strips the a parameter and query fragments from x and twitter links, opened or sent (settings → tele → privacy → links)

#### fixes

- opening many chats with server badges no longer fills memory and crashes the app (settings → tele → interface)
- settings search finds every row again, ignores case and keeps results unique (settings search)
- the menu editor no longer drops stock items when a layout is saved (settings → tele → interface → message menu → editor)
- the submenu editor follows the theme, and new items appear on top (settings → tele → interface → message menu → editor)
- badges keep the name color, and forwarded and reply headers keep their room (settings → tele → interface)
- opening the docked viewer with files no longer crashes, and spoilers survive the editor (settings → tele → sending)
- rejected .tgs sticker uploads are repaired before sending (sending)
- update buttons open tele's update page, and unsupported messages call the app tele (everywhere)

### [tele 8 · 13.1.1](https://github.com/gettele/android/releases/tag/v13.1.1-tele.8)

#### gifts

- a gift studio draws gift stickers and exports them as a picture or a video (settings → tele → profiles and ids → gift studio)
- more gifts, models, backdrops and symbols to pick in the studio (settings → tele → profiles and ids → gift studio)
- every part of a gift shows its rarity (settings → tele → profiles and ids → gift studio)
- a fake upgrade rolls on the device and shows what the gift would have become (settings → tele → profiles and ids → fake upgrade of gifts)
- a roll keeps the number and the model hidden until it ends (settings → tele → profiles and ids → fake upgrade of gifts)
- a gift grid builds a table of gifts and saves it as a picture (settings → tele → profiles and ids → gift grid)
- grid cells are edited, moved and duplicated, and whole grids are saved (settings → tele → profiles and ids → gift grid)
- anyone's gifts open in the grid, not only your own (settings → tele → profiles and ids → gift grid)
- gift search no longer runs out of memory on huge collections (settings → tele → profiles and ids → search gifts)

#### debug

- an mtproto log keeps what the app sends and receives, like the desktop inspector (settings → tele → debug → capture mtproto)
- the log shows every entry as a tree, with filters, copy and a schema link (settings → tele → debug → open the log)
- a console sends any method the app knows, and the dangerous ones ask first (settings → tele → debug → mtproto console)
- crashes without a dump and interface freezes come as reports too (settings → tele → debug)

#### server

- crash reports tell how much memory was used, and a snapshot can be kept (settings → tele → server → memory snapshot on crashing)

### [tele 7 · 13.1.1](https://github.com/gettele/android/releases/tag/v13.1.1-tele.7)

#### notifications

- a notification center keeps rate limits, updates, mentions and other tele notices in one list, also in the chats menu (settings → tele → notifications → notification center)
- telegram's waits for sending, reacting, joining or searching get a countdown and go to the center (settings → tele → notifications → rate limits)
- group messages that mention you or reply to you are kept in the center, muted chats too (settings → tele → notifications → log mentions and replies)
- ids and values copied by tele and tele's toasts are kept in the center (settings → tele → notifications → notification center)
- notices from the tele server show up in the center (settings → tele → server → notifications from the server)
- a notification when someone from your list comes online (settings → tele → notifications → notify when people come online)
- release builds get push notifications through google play services

#### gifts

- a local password or fingerprint before stars are spent, gifts leave your account or bots are paid (settings → tele → privacy → local password)
- hidden gifts are dimmed, and several gifts can be selected to show, hide, pin, transfer, sell or convert at once (settings → tele → profiles and ids → select several gifts)
- search a profile's gifts by name, model, backdrop and symbol (settings → tele → profiles and ids → search gifts)
- send several gifts at once (settings → tele → profiles and ids → send several gifts at once)
- copy a gift collection's link, and failed collections load again (settings → tele → profiles and ids → copy gift collection link)
- search, filter and export star transactions as csv (settings → tele → interface → lists → search and export star transactions)
- filter transactions, gifts and shared media by a date range (settings → tele → interface → lists → filter lists by date)

#### chats

- save downloads into Telegram/<chat name> folders (settings → tele → chats → downloads)
- turn off telegram's ai features, voice transcription stays (settings → tele → chats → turn off ai features)
- open locations in google maps, openstreetmap, yandex maps, 2gis or apple maps (settings → tele → messages → maps → map service)
- a thinner brush in the photo editor (settings → tele → interface → editor → thinner brush in the editor)

#### everywhere

- based on telegram 13.1.1
- hiding phone numbers also hides your own number in settings (settings → tele → privacy → hide phone numbers in profiles)
- a dropped update download is retried in a few seconds
- the call log loads again after a failed page

### [tele 6 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.6)

#### chats

- pin more chats than telegram allows, extras stay on this device (settings → tele → chats → pin chats past the limit)
- folders and folder chats past telegram's limits stay on this device (settings → tele → chats → folders past the limit)
- an unsorted folder with the chats no other folder takes (settings → tele → chats → unsorted folder)
- folder tabs can show only their icons (settings → tele → chats → compact icon folders)
- hide unread counters on folder tabs and the app icon, or leave out the archive and some accounts (settings → tele → chats → hide unread counters)
- chat list rows can shrink to one line without message previews (settings → tele → chats → hide message previews)
- chats jump to their new place in the list without sliding (settings → tele → chats → move chats instantly)
- community chats show up as regular chats (settings → tele → chats → hide communities)
- hide birthday banners, labels and effects (settings → tele → chats → hide birthdays)
- the chat menu jumps to the very first message of a chat or topic (settings → tele → chats → jump to the first message)
- set a chat background only you see, or hide the one the other side set (settings → tele → chats → backgrounds)
- search a chat with a regular expression (settings → tele → chats → regex search in chats)
- filter chat search by photos, videos, files, links, music, voice and more (settings → tele → chats → message type filter in chat search)
- big groups with hidden members show how many are online (settings → tele → chats → show online members in big groups)
- select up to 10000 messages, deleted and forwarded in parts (settings → tele → chats → select more than 100 messages)
- sending exactly /name sends that quick reply (settings → tele → chats → send quick replies by name)
- pin sticker and emoji sets to the front of the panel with a long press (settings → tele → chats → pin sticker and emoji sets)
- filter stickers and emoji by format: static, animated or video (settings → tele → chats → filter stickers and emoji by format)
- choose and order the reactions of the message menu (settings → tele → chats → reactions in the menu)

#### notifications

- mute every chat of a folder from its tab, or silence a chat completely, mentions included (settings → tele → notifications → mute folders)

#### messages

- bubbles can have a round corner instead of a tail (settings → tele → messages → hide bubble tails)
- quote several parts of messages in one reply, voice transcriptions too (settings → tele → messages → multiple quotes in one reply)
- code blocks of 5 lines or more get line numbers (settings → tele → messages → line numbers in code blocks)
- stickers show their captions (settings → tele → chats → show sticker captions)
- choose whether the name in a quote of a deleted message is bold, a link or a mention (settings → tele → messages → keep deleted messages → name in quotes)

#### sending

- send silently by default, with a per-chat switch (settings → tele → sending → send silently by default)
- stickers and gifs send on the second tap, voice and video messages stop in the preview (settings → tele → sending → confirm before sending)
- mkv files from the gallery go as videos (settings → tele → sending → send mkv files as videos)
- send audio files as voice messages (settings → tele → sending → send audio files as voice messages)
- send stickers with captions (settings → tele → sending → send stickers with captions)
- the menu of a failed message sends every failed message again (settings → tele → sending → retry all failed messages)
- forward messages one by one, waiting out flood limits (settings → tele → sending → forward messages one by one)
- messages queued behind an upload show it and can be sent right away (settings → tele → sending → queue behind media)
- long-press a mention suggestion to mention several people in a row (settings → tele → sending → mention several people in a row)
- markdown is styled as you type, > lines can go as quotes (settings → tele → sending → render markdown as you type)
- calcmula suggests a fixed expression and can send without calculating (settings → tele → sending → calcmula suggestions)
- typing = after an expression shows its result above the field (settings → tele → sending → inline calcmula results)
- emoji typed with the keyboard count in recent emoji (settings → tele → sending → count typed emoji in recent emoji)
- a failed upload part is retried instead of failing the whole file

#### menus

- save messages as a picture with shot, over the chat background (settings → tele → interface → shot)
- copy text as markdown or html (settings → tele → menus → copy as markdown or html)
- hide and show the pinned message bar from the chat menu (settings → tele → menus → hide and show the pinned bar)
- restrict someone from their message or userpic menu (settings → tele → menus → restrict in message and userpic menus)

#### profiles

- the blurred profile photo as the profile background, and the whole profile in its colors (settings → tele → profiles and ids → blurred photo as profile background)
- blank and invisible names show the @username, a phrase or the id (settings → tele → profiles and ids → show usernames for invisible names)
- names, bios and messages made of hidden characters show their codes (settings → tele → profiles and ids → show hidden characters)
- the media viewer shows the data center and when the media was uploaded (settings → tele → profiles and ids → media upload date in the viewer)
- settings of profiles and ids show live previews (settings → tele → profiles and ids)

#### interface

- the whole interface in lowercase (settings → tele → interface → lowercase everything)
- tele checkmarks and icons next to names in messages (settings → tele → interface → badges next to names in messages)
- what's new lists every version's changes with live switches (settings → tele → what's new)
- tg://settings/tele links open and highlight a tele setting

#### everywhere

- mini apps never open in fullscreen (settings → tele → bots → never open web apps in fullscreen)
- rewrite only the link preview, pasted links stay as typed (settings → tele → privacy → rewrite only the link preview)

### [tele 5 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.5)

#### messages

- deleted messages list their chats like the chat list, and a chat shows them as bubbles (settings → tele → messages → deleted messages)
- choose which deleted messages to keep: in bot chats, in saved messages, the ones you delete (settings → tele → messages → keep deleted messages)
- deleted messages and edit history can be forgotten after 1, 7 or 30 days, and their media survives cache cleaning (settings → tele → messages → keep deleted for)
- deleted and left chats and topics stay readable in deleted messages (settings → tele → messages → deleted chats and topics)
- a deleted channel post is rebuilt from its forward when you open it from there (settings → tele → messages → recover channel posts from forwards)
- bookmark messages and step through them with a button, a long press lists them (settings → tele → messages → message bookmarks)
- after sending while scrolled up, a button jumps back to where you were reading (settings → tele → messages → return to where you were reading)
- tele logs when private chats read your messages and shows it in the message menu (settings → tele → messages → remember read times)

#### chats

- saved gifs and favorite stickers over the server limit stay on this device (settings → tele → chats → keep saved gifs and favorite stickers past the limit)

#### sending

- closing the picker with a selection docks it above the field: tap a tile to edit it, + to pick more (settings → tele → sending → attach media above the field)

#### menus

- remove all your messages from a chat or topic, waiting out flood limits (settings → tele → menus → remove my messages)

#### interface

- setting descriptions are shorter (settings → tele)

#### everywhere

- messages the server refuses to delete come back in the chat

### [tele 4 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.4)

#### drafts

- the drafts page lists the chats like the chat list, and a chat opens its drafts as outgoing bubbles, with its own field to write new ones and attach photos and videos. (settings → tele → messages → saved drafts)
- a draft is edited in place: an editing draft bar sits over the field, the send button saves it, and the send menu can send it and remove the draft or save it as a new one. (drafts → edit)
- a draft can be sent right away or to another chat, without sound, scheduled or deleted after sending, and several drafts can be selected at once. (drafts → send now)
- a long text you erase or replace, a local draft that a cloud draft overwrites and the media you clear from the tray are kept for a week as recently discarded drafts, up to 5 per chat, to restore or keep. (send button menu → recently discarded)
- the drafts button by the field opens the drafts of the chat, a long tap edits the latest one.

#### interface

- the title above the chat list is a live template: build, version, time and date, your name, the unread count, the connection status and more, with an editor, a live preview and presets. (settings → tele → interface → chat list title)
- the tele settings follow the desktop pages: interface, chats, messages, sending, notifications, menus, privacy, profiles and ids, bots, debug, server, backup and updates, and the tele row has its own block above telegram premium. (settings → tele)
- a setting with children folds them under its switch, which counts the enabled ones and keeps their values. (settings → tele)

#### menus

- every tele menu can be rearranged: the order, the hidden items, the separators and the submenus, with presets and a text layout to copy and import. (settings → tele → menus → menu editor)
- the menu items of a feature stay hidden until the feature is on. (settings → tele → menus)
- the message menu can copy the text of a service message. (settings → tele → menus → copy the text of service messages)
- the message menu can copy the path of a downloaded file. (settings → tele → menus → copy the path of a downloaded file)
- the TL view of a message opens inside the app. (settings → tele → menus → view messages as TL)
- the menu of a message with an alias can copy or delete the alias. (settings → tele → profiles and ids → username aliases)
- the menu of a sticker set or an emoji pack can copy the id of its owner. (settings → tele → profiles and ids → copy sticker set owner id)

#### messages

- service messages that you can delete can be selected too. (settings → tele → messages → select service messages)

#### tele

- tele checks for updates when it starts, not only after the settings are opened. (settings → tele → updates)
- the test backend checkbox is on the login screen in every build, so an added account can live on the telegram test server. (login screen)

### [tele 3 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.3)

#### updates

- the new in tele page lists the settings that came with the new build, also for a user who updated from tele 1. (settings → tele → updates)
- an interrupted update download continues where it stopped, and a failed check waits longer before the next attempt. (settings → tele → updates)
- a scheduled message that the server delayed is sent on time, with a bounded number of retries. (settings → tele → sending → send scheduled messages on time)

#### interface

- service messages show their time too, like joins and pins. (settings → tele → interface → show seconds in message times)
- the similar channels block and the request behind it can be turned off. (settings → tele → interface → hide similar channels)
- the tooltip of the collectible status can be hidden. (settings → tele → interface → hide the collectible status hint)
- the animations are limited while the chat is open, and the previous state comes back when the option is turned off. (settings → tele → interface → reduce motion)
- the edited mark is not shown on the messages of a bot. (settings → tele → interface → no edited mark on bot messages)
- a long tap on the start button shows the start parameter of the bot. (settings → tele → interface → show the start parameter)

#### links

- the link rewrite presets follow the new targets: TikTok goes to tnktok.com only, X adds samekosabax.com, and the old vxtiktok.com target is migrated silently. (settings → tele → sending → rewrite rules)

#### privacy

- the phone number can be hidden in the profiles. (settings → tele → privacy → hide phone numbers in profiles)

#### tele

- the gift button in the message field and the gift entry of a channel can be hidden. (settings → tele → sending → hide the gift button in the message field)
- the copied peer id is the plain number, without the spaces and without the data center. (profile → the id and data center rows)
- the data center of a chat comes from the oldest photo of its avatar history, and the row says uncertain when the data centers differ. (settings → tele → ids → show data center)

### [tele 2 · 13.0.3](https://github.com/gettele/android/releases/tag/v13.0.3-tele.2)

#### tele

- the tele pages get section rows in a rounded card with explanatory text, and a search result opens the page scrolled to the setting. (settings → tele, settings search)
- the onboarding and permission prompts name the app too. (launcher, onboarding, settings)
- the fork's own texts are capitalized, like telegram's. (settings → tele)

#### privacy

- pick the people whose messages tele hides in the chat and in the chat list: every peer is hidden completely or faded. (settings → tele → privacy → ignored → ignored users)
- the profile of a person gets an "Ignore messages" row that hides their messages for you. (settings → tele → privacy → ignored → show the ignore button in the profile)
- the ignored users picker is its own screen with the stock chat rows, a search and a done button. (settings → tele → privacy → ignored → ignored users)
- the master switch of the ghost options: nothing is hidden while it is off. (settings → tele → privacy → ghost → ghost mode)
- the live preview of the ghost mode: the card shows what you show and what the peers see. (settings → tele → privacy → ghost)
- ghost a chat even when the global ghost switches are off, or keep a chat visible while they are on. (settings → tele → privacy → ghost → always ghost in / never ghost in)
- messages of ghosted chats go out as scheduled, so the server delivers them without marking you online, and tele goes offline again right after the send. (settings → tele → privacy → ghost → send messages as scheduled)
- the scheduled message shows up in the chat right away, before the server sends it. (settings → tele → privacy → ghost → show waiting messages in the chat)
- the ghost preview shows the read mark in the outgoing bubble instead of the word read, and the stealth icon sits on a circle. (settings → tele → privacy)
- incoming messages that match a word or a java regex are faded. (settings → tele → privacy → hidden words)
- the messages that match a word are hidden instead of faded. (settings → tele → privacy → hidden words → hide the messages completely)
- ignored people and hidden words stay quiet: no notification, no toast, no mention badge. (settings → tele → privacy → hidden words → mute ignored messages)
- briefly show the last seen of a peer that hides it, then restore your own rule. (settings → tele → privacy → peek at hidden last seen)
- block screen capture in every window and hide the sender and the message of the notifications. (settings → tele → privacy → streamer mode)
- the phone number is hidden in the chat header and in the profile while the streamer mode is on. (settings → tele → privacy → streamer mode)

#### links

- the rewrite shows a telegram bulletin with what changed instead of a toast, and every rewrite with a random target picks another one. (settings → tele → privacy → links)

### [tele 1 · 13.0.2](https://github.com/gettele/android/releases/tag/v13.0.2-tele.1)

#### tele

- a tele row in the main settings list opens the fork's own pages: interface, privacy, ids, sending, your data and server. (settings → tele)
- every page has its own icon row, and the main settings search finds every tele page and setting. (settings → tele, settings search)
- the chat list header says which tele build you're on instead of the telegram wordmark, and so does the version line in settings. (chat list header, settings → version)
- its own name, launcher icon (round and themed variants included), notification icon and settings icons, and the texts that name the app say tele. (launcher, settings)

#### interface

- message times show seconds, like 14:03:21. (settings → tele → interface)
- the all chats folder disappears from the folder tabs, the list opens on your first folder. (settings → tele → interface)
- no call buttons in private chats and profiles. (settings → tele → interface)
- starting a call asks first and names who you're calling. (settings → tele → interface)
- links open right away, without the "open this link?" box. (settings → tele → interface)
- people who aren't in your contacts keep their name in the chat header instead of their phone number. (settings → tele → interface)
- text and media spoilers are shown without a tap. (settings → tele → interface)
- hides the jump to mention and jump to reaction buttons in chats and the @ and reaction badges in the chat list. (settings → tele → interface)
- video userpics stay still. (settings → tele → interface)
- long-press a bot button to see what it carries (callback data, switch-inline query, web app url) and copy it. (settings → tele → interface)
- the tele server's checkmark and custom icon also show next to sender names in message bubbles. (settings → tele → interface)
- collectible username and number cards show their dollar price at the purchase date instead of today's. (settings → tele → interface)
- view as TL in the message menu and in the profile menu of users, groups and channels: fetches the object fresh from telegram and opens it on schema.jppgr.am in the browser. (settings → tele → interface)
- shot: save one message or a selection as a picture, over the chat background, at 1x to 4x. (message menu → shot, selection bar; settings → tele → interface)
- a one-tap eyedropper button by the palette in the photo editor picks the color from the picture with its strokes, stickers and text. (settings → tele → interface → editor)
- hide and reorder items of the message menu: drag a row by its handle, items the editor doesn't list stay after the others in stock order. (settings → tele → interface → message menu → editor)

#### privacy

- hides stories everywhere they show, and the share to story option. (settings → tele → privacy)
- watch stories without showing up among the viewers. (settings → tele → privacy)
- tele doesn't tell telegram you're online. (settings → tele → privacy)
- tele doesn't send typing actions. (settings → tele → privacy)
- opening a chat doesn't mark it as read for the other side. (settings → tele → privacy)
- playing voice and round messages or opening media doesn't send the viewed mark. (settings → tele → privacy)
- screenshots and screen recording work in the photo viewer, stories, secret chats, protected chats, voice once and on the passcode screen. (settings → tele → privacy)
- view-once and timed media can be screenshotted and recorded. (settings → tele → privacy)
- view-once and timed media open without burning, and the sender still sees them unopened. (settings → tele → privacy)
- message menu → mark as viewed burns a disappearing media you kept unopened. (message menu)
- drafts never go to the cloud. (settings → tele → privacy)
- inline bot results go out as your own messages, without via @bot. (settings → tele → privacy)
- no sponsored messages in channels and bots. (settings → tele → privacy)
- no sponsor channel pinned to the chat list when you connect through an mtproxy. (settings → tele → privacy)

#### links

- opened links lose their tracking parameters (utm, fbclid, gclid, si and more), by the same rules as the desktop link cleaner. (settings → tele → privacy → links)
- links in the messages you send are cleaned too, the rest of the text stays as it is. (settings → tele → privacy → links)
- links you paste are rewritten by your own rules, like x.com to fixupx.com. (settings → tele → privacy → links)
- an editor for the rules: domain rules (from to, www and m are kept, several targets are picked at random) and regex rules (find, replace with $1..$9), plus presets for x, instagram, tiktok, reddit, bluesky and pixiv. (settings → tele → privacy → links → rewrite rules)
- typed and pasted links get no preview, and the message is sent with no preview even from a draft. (settings → tele → privacy → links)
- choose when links get previews: for all links, not for pasted links, or only the ones you add. (settings → tele → privacy → links)
- with only the ones you add, the text selection menu of the field gets an add a link preview action for any link. (field selection menu)

#### ids

- a row with the id of the user, group or channel in its profile, tap it to copy. (settings → tele → ids)
- ids show as plain digits. (settings → tele → ids)
- ids in bot api style: -100… for channels and supergroups. (settings → tele → ids)
- a DC row in profiles: the data center the account or chat lives in, with its city. (settings → tele → ids)
- when both are shown, the dc goes next to the id in one row. (settings → tele → ids)
- the message menu starts with ID: N, tap to copy. (settings → tele → ids)
- a Gift ID row on the card of a collectible gift. (settings → tele → ids)
- regular gifts get the Gift ID row too, not only collectible ones. (settings → tele → ids)
- an open in see.tg link under the table of a collectible gift, which opens it in the see.tg mini app. (settings → tele → ids)
- long-press a custom emoji in a message to copy its id. (settings → tele → ids)

#### sending

- photos go out in hd unless you pick otherwise for a photo. (settings → tele → sending)
- photos and videos from the attach menu dock in a strip above the field instead of sending right away: remove one with ×, hide it with a spoiler, caption them in the field and send them as one album. (settings → tele → sending)
- tele sends your scheduled messages itself at the set time while it's open and online. (settings → tele → sending)
- messages sent while a media is uploading wait for it and go out after it, in order. (settings → tele → sending)
- replies to messages older than the uploading media don't wait in the queue. (settings → tele → sending)
- sending twice sends a queued message right away. (settings → tele → sending)
- business quick replies show in the / suggestions of groups and channels too, and are posted as ordinary messages (telegram only sends them in private chats). (settings → tele → sending)
- forward messages from chats that forbid it: tele sends fresh copies and uploads their media again. (settings → tele → sending)
- a message or caption that starts with = is computed with calcmula and sent as the quoted query with = result below it. (settings → tele → sending)
- the calcmula result shows in a card above the field while you type, tap it to send. (settings → tele → sending)

#### your data

- give people a name only you see: profile menu → set a name for me. (settings → tele → your data)
- your own @alias for any chat, in any letters, only for you: tapping an @alias opens the chat, typing @ suggests aliases first, and an alias in a sent message goes out as the real @username or a mention. (settings → tele → your data)
- chat search finds chats by their aliases, yours and the tele server's, and shows them as name @alias. (settings → tele → your data)
- @alias query asks the real bot. (settings → tele → your data)
- two lists, local names and aliases: tap to edit or delete, long-press to open the profile. (settings → tele → your data → manage)
- messages deleted by others or from your other devices stay in the chat, marked as deleted, and survive a restart. (settings → tele → your data)
- messages you delete yourself are kept too, not only ones deleted by others. (settings → tele → your data)
- kept deleted messages look faded, get a deleted label by the time, or a trash icon. (settings → tele → your data)
- a page listing the chats that have kept deleted messages, with their messages as full bubbles and a clear button. (settings → tele → your data → deleted messages)
- remembers what edited messages looked like: message menu → edit history opens every version as a full message in a chat-like page. (settings → tele → your data)
- when the message you're replying to gets deleted, the reply is dropped or quotes the deleted text. (settings → tele → your data)
- keep several drafts per chat with text, entities, reply, link preview and files: save as draft in the send button's menu or from the photo picker, and insert them later or send them to another chat from the drafts page. (send button menu, settings → tele → your data → saved drafts)

#### server

- checkmarks, custom verification icons, scam, fake and support marks from the tele server, drawn like telegram's own. (settings → tele → server)
- point tele at your own server, or leave the field empty to turn the server off. (settings → tele → server → server url)
- forgets the saved server data, badges included, and fetches it again. (settings → tele → server → clear cached data)
- tap a custom icon in a profile to see its description, which also replaces the bot verification line at the bottom of the profile. (profiles)
- the tele server can give accounts extra @usernames: they show in the usernames of profiles, open the real chat, and are offered in @ suggestions. (settings → tele → server)
- when tele crashed, the next start asks whether to send the report (version, build, device) to the tele server. (settings → tele → server)

#### updates

- checks the releases 15 seconds after start and every 3 hours, downloads the apk in the background, checks its sha256 and offers to install it with the system installer, which refuses an apk signed with another key. (settings → tele → update automatically)
- check now, or install a downloaded update, and see the update status. (settings → tele → check for updates)
- after an update, a local tele chat in the chat list tells you what's new, grouped by settings page, once for every account. (settings → tele → show what's new after updates, settings → tele → what's new)
- after an update, a new in tele row with a NEW badge lists the pages and settings that version added. (tele)

#### everywhere

- up to 8 accounts instead of 4.
- scheduled messages don't show a reply count.
- typing @username into the link box of the field turns it into a t.me link. (link box of the field)
- interface switches take effect without restarting the app.
