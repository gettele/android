# Пачка 29 — HTML-пузыри `.tgw`

## Назначение и границы

1. Этот документ — implementation guide для строк пачки 29 в `docs/PATCHLIST.md`.
2. Desktop numbers 0312 и 0313 означают позиции текущей очереди tele, не будущие номера Android patch-файлов.
3. Реализация идёт в соседнем Telegram checkout на ветке `tele`; здесь создаётся только этот guide.
4. Не коммитить из этого задания и не менять другие файлы.
5. После выполнения реальной реализации экспортировать commits штатным `git format-patch`, не редактируя `.patch` вручную.
6. Цель — отображать локально HTML карточки в Telegram `.tgw` attachment и дать пользователю локальную playground-песочницу.
7. Решение мейнтейнера: портировать подсистему 0312–0313 (playground-чат влит в 0313), использовать litehtml через NDK, не WebView в пузыре.
8. 0313 исполняет сценарий карточки в QuickJS; базовый QuickJS runtime принадлежит desktop 0302 и пачке Android 28.
9. Playground-часть 0313 опирается на карточки 0313 и использует локальный чат как носитель, аналог Android 0077.
10. Desktop Qt/C++ implementation — описание поведения и формата, не исходник для механического Android копирования.
11. Android UI и Android Canvas остаются нативными; C++ renderer работает через JNI и получает только ограниченный drawing surface.
12. Не включать WebView, remote HTML, произвольные сетевые картинки, tele-server APIs, wallet/script APIs либо Qt UI в эту пачку.
13. Не добавлять новые серверные TL-конструкторы и не редактировать `TLRPC.java`.
14. Не менять stock DB schema, `LAST_DB_VERSION`, обычный рендер файлов и stock message serialization.
15. Не изменять состояние `.tgw` сообщения на сервере при отображении или sandbox-тесте.
16. Feature остается debug-only и OFF по описанию desktop; Android правило — новые тумблеры default false.
17. При OFF все сообщения и `.tgw` файлы обязаны вести себя как stock Android.
18. Настройки, search IDs, экспорт и `features.md` подчиняются `AGENTS.md`.
19. Только UI thread трогает View/Canvas; file IO, HTML parsing и layout вне UI thread.
20. Ни один parser/runtime crash не должен ломать RecyclerView bind/draw или приложение.
21. Не утверждать, что безопасность обеспечена только тем, что renderer не использует WebView.
22. Отдельно ограничить входные данные, DOM, картинки, script CPU/memory, callbacks и JNI allocations.

## Источники и установленная доказательная база

23. Прочитаны `AGENTS.md`, `PATCHLIST.md`, `decisions.md`, `portability.md`, `desktop-numbers.md`, `architecture.md` и `development.md`.
24. Прочитан `local://desk-5.md`, оценка desktop 0285–0317 и патчи origin/main.
25. Desktop `origin/main:patches/tdesktop/0312-build-fetch-litehtml-for-html-bubbles.patch` вендорит litehtml revision `8848b99b1fae17026117c45c3ec9cd3e38b2e511`, SHA256 `42b8c62384f2e0383a1490c9b7688ebca4d296c9f36614583b89ef291ff75aa4`.
26. Desktop 0312 делает отдельные static targets `tele_gumbo` и `tele_litehtml`, C99 для gumbo и C++17 для litehtml.
27. Desktop 0312 добавляет собственный patch litehtml для parsed/shared CSS; Android должен проверить, требуется ли этот API текущему renderer.
28. Desktop `0313` добавляет `tele_html.cpp` (1310 строк), `tele_html_script.cpp` (698 строк), заголовки и связь с litehtml + QuickJS.
29. Desktop 0313 содержит Canvas-like backend для Qt painter, CSS light-dark conversion, fonts, data images, SVG/raster decoding и HTML/CSS layout.
30. Desktop source constants включают font size 14, максимум 64 images, 4 MiB image bytes, 4096 px сторона/pixel bound, depth 256, 5000 elements, 48 MiB document pixels.
31. Desktop source устанавливает ограничения и на SVG external references; Android обязан повторить сетевой запрет своей backend реализацией.
32. Desktop `0313` добавляет HTML media/cards, playground peer/chat, sample cards, settings toggle, help/menus и changelog chat integration (прежняя отдельная строка 0316 влита в 0313). Десктопный фикс 0321 (html-карточки не падают, когда сообщение исчезает) учесть в интеграции с `ChatMessageCell`.
33. Desktop playground имеет reset/read affordances; это локальный псевдо-чат, не Telegram remote peer.
34. PATCHLIST описывает batch 29 effort `M×1, L×1` (0312 — M, 0313 — L с playground), deps 0302, 0312 и Android 0077.
35. `decisions.md` прямо выбирает litehtml NDK rendering для `.tgw`.
36. `portability.md` уточняет Canvas JNI backend, QuickJS scripts и зависимость playground от Android 0077.
37. Android checkout branch `tele` использует `TMessagesProj/jni/CMakeLists.txt`; Android.mk по указанному пути отсутствует.
38. Android native CMake уже задаёт C++17 и ABI-specific build, visibility hidden, LTO и target-based compilation.
39. Android project builds ABI splits; `development.md` фиксирует NDK `27.2.12479018`, CMake `3.22.1` и SDK 36.
40. Нынешний Android `ChatMessageCell.java`, `TeleConfig.kt`, `TeleSearch.kt` и settings infrastructure существуют в branch tele.
41. Android 0077 уже хранит локальные changelog сообщения в Tele DB и рисует их `ChatMessageCell` в `TeleChatActivity`.
42. Android 0077 показывает, что fork-local chat pattern возможен; это не подтверждает, что вся desktop playground UX уже имеет Android аналог.
43. [INFERENCE] Полный точный формат `.tgw` (manifest, mime, attachment fields, HTML/script extraction order) определяется desktop источником, но PATCHLIST и короткий `desk-5` excerpt не фиксируют его спецификацию.
44. Перед кодом открыть соответствующие полные функции/поля в desktop 0313 и составить byte-level format contract; не угадывать формат из extension.
45. [INFERENCE] Android branch current `Document` file_name availability needs re-check through exact current `MessageObject.getDocument()` and mime metadata before implementation.
46. Search IDs `1460..1479` — плановый блок данной пачки, но до реализации проверить реестр `TeleSearch` и stock collision.
47. Search IDs — локальные navigation identifiers, не Telegram dialog IDs и никогда не отправляются в сеть.
48. PATCHLIST status remains `todo` until patch commit/export, assembled debug APK and human manual gate.

