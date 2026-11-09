export default defineScript({
  name: 'async fetch test',
  grants: ['fetch(httpbin.org)'],
  setup(tg) {
    tg.registerMessageAction({
      id: 'test-async-fetch',
      text: 'Test async fetch and abort',
      icon: 'info',
      onClick: async () => {
        const controller = new AbortController()
        let timerRan = false
        const timer = setTimeout(() => {
          timerRan = true
          tg.log('timer ran while fetch was pending')
          controller.abort()
        }, 300)
        try {
          tg.log('starting delayed fetch')
          const response = await fetch('https://httpbin.org/delay/5', { signal: controller.signal })
          tg.log('fetch finished before cancellation:', response.status)
        } catch (error) {
          tg.log('fetch rejected:', error.name, String(error), 'timer ran:', timerRan)
          tg.toast(timerRan ? 'Timer ran and fetch was cancelled; check the log' : 'Request failed before the timer; check the log')
        } finally {
          clearTimeout(timer)
        }
      },
    })
  },
})
