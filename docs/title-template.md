# chat list title template

settings → tele → interface. the title above the chat list takes a template.

the default is `tele {build}`. an empty template shows the app name.

- `{build}` (the build number, `dev` for local builds), `{version}`
- `{time}`, `{date}`, `{weekday}`, `{day}`, `{month}`, or a java date format like `{time:HH:mm:ss}` and `{date:dd MMM}`
- `{name}`, `{username}`, `{id}`, `{accounts}`
- `{unread}`, `{status}`

any variable takes modifiers after `|`, applied left to right: `{weekday|short|lower}` is `sun`, `{date:EEEE|upper}` is `SUNDAY`.

- `lower`, `upper`: `{weekday|lower}` is `sunday`
- `title` capitalizes every word, `cap` only the first letter
- `short` is the compact form, wherever it sits in the chain: `Sun` and `Sep` for weekday and month, the first name for `{name}`, `7.2` for `{version}`, `1.2k` for counters, `…` for `{status}`. other variables stay as they are
- `first`, `last`: the first or last word, `{name|first}`
- `max:N` cuts to N characters with `…`, `{name|max:20}`
- `pad:N` pads to N characters, with zeros for numbers: `{day|pad:2}` is `07`
- `k` shortens numbers: `1234` is `1.2k`, `15000` is `15k`, `2500000` is `2.5m`
- `default:text` shows text when the value is empty or 0, `{status|default:online}`

`[ … ]` hides its part when a variable inside is empty or 0, so `tele {build}[ · {unread} unread]` doesn't show "· 0 unread". a `default` counts as filled. doubled brackets are literal. a `|` that isn't followed by modifiers stays part of a java date format, and `'|'` in quotes always does. a variable or modifier with a typo is shown as typed.

the editor highlights variables in the field and points out mistakes under the preview. below are all the variables as chips: tap one to insert it, hold it for its other forms with their current values. presets has a few ready templates, and reset brings back `tele {build}`.

time and date formats are java patterns, not qt ones: use `HH:mm`, `dd MMM`, `EEEE` and so on. the title updates itself: it ticks every second or minute when the template has time or date variables, and it listens for unread counts, the connection state, your name and account changes.

this is the android title: there is no window title, taskbar or alt-tab, so `{label}`, `{chat}` and `{chat_unread}` are not here. the label above the chat list is the only place the template is shown.
