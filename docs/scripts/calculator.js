export default defineScript({
  name: 'calculator',
  grants: ['call(messages.sendMessage)'],
  setup(tg) {
    const evaluate = (source) => {
      const tokens = source.match(/\d+(?:\.\d+)?|[-+*/%^()]/g) ?? []
      if (tokens.join('') !== source.replace(/\s+/g, '')) throw new Error(`not arithmetic: ${source}`)
      let index = 0
      const peek = () => tokens[index]
      const take = () => tokens[index++]
      const primary = () => {
        const token = take()
        if (token === '(') {
          const value = sum()
          if (take() !== ')') throw new Error('a ) is missing')
          return value
        }
        if (token === '-') return -primary()
        if (token === '+') return primary()
        if (token === undefined || !/^\d/.test(token)) throw new Error(`unexpected ${token ?? 'end'}`)
        return Number(token)
      }
      const power = () => {
        const base = primary()
        if (peek() !== '^') return base
        take()
        return base ** power()
      }
      const product = () => {
        let value = power()
        while (peek() === '*' || peek() === '/' || peek() === '%') {
          const operator = take()
          const right = power()
          value = operator === '*' ? value * right : operator === '/' ? value / right : value % right
        }
        return value
      }
      const sum = () => {
        let value = product()
        while (peek() === '+' || peek() === '-') {
          const operator = take()
          const right = product()
          value = operator === '+' ? value + right : value - right
        }
        return value
      }
      const result = sum()
      if (index !== tokens.length) throw new Error(`unexpected ${peek()}`)
      return result
    }

    const reply = async (chat, source) => {
      const expression = source.trim().replace(/^\/calc\s+/, '')
      try {
        const value = evaluate(expression)
        if (!Number.isFinite(value)) throw new Error(`${expression} has no finite result`)
        await tg.sendMessage(chat, `${expression} = ${Number(value.toPrecision(12))}`)
      } catch (error) {
        await tg.sendMessage(chat, `can't calculate: ${error.message}`)
      }
    }

    tg.registerMessageAction({
      id: 'calculate',
      text: 'calculate',
      icon: 'stats',
      onClick: (context) => reply(context.chatId, context.text),
    })
  },
})
