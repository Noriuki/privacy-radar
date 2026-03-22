import { useState, useEffect, useCallback } from 'react'
import {
  getLgpdQuestions,
  submitLgpdChecklist,
  analyzeOpenApiContract,
  analyzeGraphqlContract,
} from '../api'
import { TextWithBold } from '../components'
import { labelMaturidade, labelTipoCampo, maturityBadgeClass } from '../utils/labels'
import { detectContractKind } from '../utils/detectContractKind'

export function HomePage() {
  const [tab, setTab] = useState('lgpd')
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [lgpdResult, setLgpdResult] = useState(null)
  const [contractText, setContractText] = useState('')
  const [contractResult, setContractResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    getLgpdQuestions()
      .then((d) => {
        setQuestions(d.questions || [])
        const init = {}
        ;(d.questions || []).forEach((q) => {
          if (q.options?.[0]) init[q.id] = q.options[0].value
        })
        setAnswers(init)
      })
      .catch(() => setError('Não foi possível carregar o questionário.'))
  }, [])

  const handleLgpdSubmit = async () => {
    setError(null)
    setLgpdResult(null)
    setLoading(true)
    try {
      const data = await submitLgpdChecklist(answers)
      setLgpdResult(data)
    } catch (e) {
      setError(e.message || 'Erro')
    } finally {
      setLoading(false)
    }
  }

  const handleContractSubmit = async () => {
    setError(null)
    setContractResult(null)
    setLoading(true)
    try {
      const parsed = JSON.parse(contractText)
      const kind = detectContractKind(parsed)
      if (!kind) {
        setError(
          'Não foi possível identificar o formato: use JSON OpenAPI 3.x / Swagger (com paths ou campo openapi/swagger) ou introspection GraphQL (com __schema.types).',
        )
        return
      }
      const data =
        kind === 'openapi' ? await analyzeOpenApiContract(parsed) : await analyzeGraphqlContract(parsed)
      setContractResult(data)
    } catch (e) {
      setError(e.message || 'JSON inválido ou erro na API')
    } finally {
      setLoading(false)
    }
  }

  const copyJson = useCallback((obj) => {
    navigator.clipboard.writeText(JSON.stringify(obj, null, 2)).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }, [])

  return (
    <>
      <nav className="tabs" aria-label="Modo">
        <button
          type="button"
          className={`tab ${tab === 'lgpd' ? 'active' : ''}`}
          onClick={() => {
            setTab('lgpd')
            setError(null)
          }}
        >
          Questionário LGPD
        </button>
        <button
          type="button"
          className={`tab ${tab === 'contract' ? 'active' : ''}`}
          onClick={() => {
            setTab('contract')
            setError(null)
          }}
        >
          Contrato API (OpenAPI / GraphQL)
        </button>
      </nav>

      {tab === 'lgpd' && (
        <section className="panel">
          <div className="split-head">
            <h2>5 perguntas (LGPD)</h2>
            <p className="hint">
              Bem amplas: pense no produto como um todo. Sem juridiquês — só dicas práticas e referência a artigos da LGPD
              no relatório (não é parecer jurídico).
            </p>
          </div>
          <div className="split-grid">
            <div className="split-col split-col--form">
              {questions.length === 0 && <p className="muted">Carregando perguntas…</p>}
              {questions.map((q) => (
                <div key={q.id} className="q-block">
                  <label className="q-label" htmlFor={q.id}>
                    <TextWithBold>{q.text}</TextWithBold>
                  </label>
                  <select
                    id={q.id}
                    className="select"
                    value={answers[q.id] ?? ''}
                    onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
                  >
                    {(q.options || []).map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
              <div className="form-actions">
                <button
                  type="button"
                  className="btn primary"
                  onClick={handleLgpdSubmit}
                  disabled={loading || !questions.length}
                >
                  {loading ? 'Gerando relatório…' : 'Gerar relatório LGPD'}
                </button>
              </div>
              {error && tab === 'lgpd' && (
                <div className="result error" role="alert" style={{ marginTop: '0.75rem' }}>
                  {error}
                </div>
              )}
            </div>
            <div className="split-col split-col--analysis">
              <h3 className="analysis-pane-title">Análise</h3>
              {!lgpdResult && (
                <div className="split-placeholder">O relatório aparece aqui depois que você enviar o questionário.</div>
              )}
              {lgpdResult && (
                <div className="result report report-enter">
                  <div className="report-header">
                    <h3 className="report-title">Relatório de maturidade</h3>
                    <button type="button" className="btn btn-copy" onClick={() => copyJson(lgpdResult)}>
                      {copied ? '✓ Copiado' : '📋 Copiar JSON'}
                    </button>
                  </div>
                  <p>
                    <strong>Score:</strong> {lgpdResult.score}/100 · <strong>Maturidade:</strong>{' '}
                    <span className={`score-badge ${maturityBadgeClass(lgpdResult.maturity)}`}>
                      {labelMaturidade(lgpdResult.maturity)}
                    </span>
                  </p>
                  <p className="disclaimer">{lgpdResult.disclaimer}</p>
                  {lgpdResult.gaps?.length > 0 && (
                    <>
                      <h4>Lacunas e artigos</h4>
                      <ul className="gaps-list">
                        {lgpdResult.gaps.map((g, i) => (
                          <li key={i}>
                            <strong>{g.article}</strong> — {g.title}: {g.gap}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                  <h4>Recomendações</h4>
                  <ul className="rec-list">
                    {lgpdResult.recommendations?.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {tab === 'contract' && (
        <section className="panel">
          <div className="split-head">
            <h2>Mapa de superfície — contrato da API</h2>
            <p className="hint">
              Cole o JSON do <strong>OpenAPI 3.x</strong> ou o resultado de <strong>introspection</strong> GraphQL — o
              formato é detectado automaticamente. O sistema mapeia endpoints/tipos e campos com nomes que sugerem dados
              pessoais.
            </p>
          </div>
          <div className="split-grid">
            <div className="split-col split-col--form">
              <label htmlFor="contract-json">JSON</label>
              <textarea
                id="contract-json"
                className="input"
                rows={14}
                placeholder='Cole o JSON do OpenAPI 3.x ou da introspection GraphQL…'
                value={contractText}
                onChange={(e) => setContractText(e.target.value)}
              />
              <div className="form-actions">
                <button type="button" className="btn primary" onClick={handleContractSubmit} disabled={loading}>
                  {loading ? 'Analisando…' : 'Analisar contrato'}
                </button>
              </div>
              {error && tab === 'contract' && (
                <div className="result error" role="alert" style={{ marginTop: '0.75rem' }}>
                  {error}
                </div>
              )}
            </div>
            <div className="split-col split-col--analysis">
              <h3 className="analysis-pane-title">Análise</h3>
              {!contractResult && (
                <div className="split-placeholder">
                  O resultado da análise (endpoints, campos e recomendações) aparece aqui depois que você enviar o JSON.
                </div>
              )}
              {contractResult && (
                <div className="result report report-enter">
                  <div className="report-header">
                    <h3 className="report-title">
                      {contractResult.graphql === true ? 'GraphQL' : 'OpenAPI'} — resultado
                    </h3>
                    <button type="button" className="btn btn-copy" onClick={() => copyJson(contractResult)}>
                      {copied ? '✓ Copiado' : '📋 Copiar JSON'}
                    </button>
                  </div>
                  {contractResult.error && <p className="error-inline">{contractResult.error}</p>}
                  {contractResult.graphql !== true && contractResult.endpoints && (
                    <>
                      <p className="muted">
                        {contractResult.title && <strong>{contractResult.title}</strong>}
                        {contractResult.summary && (
                          <>
                            {' '}
                            · Operações analisadas: {contractResult.summary.total_operations_with_schema ?? '—'} · Com
                            campos pessoais (heurística):{' '}
                            {contractResult.summary.operations_with_personal_data_fields ?? '—'}
                          </>
                        )}
                      </p>
                      <ul className="endpoint-list">
                        {contractResult.endpoints.map((ep, i) => (
                          <li key={i} className="endpoint-card">
                            <code>
                              {ep.method} {ep.path}
                            </code>
                            {!ep.security_documented && (
                              <span className="badge-warn">sem autenticação documentada</span>
                            )}
                            {(ep.parameters_sensitive?.length > 0 ||
                              ep.request_body_sensitive?.length > 0 ||
                              ep.response_sensitive?.length > 0) && (
                              <div className="sens-grid">
                                {ep.parameters_sensitive?.length > 0 && (
                                  <span>
                                    Parâmetros:{' '}
                                    {ep.parameters_sensitive
                                      .map((p) => `${p.field} (${labelTipoCampo(p.type)})`)
                                      .join(', ')}
                                  </span>
                                )}
                                {ep.request_body_sensitive?.length > 0 && (
                                  <span>
                                    Corpo:{' '}
                                    {ep.request_body_sensitive
                                      .map((p) => `${p.field} (${labelTipoCampo(p.type)})`)
                                      .join(', ')}
                                  </span>
                                )}
                                {ep.response_sensitive?.length > 0 && (
                                  <span>
                                    Resposta:{' '}
                                    {ep.response_sensitive
                                      .map((p) => `${p.field} (${labelTipoCampo(p.type)})`)
                                      .join(', ')}
                                  </span>
                                )}
                              </div>
                            )}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                  {contractResult.graphql === true && contractResult.types_with_personal_data_hints && (
                    <ul className="endpoint-list">
                      {contractResult.types_with_personal_data_hints.map((t, i) => (
                        <li key={i} className="endpoint-card">
                          <strong>{t.type_name}</strong>
                          <div className="sens-grid">
                            {t.sensitive_fields?.map((f, j) => (
                              <span key={j}>
                                {f.field} ({labelTipoCampo(f.type)})
                              </span>
                            ))}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                  {contractResult.recommendations && (
                    <>
                      <h4>Recomendações</h4>
                      <ul className="rec-list">
                        {contractResult.recommendations.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      )}

    </>
  )
}
