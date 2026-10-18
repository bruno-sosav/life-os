import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Login from './components/Login.jsx'
import { useAuthStore } from './store/authStore.js'
import Dashboard from './modules/dashboard/index.jsx'
import Fisico from './modules/fisico/index.jsx'
import Negocio from './modules/negocio/index.jsx'
import Mental from './modules/mental/index.jsx'
import Analytics from './modules/analytics/index.jsx'
import Finanzas from './modules/finanzas/index.jsx'

export default function App() {
  const session = useAuthStore((s) => s.session)
  if (!session) return <Login />

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/fisico/*" element={<Fisico />} />
        <Route path="/negocio" element={<Negocio />} />
        <Route path="/mental" element={<Mental />} />
        <Route path="/finanzas" element={<Finanzas />} />
        <Route path="/analytics" element={<Analytics />} />
        {/* compatibilidad con ruta vieja */}
        <Route path="/stratus" element={<Navigate to="/negocio" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