## Коммиты и зависимости

49. Один desktop feature = один Android commit, с минимальными stock hunks и fork logic в `tele/`.
50. Рекомендуемый commit 1: desktop 0312, `build: vendor litehtml for android`.
51. Он добавляет pinned source, license/upstream manifest, CMake target и ABI build integration, без parser/UI behavior.
52. Рекомендуемый commit 2: desktop 0313, `feat: render tgw html cards`.
53. Он зависит от batch 28 Android 0302 QuickJS runtime и commit 0312 litehtml.
54. При отсутствии готового 0302 runtime остановиться на dependency: не подменять QuickJS WebView, fake executor или no-op script.
55. 0313 содержит format reader, policy checks, JS bridge, litehtml document container, Canvas JNI adapter, size/measure/render cache и gated ChatMessageCell hook.
56. Рекомендуемый commit 3 (playground-часть 0313): `feat: add html playground chat`.
57. Он зависит от 0313 и Android 0077 `TeleChat`/локальных сообщений, не от network chat implementation.
58. Каждый commit должен собираться отдельно поверх предыдущего commit в очереди.
59. Если конкретные CMake integration changes требуют правки native build root, включить их в 0312, не растягивать JNI setup в несвязанные commits.
60. Если 0302 export/runtime interfaces пока не стабилизированы, согласовать интерфейс с пачкой 28 перед 0313; не добавлять speculative public JS API.
61. Playground-чат не должен переписывать или ломать обычный changelog chat Android 0077; выделить отдельный peer identity and routing.
62. Не объединять litehtml 0312 и 0313 в один commit: PATCHLIST перечисляет две строки (0312, 0313) с явными зависимостями; внутри 0313 playground — отдельный commit после карточек.
63. Изменения `features.md` добавлять при экспорте каждой user-facing feature в соответствующий commit.
64. `PATCHLIST.md` статусы обновляются только по фактической фазе (wip/queued/built/done).
65. В этом guide список commit subjects — рекомендации; подтверждённый repo format `feat:`/`build:` согласовать с AGENTS commit conventions.

## Настройки, переключатель и search IDs

66. Один общий master toggle управляет parsing/rendering HTML cards and playground, если desktop 0313 показывает единый `html_bubbles` option.
67. Desktop 0313 adds `kOptionHtmlBubbles`; setting is listed in Debug, search keywords include html, tgw, widget, card, playground.
68. Android config recommendation: `TeleConfig.HTML_BUBBLES = BoolItem("html_bubbles", false)`.
69. [INFERENCE] Android key and property spelling are proposed from desktop option semantics; inspect 0302/other current `TeleConfig` before implementation.
70. Default MUST be false; OFF bypasses parser, renderer, script startup, synthetic chat routing and extra measurement.
71. Add settings row in current Debug page unless current settings refactor has moved the feature to another page.
72. This is an experimental/debug surface; describe clearly that `.tgw` executes local card scripts and is disabled by default.
73. Add export/import spec for actual config item; do not add duplicate key for playground sub-toggle absent a confirmed independent desktop control.
74. Keep the single master toggle canonical; search aliases and help entries must route to it rather than duplicating config.
75. Search IDs planned 1460..1479. Verify all 20 IDs are free and reserved in current `TeleSearch` before use.
76. 1460 canonical setting `HTML_BUBBLES`, page debug; keywords `html`, `html bubbles`, `tgw`, `card`, `карточка`, `html-пузырь`.
77. 1461 alias “.tgw files”, keywords `tgw`, `file`, `attachment`, `файл`, `.tgw`.
78. 1462 alias “HTML playground”, keywords `playground`, `sandbox`, `test card`, `песочница`, `игровой чат`.
79. 1463 help row: local-only rendering and default-off warning; no new TeleConfig item.
80. 1464 help row: script capability/safety explanation and stop/reset affordance; no new TeleConfig item.
81. 1465–1479 remain reserved for approved aliases, not speculative settings.
82. If one search record is not needed, leave the numeric hole unused; never fill with unrelated setting.
83. Search entries use existing `TeleSearch` registry, titles, description, page route and bilingual keywords where API supports them.
84. Add row ID(s) to `TeleSettingsActivity.settingIds()` so new-settings system sees user-facing feature.
85. Config-change notification should invalidate visible cards and playground on UI thread; switching off must immediately suppress dynamic scripts and prevent future callbacks.
86. Turn-off behavior must stop JS runtimes, clear listeners and prevent stale render results from being installed.
87. Already downloaded `.tgw` files remain ordinary downloadable documents; the toggle changes presentation only.
88. Search IDs are independent of `TeleConfig` key and not exported as user settings.

## `.tgw` format, detection and trust boundary

