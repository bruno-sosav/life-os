import { useState } from 'react'
import { startOfMonth } from 'date-fns'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fetchSessions } from '../api/sesiones.api.js'
import { fetchTrainingMonth, fetchTrainingWeek } from '../api/asistencia.api.js'
import RegisterSessionModal from './RegisterSessionModal.jsx'
import WeekStrip from './WeekStrip.jsx'
import TrainingCalendar from './TrainingCalendar.jsx'
import SessionHistory from './SessionHistory.jsx'
import ProgressChart from './ProgressChart.jsx'
import TiposEntrenamiento from './TiposEntrenamiento.jsx'

export default function TrainingTab({ activities, onActivitiesChanged }) {
  const [registering, setRegistering] = useState(false)
  const [managing, setManaging] = useState(false)
  const [month, setMonth] = useState(() => startOfMonth(new Date()))
  const [day, setDay] = useState(null)

  const sessionsQ = useAsync(() => fetchSessions(undefined, 200), [])
  const weekQ = useAsync(() => fetchTrainingWeek(), [])
  const monthQ = useAsync(() => fetchTrainingMonth(month), [month])

  const byId = Object.fromEntries(activities.map((a) => [a.id, a]))
  const colorOf = (id) => byId[id]?.color || '#8C948F'
  const active = activities.filter((a) => a.active)

  function refresh() {
    sessionsQ.refetch()
    weekQ.refetch()
    monthQ.refetch()
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Button size="lg" className="flex-1 sm:flex-none" onClick={() => setRegistering(true)}>+ Registrar entrenamiento</Button>
        <Button size="lg" variant="secondary" onClick={() => setManaging(true)}>Tipos</Button>
      </div>

      <WeekStrip data={weekQ.data} colorOf={colorOf} />

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3">
          <SessionHistory
            sessions={sessionsQ.data || []}
            activities={activities}
            colorOf={colorOf}
            day={day}
            onClearDay={() => setDay(null)}
            onDeleted={refresh}
          />
        </div>
        <div className="lg:col-span-2 space-y-4">
          <TrainingCalendar month={month} onMonthChange={(m) => { setMonth(m); setDay(null) }} data={monthQ.data}
            colorOf={colorOf} selected={day} onSelect={setDay} />
          <ProgressChart activities={activities} version={sessionsQ.data?.length} />
        </div>
      </div>

      <RegisterSessionModal
        open={registering}
        activities={active}
        onClose={() => setRegistering(false)}
        onSaved={refresh}
        onTypeCreated={onActivitiesChanged}
      />
      <Modal open={managing} onClose={() => setManaging(false)} title="Tipos de entrenamiento" size="lg">
        <TiposEntrenamiento activities={activities} onChanged={() => { onActivitiesChanged(); refresh() }} />
      </Modal>
    </div>
  )
}
