export default defineScript({
  name: 'drop guard',
  grants: ['interceptDrop'],
  setup(tg) {
    const RISKY = /\.(exe|msi|bat|cmd|scr|ps1|vbs|jar|apk|dmg|pkg|sh)$/i
    let limit = tg.storage.get('limitMb') ?? 500

    tg.registerSettings(tg.ui.settingsPage({
      title: 'drop guard',
      items: () => [
        tg.ui.slider({
          text: 'largest file to share into tele',
          min: 50,
          max: 2000,
          step: 50,
          value: limit,
          onChange: (value) => {
            limit = value
            tg.storage.set('limitMb', value)
          },
        }),
        tg.ui.notice('programs, scripts and files over the limit are kept away from chats.'),
      ],
    }))

    tg.interceptDrop((drop) => {
      const risky = drop.files.filter((file) => RISKY.test(file.name))
      const huge = drop.files.filter((file) => file.size > limit * 1024 * 1024)
      if (!risky.length && !huge.length) return 'accept'
      const reasons = [
        ...risky.map((file) => `${file.name} is a program or a script`),
        ...huge.map((file) => `${file.name} is ${Math.round(file.size / 1024 / 1024)} MB`),
      ]
      tg.toast(`drop guard: not sent - ${reasons.join('; ')}`)
      return 'drop'
    })
  },
})