89. `.tgw` is a tele-specific document format; ordinary Android clients should continue to see it as a file/document.
90. Detect only the exact supported extension and verified document metadata; no HTML sniffing on arbitrary media.
91. Extension matching SHOULD be case-insensitive after extracting basename, while preserving the original filename for display.
92. [INFERENCE] Whether MIME type is `application/x-tele-widget` or another value is not evidenced; use the exact desktop source contract and tolerate only explicitly documented legacy MIME.
93. Never treat plain text messages or arbitrary downloaded `.html`/`.htm` documents as `.tgw` cards.
94. The message's document and local path can be nullable, unavailable, remote or currently downloading; defer card rendering until safe local bytes exist.
95. Validate file identity via `MessageObject`/document fields, not user-controlled display caption.
96. Treat every attachment byte, HTML, CSS, script, URL, image and metadata value as attacker-controlled, even if sender is trusted.
97. HTML card content must render locally; no web server and no remote browser session.
98. Asset loading may read only the `.tgw` package contents and explicit safe application assets; must not resolve arbitrary filesystem paths.
99. No external HTTP/HTTPS request from litehtml image/css callbacks.
100. QuickJS API available to card is not unrestricted Android bridge: only the desktop-defined card API subset and granted capabilities.
101. Do not provide `window`, DOM, Java reflection, ClassLoader, raw JNI pointers, `file://`, content URIs or process access.
102. Make link handling inert by default or route an explicit user tap through existing Telegram link confirmation/policy; no auto-navigation on parse/render.
103. No HTML form submission, downloads, intents, clipboard writes, contact/message reads or Telegram API calls unless explicitly part of approved desktop card contract and separately authorized.
104. Card JS should not make network requests unless an explicit feature/grant exists; this batch should not silently inherit general scripting fetch grants.
105. [INFERENCE] Safest initial accepted card package is self-contained HTML/CSS/JS/data with inline data assets; verify against desktop 0313 packaging and samples before fixing this as contract.
106. If package is archive/container, cap compressed and decompressed bytes, entry count and path depth; reject absolute paths, traversal, symlinks and duplicate normalized paths.
107. Reject unsupported archive encodings, encrypted archives and nested archives rather than attempting recovery.
108. If `.tgw` is a raw HTML source instead of archive, validate its source size before UTF-8 decoding, then parse under limits.
109. The exact packaging decision is a blocker to implementation details, not an excuse to skip security limits.
110. UTF-8 decoding must be bounded and deterministic; malformed sequences should yield controlled invalid-card fallback, not memory corruption.
111. Limit entity expansion and do not implement custom XML entity fetching.
112. HTML is not Android WebView DOM; litehtml parses layout and inert semantics, while QuickJS is an isolated script engine.
113. Card state and script context key must include account, message/document identity and runtime generation.
114. Avoid storing full HTML or script body in logs, crash messages, telemetry, clipboard, notifications or tele-server.
115. Never upload message text, sender identity, `.tgw` bytes or rendered pixels to tele-server.
116. No third-party network access is introduced by this renderer.

## HTML/CSS parser and allowlist

117. Use pinned litehtml/gumbo sources as local vendored third-party code; no `FetchContent` network download during configure/build.
118. Pin exact upstream commit/revision and content hash, record license and any local patch in a source manifest or commit body.
119. Review upstream license and notices before vendoring, preserve notices, do not strip copyright.
120. Keep upstream changes isolated from `tele/html` backend and JNI wrapper.
121. Prefer supported litehtml parsing hooks; do not patch stock Telegram parser or generated code.
122. Apply an explicit HTML element/attribute policy at the container or preprocess stage; do not assume browser-like behavior is safe.
123. Allow only markup necessary for the desktop card format; document all accepted elements and attributes in code structure/tests.
124. Reject or inert `script` nodes in litehtml DOM and hand approved script source to QuickJS through a separate bounded extractor.
125. Block `iframe`, `object`, `embed`, plugin, forms, meta refresh, base URL, navigation and foreign object unless desktop contract explicitly requires safe equivalent.
126. Strip event-handler attributes (`on*`) from HTML before any card rendering; script execution must use explicit card script path only.
127. Disallow `javascript:`, `file:`, `content:`, `intent:`, `data:` navigation links.
128. Handle `data:` only as bounded image data if the desktop card contract permits it; validate media type and decoded size before allocation.
129. Reject CSS `@import`, external `url()`, fonts from remote sources and CSS expressions/legacy active content.
130. CSS `url()` resolution must map only to validated package-relative local assets or bounded inline image data.
131. Canonicalize every package-relative path and reject `..`, encoded traversal, absolute path, drive prefix, NUL and backslash ambiguity.
132. Image callbacks must never open a path supplied directly to `File` or `ImageDecoder` without an approved package resolver.
133. Deny SVG external entities, external `href`, remote `<image>`, script, foreignObject and linked stylesheets.
134. SVG should be accepted only if a bounded, audited rasterizer path exists; otherwise render controlled placeholder, not WebView fallback.
135. The desktop renderer uses CSS light-dark replacement; port only the intended supported syntax and test nested parentheses/comma parsing.
136. Avoid regex-only HTML sanitization; parser-aware allowlisting and URI validation are required.
137. Bound input before parser invocation; also bound actual parsed node count/depth because byte size alone does not constrain tree amplification.
138. A parser exception/failure produces a safe ordinary attachment row or fixed “unsupported card” placeholder.
139. Error UI must not include raw HTML, scripts, filesystem paths, stack traces or attacker-provided strings without escaping.
140. Color values, font sizes, dimensions and CSS lengths must be clamped before conversion to Android/native pixel integers.
141. Prevent integer overflow in width/height/pixel arithmetic and JNI length conversions.
142. Do not allow CSS to request unbounded intrinsic dimensions or allocate a surface before hard checks.
143. Resource load errors should be local placeholders; never fall through to network.
144. Maintain a documented allowlist/version so a future format expansion receives explicit security review.

