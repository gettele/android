# Пачка 13 — структура настроек и редактор меню

## Назначение и границы

1. Этот документ — пошаговый план реализации текущей пачки 13 из `docs/PATCHLIST.md`.
2. Пачка переносит структуру настроек desktop 0169, сворачиваемые зависимости 0170 и редактор всех меню 0171.
3. Затем на общий реестр меню навешиваются 0167, 0179, 0200, 0255, 0266, 0295 и 0149.
4. Номера desktop здесь означают текущую очередь `origin/main`, а не старые номера.
5. Android-основа — ветка `tele` в `Telegram`; desktop-основа — `origin/main` в checkout `tele`.
6. Точки, явно проверенные в исходниках, помечены как проверенные.
7. Любая точка, не подтверждённая просмотренным исходником, помечена `[INFERENCE]`.
8. Порядок ниже обязателен: сначала инфраструктура, затем миграция и новые UI, затем пункты меню.
9. Весь новый fork-код размещается в `tele/` и `strings_tele.xml`.
10. В stock-файлах допускаются только короткие gated-вызовы в `TeleHooks` или helper.
11. `TLRPC.java` и stock-схема базы не изменяются.
12. Цель off-состояния — ровно stock-поведение, включая состав, порядок и сеть.

## Что уже есть в Android

13. `TeleSettingsActivity` сейчас имеет root, `interface`, `privacy`, `ids`, `sending`, `your data`, `server`.
14. `TeleSettingsActivity.SECTIONS` создаёт шесть страниц и иконки `msg2_*`.
15. `TeleSettingsActivity.buildRows` строит `Row(type,title,value,item,mode,icon,badge)`.
16. `TYPE_HEADER`, `TYPE_VALUE`, `TYPE_TOGGLE`, `TYPE_SHADOW`, `TYPE_LINK`, `TYPE_LINK_ICON` уже обслуживаются RecyclerView.
17. Нажатие тумблера вызывает `TeleConfig.set`, затем `TeleHooks.onConfigChanged`.
18. Смена значения уже работает без перезапуска для существующих опций через lifecycle bus.
19. `TeleSearch.appendAll` подключён из `ProfileActivity` в точке около строки 14716.
20. В текущем поиске root имеет GUID 950.
21. Текущие блоки поиска занимают примерно 950–1115 и должны остаться совместимыми.
22. `TeleNewSettings.fresh()` берёт идентификаторы из `TeleSettingsActivity.settingIds()`.
23. `TeleNewSettings` хранит `known`, `new`, `seen` в `TeleConfig.KNOWN_SETTINGS`.
24. На `TeleSettingsActivity.MODE_NEW` новые строки показываются и при входе вызывается `markSeen()`.
25. Проверенный stock-хук меню: `ChatActivity.fillMessageMenu` начинается около строки 46463.
26. Проверенный вызов фильтра: `tele.helpers.MessageMenu.filter(items, icons, options)` около строки 47165.
27. Проверенные вызовы построителя сообщения: около строк 31515, 40905 и 41208.
28. `MessageMenu.ALL` сейчас содержит numeric `ChatActivity` option-коды и имена.
29. Скрытие хранится в `tele_kv` под `message_menu_hidden` как JSON-массив чисел.
30. Порядок хранится в `tele_kv` под `message_menu_order` как JSON-массив чисел.
31. Текущий фильтр синхронно меняет три параллельных массива `items`, `icons`, `options`.
32. Текущий редактор `TeleMenuActivity` редактирует только message menu.
33. Текущий редактор использует `ItemTouchHelper`, long-press и видимую `list_reorder` ручку.
34. Текущий `TeleConfig.init` читает `SharedPreferences` с именем `tele_config`.
35. Текущий `TeleConfig` загружает все `configItems` один раз в `TeleHooks.init`.
36. Текущий `TeleDatabaseHelper` открывает `tele.db` версии 7.
37. `tele_kv` имеет только глобальные `key TEXT PRIMARY KEY, value TEXT`.
38. Архивные и черновиковые таблицы уже имеют явную колонку `account`.
39. Поэтому меню нельзя случайно привязывать к singleton account 0.
40. Внешний desktop `0171` использует реестр, layout, apply и editor вместо старого order-файла.

## Desktop-контракт 0169

41. Desktop 0169 добавляет страницы `interface`, `chats`, `messages`, `sending`.
42. Он также добавляет `notifications` и `menus`.
43. Сохраняются `privacy`, `profiles and ids`, `bots`, `debug`.
44. Существующие отдельные страницы `server`, `backup`, `updates` также должны иметь стабильные Android-маршруты.
45. Desktop старые ссылки перенаправляет на новые категории.
46. Desktop keywords для interface: `title`, `lowercase`, `scale`, `chat list`.
47. Desktop keywords для chats: `badges`, `userpics`, `sponsored`, `gestures`.
48. Desktop keywords для messages: `deleted`, `edited`, `bookmarks`, `links`.
49. Desktop keywords для sending: `uploads`, `drafts`, `scheduled`, `confirm`.
50. Desktop keywords для notifications: `unread`, `counters`, `online`, `mute`.
51. Desktop keywords для menus: `context`, `right click`, `message menu`.
52. Android не должен слепо копировать desktop-only window, tray и hover UX.
53. На телефоне каждая категория остаётся отдельным `BaseFragment` со списком.
54. Переносится информационная архитектура и поиск, а не Qt-вёрстка.
55. Иконки должны переиспользовать существующий `msg2_*` стиль.
56. В root порядок страниц: interface, chats, messages, sending, notifications, menus.
57. После них: privacy, profiles and ids, bots, debug, server, backup, updates.
58. `profiles and ids` можно реализовать одним Android mode, но title и slug должны быть стабильны.
59. `backup` должен быть отдельной точкой для export/import настроек, даже если сейчас содержит одну ссылку.
60. `updates` остаётся совместимым с существующим root update-блоком.
61. Старые modes `ids`, `data`, `server` не удалять до миграции deeplink/search.
62. Старые modes направлять на новые страницы через alias map.
63. Alias map: `ids` → `profiles-ids`, `data` → `backup` или `profiles-ids` по конкретной строке.
64. Alias map: `interface` сохраняется без переименования.
65. Alias map: `privacy` сохраняется без переименования.
66. Alias map: `sending` сохраняется без переименования.
67. Alias map: `server` сохраняется без переименования.
68. [INFERENCE] окончательный slug `profiles-ids` вместо `profiles_and_ids` выбрать один раз до кода.
69. [INFERENCE] `bots` и `debug` сначала могут быть пустыми страницами-заглушками только если они реально нужны root; недоступные функции не имитировать.
70. Нельзя показывать пустую ложную настройку без понятного текста о недоступности.

