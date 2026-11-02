import { Routes, Route, NavLink, Navigate, useParams } from 'react-router-dom'
import PageHeader from '../../components/PageHeader.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchActivities } from './queries.js'
import Actividad from './Actividad.jsx'
import Actividades from './Actividades.jsx'
import Peso from './Peso.jsx'

function FisicoTabs({ activities }) {
  // Solo las activas: las pausadas se gestionan (y reactivan) desde "Actividades"
  const tabs = [
    ...activities.filter((a) => a.active).map((a) => ({ to: a.id, label: `${a.emoji ? `${a.emoji} ` : ''}${a.name}` })),
    { to: 'peso', label: 'Peso & Nutrición' },
    { to: 'actividades', label: '⚙︎ Actividades' }
  ]
  return (
    <div className="inline-flex flex-wrap p-1 bg-ink-800 border border-white/[0.05] rounded-xl">
      {tabs.map((t) => (
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

function ActividadRoute({ activities }) {
  const { activityId } = useParams()
  const activity = activities.find((a) => a.id === activityId)
  if (!activity) return <Navigate to="../actividades" replace />
  return <Actividad key={activity.id} activity={activity} />
}

export default function Fisico() {
  const activitiesQ = useAsync(() => fetchActivities(), [])
  const activities = activitiesQ.data || []
  const first = activities.find((a) => a.active)

  return (
    <div>
      <PageHeader title="Físico" subtitle="Tus actividades, peso y nutrición" actions={<FisicoTabs activities={activities} />} />
      {activitiesQ.data && (
        <Routes>
          <Route index element={<Navigate to={first ? first.id : 'actividades'} replace />} />
          <Route path="peso" element={<Peso />} />
          <Route path="actividades" element={<Actividades activities={activities} onChanged={activitiesQ.refetch} />} />
          <Route path=":activityId" element={<ActividadRoute activities={activities} />} />
        </Routes>
      )}
    </div>
  )
}
