/**
 * PrivacyRadar API — LGPD checklist + OpenAPI/GraphQL contract analysis.
 */

const API_BASE =
  (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL.replace(/\/$/, '')) || 'http://localhost:8000'
const API_PREFIX = `${API_BASE}/api/v1`

export async function request(endpoint, options = {}) {
  const { method = 'GET', body } = options
  const res = await fetch(`${API_PREFIX}${endpoint}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(body != null && { body: JSON.stringify(body) }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const detail = Array.isArray(err.detail)
      ? err.detail.map((e) => e.msg || e).join('; ')
      : err.detail || res.statusText
    throw new Error(detail)
  }
  return res.json()
}

export async function getLgpdQuestions() {
  return request('/lgpd/questions', { method: 'GET' })
}

export async function submitLgpdChecklist(answers) {
  return request('/lgpd/submit', { method: 'POST', body: { answers } })
}

export async function analyzeOpenApiContract(spec) {
  return request('/contract/openapi', { method: 'POST', body: spec })
}

export async function analyzeGraphqlContract(schemaDoc) {
  return request('/contract/graphql', { method: 'POST', body: schemaDoc })
}

export const api = {
  getLgpdQuestions,
  submitLgpdChecklist,
  analyzeOpenApiContract,
  analyzeGraphqlContract,
  request,
}
