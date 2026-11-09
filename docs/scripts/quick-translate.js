export default defineScript({
  name: 'quick translate',
  grants: ['fetch(translate.googleapis.com)', 'fetch(www.google.com)', 'display(messages)'],
  setup(tg) {
    const target = tg.storage.get('target') ?? 'en'
    const shown = new Map()
    const pending = new Set()
    const cache = new Map()
    let retryAt = 0

    const limited = () => new Error(`Google Translate is temporarily rate-limited. Try again in ${Math.max(1, Math.ceil((retryAt - Date.now()) / 1000))} seconds.`)

    const translate = async (text) => {
      const key = `${target}:${text}`
      const cached = cache.get(key)
      if (cached && Date.now() - cached.time < 3600000) return cached.result
      if (Date.now() < retryAt) throw limited()
      const url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&dt=t'
        + `&tl=${encodeURIComponent(target)}&q=${encodeURIComponent(text)}`
      const response = await fetch(url, { timeout: 10_000 })
      if (response.status === 429) {
        const header = response.headers?.get('retry-after')
        const seconds = header != null && /^\d+$/.test(header.trim()) ? Number(header) : NaN
        const deadline = Number.isFinite(seconds) ? Date.now() + seconds * 1000 : Date.parse(header ?? '')
        retryAt = Math.max(Date.now() + 60000, Number.isFinite(deadline) ? deadline : 0)
        throw limited()
      }
      if (!response.ok) throw new Error(`translate answered ${response.status}`)
      const data = await response.json()
      const result = { text: data[0].map((part) => part[0]).join(''), from: data[2] }
      if (text.length + result.text.length <= 32768) {
        cache.delete(key)
        cache.set(key, { time: Date.now(), result })
        if (cache.size > 32) cache.delete(cache.keys().next().value)
      }
      return result
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