## litehtml Canvas/Bitmap backend and JNI

145. Implement Android document container in new fork native sources under `TMessagesProj/jni/tele_html/` or the established `tele` native subtree.
146. Add a `tele_litehtml` static target and, if required by pinned litehtml revision, separate `tele_gumbo` static target.
147. Use target-local include directories/compile flags; do not globally change Telegram C/C++ flags to satisfy litehtml.
148. Compile litehtml as C++17, gumbo as C99, aligning with upstream's current 0312 source contract.
149. Link targets into the existing native library only after confirming Java loader and JNI registration path; avoid a second `.so` without packaging rationale.
150. Follow existing Android CMake conventions and `RegisterNatives` pattern; use hidden visibility and export only necessary JNI entry points.
151. Build the static libraries for every configured ABI, not only the development machine's architecture.
152. Implement JNI bridge in Java/Kotlin native declaration layer plus C++ registration; keep signatures narrow and typed.
153. JNI receives HTML/card bytes, viewport width, theme/font metrics and output Bitmap target or drawing command result; no Java object graph crossing into C++.
154. [INFERENCE] Direct drawing into Android `Canvas` is not available to native litehtml without a carefully designed JNI-backed painter; choose either native raster `Bitmap` or bounded drawing-command backend after measuring cost.
155. If using Android Bitmap pixels, validate config, dimensions, row stride and byte count; lock/unlock pixels in RAII scope and always unlock after native errors.
156. Prefer premultiplied ARGB_8888 for Android Canvas compatibility; verify alpha compositing at translucent edges.
157. Native code must not retain a `JNIEnv*`, local ref, Bitmap pointer or byte-array pointer beyond the call.
158. Global refs, if unavoidable, require explicit owner and release at renderer destruction.
159. Never throw C++ exception across JNI; translate parse/layout failures to bounded error status and fallback path.
160. Check JNI exception after Java callbacks and clear only exceptions owned by bridge code.
161. Keep all UI View access on main thread; JNI layout/raster can execute on worker thread only over immutable snapshot/input.
162. Every card request and callback carries `currentAccount`, message identity and generation; reject stale result after rebind/account change/feature disable.
163. Callbacks cannot mutate `ChatMessageCell` directly from worker; dispatch to main and recheck bound message key.
164. Avoid calling Java image/font resolver repeatedly per CSS token; pre-resolve bounded resource table where possible.
165. Native allocation failures and litehtml assertions must be contained; no native abort on untrusted input.
166. Add deterministic destroy/free path for document, container, image handles, font handles, JS runtime references and pending callbacks.
167. CMake source set and vendored library must not trigger network fetch during Gradle configure; source must be checked in.
168. ABI-specific prebuilt libraries are not substitutes for source compilation unless provenance and reproducibility are explicitly approved.
169. Strip unused litehtml features only if the resulting behavior still satisfies the supported `.tgw` contract.
170. Keep diagnostics non-sensitive: account index and error category are acceptable; message text and document bytes are not.

## Fonts, images, theme and layout

171. Backend font resolver maps requested CSS families to approved Android/system fonts, never opens arbitrary paths.
172. Use Android font metrics consistently across measurement and drawing; cache metrics by resolved family, weight, style and density.
173. Define default CSS font size based on desktop 14 px reference while converting CSS px to device-independent pixel policy deliberately.
174. [INFERENCE] A 14 CSS px desktop value is not automatically 14 Android dp; choose scaling that respects density, user font scale and bubble readability.
175. Avoid silently scaling all card CSS with Android system font scale if it breaks authored geometry; accessibility review should define text scaling behavior.
176. At minimum, user accessibility font scale must not make text clipped or unreachable; test minimum/maximum supported scale.
177. Resolve foreground/background colors through theme-aware palette, including dark/light behavior and `light-dark()` where supported.
178. On theme switch, invalidate color/render cache and rerender without restarting the app.
179. No card can draw outside its measured bounds or over neighboring bubble content.
180. Layout width is the actual available message content width after ChatMessageCell paddings, reply/forward headers and media constraints.
181. Card layout height is computed from litehtml under a fixed clamped width and capped maximum height.
182. Long cards must clip/scroll through an explicit container or show a bounded preview; do not allocate a bitmap taller than the document limit.
183. [INFERENCE] Desktop card UX may support a “show more” expansion; confirm from source before implementing Android expansion.
184. If no expansion contract exists, select a deterministic truncation/height policy and expose accessible open/expand action only after approval.
185. Line wrapping must handle CJK, emoji, bidi text and unbreakable URLs without escaping bubble bounds.
186. RTL layout must be tested with mixed Arabic/Hebrew and Latin text; ensure Canvas text alignment and hit regions agree.
187. Image loader supports only reviewed raster types and optional safe SVG policy; cap decoded bounds before rasterization.
188. Enforce both encoded image byte and decoded pixel limits; compressed tiny image can expand to huge allocation.
189. Desktop reference: at most 64 images, 4 MiB encoded image bytes, 4096 px max side and 4096² pixels per image.
190. Desktop reference: max total rendered document pixels 48 Mi pixels; additionally cap Android peak bitmap memory across in-flight cards.
191. [INFERENCE] Android per-card max height and aggregate visible-card bitmap budget need device measurements; keep them centralized and below desktop-only allowance when necessary.
192. Use downsampling before bitmap allocation when source dimensions exceed allowed side/pixel budget.
193. Avoid duplicating decoded image bytes; release temporary arrays after bitmap/cache transfer.
194. Decide image cache ownership: per card, process LRU or shared immutable asset cache; keys must include source hash and theme if output is theme-dependent.
195. Cache should not retain large bitmap references after message leaves visible/recyclable lifecycle.
196. Support card image placeholders/loading state without flicker and without calling storage IO during `draw`.
197. Keep image resolution on bounded IO executor and bitmap decode on bounded worker queue; no unbounded task-per-cell creation.
198. Native render should be deterministic for same HTML, style, width, theme and font configuration.
199. Avoid repeated full DOM parse on scroll/bind; parse once per immutable input identity, measure/cache by viewport and style revision.
200. Cache invalidation triggers include source revision, available width, density/font configuration, theme, locale/direction and card setting.
201. Any cache keyed by account or message must include account identity; do not mix cache content across accounts.
202. Never cache failures as successful blank cards; permit retry on file availability/update with bounded backoff or lifecycle event.