## Полная карта текущих Android-настроек

71. `SHOW_SECONDS` (`show_seconds`, off) остаётся в `messages`, группа Message times.
72. `HIDE_ALL_CHATS_FOLDER` (`hide_all_chats_folder`, off) переходит из interface в `chats`, группа Chat list.
73. `HIDE_CALL_BUTTONS` (`hide_call_buttons`, off) остаётся в `chats`, группа Call buttons.
74. `CONFIRM_CALLS` (`confirm_calls`, off) остаётся рядом с Call buttons в `chats`.
75. `OPEN_LINKS_DIRECTLY` (`open_links_directly`, off) остаётся в `privacy`, группа Link safety.
76. `NAME_INSTEAD_OF_PHONE` (`name_instead_of_phone`, off) переходит в `chats`, группа Chats and profiles.
77. `REVEAL_SPOILERS` (`reveal_spoilers`, off) переходит в `messages`, группа Spoilers.
78. `HIDE_MENTION_REACTIONS` (`hide_mention_reactions`, off) переходит в `chats`, группа Chat controls.
79. `STATIC_AVATARS` (`static_avatars`, off) переходит в `chats`, группа Chats and profiles.
80. `HIDE_STORIES` (`hide_stories`, off) остаётся в `privacy`, группа Stories.
81. `INVISIBLE_STORIES` (`invisible_stories`, off) остаётся в `privacy`, группа Stories.
82. `GHOST_ONLINE` (`ghost_online`, off) остаётся в `privacy`, группа Ghost mode.
83. `GHOST_TYPING` (`ghost_typing`, off) остаётся в `privacy`, группа Ghost mode.
84. `GHOST_READ` (`ghost_read`, off) остаётся в `privacy`, группа Ghost mode.
85. `GHOST_CONTENTS_READ` (`ghost_contents_read`, off) остаётся в `privacy`, группа Ghost mode.
86. `NEVER_BLOCK_SCREENSHOTS` (`never_block_screenshots`, off) остаётся в `privacy`, группа Screen capture.
87. `ALLOW_SCREENSHOTS_DISAPPEARING` (`allow_screenshots_disappearing`, off) остаётся в `privacy`, группа Screen capture.
88. `LOCAL_DRAFTS` (`local_drafts`, off) переходит в `messages`, группа Drafts/privacy.
89. `TELE_SERVER_URL` (`tele_server_url`, default URL) остаётся в `server`, не тумблер.
90. `SERVER_USERNAMES` (`server_usernames`, on) остаётся в `server`, network feature.
91. `BUBBLE_BADGES` (`bubble_badges`, off) переходит в `chats`, группа Chats and profiles.
92. `SEND_CRASH_REPORTS` (`send_crash_reports`, on) остаётся в `server`, consent row.
93. `AUTO_UPDATE` (`auto_update`, on) переходит в `updates`.
94. `SHOW_CHANGELOG` (`show_changelog`, on) переходит в `updates`.
95. `CHANGELOG_ACCOUNTS` (`changelog_accounts`, internal string) не показывать строкой; оставить в updates storage.
96. `KNOWN_SETTINGS` (`known_settings`, internal JSON) не показывать строкой; оставить в new-settings storage.
97. `KEEP_DISAPPEARING_MEDIA` (`keep_disappearing_media`, off) переходит в `messages`, Disappearing media.
98. `KEEP_DELETED_MESSAGES` (`keep_deleted_messages`, off) переходит в `messages`, Deleted messages parent.
99. `KEEP_SELF_DELETED_MESSAGES` (`keep_self_deleted_messages`, off) становится child Deleted messages.
100. `DELETED_MARKER` (`deleted_marker`, fade) становится child choice Deleted messages.
101. `DELETED_REPLY` (`deleted_reply`, skip) становится child choice Deleted messages.
102. `EDIT_HISTORY` (`edit_history`, off) остаётся в `messages`, Edited history.
103. `SHOW_PEER_ID` (`show_peer_id`, off) переходит в `profiles-ids`, Peer IDs parent.
104. `PEER_IDS_WITHOUT_SPACES` (`peer_ids_without_spaces`, off) становится child Peer IDs.
105. `BOT_API_PEER_IDS` (`bot_api_peer_ids`, off) становится child Peer IDs.
106. `SHOW_DC` (`show_dc`, off) становится child Peer IDs.
107. `MERGE_ID_DC` (`merge_id_dc`, off) становится child Peer IDs.
108. `MESSAGE_ID_MENU` (`message_id_menu`, off) переходит в `menus`, Message menu items.
109. `SHOW_GIFT_IDS` (`show_gift_ids`, off) переходит в `profiles-ids`, Gifts and IDs.
110. `SHOW_REGULAR_GIFT_IDS` (`show_regular_gift_ids`, off) становится child Gift IDs.
111. `PURCHASE_PRICE` (`purchase_price`, off) переходит в `profiles-ids`, Collectibles.
112. `SEETG_BUTTON` (`seetg_button`, off) переходит в `profiles-ids`, Collectibles.
113. `COPY_EMOJI_ID` (`copy_emoji_id`, off) переходит в `menus`, Message menu items.
114. `LOCAL_NAMES` (`local_names`, off) переходит в `profiles-ids`, Local names.
115. `USERNAME_ALIASES` (`username_aliases`, off) переходит в `profiles-ids`, Aliases parent.
116. `INLINE_NO_VIA` (`inline_no_via`, off) переходит в `sending` или `bots`; [INFERENCE] выбрать `bots` только после появления bot page.
117. `BOT_BUTTON_PAYLOADS` (`bot_button_payloads`, on) переходит в `bots`, default remains on.
118. `VIEW_AS_TL` (`view_as_tl`, off) переходит в `menus`, Message tools.
119. `HIDE_SPONSORED` (`hide_sponsored`, off) переходит в `chats`, Sponsored.
120. `HIDE_PROXY_SPONSOR` (`hide_proxy_sponsor`, off) переходит в `chats`, Sponsored.
121. `CLEAN_OPENED_LINKS` (`clean_opened_links`, off) остаётся в `privacy`, Links.
122. `CLEAN_SENT_LINKS` (`clean_sent_links`, off) остаётся в `privacy`, Links.
123. `REWRITE_PASTED_LINKS` (`rewrite_pasted_links`, off) остаётся в `privacy`, Links.
124. `NO_LINK_PREVIEWS` (`no_link_previews`, off) остаётся в `messages`, Links.
125. `LINK_PREVIEW_MODE` (`link_preview_mode`, all) остаётся в `messages`, choice row.
126. `HD_PHOTOS` (`hd_photos`, off) остаётся в `sending`, Uploads.
127. `DOCKED_MEDIA` (`docked_media`, off) остаётся в `sending`, Uploads.
128. `PUNCTUAL_SCHEDULED` (`punctual_scheduled`, off) остаётся в `sending`, Scheduled.
129. `QUEUE_BEHIND_MEDIA` (`queue_behind_media`, off) остаётся в `sending`, Sending order parent.
130. `COPY_PROTECTED` (`copy_protected`, off) остаётся в `sending`, Sending order.
131. `SEND_OLDER_REPLIES` (`send_older_replies`, off) становится child Sending order.
132. `DOUBLE_ENTER_SEND` (`double_enter_send`, off) становится child Sending order.
133. `QUICK_REPLIES_IN_GROUPS` (`quick_replies_in_groups`, off) переходит в `chats`, Chat features.
134. `CALCMULA` (`calcmula`, off) остаётся в `sending`, Message field parent.
135. `EDITOR_EYEDROPPER` (`editor_eyedropper`, off) переходит в `interface`, Editor.
136. `CALCMULA_PREVIEW` (`calcmula_preview`, off) становится child Calcmula.
137. `SHOT` (`shot`, off) переходит в `menus`, Message tools.
138. `SHOT_VIEW` (`shot_view`, empty internal value) не показывать как строку; оставить рядом с Shot.
139. Новые строки 0167 не создают `*_menu`-тумблеры: это решение `docs/decisions.md`.
140. Все существующие defaults сохраняются; перенос страницы не является миграцией значения.
141. `BOT_BUTTON_PAYLOADS`, `SERVER_USERNAMES`, `SEND_CRASH_REPORTS`, `AUTO_UPDATE`, `SHOW_CHANGELOG` остаются единственными текущими on/default-on из этой карты.
142. Любой новый feature toggle этой пачки, если он всё-таки потребуется, обязан быть `BoolItem(key,false)`.

