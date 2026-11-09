export default defineScript({
  name: 'quick translate',
  grants: ['fetch(translate.googleapis.com)', 'display(messages)'],
  setup(tg) {
    const target = tg.storage.get('target') ?? 'en'
    const shown = new Map()

    const translate = async (text) => {
      const url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&dt=t'
        + `&tl=${encodeURIComponent(target)}&q=${encodeURIComponent(text)}`
      const response = await fetch(url, { timeout: 10_000 })
      if (!response.ok) throw new Error(`translate answered ${response.status}`)
      const data = await response.json()
      return { text: data[0].map((part) => part[0]).join(''), from: data[2] }
    }

    tg.registerMessageAction({
      id: 'translate',
      text: 'translate',
      icon: 'message',
      onClick: async (context) => {
        try {
          const result = await translate(context.text)
          tg.toast(`${result.from} → ${target}: ${result.text}`)
        } catch (error) {
          tg.toast(`translate failed: ${String(error)}`)
          tg.log('translate failed', String(error))
        }
      },
    })
  },
})
