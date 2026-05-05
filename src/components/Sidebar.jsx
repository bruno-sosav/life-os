import { NavLink } from 'react-router-dom'
import { useUIStore } from '../store/uiStore.js'
import { NAV_ITEMS } from './navItems.jsx'

export default function Sidebar() {
  const { theme, toggleTheme } = useUIStore()
  return (
    <aside className="hidden md:flex fixed inset-y-0 left-0 w-56 flex-col z-30 sidebar-surface">
      {/* Logo */}
      <div className="px-4 py-5 flex items-center gap-2.5 border-b border-white/[0.05]">
        <div
          className="w-9 h-9 rounded-[11px] grid place-items-center shrink-0"
          style={{ background: 'linear-gradient(135deg, #BF5AF2, #0A84FF)' }}
        >
          <span className="text-white text-base font-black">L</span>
        </div>
        <div>
          <div className="font-display font-bold text-sm">Life OS</div>
          <div className="text-[10px] text-white/30">Segundo cerebro</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2.5 py-3 space-y-0.5">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.exact}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-[12px] text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-[#0A84FF]/20 text-[#0A84FF]'
                  : 'text-white/50 hover:bg-white/[0.05] hover:text-white/80'
              }`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-2.5 border-t border-white/[0.05]">
        <button
          onClick={toggleTheme}
          className="w-full text-xs text-white/30 hover:text-white/60 px-3 py-2.5 rounded-xl hover:bg-white/[0.04] flex items-center justify-between transition"
        >
          <span>Apariencia</span>
          <span>{theme === 'dark' ? 'Oscuro' : 'Claro'}</span>
        </button>
      </div>
    </aside>
  )
}