## TeleConfig, prefs и миграция

143. Не переименовывать существующие ключи при смене страницы: `show_seconds` и остальные уже являются API хранилища.
144. Не менять default только ради паритета desktop: Android правило — off = stock.
145. Для 0171 layout не использовать `TeleConfig` как большой строковый blob без явной причины.
146. Рекомендуемая новая модель: `TeleMenuLayout` хранит serialised text в `tele_kv`.
147. Ключ рекомендуется формировать как `menu_layouts:<account>`; [INFERENCE] это решение для per-account изоляции.
148. Значение содержит по одной строке на настроенный вид меню: `menu-id=layout`.
149. Порядок строк незначим, дубликат `menu-id` считается ошибкой импорта.
150. Список допустимых `menu-id`: `message`, `chat`, `chat-row`, `folder`, `profile`, `send`, `field`.
151. Старый `message_menu_hidden` содержит numeric-коды скрытых пунктов.
152. Старый `message_menu_order` содержит numeric-коды в пользовательском порядке.
153. Мигратор строит обратный индекс `ChatActivity option code -> MessageMenu item key`.
154. Порядок из `message_menu_order` переносится в `message` layout первым.
155. Коды из hidden получают prefix `-` в новом layout.
156. Коды `MessageMenu.ALL`, которых нет в old order, дописываются в stock order.
157. Неизвестный numeric-код не должен ломать миграцию; его пропустить и записать `FileLog`.
158. При непустом old hidden/order создать layout даже если custom order неполный.
159. Если оба старых ключа пусты, новый layout не создавать: применяется Default preset.
160. После успешного parse, validate и save записать migration marker `menu_layout_migration_v2`.
161. Удалять old keys только после успешной записи нового значения.
162. При ошибке оставить old keys и повторить миграцию при следующем старте.
163. [INFERENCE] legacy global layout сначала читать как fallback для каждого account.
164. [INFERENCE] материализовать fallback при первом открытии account, чтобы старые настройки не пропали на multi-account.
165. Для всех ключей нового layout применять `currentAccount`, не `UserConfig.selectedAccount` из background callback.
166. `TeleConfig` prefs сейчас реально называются `tele_config`; это отличается от общей формулировки architecture про `tele`.
167. Не переименовывать prefs без миграции: сначала читать `tele_config`, затем canonical prefs только если они появятся.
168. [INFERENCE] если будет выбран canonical name `tele`, миграция должна copy-if-missing по всем `configItems` и сохранить marker.
169. При миграции prefs никогда не затирать уже существующее canonical значение legacy default-ом.
170. Не мигрировать internal `KNOWN_SETTINGS` вручную в новые IDs: алгоритм должен увидеть смену IDs как новые строки.
171. Для TeleNewSettings нужны стабильные semantic IDs страниц и ключей, а не позиции rows.
172. `settingIds()` должен включать все новые page IDs и все `row.item.key`.
173. `settingIds()` не должен включать separator, shadow и transient update action.
174. Старый key, переехавший между страницами, должен остаться тем же ID и не показываться как новая feature.
175. Новый `menus/<menu-id>` должен считаться новым page/child ID один раз.
176. `TeleNewSettings` должен очищать duplicate IDs перед записью `known`.
177. При повреждённом JSON `KNOWN_SETTINGS` считать known пустым, но не падать на UI thread.
178. Не экспортировать `KNOWN_SETTINGS`, migration markers и runtime `seen` как пользовательские settings.
179. Export/import config должен экспортировать все публичные `TeleConfig` items по существующему spec table.
180. Layout export/import должен идти отдельным типом `menu_layouts`, потому что это структурированный текст.
181. Не экспортировать account-specific layouts в другой account без явного выбора пользователя.
182. [INFERENCE] all-menu import должен предлагать merge/replace; безопасный default — replace только перечисленные семь меню.

## Поиск: IDs 1140–1159

