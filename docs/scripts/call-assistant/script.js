export default defineScript({
  name: 'call assistant',
  grants: ['calls', 'app'],
  setup(tg) {
    let autoMute = tg.storage.get('autoMute') ?? false
    let resume = false
    let connected = 0
    let muted = false
    let partner = ''

    const page = tg.ui.settingsPage({
      title: 'call assistant',
      items: () => [
        tg.ui.check({
          text: 'mute me when a call connects',
          value: autoMute,
          onChange: (value) => {
            autoMute = value
            tg.storage.set('autoMute', value)
          },
        }),
        tg.ui.notice('the music is paused while you talk and comes back after the call.'),
      ],
    })
    tg.registerSettings(page)

    tg.calls.onChange((call) => {
      if (call && !partner) {
        partner = call.user && call.user.name ? call.user.name : 'unknown'
        const track = tg.app.player.current()
        resume = track?.playing === true
        if (resume) tg.app.player.pause()
      }
      if (call?.state === 'established' && !connected) {
        connected = Date.now()
        if (autoMute && !muted) {
          muted = true
          tg.calls.setMuted(true)
          tg.toast('you are muted')
        }
      }
      if (!call && partner) {
        const minutes = connected ? Math.max(1, Math.round((Date.now() - connected) / 60000)) : 0
        tg.toast(minutes ? `call with ${partner}: ${minutes} min` : `missed or declined call with ${partner}`)
        if (resume) tg.app.player.play()
        resume = false
        connected = 0
        muted = false
        partner = ''
      }
    })
  },
})
