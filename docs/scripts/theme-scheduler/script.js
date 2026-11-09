export default defineScript({
  name: 'theme scheduler',
  grants: ['app'],
  setup(tg) {
    const TIME = /^([01]?\d|2[0-3]):([0-5]\d)$/
    let night = tg.storage.get('night') ?? '21:00'
    let day = tg.storage.get('day') ?? '07:30'
    let schedules = []

    const minutes = (time) => {
      const found = TIME.exec(time)
      if (!found) return 0
      return Number(found[1]) * 60 + Number(found[2])
    }

    const shouldBeDark = () => {
      const now = new Date()
      const current = now.getHours() * 60 + now.getMinutes()
      const from = minutes(night)
      const to = minutes(day)
      return from > to ? (current >= from || current < to) : (current >= from && current < to)
    }

    const arm = () => {
      for (const dispose of schedules) dispose()
      schedules = [
        tg.schedule({ daily: night }, () => tg.app.theme.setDark(true)),
        tg.schedule({ daily: day }, () => tg.app.theme.setDark(false)),
      ]
      tg.app.theme.setDark(shouldBeDark())
    }

    const timeRow = (text, value, save) => tg.ui.input({
      text,
      value,
      placeholder: 'HH:MM',
      maxLength: 5,
      onChange: (next) => {
        if (!TIME.test(next.trim())) {
          tg.toast(`"${next}" isn't a time like 21:00`)
          return
        }
        save(next.trim())
        arm()
      },
    })

    tg.onUnload(() => {
      for (const dispose of schedules) dispose()
      schedules = []
    })

    tg.registerSettings(tg.ui.settingsPage({
      title: 'theme scheduler',
      items: () => [
        timeRow('night mode from', night, (value) => { night = value; tg.storage.set('night', value) }),
        timeRow('day mode from', day, (value) => { day = value; tg.storage.set('day', value) }),
      ],
    }))
    arm()
  },
})
