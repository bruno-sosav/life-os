import { useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import PageHeader from '../../components/PageHeader.jsx'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import DayStrip from './DayStrip.jsx'
import RoutineList from './RoutineList.jsx'
import EditRoutineModal from './EditRoutineModal.jsx'
import HabitModal from './HabitModal.jsx'
import WeeklyReview from './WeeklyReview.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import {
  fetchAgenda, fetchGlobalStreak,
  toggleHabitLog, toggleRoutineCompletion, deleteHabit,
} from './queries.js'
import { todayISO } from '../../lib/dates.js'

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días, Bruno ☀️'
  if (h < 20) return 'Buenas tardes, Bruno 🌤'
  return 'Buenas noches, Bruno 🌙'
}

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(todayISO)
  const [editBlock, setEditBlock] = useState(null)
  const [blockModalOpen, setBlockModalOpen] = useState(false)
  const [habitModal, setHabitModal] = useState({ open: false, initial: null })
  const [reviewOpen, setReviewOpen] = useState(false)

  // La agenda llega armada: secciones, estado de cada ítem y progreso del día
  const agendaQ = useAsync(() => fetchAgenda(selectedDate), [selectedDate])
  const streakQ = useAsync(() => fetchGlobalStreak(), [])
  const agenda = agendaQ.data
  const globalStreak = streakQ.data ?? null

  function refetchAll() {
    agendaQ.refetch()
    streakQ.refetch()
  }

  async function handleToggle(item) {
    const completed = !item.done
    try {
      if (item.kind === 'block') {
        await toggleRoutineCompletion({ block_id: item.id, date: selectedDate, completed })
      } else {
        await toggleHabitLog({ habit_id: item.id, date: selectedDate, completed })
      }
      toast.success(completed ? '¡Completado! ✓' : 'Marcado como pendiente')
      refetchAll()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  async function handleDeleteHabit(habit) {
    if (!confirm(`¿Eliminar "${habit.name}"?`)) return
    try {
      await deleteHabit(habit.id)
      toast.success('Hábito eliminado')
      refetchAll()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  return (
    <div>
      <PageHeader
        title={format(new Date(), "EEEE, d 'de' MMMM", { locale: es }).replace(/^\w/, c => c.toUpperCase())}
        subtitle={greeting()}
        actions={
          <Button size="sm" variant="secondary" onClick={() => setReviewOpen(true)}>
            Revisión semanal
          </Button>
        }
      />

      {/* Day selector */}
      <Card className="mb-4">
        <DayStrip week={agenda?.week || []} selected={selectedDate} onChange={setSelectedDate} />
      </Card>

      {/* Progress */}
      {agenda?.total > 0 && (
        <div className="mb-4 px-1">
          <div className="flex items-center justify-between text-xs text-white/40 mb-1.5">
            <span>{agenda.completed} de {agenda.total} completadas</span>
            <span className="font-semibold text-white/70">{agenda.pct}%</span>
          </div>
          <div className="h-1.5 bg-white/[0.07] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${agenda.pct}%`, background: '#30D158' }}
            />
          </div>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card>
          <div className="text-[11px] text-white/35">Hoy</div>
          <div className="stat-num text-[#30D158]">{agenda ? `${agenda.completed}/${agenda.total}` : '—'}</div>
        </Card>
        <StreakCard streak={globalStreak} />
        <Card>
          <div className="text-[11px] text-white/35">Hora</div>
          <div className="stat-num">{new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })}</div>
        </Card>
      </div>

      {/* Routine list */}
      <Card
        title="Agenda del día"
        action={
          <div className="flex gap-1.5">
            <Button size="sm" variant="secondary" onClick={() => { setEditBlock(null); setBlockModalOpen(true) }}>+ Actividad</Button>
            <Button size="sm" variant="secondary" onClick={() => setHabitModal({ open: true, initial: null })}>+ Hábito</Button>
          </div>
        }
      >
        <RoutineList
          sections={agenda?.sections || []}
          onToggle={handleToggle}
          onEditBlock={(b) => { setEditBlock(b); setBlockModalOpen(true) }}
          onEditHabit={(h) => setHabitModal({ open: true, initial: h })}
          onDeleteHabit={handleDeleteHabit}
        />
      </Card>

      <EditRoutineModal
        open={blockModalOpen}
        onClose={() => setBlockModalOpen(false)}
        initial={editBlock}
        selectedWeekday={agenda?.weekday ?? 0}
        onSaved={refetchAll}
      />
      <HabitModal
        open={habitModal.open}
        onClose={() => setHabitModal({ open: false, initial: null })}
        initial={habitModal.initial}
        onSaved={refetchAll}
      />
      <WeeklyReview open={reviewOpen} onClose={() => setReviewOpen(false)} />
    </div>
  )
}

function StreakCard({ streak }) {
  const color = streak >= 7 ? '#FF9F0A' : streak >= 3 ? '#30D158' : '#0A84FF'
  return (
    <Card>
      <div className="text-[11px] text-white/35">Racha</div>
      <div className="stat-num" style={{ color }}>
        {streak === null ? '—' : streak}
      </div>
      <div className="text-[10px] text-white/25 mt-0.5">
        {streak === null ? '' : streak === 0 ? 'hoy es el día' : streak === 1 ? 'día seguido' : 'días seguidos'}
      </div>
    </Card>
  )
}