## QuickJS card scripts

203. Reuse the batch 28 QuickJS runtime; do not instantiate an independent unsynchronized engine or vendor duplicate QuickJS.
204. Add a narrow HTML-card module/runtime API only after 0302 public contracts are stable.
205. Each card script runs in its own isolated context, associated with account and message/card identity.
206. Do not share mutable JS global state across cards, scripts or accounts.
207. Card script should produce explicit state/data to renderer; it must not construct Android Views or call Canvas directly.
208. Keep renderer output data-only and validated; HTML layout does not gain additional capabilities from JS.
209. Execution, initialization and event callbacks must run off main thread and off Telegram networking/storage critical queues.
210. Use QuickJS instruction interrupt/deadline, memory cap and bounded recursion from batch 28 policy.
211. [INFERENCE] Desktop 0313 exact JS timeout and memory budget are not established by PATCHLIST/local note; align with batch 28 runtime constants and document Android cap.
212. Never allow script infinite loop to block chat scrolling, stage queue, or settings UI.
213. Cancel runtime work on message recycle when no longer needed, card removal, toggle OFF, account logout, chat close and process shutdown.
214. Use generation tokens to suppress stale completion after cancellation or rebind.
215. Runtime may not outlive corresponding message view/account reference unless explicit stable cache data has been copied.
216. QuickJS callbacks crossing to Java use immutable bounded values, not borrowed native/Java mutable objects.
217. Promise jobs/timers require a bounded scheduler integrated with 0302 lifecycle; do not create a thread per card.
218. No timers/workers unless desktop 0313 and batch 28 explicitly expose these capabilities to HTML card scripts.
219. No `fetch`, WebSocket, filesystem, Telegram client API, clipboard, media playback, notifications or generic `tg` bridge by inheritance.
220. Any exposed script capability must have an explicit security review and user-visible policy; card rendering alone is not a grant.
221. Separate script parse errors from HTML parse errors; fallback UI must remain understandable and must not expose source code.
222. Script logs redact values and omit HTML, message text, sender, URLs with secrets, and any account content.
223. Avoid storing script state persistently unless format source establishes it; if needed, scope storage per account and card id and bound it.
224. Script mutation of card state must trigger remeasure only when output changes; debounce repeated updates.
225. Validate all JS-to-native numbers for finite range before using as coordinates or dimensions.
226. Treat QuickJS OOM/error/timeout as nonfatal card failure and destroy context reliably.
227. `LiteMode` and performance-class policy must be respected for animated card updates; static render remains unaffected.
228. Default-off switch must prevent JS context creation, not merely hide drawn output.

## ChatMessageCell integration, measurement and recycling

229. Use exact current Android `ChatMessageCell` anchors after `git show tele:` or `rg` in Telegram checkout; do not copy guessed line numbers from other branches.
230. New stock edits remain minimal: gated call before stock document rendering or add-after-stock fallback, no broad refactor/reindent.
231. Fork coordinator belongs in `tele/` (e.g. helper / UI cell renderer); no large feature implementation inside stock hot file.
232. Detection hook is gated by `TeleConfig.HTML_BUBBLES.getValue()` and exact `.tgw` document eligibility.
233. When disabled or unsupported, continue original stock file bubble path exactly.
234. When enabled and eligible, choose card type only after local file is available and metadata/package validation passes.
235. Preserve normal sender, timestamp, delivery/read status, selection, reply, forward, reactions and menu behavior of the message cell.
236. Do not replace Telegram message object or mutate document MIME/name fields to trick stock rendering.
237. Measurement uses same card layout result used by draw; no divergence between `onMeasure`/cell layout and actual drawn height.
238. Account for message caption, service/time labels, grouped media and reply/forward components without overlap.
239. Each bound card receives explicit immutable key `{account, dialog/message identity, document revision, dimensions, theme revision}`.
240. During `setMessageObject`/rebind clear prior card state immediately before attaching new key.
241. A recycled holder cannot display the previous message's cached bitmap or an asynchronous script result.
242. On invalid/no local file, preserve stock attachment row or show explicitly approved loading state; no empty space reserved indefinitely.
243. If download finishes, request UI rebind/invalidation on main thread and recheck current message identity before applying.
244. On cell detach/recycle cancel only view-bound work; shared immutable parsed cache may remain subject to bounded LRU policy.
245. Touch hit regions for card links/buttons must not conflict with Telegram long-press, selection, swipe or link handling.
246. Any card interaction uses existing cell dispatch events and explicit allowlisted action; do not let litehtml consume all touches.
247. Long press/context menu, copy, forward, reply and message selection must retain stock behavior.
248. Grouped albums: establish whether `.tgw` can participate; if unsupported, use normal single attachment behavior and test mixed album.
249. Secret chats, protected/no-forward messages, disappearing media, downloaded and cloud-only documents need explicit policy review.
250. [INFERENCE] Safest initial behavior is to disable script execution/render cards for secret/disappearing contexts until desktop format/security semantics are confirmed.
251. Do not leak card content into list previews, notification text, accessibility announcements outside the message, or screenshots when stock policy blocks content.
252. Avoid holding a static reference to `ChatMessageCell`, Activity, Fragment, account or `Bitmap` in global cache.
253. Render at the exact cell clip; preserve bubble background/radius and normal message padding unless desktop source requires a specific presentation.
254. Ensure hit-tested geometry follows width/height and display density after rotation, split-screen or font-scale changes.
255. Unknown/unsupported CSS should degrade gracefully; preserve plain text and attachment affordances.

