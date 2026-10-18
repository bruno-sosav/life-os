import { NavLink } from 'react-router-dom'
import { NAV_ITEMS } from './navItems.jsx'

export default function BottomNav() {
  return (
    <nav
      className="md:hidden fixed bottom-0 inset-x-0 z-30 bottom-nav-surface"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      <ul className="grid grid-cols-7">
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.exact}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center gap-[3px] py-2.5 min-h-[52px] ${
                  isActive ? 'text-[#0A84FF]' : 'text-white/30'
                }`
              }
            >
              {item.icon}
              <span className="text-[9px] font-medium tracking-wide leading-none">{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
