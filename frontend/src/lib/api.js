import { useAuthStore } from '../store/authStore.js'

const BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

// Cliente mínimo para la API de LifeOS. Agrega el token de sesión y lanza Error con el
// detalle que devuelve FastAPI. Un 401 en cualquier ruta cierra la sesión.
export async function api(path, { method = 'GET', params, body } = {}) {
  const url = new URL(`${BASE_URL}/api${path}`)
  Object.entries(params ?? {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v)
  })

  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const token = useAuthStore.getState().session?.token
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401 && path !== '/auth/login') useAuthStore.getState().logout()

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
