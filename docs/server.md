# tele server

tele can take extra account data from an optional server (settings → tele → server): checkmarks, custom verification, scam / fake / support marks, extra usernames, notices and crash reports. the server only ever sends one public feed; it never learns which accounts you look at. leave the server url empty to turn it off.

the app fetches `GET <server>/v1/badges` 10 seconds after start and every 10 minutes after that. "refresh now" fetches it immediately, "clear cached data" drops the saved copy and fetches it again. a `304 Not Modified` keeps the current feed. the feed is cached per url in `tele_badges.json`; a different url starts from an empty cache.

## what the server gives

- **badges** — a checkmark, a custom emoji icon, a description, and the scam, fake and support marks on users and channels. the feed keys are argon2 hashes, so the list does not contain account ids.
- **usernames** — extra public @aliases for accounts, shown next to their real usernames and resolved to the real account. the mapping is plain text because usernames are public.
- **notices** — entries with a title, formatted text, a photo, buttons and a toast, shown in the notification centre.
- **crash reports** — the app offers to send a crash report on the next start; the server can accept it and forward it to a Telegram chat.

## running your own server

the reference server is the `tele-server` checkout next to this repository: Node 22, Fastify and PostgreSQL, with a Docker image and an admin API. it is a separate repository and is not shipped inside this one.

### 1. configure

```bash
cd ../tele-server
cp .env.example .env
```

put secrets and ports into `.env`:

| variable | what it is |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | the database container; use a random password |
| `HOST_PORT` | the local port of the server, default `10200` |
| `POSTGRES_HOST_PORT` | the local port of postgres, default `10201`; never expose it publicly |
| `BADGES_SECRET` | the secret the feed salt is derived from; random, never public. rotating it invalidates old keys |
| `ARGON2_MEMORY`, `ARGON2_PASSES`, `ARGON2_LANES` | argon2id costs; the defaults `8192 / 1 / 1` are what the client expects |
| `ADMIN_TOKEN` | 32+ random characters; enables `/v1/admin`. keep it private |
| `CRASH_NOTIFY_BOT_TOKEN` | optional bot token; enables `/v1/crash.php` and forwards reports to a chat |
| `CRASH_NOTIFY_CHAT_ID` | the chat that receives crash reports |
| `CRASH_DAILY_LIMIT` | the daily cap for crash reports, default `200` |

`BADGES_SECRET` is the one value you cannot lose: changing it changes every key in the feed, so every badge has to be recomputed. back up `.env` and the postgres volume.

### 2. run

```bash
docker compose up -d --build
```

the entrypoint applies the drizzle migrations, then starts the server. check it:

```bash
curl -s http://127.0.0.1:10200/v1/badges
```

it must answer with json containing `salt`, `argon2` and `peers`.

### 3. put it behind tls

the app only accepts `https://` urls, except `http://localhost` and `http://127.0.0.1` for development. expose only the reverse proxy, not the app or postgres ports. a caddy example:

```
tele.example.com {
    reverse_proxy 127.0.0.1:10200
}
```

then set settings → tele → server → server url to `https://tele.example.com` and tap refresh now. the url must have no query, fragment or user info; trailing slashes are ignored.

### 4. add badges and usernames

with `ADMIN_TOKEN` set, the server has an admin api under `/v1/admin`. every request needs `Authorization: Bearer <token>`.

```bash
# a checkmark with a custom icon and a description for user 777000
curl -X PATCH https://tele.example.com/v1/admin/badges/prod/777000 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"checkmark":true,"icon":"5368324170671202286","description":"official"}'

# the extra @tele username for @teleAppUpdates
curl -X PUT https://tele.example.com/v1/admin/usernames/tele \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"username":"teleAppUpdates","position":0}'

# recent crash reports
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  'https://tele.example.com/v1/admin/crashes?limit=20'
```

