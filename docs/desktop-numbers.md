# Номера патчей десктопа: старые → текущие

[docs/PATCHLIST.md](PATCHLIST.md) и [docs/portability.md](portability.md) ведут патчи по **текущей** нумерации очереди [nitreojs/tele](https://github.com/nitreojs/tele) (`patches/tdesktop/NNNN-*.patch`, ветка `main`, патчи 0001–0322; отдельная очередь `lib_ui` — 0001–0008). Очередь десктопа была перенумерована: исходный разбор (v7.2.9, патчи 0001–0127) шёл по старым номерам. Ниже — полная карта старый → новый.

обозначения: `=` без изменений, `~` косметика (портировать нечего), `Δ` поведение изменилось, `⇢` влит в другой патч (отдельного номера в новой очереди нет). Влитые: старый 0043 → 0017, старый 0079 → 0077, старый 0118 → 0107.

| старый | новый | тема | класс |
|---|---|---|---|
| 0001 | 0001 | feat: show the tele build number in the title bar | = |
| 0002 | 0002 | feat: add a tele section to the settings | = |
| 0003 | 0003 | feat: add an option to hide stories everywhere | = |
| 0004 | 0004 | feat: add an option to watch stories invisibly | = |
| 0005 | 0005 | feat: show bot button payloads in tooltips | = |
| 0006 | 0006 | feat: update from the tele github releases | Δ |
| 0007 | 0007 | feat: rename the app to tele | = |
| 0008 | 0008 | feat: send quick replies in groups and channels | = |
| 0009 | 0009 | feat: apply verification and marks from the tele server | = |
| 0010 | 0010 | feat: make the title bar label a live template | = |
| 0011 | 0011 | feat: remove the account limit | = |
| 0012 | 0012 | feat: show checkmarks and custom verification everywhere | = |
| 0013 | 0013 | feat: show gift ids | = |
| 0014 | 0014 | feat: show the peer id as its own profile row | = |
| 0015 | 0015 | feat: copy links to tele settings | = |
| 0016 | 0016 | feat: ignore users by hiding or fading their messages | = |
| 0017 | 0017 | feat: show seconds in message times | Δ |
| 0018 | 0018 | feat: keep the edit history of messages | = |
| 0019 | 0019 | feat: keep deleted messages | ~ |
| 0020 | 0020 | fix: fade every unsupported experimental option | = |
| 0021 | 0021 | feat: hide call buttons | = |
| 0022 | 0022 | feat: lowercase every interface text | = |
| 0023 | 0023 | feat: show the data center in profiles | = |
| 0024 | 0024 | feat: hide sponsored messages | = |
| 0025 | 0025 | feat: open links without confirmation | = |
| 0026 | 0026 | feat: open disappearing media without burning it | = |
| 0027 | 0027 | feat: allow screenshots of disappearing media | = |
| 0028 | 0028 | feat: copy the callback data of bot buttons | = |
| 0029 | 0029 | feat: show the message id in the message menu | = |
| 0030 | 0030 | feat: hide the all chats folder | = |
| 0031 | 0031 | feat: jump to the first message of a chat | = |
| 0032 | 0032 | feat: add ghost mode | = |
| 0033 | 0033 | feat: view messages and telegram objects as tl | = |
| 0034 | 0034 | feat: hide the mtproxy sponsor channel | = |
| 0035 | 0035 | feat: lowercase tele's own texts too | = |
| 0036 | 0036 | fix: stop maximized windows jittering on monitors without a taskbar | ~ |
| 0037 | 0037 | feat: send crash reports to the tele server | = |
| 0038 | 0038 | feat: turn off animated userpics | = |
| 0039 | 0039 | feat: show what's new in tele after an update | = |
| 0040 | 0040 | feat: call the app tele everywhere | = |
| 0041 | 0041 | feat: customize the window title and format template values | = |
| 0042 | 0042 | feat: group and search tele settings | ~ |
| 0043 | 0017 (влит) | feat: show times on service messages | ⇢ |
| 0044 | 0043 | feat: upload media in several chats at once | = |
| 0045 | 0044 | feat: reply timestamps for media in rich messages | = |
| 0046 | 0045 | feat: compute messages starting with = via calcmula | = |
| 0047 | 0046 | feat: move show peer ids into tele settings | = |
| 0048 | 0047 | feat: show the tele build in the main menu | = |
| 0049 | 0048 | feat: open collectible gifts in see.tg | = |
| 0050 | 0049 | feat: move late-sent messages to the bottom | = |
| 0051 | 0050 | feat: queue messages behind an uploading media | = |
| 0052 | 0051 | feat: open links in their desktop apps | = |
| 0053 | 0052 | feat: clean tracking parameters from links | ~ |
| 0054 | 0053 | feat: reveal spoilers automatically | = |
| 0055 | 0054 | feat: move tele tools to the bottom of the message menu | = |
| 0056 | 0055 | feat: copy custom emoji ids from the message menu | = |
| 0057 | 0056 | fix: change the speed instead of moving the media viewer while holding | = |
| 0058 | 0057 | feat: reorder and hide message menu items | = |
| 0059 | 0058 | feat: keep messages you delete yourself | = |
| 0060 | 0059 | feat: show server and updates on the tele settings page | = |
| 0061 | 0060 | feat: pick brush colors from the image | = |
| 0062 | 0061 | feat: show edit history as a chat | = |
| 0063 | 0062 | feat: hide or confirm call and voice chat buttons | = |
| 0064 | 0063 | feat: group the tele interface and profile settings | = |
| 0065 | 0064 | feat: more ghost mode options | = |
| 0066 | 0065 | feat: show ids on regular gifts | = |
| 0067 | 0066 | feat: send inline results without via | = |
| 0068 | 0067 | feat: skip the rich message prompt on paste | = |
| 0069 | 0068 | feat: set or remove chat backgrounds only for you | = |
| 0070 | 0069 | feat: skip or quote deleted messages when replying | = |
| 0071 | 0070 | feat: add test server accounts with a plain right-click | = |
| 0072 | 0071 | feat: link usernames to profiles locally | = |
| 0073 | 0072 | feat: hide the mentions and reactions buttons | = |
| 0074 | 0073 | feat: pick ignored users and ghost chats like privacy exceptions | = |
| 0075 | 0074 | feat: show what's new in a local tele chat | = |
| 0076 | 0075 | feat: show names instead of phone numbers in chat headers | = |
| 0077 | 0076 | feat: open the emoji panel and attach menu by click only | = |
| 0078 | 0077 | feat: rewrite pasted links with your own rules | Δ |
| 0079 | 0077 (влит) | feat: edit link rewrite rules and presets | ⇢ |
| 0080 | 0078 | feat: name people only for you | = |
| 0081 | 0079 | feat: add launch flags to turn off tele's own network use | = |
| 0082 | 0080 | feat: preview calcmula results while typing | = |
| 0083 | 0081 | feat: clear server data and explain custom verifications | ~ |
| 0084 | 0082 | feat: move chats instantly in the chat list | = |
| 0085 | 0083 | feat: show collectible prices at the purchase date | = |
| 0086 | 0084 | feat: set your own app and tray icons | = |
| 0087 | 0085 | feat: choose when links get previews and set your own | = |
| 0088 | 0086 | feat: turn @username into a t.me link in the link box | ~ |
| 0089 | 0087 | feat: save messages as a picture | Δ |
| 0090 | 0088 | feat: debug logs and an mtproto inspector | ~ |
| 0091 | 0089 | feat: new tele app and tray icons | = |
| 0092 | 0090 | fix: name the item Copy Callback Data like telegram does | = |
| 0093 | 0091 | feat: usernames from the tele server | = |
| 0094 | 0092 | fix: open custom emoji in rich and emoji-only messages | Δ |
| 0095 | 0093 | feat: send gifs as videos and videos as gifs | Δ |
| 0096 | 0094 | feat: keep drafts on this device | = |
| 0097 | 0095 | feat: send scheduled messages on time | Δ |
| 0098 | 0096 | feat: show id and dc in one row | = |
| 0099 | 0097 | feat: redesign the title template editor | = |
| 0100 | 0098 | fix: ignore reply counters on scheduled messages | = |
| 0101 | 0099 | feat: save drafts for later | = |
| 0102 | 0100 | feat: send photos in hd by default | = |
| 0103 | 0101 | feat: find chats by their aliases | = |
| 0104 | 0102 | fix: show seen and reacted counts separately | = |
| 0105 | 0103 | feat: send an inline bot query as text | = |
| 0106 | 0104 | feat: choose which app opens each service | = |
| 0107 | 0105 | feat: scale shots up to 4x and show your messages as incoming | = |
| 0108 | 0106 | feat: export and import tele settings | = |
| 0109 | 0107 | feat: attach media above the field (beta) | Δ |
| 0110 | 0108 | fix: show server badges on the personal channel in profiles | = |
| 0111 | 0109 | fix: explain a missing changelog instead of doing nothing | = |
| 0112 | 0110 | feat: show new settings after an update | = |
| 0113 | 0111 | feat: never block screen capture | = |
| 0114 | 0112 | feat: choose what shots show | Δ |
| 0115 | 0113 | fix: trim settings descriptions | = |
| 0116 | 0114 | feat: forward protected messages as copies | ~ |
| 0117 | 0115 | fix: stop videos at their end | = |
| 0118 | 0107 (влит) | feat: caption docked media and bring it to parity with the send box | ⇢ |
| 0119 | 0116 | feat: hide settings until their parent is on | = |
| 0120 | 0117 | feat: hide communities | = |
| 0121 | 0118 | feat: send replies to older messages past the queue | = |
| 0122 | 0119 | feat: send right away on double enter | = |
| 0123 | 0120 | feat: regroup the sending settings | = |
| 0124 | 0121 | feat: use aliases for inline bots | = |
| 0125 | 0122 | feat: hide mention and reaction badges in the chat list | = |
| 0126 | 0123 | feat: pin chats past the limit | Δ |
| 0127 | 0124 | feat: folders past the limit | = |
