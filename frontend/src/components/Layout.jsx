import { Header } from './Header'
import { Footer } from './Footer'

export function Layout({ children, theme, onToggleTheme }) {
  return (
    <>
      <Header theme={theme} onToggleTheme={onToggleTheme} />
      <main className="main">{children}</main>
      <Footer />
    </>
  )
}