183. Диапазон 1140–1159 зарезервировать под новую структуру; текущие GUID 950–1115 не перенумеровывать.
184. [INFERENCE] это плановые Android IDs, потому что desktop patch не задаёт Android GUID.
185. 1140 — `tele interface`, открыть mode `interface`.
186. 1141 — `tele chats`, открыть mode `chats`.
187. 1142 — `tele messages`, открыть mode `messages`.
188. 1143 — `tele sending`, открыть mode `sending`.
189. 1144 — `tele notifications`, открыть mode `notifications`.
190. 1145 — `tele menus`, открыть mode `menus`.
191. 1146 — `tele privacy`, открыть mode `privacy`.
192. 1147 — `tele profiles and ids`, открыть mode `profiles-ids`.
193. 1148 — `tele bots`, открыть mode `bots`.
194. 1149 — `tele debug`, открыть mode `debug`.
195. 1150 — `tele server`, открыть mode `server`.
196. 1151 — `tele backup`, открыть mode `backup`.
197. 1152 — `tele updates`, открыть mode `updates`.
198. 1153 — `tele menu editor`, открыть общий editor selector.
199. 1154 — `message menu`, открыть editor `MESSAGE`.
200. 1155 — `chat menu`, открыть editor `CHAT`.
201. 1156 — `chat row menu`, открыть editor `CHAT_ROW`.
202. 1157 — `folder tab menu`, открыть editor `FOLDER`.
203. 1158 — `profile menu`, открыть editor `PROFILE`.
204. 1159 — `send and field menus`, открыть selector, не дублировать отдельные IDs.
205. Для каждой записи добавить keywords: `tele`, `settings`, русско-английские synonyms при необходимости.
206. SearchResult link/path должен вести в тот же mode, что и root row.
207. Старые search results, ведущие на `MODE_IDS`/`MODE_DATA`, оставить alias-переходами.
208. Search IDs должны быть уникальны и не зависеть от порядка `buildRows`.
209. [INFERENCE] если stock search уже занял один из 1140–1159, выбрать другой свободный ID и зафиксировать его до merge.
210. После добавления новых settings вызвать `TeleNewSettings.fresh()` только на UI thread.
211. Search callback не должен читать `TeleConfig` с background thread.

## 0169 — новый каркас SettingsActivity

212. Плановый commit: `feat: regroup tele settings`.
213. Усилие: M, потому что меняются root, modes, rows, search и new-settings IDs.
214. Зависит от текущей TeleSettingsActivity и не зависит от 0171 runtime.
215. Сначала добавить constants для всех новых modes и alias map.
216. Затем заменить `SECTIONS` на ordered `SECTION_SPECS` с mode, title, icon, search path.
217. Не удалять `MODE_INTERFACE`, `MODE_PRIVACY`, `MODE_SENDING`, `MODE_SERVER`.
218. Добавить `MODE_CHATS`, `MODE_MESSAGES`, `MODE_NOTIFICATIONS`, `MODE_MENUS`.
219. Добавить `MODE_PROFILES_IDS`, `MODE_BOTS`, `MODE_DEBUG`, `MODE_BACKUP`, `MODE_UPDATES`.
220. `MODE_UPDATES` должен открывать отдельную страницу, а root может оставить компактный summary.
221. Перенести строки согласно карте 71–142, сохранив item и default.
222. Для каждой страницы добавить HeaderCell и группы desktop 0169.
223. Группа не должна менять порядок или значение опции при одном лишь переходе.
224. Добавить rows `menus` и selector editor, но пока не подключать layout application.
225. Добавить `backup` rows для settings export/import, используя существующую IO инфраструктуру.
226. Если IO UI ещё отсутствует, row должен вести на существующий экспорт, а не быть no-op.
227. В `sectionTitle()` использовать стабильные human-readable titles.
228. В root показывать `new in tele` перед sections, как сейчас.
229. `settingIds()` обходить `SECTION_SPECS` и alias-free canonical modes.
230. Не считать alias mode отдельной новой страницей.
231. В `TeleSearch.kt` оставить старые entries, но новые canonical entries добавить явно.
232. Для mode `updates` не создавать дубликат `GUID_UPDATES` старого root блока.
233. Проверить deeplink `tg://settings/tele/new` и существующие `TeleChatActivity.NEW_SETTINGS_LINK`.
234. Проверить back stack: root → page → editor → back возвращается в page.
235. Проверить RecyclerView recycling для every row type после reordering sections.
236. Кнопки update/server должны по-прежнему вызывать существующие helpers.
237. `TeleHooks.onConfigChanged` не должен зависеть от номера новой страницы.
238. [INFERENCE] для settings export/import deeplink подобрать slug `backup` и не скрывать его в root.

## 0170 — сворачиваемые под-тумблеры

239. Плановый commit: `feat: collapse tele setting suboptions`.
240. Усилие: S, но только после каркаса 0169.
241. Добавить в `Row` поля `parent: BoolItem?`, `indent`, `expandable`, `childCount`.
242. Добавить отдельный `TYPE_GROUP_TOGGLE` или расширить `TYPE_TOGGLE` без изменения bind для обычных rows.
243. Parent row имеет switch и стрелку раскрытия; tapping title toggles expansion, tapping switch toggles value.
244. Child rows скрываются при collapsed, но их значения не удаляются.
245. Parent off делает child rows disabled/alpha и не запускает child behavior.
246. Не стирать child values при выключении parent: desktop 0170 специально их помнит.
247. Включение одного child при parent off сначала включает parent.
248. Если parent включён с нулём включённых children, включить все children группы.
249. Если parent выключен, group counter показывает сохранённое количество либо 0 — решение должно быть единым.
250. Рекомендуемый counter: `N on` только по фактически включённым children.
251. Expand state — transient UI state, не `TeleConfig` и не export.
252. Parent/child graph должен проверяться на cycle при построении rows.
253. Рекомендуемые группы: `KEEP_DELETED_MESSAGES` → self-deleted, marker, deleted-reply.
254. Рекомендуемые группы: `SHOW_PEER_ID` → spaces, Bot API, DC, merged DC.
255. Рекомендуемые группы: `QUEUE_BEHIND_MEDIA` → older replies, double enter.
256. Рекомендуемые группы: `CALCMULA` → preview.
257. `USERNAME_ALIASES` → alias actions только если их UI row действительно toggleable.
258. Не делать parent для `TELE_SERVER_URL`: это choice/storage, не BoolItem.
259. Не делать parent для screenshot options: `NEVER_BLOCK_SCREENSHOTS` имеет отдельную privacy семантику.
260. `TextCheckCell` не поддерживает стрелку сам по себе: добавить новый fork cell/layout в `tele/ui/settings/`.
261. Recycler bind обязан каждый раз выставлять checked, enabled, alpha, indent и arrow state.
262. `notifyDataSetChanged` допустим для первого патча; не оставлять stale holder visibility.
263. `TeleHooks.onConfigChanged` вызывается после parent и после child изменений.
264. Не выполнять тяжелую проверку графа на main thread после каждого tap; граф строится один раз.
265. Accessibility: child disabled должен быть недоступен для click, но его сохранённое значение видно после включения.
266. В settings search child ID остаётся key item, а открытие ведёт на страницу parent.
267. New-settings сравнивает key, а не expanded state.
268. Для off default все текущие rows должны визуально и функционально остаться stock fork UI.

## 0171 — ядро all-menu editor

