import { useState, useEffect } from 'react'
import { HomePage } from './pages'
import { Layout } from './components'
import './styles/global.css'
import './styles/app.css'

const THEME_KEY = 'privacyRadarTheme'

export default function App() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem(THEME_KEY) || 'dark'
    } catch {
      return 'dark'
    }
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    try {
      localStorage.setItem(THEME_KEY, theme)
    } catch (_) {}
  }, [theme])

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))

  return (
    <Layout theme={theme} onToggleTheme={toggleTheme}>
      <HomePage />
    </Layout>
  )
}
