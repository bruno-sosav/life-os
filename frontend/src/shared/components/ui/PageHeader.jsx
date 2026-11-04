import { useAuthStore } from '../../store/authStore.js'

function LogoutIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  )
}

export default function PageHeader({ title, subtitle, actions }) {
  const logout = useAuthStore((s) => s.logout)

  return (
    <div className="mb-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            {title}
          </h1>
          {subtitle && <p className="text-sm text-ink-400 mt-1">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          {actions}
          <button
            onClick={logout}
            className="md:hidden w-9 h-9 rounded-lg bg-ink-800 border border-ink-700 grid place-items-center text-ink-400 hover:text-down transition"
            title="Cerrar sesión"
            aria-label="Cerrar sesión"
          >
            <LogoutIcon />
          </button>
        </div>
      </div>
    </div>
  )
}
