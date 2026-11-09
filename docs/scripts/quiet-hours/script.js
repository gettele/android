export default defineScript({
  name: 'quiet hours',
  grants: ['interceptNotification', 'account.read(messages)'],
  setup(tg) {
    let from = tg.storage.get('from') ?? 22
    let to = tg.storage.get('to') ?? 8
    let mentions = tg.storage.get('mentions') ?? true
    let hidden = 0

    const quietNow = () => {
      const hour = new Date().getHours()
      return from === to ? false : from < to ? (hour >= from && hour < to) : (hour >= from || hour < to)
    }

    const hourRow = (text, value, save) => tg.ui.slider({
      text,
      min: 0,
      max: 23,
      value,
      onChange: (next) => {
        save(next)
        page.invalidate()
      },
    })

    const page = tg.ui.settingsPage({
      title: 'quiet hours',
      items: () => [
        hourRow('quiet from', from, (value) => { from = value; tg.storage.set('from', value) }),
        hourRow('until', to, (value) => { to = value; tg.storage.set('to', value) }),
        tg.ui.check({
          text: 'let mentions through',
          value: mentions,
          onChange: (value) => { mentions = value; tg.storage.set('mentions', value) },
        }),
        tg.ui.notice(`${hidden} notifications hidden since tele started.`),
      ],
    })
    tg.registerSettings(page)

    tg.interceptNotification(({ kind, message }) => {
      if (!quietNow()) return 'show'
      if (mentions && kind === 'message' && message?.mentioned) return 'show'
      hidden++
      return 'drop'
    })
  },
})