## Measurement, caching, accessibility and resource limits

256. Parse and measure on worker executor; only publish immutable layout/bitmap to UI.
257. `ChatMessageCell` measure must never synchronously wait for parser, native renderer, disk or script thread.
258. While render is pending, reserve only a bounded placeholder height and remeasure when finished.
259. Prevent repeated measure/render loops by comparing measured size and generation before calling requestLayout.
260. Cache DOM/layout only when litehtml objects are safe for thread confinement; otherwise cache serialized parsed input and render result, not mutable DOM cross-thread.
261. Per-card cache has byte accounting; item-count limits alone are insufficient for bitmap memory.
262. Process-wide cache must have LRU eviction and low-memory trim integration.
263. Avoid rendering invisible/offscreen cards before RecyclerView needs them; use viewport/bind lifecycle with deduplicated requests.
264. Avoid recomputing on every draw or animation frame unless content/style changed.
265. Accessibility: provide a meaningful node description and/or native text representation derived from approved rendered text.
266. Native renderer's bitmap alone is not accessible; define a bounded text extraction path for TalkBack.
267. Link/button semantics must expose label and action to accessibility and support keyboard/accessibility activation without pixel hit test.
268. Do not announce raw HTML tags, script source, file path or technical errors to screen readers.
269. Respect Android touch target/accessibility focus for interactive card controls; avoid invisible links.
270. Establish text-selection/copy behavior; card contents should not become unselectable if desktop UX promises selectable text.
271. [INFERENCE] Desktop source's exact selection semantics are not available from PATCHLIST; inspect 0313 behavior and decide Android native equivalent before implementation.
272. TalkBack order should follow document reading order, including RTL.
273. Contrast and color selection must remain legible in Telegram light/dark theme; authored CSS should not bypass basic safe defaults.
274. Enforce source file cap at least no larger than desktop 4 MiB reference for card document; account for container metadata/entries where applicable.
275. Enforce max images 64, per encoded image 4 MiB, max width/height 4096 px, and max 4096² pixels per decoded image from desktop implementation.
276. Enforce max depth 256 and max elements 5000; validate after parsing, with early abort where library supports it.
277. Enforce total layout/document pixel budget 48 Mi pixels as desktop reference, with stricter Android aggregate memory cap if needed.
278. Cap CSS/HTML string bytes, attributes per element, text node size, URL length, CSS rules and image decode concurrency.
279. [INFERENCE] Exact additional byte ceilings for text, CSS rules, cache, QuickJS and aggregate concurrent card images must be set by implementation constants after device profiling; never leave these unbounded.
280. Set integer-safe dimensions and cap layout width to actual bubble bounds; reject NaN/infinite/negative/overflow dimensions.
281. Cap card count concurrently parsing/rendering per chat/account, deduplicate same document request.
282. Cap queued jobs and cancel stale work; do not grow a queue as user scrolls quickly.
283. Time out parse/layout/image decode and script execution; controlled cancellation must release all native and Java resources.
284. Handle low memory by evicting card bitmaps and stopping off-screen runtimes before Telegram's existing memory pressure becomes fatal.
285. Avoid duplicate copies between downloaded file, Java byte[], JNI byte buffer, parser strings and Bitmap; stream/bounded decode where practical.
286. Preserve normal Android `Bitmap` lifecycle and never recycle a bitmap still referenced by Canvas/cache/UI.
287. Crash handling must not suppress unrelated app exceptions; catch only expected parse/native failures at boundary.
288. No telemetry or new network logging is needed for this feature.

## Playground UX and local data

289. The playground part of 0313 adds a local playground chat whose messages demonstrate/test HTML cards; it is not a real remote Telegram conversation.
290. Follow Android 0077 `TeleChatActivity`/`TeleChangelog` pattern where it fits, not a synthetic server message or fake peer on network.
291. Use a distinct local peer/chat identity from changelog peer and any Telegram dialog IDs.
292. [INFERENCE] Stable synthetic peer ID and account storage strategy are not established in provided docs; inspect Android 0077 (`TeleChangelog`) and choose collision-proof local-only identity before coding.
293. Keep playground messages and sample cards in fork-owned storage/resources, never stock dialog/message tables or server synchronization.
294. If reusing `tele.db`, extend only fork-owned `tele_*` tables through `TeleDatabaseHelper`; do not alter stock schema/version.
295. If samples are packaged resources, version and validate them; do not treat sample as permission to execute arbitrary user file.
296. The settings entry opens playground only while `HTML_BUBBLES` is ON; when OFF, keep row available to enable the parent but do not enter active parser path.
297. Exact route (settings row, local chat list item, or both) should match desktop 0313 and Android conventions after source review.
298. Entering playground shows locally generated sample cards/messages with clear “local test” identity and no misleading online status.
299. Playground must be clearly distinguishable from real user, bot, group and channel to avoid accidental sends.
300. Disable message composer/send-to-server behavior unless desktop UX specifically supports card source editing locally.
301. If user input is supported, treat it as untrusted HTML/script, run same package validator and runtime restrictions, and persist only locally if the desktop contract requires persistence.
302. Reset action clears playground content/state with confirmation if destructive; do not clear normal chat history or settings.
303. Mark-read/unread semantics should be local and should not send `messages.readHistory` or any other Telegram RPC.
304. Do not include playground in chat search, notifications, badge counts or account server requests unless explicitly specified.
305. Per-account separation: playground data, config effects and card caches must not cross currentAccount boundaries.
306. Account switch and logout invalidate local card runtime state and account-specific synthetic chat data as policy defines.
307. Display normal back/navigation behavior and accessibility labels; opening sample card should not exit the playground unexpectedly.
308. Keep reset/help/disable affordances reachable without long press only.
309. [INFERENCE] Exact playground samples, empty state, editor affordance and reset confirmation wording are not specified in docs; copy desktop 0313 UX only after source inspection and adapt to Android.
310. No placeholder empty “playground” page counts as implementation; it must demonstrate the real 0313 renderer and a safe supported card sample.