badge paths take `prod` or `test` (accounts on Telegram's test servers) and the bot-api peer id: `777000` for a user, `-1001234567890` for a channel or supergroup. basic groups cannot have entries. bad values are rejected by the admin api.

## the feed

the full format of `GET /v1/badges`:

```json
{
  "salt": "AAECAwQFBgcICQoLDA0ODw==",
  "argon2": { "memory": 8192, "passes": 1, "lanes": 1 },
  "peers": {
    "iguxbtP_SnLvK69aBff2OQ": { "checkmark": true, "icon": "5368324170671202286", "description": "official" },
    "w5Zbi-HfwlqkJ6S4wjwqcw": { "scam": true }
  },
  "usernames": {
    "tele": { "username": "teleAppUpdates", "position": 0 }
  },
  "notices": []
}
```

- `salt` is 8 to 64 random bytes in standard base64 with padding.
- `argon2` is the argon2id cost: `memory` in KiB (1024 to 65536), `passes` (1 to 8), `lanes` (1 to 8), `memory × passes` at most 65536.
- a `peers` key is `base64url` without padding of a 16-byte argon2id tag, version `0x13`, of the password `<scope>:<id>`. `scope` is `prod` or `test`; `id` is the bot-api id (`777000`, `-1001234567890`).
- every peer field is optional: `checkmark`, `scam`, `fake`, `support` are booleans, `icon` is a custom emoji document id as a decimal string, `description` is plain text shown with the icon, and `supportText` (up to 64 characters) replaces “support” under the name.
- `usernames` maps an extra alias (2 to 32 latin letters, digits and underscores) to the real username (4 to 32 of them) and an optional position. both start with a letter and are compared ignoring case. a position past the end puts the alias last; without one it goes after the real usernames. test accounts ignore this section.
- `notices` is optional; [notices](#notices) describes it.
- the whole feed is limited to 4 MiB and 100000 entries. unknown fields are ignored, but a known field with the wrong type or length can reject the feed.

### checking your keys

with the salt from the example, `prod:777000` must produce `iguxbtP_SnLvK69aBff2OQ`:

```python
from argon2.low_level import hash_secret_raw, Type
import base64

raw = hash_secret_raw(b"prod:777000", bytes(range(16)), time_cost=1,
                      memory_cost=8192, parallelism=1, hash_len=16,
                      type=Type.ID, version=0x13)
print(base64.urlsafe_b64encode(raw).rstrip(b"=").decode())
```

serve the keys sorted and rotate the salt regularly, so feeds from different times cannot be compared key by key. keep the argon2 costs within the limits: the app computes one key per shown account and refuses a feed that asks for more.

### etag

the app sends `If-None-Match: "<sha256 of the body it has>"`. answer `304` when it matches the current body; tele then keeps using the cached feed. a server cannot tag clients with its own etag.

## usernames

```json
"usernames": {
  "tele": { "username": "teleAppUpdates", "position": 0 },
  "teleNews": { "username": "teleAppUpdates" }
}
```

with settings → tele → server → usernames from the server on (the default), a profile shows the extra aliases after the real ones, or at the requested position. `@tele`, `t.me/tele` and `tg://resolve?domain=tele` open the real account; in a message you send, `@tele` becomes the real `@teleAppUpdates`. your own local aliases take precedence.

the app skips a bad alias on its own and keeps the rest: a wrong name, an alias equal to the target, or the same alias in different case. only the first 1000 entries count. `usernames` never rejects the feed, but `salt`, `argon2` and `peers` are required.

## notices

`notices` is an array on the same feed. the app keeps up to 64 notices and writes them to the notification centre for every account that matches the filters.

```json
"notices": [{
  "id": "tele-14",
  "rev": 0,
  "type": "info",
  "title": "tele 14 is out",
  "text": "update from settings",
  "entities": [{ "type": "bold", "offset": 0, "length": 6 }],
  "photo": { "url": "/v1/notices/tele-14/photo?rev=0", "width": 1280, "height": 720 },
  "buttons": [{ "text": "release notes", "url": "https://github.com/nitreojs/tele/releases" }],
  "toast": true,
  "builds": { "min": 13, "max": null },
  "platforms": ["android"],
  "users": null,
  "from": 1791000000,
  "until": 1792000000
}]
```

- `id` is 1 to 64 latin letters, digits and dashes. bump `rev` when you edit a notice: the app replaces the entry in the centre, but toasts each id once.
- `type` is `info`, `success`, `warning` or `critical`; it picks the toast colour. `toast: true` also shows a toast, otherwise the notice only goes to the centre.
- `title` or `text` must not be empty. `text` is cut at 4096 characters and `entities` at 256; entities use utf-16 offsets like the bot api. `photo.url` is relative to the server and serves a jpeg or png up to 1 MiB. up to two buttons are allowed, with `http://`, `https://` or `tg://` urls.
- `builds.min` and `builds.max` are tele build numbers, not the Telegram version. `platforms` is optional; include `android` for this client. `users` is an array of peer keys made exactly like the `peers` keys, or `null` for everyone. `from` and `until` are unix seconds.
- the bundled `tele-server` at this commit serves badges and usernames; to use notices, add the top-level `notices` array to its `/v1/badges` response. invalid notices are skipped individually.

## crash reports

the Android client does not use Telegram's minidump protocol. it writes a text report, asks on the next start, and sends it only after a tap. the request is:

```text
POST <server>/v1/crash.php?act=report
content-type: multipart/form-data

platform = Android
version  = <android versionCode>
report   = report.txt (text/plain)
```

the report starts with:

```text
platform: Android
Version: 13.1.1 (7237)
tele: 49
Device: <manufacturer> <model>, android <release> (sdk <sdk>)
memory: java <used>/<max> MB, native <native> MB, pss <pss> MB
thread: <thread>
report:
<stack trace>
```

answer `200` with `Done` or `Done <id>`. tele shows “crash report sent” and the notification centre shows the id. the app does not send a minidump; an out-of-memory heap snapshot is a separate file that the user shares by hand through the system chooser and the server never receives it automatically. it does not call `query_report` and does not send `dump`; implement `GET` only if you also support other clients.

if the server is empty or `send crash reports` is off, nothing is offered. the tele-server keeps a daily limit and a per-ip hourly limit; tune `CRASH_DAILY_LIMIT` and use a bot that can post to the target chat.

## privacy

- the server never learns which peers you look at: the feed contains public hashed keys and the app matches them locally. usernames are public and intentionally plain text.
- do not put ids, usernames, contacts or messages into the feed or into notices. a crash report is the only thing that comes from the user, and only after the user taps send; the report shows what it contains first and lets the user untick their username.
- serve the server over https, keep postgres and the admin api off the public internet, and never commit `.env`.
- rotate `BADGES_SECRET` from time to time; the official server derives a new salt every month. every key is recomputed from the new salt.
- back up the postgres volume and `.env`: losing `BADGES_SECRET` means recomputing the entire feed, losing the database means losing the entries.

## troubleshooting

| symptom | check |
|---|---|
| the app says the url is invalid | use `https://`, no query, fragment or user info; only `localhost` and `127.0.0.1` may use http |
| badges do not change | refresh now; check the feed etag and the 10-minute cache; clear cached data drops the saved feed |
| the feed is rejected | json, salt size, argon2 limits, peer key size and field types; the whole feed is rejected on a bad known field |
| `304` every time | the server hashes the body it sends; compare `If-None-Match` with the current body |
| crash reports are not offered | `send crash reports` on, server url set, and a pending report; the app writes it only when both are true |
| crash reports are refused | the tele-server requires platform `Android`, a numeric version and a non-empty `report`; check the bot token and daily limit |
| notices do not appear | notification centre on, `notifications from the server` on, `platforms` contains `android`, `builds` and `until` match, and the feed actually has `notices` |
