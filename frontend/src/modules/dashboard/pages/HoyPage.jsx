import { useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import PageHeader from '../../../components/PageHeader.jsx'
import Card from '../../../components/Card.jsx'
import Button from '../../../components/Button.jsx'
import DayStrip from '../components/DayStrip.jsx'
import Agenda from '../components/Agenda.jsx'
import BlockModal from '../components/BlockModal.jsx'
import HabitModal from '../components/HabitModal.jsx'
import WeeklyReview from '../components/WeeklyReview.jsx'
import { useAsync } from '../../../hooks/useAsync.js'
import { toast } from '../../../store/toastStore.js'
import { toggleRoutineCompletion } from '../api/bloques.api.js'
import { fetchAgenda, fetchGlobalStreak } from '../api/dashboard.api.js'
import { deleteHabit, toggleHabitLog } from '../api/habitos.api.js'
import { todayISO } from '../../../lib/dates.js'

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días, Bruno'
  if (h < 20) return 'Buenas tardes, Bruno'
  return 'Buenas noches, Bruno'
}

export default function HoyPage() {
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
      toast.success(completed ? 'Hecho' : 'Marcado como pendiente')
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

      {/* Resumen del día: hechas contra lo que falta, y la racha */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <DaySummary agenda={agenda} />
        <StreakCard streak={globalStreak} />
      </div>

      {/* Routine list */}
      <Card
        title="Agenda del día"
        action={
          <div className="flex gap-1.5">
            <Button size="sm" variant="secondary" onClick={() => { setEditBlock(null); setBlockModalOpen(true) }}>+ Bloque</Button>
            <Button size="sm" variant="secondary" onClick={() => setHabitModal({ open: true, initial: null })}>+ Hábito</Button>
          </div>
        }
      >
        <Agenda
          sections={agenda?.sections || []}
          onToggle={handleToggle}
          onEditBlock={(b) => { setEditBlock(b); setBlockModalOpen(true) }}
          onEditHabit={(h) => setHabitModal({ open: true, initial: h })}
          onDeleteHabit={handleDeleteHabit}
        />
      </Card>

      <BlockModal
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

function DaySummary({ agenda }) {
  const done = agenda?.completed ?? 0
  const missing = (agenda?.total ?? 0) - done
  return (
    <Card className="col-span-2">
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-[11px] text-ink-400 font-medium">Agenda del día</span>
        <span className="font-mono text-xs text-ink-400">{agenda ? `${agenda.pct}%` : ''}</span>
      </div>
      {agenda?.total ? (
        <>
          <div className="flex items-baseline gap-2 font-mono">
            <span className="text-3xl font-bold text-up">{done}</span>
            <span className="text-ink-500">/</span>
            <span className={`text-3xl font-bold ${missing ? 'text-down' : 'text-ink-400'}`}>{missing}</span>
            <span className="text-xs text-ink-400 font-sans ml-1">hechas · faltan</span>
          </div>
          <div className="flex gap-[3px] h-1.5 mt-3" aria-hidden="true">
            <div className="bg-up rounded-sm transition-all duration-500" style={{ flex: done }} />
            <div className="bg-down rounded-sm transition-all duration-500" style={{ flex: missing }} />
          </div>
        </>
      ) : (
        <div className="text-sm text-ink-400 mt-2">{agenda ? 'Nada agendado este día' : '—'}</div>
      )}
    </Card>
  )
}

function StreakCard({ streak }) {
  return (
    <Card>
      <div className="text-[11px] text-ink-400 font-medium mb-2">Racha</div>
      <div className={`font-mono text-3xl font-bold ${streak ? 'text-up' : 'text-ink-100'}`}>{streak ?? '—'}</div>
      <div className="text-[11px] text-ink-400 mt-1">
        {streak === null ? '' : streak === 0 ? 'hoy es el día' : streak === 1 ? 'día seguido' : 'días seguidos'}
      </div>
    </Card>
  )
}
