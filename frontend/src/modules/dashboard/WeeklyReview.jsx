import { useEffect, useMemo, useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Modal from '../../components/Modal.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import {
  fetchWeeklyReviewStats, fetchWeeklyReview, saveWeeklyReview, getWeekBounds
} from './queries.js'

function habitPctForWeek(logs, habits, startISO, endISO) {
  let expected = 0, done = 0
  const d = new Date(startISO + 'T12:00:00')
  const end = new Date(endISO + 'T12:00:00')
  const today = new Date(); today.setHours(23, 59, 59)
  while (d <= end && d <= today) {
    const iso = d.toISOString().slice(0, 10)
    const dow = (d.getDay() + 6) % 7
    const active = habits.filter(h => !h.days_of_week?.length || h.days_of_week.includes(dow))
    expected += active.length
    done += logs.filter(l => l.date === iso && l.completed).length
    d.setDate(d.getDate() + 1)
  }
  return expected > 0 ? Math.round((done / expected) * 100) : 0
}

function fmt(d) {
  return format(new Date(d + 'T12:00:00'), "d 'de' MMM", { locale: es })
}

function Delta({ current, prev }) {
  const diff = current - prev
  if (prev === 0) return null
  const color = diff >= 0 ? '#30D158' : '#FF453A'
  const arrow = diff >= 0 ? '↑' : '↓'
  return (
    <span className="text-xs font-semibold ml-1.5" style={{ color }}>
      {arrow} {Math.abs(diff)}% vs semana ant.
    </span>
  )
}

export default function WeeklyReview({ open, onClose }) {
  const thisWeek = useMemo(() => getWeekBounds(0), [])
  const prevWeek = useMemo(() => getWeekBounds(1), [])

  const statsQ = useAsync(
    () => fetchWeeklyReviewStats(thisWeek.start, thisWeek.end, prevWeek.start, prevWeek.end),
    [thisWeek.start]
  )
  const reviewQ = useAsync(() => fetchWeeklyReview(thisWeek.start), [thisWeek.start])

  const [wentWell, setWentWell] = useState('')
  const [wouldChange, setWouldChange] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    if (reviewQ.data) {
      setWentWell(reviewQ.data.went_well || '')
      setWouldChange(reviewQ.data.would_change || '')
    }
  }, [open, reviewQ.data])

  const stats = useMemo(() => {
    if (!statsQ.data) return null
    const { thisLogs, prevLogs, habits, gym, mma, mood } = statsQ.data
    const thisHabitPct = habitPctForWeek(thisLogs, habits, thisWeek.start, thisWeek.end)
    const prevHabitPct = habitPctForWeek(prevLogs, habits, prevWeek.start, prevWeek.end)
    const gymDays = gym.filter(g => g.attended).length
    const mmaDays = mma.filter(m => m.attended).length
    const avgMood = mood.filter(m => m.mood_score).length
      ? mood.reduce((s, m) => s + (m.mood_score || 0), 0) / mood.filter(m => m.mood_score).length
      : 0
    return { thisHabitPct, prevHabitPct, gymDays, mmaDays, avgMood }
  }, [statsQ.data, thisWeek, prevWeek])

  async function handleSave() {
    setSaving(true)
    try {
      await saveWeeklyReview({ week_start: thisWeek.start, went_well: wentWell.trim(), would_change: wouldChange.trim() })
      toast.success('Revisión guardada ✓')
      onClose()
    } catch (e) {
      toast.error('Error: ' + e.message)
    } finally { setSaving(false) }
  }

  const weekLabel = `${fmt(thisWeek.start)} – ${fmt(thisWeek.end)}`

  return (
    <Modal
      open={open} onClose={onClose}
      title="Revisión semanal"
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSave} disabled={saving}>{saving ? 'Guardando…' : 'Guardar'}</Button>
        </div>
      }
    >
      <div className="space-y-5">
        {/* Semana */}
        <p className="text-xs text-white/35 -mt-1">{weekLabel}</p>

        {/* KPIs */}
        {statsQ.loading ? (
          <div className="text-sm text-white/30 text-center py-4">Cargando datos…</div>
        ) : stats ? (
          <div className="grid grid-cols-2 gap-2.5">
            <KPITile
              label="Hábitos"
              value={`${stats.thisHabitPct}%`}
              color={stats.thisHabitPct >= 70 ? '#30D158' : stats.thisHabitPct >= 50 ? '#FF9F0A' : '#FF453A'}
              sub={<Delta current={stats.thisHabitPct} prev={stats.prevHabitPct} />}
            />
            <KPITile
              label="Mood promedio"
              value={stats.avgMood > 0 ? `${stats.avgMood.toFixed(1)}/5` : '—'}
              color="#BF5AF2"
              sub={moodLabel(stats.avgMood)}
            />
            <KPITile label="Días de Gym" value={stats.gymDays} color="#30D158" />
            <KPITile label="Días de MMA" value={stats.mmaDays} color="#FF9F0A" />
          </div>
        ) : (
          <div className="text-sm text-white/30 text-center py-2">Sin datos por ahora.</div>
        )}

        {/* Reflection */}
        <div>
          <label className="label">¿Qué salió bien esta semana?</label>
          <textarea
            className="input min-h-[80px] resize-none"
            value={wentWell}
            onChange={(e) => setWentWell(e.target.value)}
            placeholder="Entrenamientos, hábitos cumplidos, logros…"
          />
        </div>
        <div>
          <label className="label">¿Qué cambiaría o mejoraría?</label>
          <textarea
            className="input min-h-[80px] resize-none"
            value={wouldChange}
            onChange={(e) => setWouldChange(e.target.value)}
            placeholder="Hábitos que fallé, qué me frenó, próxima semana hago…"
          />
        </div>
      </div>
    </Modal>
  )
}

function KPITile({ label, value, color, sub }) {
  return (
    <div className="bg-white/[0.05] border border-white/[0.07] rounded-[16px] p-3.5">
      <div className="text-[11px] text-white/35 mb-1">{label}</div>
      <div className="text-2xl font-bold tabular-nums" style={{ color }}>{value}</div>
      {sub && <div className="text-[11px] text-white/40 mt-0.5">{sub}</div>}
    </div>
  )
}

function moodLabel(avg) {
  if (!avg) return ''
  if (avg >= 4.5) return 'Excelente semana'
  if (avg >= 3.5) return 'Buena semana'
  if (avg >= 2.5) return 'Semana regular'
  return 'Semana difícil'
}