269. Плановый commit: `feat: customize all tele menus`.
270. Усилие: L.
271. Зависит от Android 0042 hide message menu, Android 0049 reorder message menu и Android 0050 drag handles.
272. Также зависит от 0169 page `menus`.
273. Desktop registry имеет ровно семь видов меню: Message, Chat, ChatRow, FolderTab, Profile, Send, Field.
274. Android enum должен иметь семь стабильных values, не зависимых от Java option constants.
275. Рекомендуемые IDs: `message`, `chat`, `chat-row`, `folder`, `profile`, `send`, `field`.
276. Каждый registry item получает stable string key, label, icon, contexts и optional feature gate.
277. Numeric Java option code остаётся только compatibility input для migration.
278. Не использовать отображаемый label как storage ID: локализация меняет label.
279. Layout entry types: Item, Separator, Submenu.
280. Separator styles: Auto, Thin, Thick.
281. Item entry поддерживает `hidden` и `fresh` metadata.
282. Submenu entry поддерживает title, optional icon и nested entries.
283. Editor должен уметь reorder item, hide/unhide, add/remove separator, create submenu.
284. Editor должен уметь move item into/out of submenu.
285. Editor должен уметь rename submenu и выбрать icon из безопасного набора.
286. Preview должен строиться из того же resolved layout, что и runtime menu.
287. Context chips нужны для context-dependent visibility: own/other/media/service/selection и peer type.
288. Greyed feature-gated item показывает причину, но не должен запускать action.
289. Eye action может открыть соответствующую settings row; [INFERENCE] Android может заменить eye на `Open setting`.
290. Не включать автоматически privacy/network feature только из preview tap.
291. Editor save должен быть explicit; Cancel отбрасывает unsaved layout.
292. Reset применяет Default preset в editor, но сохраняет только после Save.
293. На телефоне использовать RecyclerView + nested list или flat path model, не копировать Qt widgets.
294. Для drag использовать `ItemTouchHelper`; nested submenu drag должен иметь path `[parent,index]`.
295. После remove корректировать paths выбранных/preview элементов.
296. Не разрешать submenu в submenu глубже лимита 8.
297. Не разрешать пустой submenu при Save либо сохранить его как удалённый.
298. Не разрешать duplicate item key в одном resolved layout.
299. Непоказанные в registry items должны автоматически появляться в stock tail.
300. Unknown stored keys не должны становиться executable action.
301. Unknown stored keys сохранить в diagnostic log и убрать при normalise.
302. Layout resolver должен отличать missing fresh, visible и hidden.
303. Default preset — текущий безопасный порядок Android/stock с телепунктами в конце.
304. Upstream preset — stock order без форк-реорганизации.
305. Minimal preset — только безопасный минимум, остальные hidden.
306. Power preset — все доступные feature-gated items visible.
307. Названия preset: Default, Upstream order, Minimal, Power user.
308. Решение desktop о четырёх preset обязательно перенести на Android.
309. `MenuLayout` должен быть единственным источником порядка после migration.
310. Старый `MessageMenu.filter` заменить вызовом resolver/apply, сохранив ранний off-path.

## Формат export/import меню

311. Формат — plain text, не JSON, по решению `docs/decisions.md`.
312. Строка имеет вид `message=reply,copy,|,view_as_tl`.
313. Один layout clipboard export может иметь prefix `message=`.
314. Full export содержит до семи строк, по одной на menu ID.
315. Item key состоит из lowercase `[a-z0-9_.]`.
316. Hidden item кодируется prefix `-`, например `-copy`.
317. Обычный separator кодируется `|`.
318. Thin separator кодируется `|-`.
319. Thick separator кодируется `|=`.
320. Submenu кодируется `[Title#icon:item1,item2]`.
321. В title экранировать `\`, `,`, `:`, `[`, `]`, `#`, `|`.
322. Удалять CR/LF из title при serialize.
323. При import trim whitespace вокруг всей строки и item tokens.
324. Reject malformed brackets, duplicate menu IDs, duplicate keys и trailing garbage.
325. Reject menu prefix другого вида при single-menu import.
326. При import без prefix разрешать только layout текущего editor menu.
327. Ограничить single layout 64 KiB и full export 256 KiB.
328. Ограничить submenu title 64 UTF-16 code units.
329. Ограничить item count per menu 512 после resolve.
330. Ограничить submenu depth 8.
331. Парсер не должен делать network request.
332. После parse вызвать normalize, разрешить missing registry items и проверить gates.
333. Copy использует Android clipboard, Share sheet — только для full export по желанию.
334. Paste показывает понятную Bulletin при invalid format и не меняет текущий layout.
335. Import не должен включать `TeleConfig` values и account data.
336. Export не должен содержать usernames, IDs, message text или server data.

## Runtime hooks семи меню

337. Message menu: сохранить verified hook `ChatActivity.fillMessageMenu` около 46463/47165.
338. Перед применением layout проверить `TeleConfig`/gate, затем filter item arrays.
339. Для selected/grouped message применять один resolved layout, не сортировать каждый item отдельно.
340. Reactions должны иметь отдельный stable key и быть hidden только layout-решением.
341. Chat menu: hook `ChatActivity.headerItem`/chat header action construction.
342. [INFERENCE] точный builder callsite для Chat menu не был повторно выведен из ветки; искать exact `headerItem.addSubItem` перед edit.
343. ChatRow menu: hook `DialogsActivity` action-mode/row `ItemOptions` construction.
344. [INFERENCE] exact `ItemOptions` method и anchor подтвердить grep перед кодом.
345. FolderTab menu: hook `FilterTabsView` long-press/options popup.
346. [INFERENCE] проверить отдельный path для all chats, archive и custom filters.
347. Profile menu: hook `ProfileActivity` `otherItem`/profile options.
348. [INFERENCE] не смешивать profile row menu и message menu; registry kind должен быть PROFILE.
349. Send menu: hook `ChatActivityEnterView` send popup construction.
350. [INFERENCE] найти exact `sendPopupLayout`/`SenderSelectPopup` builder и применить после stock items.
351. Field menu: hook `EditTextCaption`/`ActionMode.Callback` field context menu.
352. [INFERENCE] Android selection action mode API отличается от desktop right-click; сохранить system Copy/Select all fixed.
353. Все hooks обязаны вызывать общий `TeleMenuLayout.apply(kind, context, menu)`, а не копировать sort code.
354. Каждый hook должен иметь early return, если layout feature infrastructure выключена или layout отсутствует.
355. Default layout off-path должен оставлять stock menu identity and order.
356. Recycler/action menu holders не должны сохранять hidden state между bind.
357. Menu callbacks сохраняют original action object; layout меняет только placement/visibility.
358. Submenu action должен повторно создать popup с child layout и сохранить context.
359. Android back/swipe-back закрывает submenu перед закрытием parent menu.
360. Не использовать long-press drag на action callback item как runtime gesture.

## 0167 — пункты только при включённой фиче

