function Ico({ children }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  )
}

export const NAV_ITEMS = [
  {
    to: '/', label: 'Hoy', exact: true,
    icon: <Ico><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></Ico>
  },
  {
    to: '/fisico', label: 'Físico',
    icon: <Ico><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></Ico>
  },
  {
    to: '/negocio', label: 'Negocio',
    icon: <Ico><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></Ico>
  },
  {
    to: '/mental', label: 'Mental',
    icon: <Ico><line x1="12" y1="2" x2="12" y2="6"/><path d="M12 6a6 6 0 016 6c0 4-3 6-6 6s-6-2-6-6a6 6 0 016-6z"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.22" y1="4.22" x2="7.05" y2="7.05"/><line x1="19.78" y1="4.22" x2="16.95" y2="7.05"/></Ico>
  },
  {
    to: '/finanzas', label: 'Finanzas',
    icon: <Ico><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></Ico>
  },
  {
    to: '/listas', label: 'Listas',
    icon: <Ico><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></Ico>
  },
  {
    to: '/analytics', label: 'Stats',
    icon: <Ico><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></Ico>
  },
]
