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
        const key = `${context.chatId}:${context.messageId}`
        const existing = shown.get(key)
        if (existing) {
          existing()
          shown.delete(key)
          return
        }
        try {
          const result = await translate(context.text)
          shown.set(key, await tg.decorateMessage(context.chatId, context.messageId, {
            footer: `${result.from} → ${target}: ${result.text}`,
          }))
        } catch (error) {
          tg.log('translate failed', String(error))
        }
      },
    })
  },
})