## TeleConfig state, account scope, threads and LiteMode

311. Config is process-wide fork preference per existing TeleConfig design; per-account card data/runtime is separately scoped where applicable.
312. Java hooks use generated/accessor-compatible `TeleConfig.HTML_BUBBLES.getValue()` (confirm current API on branch); never access Kotlin internal `value` directly from Java.
313. Settings changes invoke existing `TeleHooks.onConfigChanged` then post visible UI refresh on main thread.
314. On OFF stop QuickJS card execution and detach callbacks before invalidating cells.
315. On OFF fallback must be exact stock file view, including same sizing, menus, downloading behavior and touch handling.
316. Worker callbacks capture immutable `currentAccount`; never resolve account 0 from static singleton or current selected account after async wait.
317. Each callback validates account still active and card generation/message key matches bound cell.
318. Parse, IO, image decode, native layout and JS work run away from UI thread and `Utilities.stageQueue`.
319. Main thread owns Android View, Canvas drawing entry point, RecyclerView mutation and settings/navigation.
320. No per-cell thread/executor creation; use bounded shared feature executors or batch 28 scheduler according to ownership contracts.
321. Respect `LiteMode` and performance class: do not animate card changes continuously when reduced motion/performance policy disables animation.
322. Static cards should remain deterministic under LiteMode; no animated image/script updates without explicit support.
323. Rotation/configuration change cancels obsolete bitmap sizing request and requests layout for new viewport.
324. App background/foreground should suspend or stop nonessential card timers and release temporary resources.
325. Process death requires no in-memory QuickJS state recovery; stored local playground/card state must validate and recover safely.
326. No native script thread should prevent app shutdown or account logout.

## Feature rows and documentation

327. Add one English `features.md` row for user-facing 0313 according to actual setting page and default.
328. Candidate row: “Render `.tgw` HTML cards in message bubbles and open a local playground; debug setting, default off; Android patch file and desktop 0313.”
329. Do not add row before patch export; patch filenames are assigned by queue order and must be exact.
330. If 0312 is strictly build infrastructure with no user-facing option, no separate feature row is required.
331. Link current desktop origin/main numbers 0312 and 0313; never old numbering or generated Android patch number in desktop column.
332. Feature row belongs in same repository commit as exported user-facing patch per AGENTS.
333. Settings text goes only to `strings_tele.xml`, prefixed `Tele`; do not edit stock `strings.xml`.
334. Search descriptions should say “HTML card scripts are local, experimental and disabled by default”; do not promise secure sandbox or web compatibility.
335. Export/import only actual `TeleConfig` item; exclude search IDs, cache, parsed content, local samples and runtime state.

## Tests: OFF and ON

336. Build matrix includes every configured Android ABI, including arm64 and 32-bit/other ABIs still shipped by current Gradle splits.
337. Confirm CMake config and compilation are offline/reproducible with vendor sources and no `FetchContent` network requirement.
338. OFF test: open `.tgw` in ordinary chat; it renders as stock file row, with no litehtml parse or QuickJS runtime initialization.
339. OFF test: open ordinary `.html`, `.htm`, text, image, sticker, video, generic document; stock behavior unchanged.
340. OFF test: opening playground route does not create network peer or background execution; settings offers enable toggle only.
341. ON test: valid `.tgw` sample downloads/local-available and displays correct bubble layout with script-backed card behavior.
342. ON test: file pending download transitions to card once local data available, without stale cell flash or duplicate render.
343. ON test: use light/dark theme, theme switch, font scale, display density, orientation, narrow width and large screen.
344. Test light-dark CSS, inline styles, supported font weight/style, nested blocks, links, lists, tables only if allowlisted.
345. Test English, Russian, Arabic/Hebrew mixed RTL, CJK, emoji and long unbroken text.
346. Test images: small PNG/JPEG/WebP if supported, valid SVG if supported, invalid/truncated bytes, data URL, excessive dimensions and external reference attempt.
347. Test every configured limit at boundary and one over: file bytes, 64/65 images, 4 MiB image, 4096/4097 side, 4096²+ pixels, 256/257 depth, 5000/5001 elements, total pixel ceiling.
348. Test malformed UTF-8, broken HTML/CSS, deep nesting, huge attributes/text and invalid CSS numeric values.
349. Test rejected URI schemes `javascript:`, `file:`, `content:`, `intent:` and remote HTTPS image/CSS; ensure no request or intent occurs.
350. Test archive traversal/absolute/duplicate paths if archive format; verify corrupt, encrypted, nested and oversized archive rejection.
351. Test JS success, syntax error, thrown error, infinite loop/deadline, memory exhaustion and stale callback after toggle OFF.
352. Test QuickJS runtime created only with setting ON, destroyed on OFF, logout, message removal and process lifecycle.
353. Test rapid scroll/recycling between cards with different content; verify no previous bitmap, link target or script result bleeds into new cell.
354. Test measure/draw height agreement, no clipping or overflow into adjacent message, reply/forward/status labels, selection and long-press.
355. Test grouped album behavior, cloud-only document, local cache clear, secret chat, disappearing media and protected/no-forward message policy.
356. Test TalkBack description/order, link actions and keyboard/accessibility focus; no raw markup announced.
357. Test playground entry, sample rendering, local reset, back navigation, account switch, logout and airplane/offline mode.
358. Verify playground actions do not send Telegram RPC, tele-server requests, notifications or account data.
359. Test low memory while several visible/in-flight cards exist; confirm bitmap/cache eviction and no ANR/OOM.
360. Test config import/export and default setting migration: default false for existing users; export/import restores only chosen option.
361. Compare OFF screenshot/layout with stock for regular files and unsupported `.tgw`; no visible regression.
362. Do not claim done based on compilation; run manual on/off test on device or emulator and receive human verification.