361. Плановый commit: `feat: gate tele menu items`.
362. Усилие: S, после registry 0171.
363. Решение: отдельные `*_menu` под-тумблеры не добавлять.
364. Реестр хранит gate `TeleConfig` для каждого feature item.
365. Gate проверяется в момент построения меню и в editor preview.
366. Message ID item требует `MESSAGE_ID_MENU`.
367. TL item требует `VIEW_AS_TL`.
368. Emoji ID item требует `COPY_EMOJI_ID`.
369. Alias item требует `USERNAME_ALIASES`.
370. Local name item требует `LOCAL_NAMES`.
371. Shot item требует `SHOT`.
372. Mark viewed item требует `KEEP_DISAPPEARING_MEDIA`.
373. Pinned bar item требует соответствующий существующий feature toggle.
374. Link preview menu item требует link preview feature, если такой toggle добавлен позже.
375. Gate не должен читать `TeleConfig` с account 0 из background callback.
376. Изменение toggle должно refresh visible menus on UI thread.
377. Menu editor может показать off-gated item grey, но runtime не должен показывать его.
378. Audit должен пройти profile, chat, chat-row, message, send и field items.

## 0179 — copy/delete aliases

379. Плановый commit: `feat: manage aliases from menus`.
380. Усилие: S.
381. Зависит от Android 0029 и Android 0032 (`Aliases.kt` и existing names UI).
382. `Aliases` уже валидирует alias length 32 и `[letter][letter/digit/_]`.
383. `Aliases` уже хранит JSON per account в `tele_kv` key `username_aliases:<account>`.
384. В menu registry добавить keys `copy_alias`, `delete_alias` только в Profile/Chat contexts.
385. Chat message `@alias` link menu должен распознать alias через `Aliases.dialogId(currentAccount, alias)`.
386. Copy кладёт оригинальную alias text без `@` или с `@` — решение должно быть единым; [INFERENCE] рекомендовать с `@`.
387. Delete показывает confirm с alias и chat title, затем вызывает `Aliases.remove(currentAccount, alias)`.
388. После delete invalidировать mentions/search caches и refresh текущего menu.
389. Profile menu alias row использует тот же helper, не второй JSON map.
390. При `USERNAME_ALIASES` off пункты не строятся.
391. Per-account проверка обязательна при long-press на profile другого account.
392. Recycler rows/links должны rebind visibility after account switch.

## 0200 — выбирать сервисные сообщения

393. Плановый commit: `feat: select service messages`.
394. Усилие: M.
395. Hook candidate verified in docs: `ChatActivity.processRowSelect` currently excludes service rows before selection.
396. Разрешить selection только если `MessageObject.canDeleteMessage` и current action supports it.
397. `ChatActionCell` должен рисовать selected overlay/state так же, как обычный bubble.
398. Service messages должны попадать в selection count.
399. Copy, forward, save media и download должны пропускать service messages.
400. Delete/batch-delete должны использовать existing permission and flood handling.
401. Selection across mixed normal/service rows must not crash grouped messages.
402. Recycled `ChatActionCell` must clear selected state in bind.
403. Default off leaves existing exclusion unchanged.
404. Privacy: service content не отправлять в Tele server.

## 0255 — копировать путь файла

405. Плановый commit: `feat: copy downloaded file paths`.
406. Усилие: S.
407. Зависит от 0171, Android 0042 and Android 0049.
408. Add registry key `copy_file_path` to Message menu, gate `COPY_FILE_PATH`.
409. Add `BoolItem("copy_file_path", false)` and Menus row, default off.
410. Проверять только downloaded local file; не показывать для cloud-only media.
411. Resolve path through `FileLoader`/existing local media path helper, not guessed filesystem path.
412. Reject secret chat, disappearing media and inaccessible provider URI unless exact local path exists.
413. Copy path via `AndroidUtilities.addToClipboard` and show Bulletin.
414. Do not expose path to Tele server or logs.
415. On recycled menu, re-evaluate file availability at bind/open time.
416. [INFERENCE] exact `FileLoader` method name must be confirmed by grep before edit.

## 0266 — copy sticker/emoji set owner ID

417. Плановый commit: `feat: copy sticker set owner ids`.
418. Усилие: S, but data formula is unresolved.
419. Hook surfaces named by PATCHLIST: `StickersAlert`, `EmojiPacksAlert`, `PeerId.kt`.
420. Add registry keys separately for sticker set and emoji pack owner if menu context differs.
421. Add `BoolItem` default off only after confirming desktop/API semantics.
422. Owner ID must come from the set owner field/API object, not sticker document ID.
423. `TLRPC` fields are nullable; check owner object before rendering action.
424. Do not invent conversion from access hash to user ID.
425. `[INFERENCE]` portability explicitly calls formula empirical; obtain a known set with known owner and compare desktop/API values.
426. Until formula is verified, keep row hidden or show disabled explanatory state, never copy guessed number.
427. Copy bare numeric value, matching PeerId copy policy only after maintainer decision.
428. Per-account request/cache must use current account.

## 0295 — копировать текст сервисного сообщения

429. Плановый commit: `feat: copy service message text`.
430. Усилие: S.
431. Add `BoolItem("copy_service_text", false)`; settings row in Menus, default off.
432. Add `copy_service_text` item to MessageMenu registry with service context only.
433. Hook existing `ChatActivity.fillMessageMenu` after service message text is available.
434. Text must be generated from current localized `MessageObject`, not raw server-only template.
435. Preserve entities only if clipboard helper supports them; plain text is minimum.
436. Do not add item for ordinary messages because stock Copy already exists.
437. Explicitly test wallet card/service card; PATCHLIST calls out wallet-card check.
438. Gate item both by TeleConfig and message service type.
439. Default off leaves stock service menu unchanged.

## 0149 — view as TL inside application

440. Плановый commit: `feat: view TL in app`.
441. Усилие: S after Android 0051.
442. Existing `tele.helpers.ViewAsTl` is verified and gated by `TeleConfig.VIEW_AS_TL`.
443. Existing helper fetches fresh message/peer with `ConnectionsManager.sendRequest`.
444. Existing callbacks hop to UI with `AndroidUtilities.runOnUIThread`.
445. Existing serializer uses `SerializedData`, URL-safe Base64 and raw deflate above 512 bytes.
446. Existing long URL fallback creates a FileProvider redirect and opens external Browser.
447. 0149 adds an in-app `ui/web` viewer rather than changing TL serialization.
448. Add `ViewAsTl.openInApp(fragment,url)` behind same `VIEW_AS_TL` gate.
449. Use existing `ui/web` screen/Browser bridge if present; do not add a second WebView abstraction.
450. Keep external fallback for unsupported WebView or very large payload.
451. The schema URL remains third-party network and the master option is default off.
452. Never include account token or unrelated account data in URL.
453. Bind request to fragment class GUID as current helper does.
454. Close WebView on fragment destruction and cancel pending request.
455. Error callbacks must return to UI thread and show Bulletin.
456. [INFERENCE] exact existing `ui/web` class name must be confirmed before code.

