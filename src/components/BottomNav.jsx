import { NavLink } from 'react-router-dom'
import { NAV_ITEMS } from './navItems.jsx'

export default function BottomNav() {
  return (
    <nav
      className="md:hidden fixed bottom-0 inset-x-0 z-30 safe-area-bottom"
      style={{
        background: 'rgba(10,10,20,0.88)',
        borderTop: '1px solid rgba(255,255,255,0.07)',
        backdropFilter: 'blur(30px)',
        WebkitBackdropFilter: 'blur(30px)',
        paddingBottom: 'env(safe-area-inset-bottom)'
      }}
    >
      <ul className="grid grid-cols-6">
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.exact}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center gap-1 py-3 min-h-[56px] ${
                  isActive ? 'text-[#0A84FF]' : 'text-white/35'
                }`
              }
            >
              <span className="text-xl leading-none">{item.icon}</span>
              <span className="text-[9px] font-semibold tracking-wide">{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
