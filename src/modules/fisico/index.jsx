import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import PageHeader from '../../components/PageHeader.jsx'
import Gym from './Gym.jsx'
import MMA from './MMA.jsx'
import Peso from './Peso.jsx'

const TABS = [
  { to: 'gym', label: 'Gym' },
  { to: 'mma', label: 'MMA' },
  { to: 'peso', label: 'Peso & Nutrición' }
]

function FisicoTabs() {
  return (
    <div className="inline-flex p-1 bg-ink-800 border border-white/[0.05] rounded-xl">
      {TABS.map((t) => (
        <NavLink
          key={t.to}
          to={t.to}
          className={({ isActive }) =>
            `px-3 py-1.5 text-xs sm:text-sm rounded-lg transition-colors ${
              isActive ? 'bg-ink-600 text-white' : 'text-ink-300 hover:text-white'
            }`
          }
        >
          {t.label}
        </NavLink>
      ))}
    </div>
  )
}

export default function Fisico() {
  return (
    <div>
      <PageHeader title="Físico" subtitle="Gym, MMA, peso y nutrición" actions={<FisicoTabs />} />
      <Routes>
        <Route index element={<Navigate to="gym" replace />} />
        <Route path="gym" element={<Gym />} />
        <Route path="mma" element={<MMA />} />
        <Route path="peso" element={<Peso />} />
      </Routes>
    </div>
  )
}