## Потоки, аккаунты и privacy

457. `TeleConfig` reads/writes happen on main settings thread unless helper explicitly serializes access.
458. `TeleDatabaseHelper` SQLite calls must not run on UI for large import/export.
459. Parse/import on a worker, then atomically commit on database executor.
460. UI refresh after commit uses `AndroidUtilities.runOnUIThread`.
461. Menu construction itself runs on main thread because Android menu views are UI objects.
462. Per-account key is derived from the menu owner account, never selected account global.
463. Every `MessagesController`, `UserConfig`, `ConnectionsManager` lookup uses `currentAccount`.
464. Account switch must invalidate in-memory layout cache and reload that account.
465. Layout cache needs synchronized access or main-thread confinement; do not use unsynchronized global singleton.
466. `tele_kv` writes for migration should be transaction-like: write new, verify read/parse, then marker.
467. Existing SQLite helper has no generic transaction API; add one only in helper if required.
468. Do not change `LAST_DB_VERSION` or stock database.
469. Do not send menu layouts, aliases, file paths or service text to Tele server.
470. Network-backed TL viewer remains behind `VIEW_AS_TL` default off.
471. File path and owner ID are local clipboard data, never telemetry.
472. Notification channels are irrelevant to this batch; do not reuse them for bulletins.
473. LiteMode: editor animation and preview must respect `LiteMode` flags.
474. Use no drag animation or shorten it when LiteMode disables UI animation.
475. Do not add a custom animation that bypasses `LiteMode` or performance class.
476. Screenshot/privacy settings are not changed by menu editor.
477. `FLAG_SECURE` remains governed by existing 0113 hooks, not by 0171.
478. `onConfigChanged` should post menu refresh only to visible fragments, not every account unnecessarily.
479. Main-thread UI rows must be safe under RecyclerView recycling.
480. Every bind sets text, checked, enabled, alpha, icon, separator and badge from current state.
481. Do not capture Activity or Fragment strongly in long-lived menu caches.
482. Clear cache on `onFragmentDestroy` and account switch.

## UX и лимиты

483. Root page must remain usable on a phone width; do not reproduce desktop two-column editor literally.
484. Menu editor list shows handle, icon, label, gate state and hidden state.
485. A submenu row shows chevron and child count.
486. Separator insertion has thin/thick choice; auto is the default.
487. Drag target must have a minimum touch size compatible with Android guidelines.
488. Long press on row body starts drag only when not tapping switch/eye.
489. Keep explicit Save and Cancel buttons; back behaves as Cancel with confirmation if dirty.
490. Import preview must show number of menus, unknown keys and rejected entries before replace.
491. Export copy should show a short success Bulletin, not a Toast from background.
492. Invalid import must not partially apply any menu.
493. Full replace should be atomic across seven layouts where possible.
494. If atomic multi-row SQLite transaction is unavailable, write temp keys then commit marker.
495. Menu labels are localized display text; storage keys remain English stable IDs.
496. Titles for user-created submenus are local only and may be empty only as default title.
497. Hide action and gate action are distinct: hidden user choice survives gate off/on.
498. Turning a feature off must hide its runtime menu action but not erase its custom placement.
499. Turning it on restores it at saved position or fresh tail according to resolver policy.
500. Unknown/new future registry items must be fresh and visible only under chosen preset policy.
501. A malformed stored layout falls back to Default and keeps a diagnostic line.
502. Do not crash if a stock menu omits an item for a particular context.
503. Do not reorder fixed safety items such as destructive confirmations unless registry explicitly allows it.
504. `Power` preset must not bypass feature gates or privacy confirmations.
505. Service-message selection must respect delete permissions and channel restrictions.
506. File path action must not reveal inaccessible private storage through a misleading path.
507. Owner ID action must remain absent until its data source is proven.
508. In-app TL viewer must display loading/error/offline states.

## План commits и порядок

509. Commit 1: `feat: regroup tele settings`; 0169, M, base for search and new settings.
510. Commit 2: `feat: collapse tele setting suboptions`; 0170, S, depends on 0169.
511. Commit 3: `feat: customize all tele menus`; 0171, L, depends on Android 0042/0049/0050 and 0169.
512. Commit 4: `feat: gate tele menu items`; 0167, S, depends on registry/runtime 0171.
513. Commit 5: `feat: manage aliases from menus`; 0179, S, depends on Android 0029/0032 and registry.
514. Commit 6: `feat: select service messages`; 0200, M, independent runtime but ship after common menu/editor.
515. Commit 7: `feat: copy downloaded file paths`; 0255, S, depends on 0171 and message menu.
516. Commit 8: `feat: copy sticker set owner ids`; 0266, S, depends on confirmed owner formula and menu registry.
517. Commit 9: `feat: copy service message text`; 0295, S, depends on 0171 and service selection audit.
518. Commit 10: `feat: view TL in app`; 0149, S, depends on Android 0051 and existing ViewAsTl.
519. Queue order is intentionally 0169 → 0170 → 0171 before all menu consumers.
520. Do not combine 0171 with a consumer feature; fixes to an unreleased commit may be fixup.
521. Each commit gets its own exported `patches/android/` file.
522. Each user-facing commit updates `features.md` in the same repository commit.
523. Settings-only infrastructure may update features rows for new visible settings pages.
524. Planned patch file names are generated from subjects; never hand-edit patch files.

## features.md rows

525. Add English row for `settings structure`: pages interface/chats/messages/sending/notifications/menus/privacy/profiles and IDs/bots/debug.
526. Add English row for `collapsible sub-settings`: parent groups fold children and remember child values.
527. Add English row for `all menu editor`: seven menus, reorder/hide/groups/submenus, four presets and text clipboard import/export.
528. Add English row for `feature-gated menu items`: menu actions appear only while their feature is enabled; no separate menu toggles.
529. Add English row for alias menu actions: copy/delete alias from alias/profile menu, with username aliases default off.
530. Add English row for service selection: select service messages with permission-aware copy/forward exclusions.
531. Add English row for downloaded path: copy local path only for downloaded files, default off.
532. Add English row for sticker owner ID only after formula verification, default off.
533. Add English row for copy service text, default off, under Menus.
534. Add English row for in-app TL viewer, default follows `VIEW_AS_TL` and remains off.
535. Each row must include Android patch link and current desktop number.
536. Do not add desktop-only rows 0169/0170 as fake toggles.
537. Keep `features.md` prose user-facing; implementation anchors stay here.

