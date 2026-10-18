import { create } from 'zustand'

const KEY = 'lifeos.session'

function loadSession() {
  try {
    const session = JSON.parse(localStorage.getItem(KEY))
    if (session?.token && new Date(session.expiresAt) > new Date()) return session
  } catch { /* sesión corrupta o storage bloqueado */ }
  localStorage.removeItem(KEY)
  return null
}

export const useAuthStore = create((set) => ({
  session: loadSession(),
  login: (token, expiresAt) => {
    const session = { token, expiresAt }
    localStorage.setItem(KEY, JSON.stringify(session))
    set({ session })
  },
  logout: () => {
    localStorage.removeItem(KEY)
    // Borra las respuestas de la API que el service worker guardó para modo offline
    if ('caches' in window) caches.delete('api-cache')
    set({ session: null })
  },
}))
