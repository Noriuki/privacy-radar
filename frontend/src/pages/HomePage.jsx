import { useState, useEffect, useCallback } from 'react'
import { scanPayload, getStats } from '../api'

const STORAGE_LAST = 'privacyRadarLastScan'
const STORAGE_HISTORY = 'privacyRadarHistory'

const EXAMPLES = [
  {
    label: 'Pessoal (email, nome, telefone)',
    payload: { email: 'user@email.com', name: 'John Doe', phone: '+551199999999' },
  },
  {
    label: 'Com CPF e endereço',
    payload: {
      nome: 'Maria Silva',
      cpf: '123.456.789-00',
      email: 'maria@example.com',
      endereco: 'Rua das Flores, 100',
      cep: '01310-100',
    },
  },
  {
    label: 'Vazio (sem PII)',
    payload: { productId: 'abc-123', quantity: 2, discount: 0.1 },
  },
]

const DEFAULT_JSON = JSON.stringify(EXAMPLES[0].payload, null, 2)

function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_HISTORY)
    if (!raw) return []
    const list = JSON.parse(raw)
    return Array.isArray(list) ? list.slice(0, 5) : []
  } catch {
    return []
  }
}

function saveToHistory(entry) {
  try {
    const list = loadHistory()
    const next = [entry, ...list.filter((e) => e.at !== entry.at)].slice(0, 5)
    localStorage.setItem(STORAGE_HISTORY, JSON.stringify(next))
  } catch (_) {}
}

export function HomePage() {
  const [payloadText, setPayloadText] = useState(DEFAULT_JSON)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)
  const [stats, setStats] = useState(null)
  const [history, setHistory] = useState(loadHistory)

  const handleScan = useCallback(async () => {
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const payload = JSON.parse(payloadText)
      if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
        throw new Error('Payload deve ser um objeto JSON')
      }
      const data = await scanPayload(payload)
      setResult(data)
      saveToHistory({
        payload: payloadText,
        result: data,
        at: Date.now(),
        risk: data.risk_level,
        score: data.score,
      })
      setHistory(loadHistory())
      try {
        const s = await getStats()
        setStats(s)
      } catch (_) {}
    } catch (err) {
      setError(err.message || 'Erro ao escanear')
    } finally {
      setLoading(false)
    }
  }, [payloadText])

  useEffect(() => {
    const onKey = (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault()
        handleScan()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [handleScan])

  const handleCopyReport = () => {
    if (!result) return
    const text = JSON.stringify(result, null, 2)
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const loadFromHistory = (entry) => {
    setPayloadText(entry.payload)
    setResult(entry.result)
    setError(null)
  }

  return (
    <section className="panel">
        <h2>Escanear payload</h2>
        <p className="hint">
          Cole um JSON (objeto) ou use um exemplo. <kbd>Ctrl+Enter</kbd> para escanear.
        </p>

        <div className="examples-row">
          <span className="examples-label">Exemplos:</span>
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              className="btn btn-example"
              onClick={() => setPayloadText(JSON.stringify(ex.payload, null, 2))}
            >
              {ex.label}
            </button>
          ))}
        </div>

        <label htmlFor="payload">JSON</label>
        <textarea
          id="payload"
          className="input"
          rows={10}
          placeholder='{"email": "...", "name": "...", "phone": "..."}'
          value={payloadText}
          onChange={(e) => setPayloadText(e.target.value)}
        />
        <button
          type="button"
          className="btn primary"
          onClick={handleScan}
          disabled={loading}
        >
          {loading ? 'Escanando…' : 'Escanear'}
        </button>

        {error && (
          <div className="result error" role="alert">
            {error}
          </div>
        )}

        {result && !error && (
          <div className={`result report report-enter risk-${result.risk_level}`}>
            <div className="report-header">
              <h3 className="report-title">Privacy Radar Report</h3>
              <div className="report-actions">
                <button
                  type="button"
                  className="btn btn-copy"
                  onClick={handleCopyReport}
                  title="Copiar relatório (JSON)"
                >
                  {copied ? '✓ Copiado!' : '📋 Copiar'}
                </button>
              </div>
            </div>

            <div className="report-section">
              <h4>Campos sensíveis detectados</h4>
              {result.sensitive_fields.length === 0 ? (
                <p className="muted">Nenhum campo sensível detectado.</p>
              ) : (
                <ul className="field-list">
                  {result.sensitive_fields.map((f, i) => (
                    <li key={i}>
                      <strong>{f.field_name}</strong> ({f.pattern_type})
                      {f.sample_value && (
                        <span className="sample"> — {f.sample_value}</span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="report-section score-section">
              <span className="score-label">Nível de risco</span>
              <span className={`score-badge risk-${result.risk_level}`}>
                {result.risk_level}
              </span>
              <span className="score-label">Score</span>
              <span className="score-value">{result.score}/100</span>
            </div>

            {result.risks?.length > 0 && (
              <div className="report-section">
                <h4>Riscos</h4>
                <ul className="risks-list">
                  {result.risks.map((r, i) => (
                    <li key={i} className={`risk-item severity-${r.severity}`}>
                      <span className="risk-code" title={r.recommendation}>{r.code}</span>
                      <span className="risk-desc">{r.description}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="report-section">
              <h4>Recomendações</h4>
              <ul className="rec-list">
                {result.recommendations?.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {stats && (stats.total_scans > 0) && (
          <div className="stats-bar">
            <span className="muted">
              Total de escaneamentos nesta sessão: <strong>{stats.total_scans}</strong>
              {stats.by_risk_level && Object.keys(stats.by_risk_level).length > 0 && (
                <> · Por nível: {Object.entries(stats.by_risk_level).map(([k, v]) => `${k}: ${v}`).join(', ')}</>
              )}
            </span>
          </div>
        )}

        {history.length > 0 && (
          <div className="history-section">
            <h4>Últimos escaneamentos</h4>
            <ul className="history-list">
              {history.map((entry, i) => (
                <li key={entry.at || i} className="history-item">
                  <span className={`score-badge risk-${entry.risk}`}>{entry.risk}</span>
                  <span className="history-score">{entry.score}/100</span>
                  <button
                    type="button"
                    className="btn btn-link"
                    onClick={() => loadFromHistory(entry)}
                  >
                    Restaurar
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
    </section>
  )
}
