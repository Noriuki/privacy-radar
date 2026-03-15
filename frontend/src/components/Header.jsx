export function Header({ theme, onToggleTheme }) {
  return (
    <header className="header">
      <div className="header-row">
        <div>
          <h1 className="logo">PrivacyRadar</h1>
          <p className="tagline">Análise de privacidade LGPD/GDPR em APIs e payloads</p>
        </div>
        {onToggleTheme && (
          <button
            type="button"
            className="btn theme-toggle"
            onClick={onToggleTheme}
            title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
            aria-label={theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        )}
      </div>
    </header>
  )
}
