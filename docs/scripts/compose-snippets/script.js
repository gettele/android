export default defineScript({
  name: 'compose snippets',
  grants: ['account.read(draft, peers)', 'account.write(draft)'],
  setup(tg) {
    let snippets = tg.storage.get('snippets') ?? { ':shrug:': '¯\\_(ツ)_/¯', ':tm:': '™' }

    const save = () => {
      tg.storage.set('snippets', snippets)
      page.invalidate()
    }

    const page = tg.ui.settingsPage({
      title: 'compose snippets',
      items: () => [
        tg.ui.header('snippets'),
        ...Object.entries(snippets).map(([code, text]) => tg.ui.item({
          id: code,
          text: code,
          detail: text.length > 24 ? `${text.slice(0, 24)}...` : text,
          onClick: () => {
            delete snippets[code]
            save()
          },
        })),
        tg.ui.button({
          text: 'add a snippet',
          onClick: async () => {
            const code = await tg.ui.prompt({ title: 'code', placeholder: ':code:', maxLength: 32 })
            if (!code || !code.trim()) return
            const value = await tg.ui.prompt({ title: `${code.trim()} expands to` })
            if (value === null) return
            snippets = { ...snippets, [code.trim()]: value }
            save()
          },
        }),
      ],
    })
    tg.registerSettings(page)

    tg.compose.onInput(({ text }) => {
      let next = text
      for (const [code, value] of Object.entries(snippets)) next = next.split(code).join(value)
      if (next !== text) tg.compose.set(next)
    })
  },
})
