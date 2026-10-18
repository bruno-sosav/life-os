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
  sidebarOpen: false,
  setTheme: (theme) => {
    localStorage.setItem('lifeos.theme', theme)
    document.documentElement.classList.toggle('light', theme === 'light')
    set({ theme })
  },
  toggleTheme: () => set((s) => {
    const next = s.theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('lifeos.theme', next)
    document.documentElement.classList.toggle('light', next === 'light')
    return { theme: next }
  }),
  setSidebarOpen: (v) => set({ sidebarOpen: v })
}))
