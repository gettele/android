export default defineScript({
  name: 'away auto-reply',
  grants: ['onUpdate(new_message)', 'call(messages.sendMessage)'],
  setup(tg) {
    let away = tg.storage.get('away') ?? false
    const text = tg.storage.get('text') ?? "i'm away right now, i'll answer when i'm back."
    const answered = new Set()

    const send = (message, body) => tg.sendMessage(message.chat?.input ?? message.chatId, body)

    tg.registerMessageAction({
      id: 'away',
      text: 'away',
      icon: 'message',
      onClick: async (context) => {
        away = !away
        answered.clear()
        tg.storage.set('away', away)
        await tg.sendMessage(context.chatId, away ? 'away mode on' : 'welcome back')
      },
    })

    tg.onNewMessage(async (message) => {
      if (message.out) {
        if (message.text.trim() === '/away') {
          away = !away
          answered.clear()
          tg.storage.set('away', away)
          await send(message, away ? 'away mode on' : 'welcome back')
        }
        return
      }
      if (!away || message.chat?.kind !== 'user') return
      const from = message.senderId
      if (from === null || answered.has(from)) return
      answered.add(from)
      await send(message, text)
    })
  },
})