## Проверка каждой фичи

538. Before build, grep every new `TeleConfig` item and confirm settings row, export spec and every callsite gate.
539. Verify no new stock DB column and no `TLRPC.java` diff.
540. Verify no old `message_menu_hidden`/`message_menu_order` is deleted before migration success.
541. Install debug APK with an existing account containing hidden and reordered message items.
542. Cold start: old hidden/order must appear in Message layout editor after migration.
543. Restart: migration must be idempotent and not duplicate entries.
544. Add second account: layout must not leak from account 0 or first account.
545. Switch accounts: editor and runtime menu must change immediately after reload.
546. Toggle parent off/on: child values survive and runtime remains gated.
547. Search each ID 1140–1159 and verify it opens the intended page/editor.
548. Search an old setting key and verify it opens its new canonical page.
549. Open all root pages; no empty click, crash or wrong back stack.
550. Message menu off/default: compare item order and visibility with stock/current behavior.
551. Message menu on: hide, drag, separator, submenu, reset and save.
552. Repeat editor for Chat, ChatRow, FolderTab, Profile, Send and Field.
553. Verify all seven runtime menus use saved layout, not only preview.
554. Import one menu line; verify only that menu changes.
555. Import seven lines; verify atomic validation and all seven changes.
556. Import malformed brackets, duplicate key, unknown menu, oversized text and wrong prefix.
557. Verify invalid import preserves previous layout byte-for-byte.
558. Select a feature-gated item in editor while feature is off; ensure it cannot execute.
559. Turn feature on; item appears at saved position or documented fresh tail.
560. Alias copy/delete: test current account and second account, then alias feature off.
561. Service selection: select, scroll, recycle, mixed rows, copy/forward exclusion and delete permissions.
562. File path: downloaded file, not downloaded file, secret/disappearing media, provider URI.
563. Owner ID: known sticker and emoji set, null owner, wrong account; do not accept guessed formula.
564. Service text: ordinary service, wallet card, localization, off behavior.
565. TL viewer: short payload, long redirect payload, request error, offline WebView, toggle off.
566. LiteMode: editor drag/preview with animation flags disabled and enabled.
567. Privacy: inspect logcat and network; no menu/layout/file path/service text uploads.
568. Threading: no `CalledFromWrongThreadException`; DB import never blocks frame loop.

## Logcat expectations

569. Migration success may log one concise `tele menu migration v2 account=N` line.
570. Unknown numeric old option may log `tele menu migration unknown code=N` without user data.
571. Invalid import may log type and reason, never clipboard contents.
572. Owner-ID unresolved case may log only a stable reason, never raw account identifiers.
573. Background parse exceptions must be caught and surfaced as a UI Bulletin.
574. No repeated migration log on every launch after marker.
575. No noisy per-menu-per-bind logs in RecyclerView.
576. With all new toggles off, logcat should show no new network request.
577. With `VIEW_AS_TL` on, only existing schema request path is allowed.
578. With `COPY_FILE_PATH` on, copying path must not trigger upload/download.
579. Use `FileLog` for diagnostics; do not use `System.out`.

## Pitfalls and explicit open questions

580. Architecture says prefs name `tele`, while current code uses `tele_config`; decide canonical name before changing it.
581. Current `tele_kv` is global, while feature data often embeds account in key; standardize menu key convention.
582. Existing MessageMenu numeric codes can change when stock adds options; migration must be one-time and keyed by current registry map.
583. Stock menu arrays may contain options absent from `MessageMenu.ALL`; resolver must preserve them at stock tail or fixed position.
584. A submenu can be created by stock code; apply must not recursively duplicate it on every open.
585. Popup menu callbacks may be invalid after a recycled holder; keep action identity, not view references.
586. `TextCheckCell` rows are recycled; never rely on constructor state for disabled child state.
587. `TeleNewSettings` can recursively call `settingIds` while building MODE_NEW; avoid new-row recursion.
588. Search ID collisions with stock are unobserved and must be checked before landing.
589. `[INFERENCE]` exact Android anchors for ChatRow, FolderTab, Send and Field are not established in the reviewed excerpt.
590. `[INFERENCE]` owner ID formula for 0266 is intentionally unresolved by portability analysis.
591. `[INFERENCE]` all-menu atomic transaction API is not present in the reviewed TeleDatabaseHelper.
592. Should legacy global message order be copied to every account or only current account? Recommended fallback-then-materialize.
593. Should new `menus` page expose one selector or seven rows? Recommended seven rows plus one editor overview.
594. Should full export use clipboard only or Android share sheet? Recommended clipboard plus share for full text.
595. Should user-created submenu titles be translated? Recommended no; store local title and show as typed.
596. Should hidden gated items be visible in editor? Recommended yes, greyed with setting link.
597. Should unknown future keys survive import? Recommended preserve only as inert diagnostics, never execute.
598. Should `copy_file_path` be under Menus or Your data? PATCHLIST says Menus; use Menus.
599. Should 0266 copy Bot API ID or Telegram peer ID? Do not decide by guess; verify desktop/API and document result.
600. Should 0149 WebView allow external navigation? Restrict to schema origin or use existing Browser policy.
601. Should service text include localized formatting entities? Start plain text; document any later entity support separately.
602. Should `MESSAGE_ID_MENU` and layout gate interact? Layout may hide; feature toggle still controls availability.
603. Should user reset restore old Android order or Desktop Default? Decision implies desktop Default; document migration result in UI.

## Batch gate

604. The batch is not `done` because pages compile; manual verification is mandatory.
605. Every ten planned rows must be committed and exported before gate.
606. Run `./gradlew :TMessagesProj_App:assembleDebug` from `Telegram` after all commits land.
607. Install the correct debug ABI APK on a device or emulator.
608. Exercise every new toggle on, off and default where applicable.
609. Exercise migration with pre-existing 0047/0057/0058 state.
610. Exercise all seven menus and all four presets.
611. Exercise text export/import with valid and invalid payloads.
612. Exercise account switching and RecyclerView recycling.
613. Exercise LiteMode and privacy/network assertions.
614. Hand over exact numbered manual steps and logcat filters to maintainer.
615. Only human confirmation may change PATCHLIST statuses to `built`, then `done`.
616. Batch gate acceptance matches PATCHLIST: pages open, search finds toggles, hidden/order migrate, presets and export/import work.
617. Conditional items 0255, 0295, 0266 and 0179 must appear only when their master feature/data is available.
618. Off/default must leave stock menu/settings behavior unchanged.
619. Update `docs/PATCHLIST.md` statuses only after export and manual verification.
620. Update `features.md` in the same per-patch repository commit.
621. No commit, patch export, source edit or generated file belongs in this documentation-only task.
