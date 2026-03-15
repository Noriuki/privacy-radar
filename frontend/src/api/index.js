/**
 * HTTP client for PrivacyRadar API.
 * VITE_API_URL: backend base URL (e.g. http://localhost:8000).
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
    const detail = Array.isArray(err.detail) ? err.detail.map((e) => e.msg || e).join('; ') : (err.detail || res.statusText)
    throw new Error(detail)
  }
  return res.json()
}

/**
 * Scan a JSON payload for privacy risks.
 * @param {Record<string, unknown>} payload - JSON object to scan (e.g. { email, name, phone })
 * @returns {Promise<ScanReport>}
 */
export async function scanPayload(payload) {
  return request('/scan', { method: 'POST', body: payload })
}

/** Stats for observability (total scans, by risk level). */
export async function getStats() {
  return request('/stats', { method: 'GET' })
}

export const api = { scanPayload, getStats, request }
