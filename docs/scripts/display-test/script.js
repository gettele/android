export default defineScript({
  name: 'message display test',
  grants: ['display(messages)'],
  setup(tg) {
    const shown = new Map()
    tg.registerMessageAction({
      id: 'test-message-display',
      text: 'Test local text replacement',
      icon: 'message',
      onClick: async (context) => {
        const key = `${context.chatId}:${context.messageId}`
        try {
          const restore = shown.get(key)
          if (restore) {
            restore()
            shown.delete(key)
            return
          }
          const text = `Local display test ✓\n\n${context.text}`
          if (context.canReplaceText === false) {
            tg.ui.show({ title: 'Local display test', text })
            return
          }
          shown.set(key, await tg.decorateMessage(context.chatId, context.messageId, { text }))
        } catch (error) {
          tg.toast(`display test failed: ${String(error)}`)
          tg.log('display test failed', String(error))
        }
      },
    })
    tg.registerMessageAction({
      id: 'test-text-dialog',
      text: 'Test text dialog',
      icon: 'info',
      onClick: (context) => tg.ui.show({ title: 'Local display test', text: context.text }),
    })
  },
})
