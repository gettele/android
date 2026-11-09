export default defineScript({
  name: 'async display test',
  grants: ['display(messages)'],
  setup(tg) {
    let enabled = false
    let dispose = null
    tg.registerMessageAction({
      id: 'toggle-async-decoration',
      text: 'Toggle async decorator test',
      icon: 'message',
      onClick() {
        enabled = !enabled
        if (dispose) {
          dispose()
          dispose = null
        }
        if (enabled) {
          dispose = tg.decorateMessages(async (message) => {
            if (!message.text?.startsWith('async-test:')) return null
            await new Promise(resolve => setTimeout(resolve, 1500))
            return { text: `Async decoration ✓\n${message.text}` }
          })
        }
        tg.toast(enabled ? 'Async test enabled: use messages starting with async-test:' : 'Async test disabled')
      },
    })
  },
})