## Logcat and diagnostics

363. Use one concise tag such as `TeleHtml` and stable event categories: init, parse-failed, rejected-limit, render-failed, cancelled, cache-evict.
364. Never log card HTML, JS source, message text, image bytes, URLs/query, peer/user IDs or local file path.
365. [INFERENCE] Logging account index should be avoided unless needed; when logged, never include account credentials or dialog identifiers.
366. Expected invalid-card errors should be warnings/debug diagnostics with reason code, not stacktrace on every cell bind.
367. Native crashes must be investigated, not swallowed; report reproducible native failure with ABI, Android version and sanitized reason.
368. Confirm no exception loop or per-frame log spam while scrolling.
369. Include toggle state, renderer version and ABI in developer diagnostics only if privacy-safe and user-configured.
370. Avoid adding a new telemetry pipeline for renderer performance.

## Manual device gate

371. Install debug APK matching device ABI; modern devices generally use arm64 split, but inspect actual device ABI before selecting artifact.
372. Start with the setting OFF and confirm ordinary attachment UX exactly matches stock.
373. Enable HTML bubbles in tele Debug settings and open playground; inspect sample card plus local labels.
374. Open a valid card in normal chat and verify layout, fonts, image, link tap and message actions.
375. Disable setting while chat is open; verify card reverts to attachment and script stops promptly.
376. Re-enable after scrolling and rotate device; verify new card is rendered for correct width and theme.
377. Switch accounts while a card is parsing; confirm callback cannot update another account's cell.
378. Test offline mode; local sample/card still works and no remote assets are fetched.
379. Test TalkBack and large font size before passing accessibility gate.
380. Capture sanitized logcat for parse/limit/native failures only; redact content and identifiers.
381. Batch gate requires both rows 0312 and 0313 committed/exported, full debug build, ABI native result, APK delivered and human on/off verification.
382. Mark statuses built/done only after their documented gates are actually met.

## Features rows/gates and remaining questions

383. PATCHLIST gate remains: litehtml builds on all ABIs; `.tgw` card renders in bubble with script; playground chat opens.
384. Extend this minimum gate with explicit OFF-is-stock, no-network, malformed input, resource limits, recycling, theme and accessibility checks above.
385. 0312 build row depends on pinned litehtml/gumbo sources and native compilation for all packaged ABIs.
386. 0313 feature row depends on 0302 QuickJS runtime, format contract, secure allowlist, native Canvas/Bitmap renderer and ChatMessageCell lifecycle integration.
387. The playground part of 0313 depends on the card part and Android 0077 local-chat pattern plus approved local identity/storage.
388. Open question: what is exact `.tgw` byte format and how are HTML, CSS, JS, assets and metadata encoded?
389. Open question: which desktop-defined HTML tags/CSS properties, script APIs, events and `light-dark()` behaviors are contractual?
390. Open question: are scripts active on every `.tgw`, require consent/grants, or only use a restricted card API?
391. Open question: desktop 0313 exact image formats, `app:` asset names, and SVG rules—verify full implementation before port.
392. Open question: which secret, protected, disappearing, scheduled, album and local-only contexts may render or execute scripts?
393. Open question: should link clicks be inert, use Telegram open-link confirmation, or support only a narrow allowlist?
394. Open question: exact max `.tgw` source/packaging size, script time/memory cap, cache budget and per-device concurrency.
395. Open question: bitmap versus JNI drawing-command backend; profile scrolling, allocation rate, font parity and accessibility before choosing.
396. Open question: card text selection, expansion/height cap, button accessibility and playground editing/reset UX on Android.
397. Open question: confirm 1460..1479 are unused in actual TeleSearch and stock search registry at implementation time.
398. Open question: confirm TeleSettingsActivity has Debug mode in the implementation checkout or route setting to current equivalent page.
399. Main risks: native parser memory safety, HTML/script trust boundary, untrusted archive path traversal, stale callbacks into recycled cells, bitmap OOM and cross-account cache leakage.
400. Main non-goals: WebView fallback, generic arbitrary HTML viewer, new scripting subsystem parallel to batch 28, external assets/network access, server-side playground, user tracking or broad Telegram UI changes.
401. Any behavior not supported by sources remains explicitly unresolved; do not invent desktop parity or security claims.
402. When source inspection settles a question, update this guide or the implementation contract before changing code; keep all claims evidence-backed.
