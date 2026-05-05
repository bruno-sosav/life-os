import { useMemo, useState } from 'react'
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
  fetchActiveHabits, fetchHabitLogsRange,
  fetchRoutineBlocks, fetchRoutineCompletions,
  toggleHabitLog, toggleRoutineCompletion,
  fetchStreakRawData, calcGlobalStreak
} from './queries.js'
import { weekRange } from '../../lib/dates.js'

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días, Bruno ☀️'
  if (h < 20) return 'Buenas tardes, Bruno 🌤'
  return 'Buenas noches, Bruno 🌙'
}

function dateISO(dow) {
  const today = new Date()
  const todayDow = (today.getDay() + 6) % 7
  const d = new Date(today)
  d.setDate(today.getDate() + (dow - todayDow))
  return d.toISOString().slice(0, 10)
}

export default function Dashboard() {
  const todayDow = (new Date().getDay() + 6) % 7
  const [selectedDow, setSelectedDow] = useState(todayDow)
  const [editBlock, setEditBlock] = useState(null)
  const [blockModalOpen, setBlockModalOpen] = useState(false)
  const [habitModal, setHabitModal] = useState({ open: false, initial: null })
  const [reviewOpen, setReviewOpen] = useState(false)

  const selectedDateISO = dateISO(selectedDow)
  const { start, end } = weekRange()
  const startISO = start.toISOString().slice(0, 10)
  const endISO = end.toISOString().slice(0, 10)

  const habitsQ = useAsync(() => fetchActiveHabits(), [])
  const habitLogsQ = useAsync(() => fetchHabitLogsRange(startISO, endISO), [startISO, endISO])
  const blocksQ = useAsync(() => fetchRoutineBlocks(), [])
  const completionsQ = useAsync(() => fetchRoutineCompletions(selectedDateISO), [selectedDateISO])
  const streakQ = useAsync(() => fetchStreakRawData(), [])

  const habits = habitsQ.data || []
  const blocks = blocksQ.data || []

  const dayBlocks = useMemo(() => blocks.filter((b) => {
    if (!b.repeat_weekly) return b.specific_date === selectedDateISO
    if (b.days_of_week?.length) return b.days_of_week.includes(selectedDow)
    return b.day_of_week === selectedDow
  }), [blocks, selectedDow, selectedDateISO])

  const dayHabits = useMemo(() => habits.filter((h) => {
    if (!h.days_of_week || h.days_of_week.length === 0) return true
    return h.days_of_week.includes(selectedDow)
  }), [habits, selectedDow])

  const totalItems = dayBlocks.length + dayHabits.length
  const completedBlocksSet = useMemo(
    () => new Set((completionsQ.data || []).map((c) => c.block_id)),
    [completionsQ.data]
  )
  const completedHabitsCount = useMemo(() => {
    return (habitLogsQ.data || []).filter((l) => l.date === selectedDateISO && l.completed).length
  }, [habitLogsQ.data, selectedDateISO])
  const completedCount = completedBlocksSet.size + completedHabitsCount
  const pct = totalItems ? Math.round((completedCount / totalItems) * 100) : 0

  const globalStreak = useMemo(() => {
    if (!streakQ.data) return null
    return calcGlobalStreak(blocks, habits, streakQ.data.completions, streakQ.data.habitLogs)
  }, [blocks, habits, streakQ.data])

  async function handleToggleBlock(block) {
    const done = completedBlocksSet.has(block.id)
    try {
      await toggleRoutineCompletion({ block_id: block.id, date: selectedDateISO, completed: !done })
      toast.success(done ? 'Marcado como pendiente' : '¡Completado! ✓')
      completionsQ.refetch()
      streakQ.refetch()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  async function handleToggleHabit(habit) {
    const curLog = (habitLogsQ.data || []).find((l) => l.date === selectedDateISO && l.habit_id === habit.id)
    const done = !!curLog?.completed
    try {
      await toggleHabitLog({ habit_id: habit.id, date: selectedDateISO, completed: !done })
      toast.success(done ? 'Marcado como pendiente' : '¡Hábito completado! ✓')
      habitLogsQ.refetch()
      streakQ.refetch()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  function refetchAll() {
    habitsQ.refetch()
    habitLogsQ.refetch()
    blocksQ.refetch()
    completionsQ.refetch()
    streakQ.refetch()
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
        <DayStrip selected={selectedDow} onChange={setSelectedDow} />
      </Card>

      {/* Progress */}
      {totalItems > 0 && (
        <div className="mb-4 px-1">
          <div className="flex items-center justify-between text-xs text-white/40 mb-1.5">
            <span>{completedCount} de {totalItems} completadas</span>
            <span className="font-semibold text-white/70">{pct}%</span>
          </div>
          <div className="h-1.5 bg-white/[0.07] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${pct}%`, background: '#30D158' }}
            />
          </div>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card>
          <div className="text-[11px] text-white/35">Hoy</div>
          <div className="stat-num text-[#30D158]">{completedCount}/{totalItems}</div>
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
          blocks={dayBlocks}
          blockCompletions={completionsQ.data || []}
          habits={dayHabits}
          habitLogs={habitLogsQ.data || []}
          dateISO={selectedDateISO}
          onToggleBlock={handleToggleBlock}
          onToggleHabit={handleToggleHabit}
          onEditBlock={(b) => { setEditBlock(b); setBlockModalOpen(true) }}
          onEditHabit={(h) => setHabitModal({ open: true, initial: h })}
        />
      </Card>

      <EditRoutineModal
        open={blockModalOpen}
        onClose={() => setBlockModalOpen(false)}
        initial={editBlock}
        selectedDow={selectedDow}
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
