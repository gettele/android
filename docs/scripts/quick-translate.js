export default defineScript({
  name: 'quick translate',
  grants: ['fetch(translate.googleapis.com)', 'fetch(www.google.com)', 'display(messages)'],
  setup(tg) {
    const target = tg.storage.get('target') ?? 'en'
    const shown = new Map()
    const pending = new Set()

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
        const restore = shown.get(key)
        if (restore) {
          restore()
          shown.delete(key)
          return
        }
        if (pending.has(key)) return
        pending.add(key)
        tg.log('translate tapped:', context.messageId)
        try {
          const result = await translate(context.text)
          tg.log('translated:', result.text.length, 'chars')
          if (context.canReplaceText === false) {
            tg.ui.show({ title: `${result.from} → ${target}`, text: result.text })
            return
          }
          try {
            const dispose = await tg.decorateMessage(context.chatId, context.messageId, { text: result.text })
            shown.set(key, dispose)
          } catch (error) {
            tg.log('message decoration failed:', String(error))
            tg.ui.show({ title: `${result.from} → ${target}`, text: result.text })
          }
        } catch (error) {
          tg.toast(`translate failed: ${String(error)}`)
          tg.log('translate failed', String(error))
        } finally {
          pending.delete(key)
        }
      },
    })
  },
})
