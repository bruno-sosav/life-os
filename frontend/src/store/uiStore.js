import { create } from 'zustand'

const initialTheme = (() => {
  if (typeof window === 'undefined') return 'dark'
  return localStorage.getItem('lifeos.theme') || 'dark'
})()

if (typeof document !== 'undefined') {
  document.documentElement.classList.toggle('light', initialTheme === 'light')
}

export const useUIStore = create((set) => ({
  theme: initialTheme,
  toggleTheme: () => set((s) => {
    const next = s.theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('lifeos.theme', next)
    document.documentElement.classList.toggle('light', next === 'light')
    return { theme: next }
  })
}))
