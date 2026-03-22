/**
 * Renderiza trechos entre ** como <strong> (estilo Markdown leve).
 */
export function TextWithBold({ children }) {
  const text = typeof children === 'string' ? children : ''
  if (!text.includes('**')) {
    return <>{text}</>
  }
  const parts = text.split('**')
  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <strong key={i}>{part}</strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  )
}
