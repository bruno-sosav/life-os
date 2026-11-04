import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './layout/Layout.jsx'
import { useAuthStore } from '../shared/store/authStore.js'
import LoginPage from '../features/auth/pages/LoginPage.jsx'
import HoyPage from '../features/dashboard/pages/HoyPage.jsx'
import FisicoPage from '../features/fisico/pages/FisicoPage.jsx'
import NegocioPage from '../features/negocio/pages/NegocioPage.jsx'
import MentalPage from '../features/mental/pages/MentalPage.jsx'
import FinanzasPage from '../features/finanzas/pages/FinanzasPage.jsx'
import StatsPage from '../features/analytics/pages/StatsPage.jsx'

export default function App() {
  const session = useAuthStore((s) => s.session)
  if (!session) return <LoginPage />

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HoyPage />} />
        <Route path="/fisico" element={<FisicoPage />} />
        <Route path="/negocio" element={<NegocioPage />} />
        <Route path="/mental" element={<MentalPage />} />
        <Route path="/finanzas" element={<FinanzasPage />} />
        <Route path="/analytics" element={<StatsPage />} />
        {/* compatibilidad con ruta vieja */}
        <Route path="/stratus" element={<Navigate to="/negocio" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
