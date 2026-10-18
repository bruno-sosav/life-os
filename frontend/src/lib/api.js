const BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

// Cliente mínimo para la API de LifeOS. Lanza Error con el detalle que devuelve FastAPI.
export async function api(path, { method = 'GET', params, body } = {}) {
  const url = new URL(`${BASE_URL}/api${path}`)
  Object.entries(params ?? {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v)
  })

  const res = await fetch(url, {
    method,
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    } catch { /* respuesta sin JSON */ }
    throw new Error(detail || `HTTP ${res.status}`)
  }
  return res.status === 204 ? null : res.json()
}
