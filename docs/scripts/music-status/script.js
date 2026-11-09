export default defineScript({
  name: 'music status',
  grants: ['call(account.updateProfile)'],
  setup(tg) {
    let normal = tg.storage.get('bio') ?? ''
    let shown = null
    let lastUpdate = 0
    let timer = 0

    const write = async (about) => {
      if (about === shown) return
      shown = about
      lastUpdate = Date.now()
      tg.log('writing bio:', about)
      await tg.call({ _: 'account.updateProfile', about })
      tg.log('bio written')
    }

    const statusOf = (track) =>
      (track?.type === 'song')
        ? `🎧 ${track.performer ? `${track.performer} - ` : ''}${track.title}`.slice(0, 70)
        : normal

    const update = () => {
      clearTimeout(timer)
      const wait = Math.max(0, lastUpdate + 30000 - Date.now())
      timer = setTimeout(() => {
        write(statusOf(tg.app.player.current())).catch((error) => console.warn('bio update failed', error))
      }, wait)
    }

    const page = tg.ui.settingsPage({
      title: 'music status',
      items: () => [
        tg.ui.input({
          text: 'my normal bio',
          value: normal,
          maxLength: 70,
          onChange: (value) => {
            normal = value
            tg.storage.set('bio', value)
            update()
          },
        }),
      ],
    })
    tg.registerSettings(page)

    // a song may already be playing: show it without waiting for the first change
    update()

    let lastKey = ''
    tg.app.player.onChange((track) => {
      tg.log('track:', track ? `${track.type} ${track.performer} - ${track.title}` : 'none')
      const key = (track?.type === 'song') ? String(track.documentId) : ''
      if (key === lastKey) return
      lastKey = key
      update()
    })
  },
})
