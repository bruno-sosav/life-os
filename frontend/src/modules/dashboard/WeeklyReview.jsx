import { useEffect, useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Modal from '../../components/Modal.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import { fetchWeeklyReview, saveWeeklyReview } from './queries.js'

const MOOD_LABELS = {
  excelente: 'Excelente semana',
  buena: 'Buena semana',
  regular: 'Semana regular',
  dificil: 'Semana difícil',
}

function fmt(d) {
  return format(new Date(d + 'T12:00:00'), "d 'de' MMM", { locale: es })
}

// `diff` viene calculado; null = sin datos de la semana anterior
function Delta({ diff }) {
  if (diff == null) return null
  const color = diff >= 0 ? '#30D158' : '#FF453A'
  const arrow = diff >= 0 ? '↑' : '↓'
  return (
    <span className="text-xs font-semibold ml-1.5" style={{ color }}>
      {arrow} {Math.abs(diff)}% vs semana ant.
    </span>
  )
}

export default function WeeklyReview({ open, onClose }) {
  // Estadísticas, límites de la semana y revisión guardada, todo en una llamada
  const weekQ = useAsync(() => (open ? fetchWeeklyReview() : Promise.resolve(null)), [open])
  const week = weekQ.data

  const [wentWell, setWentWell] = useState('')
  const [wouldChange, setWouldChange] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setWentWell(week?.review?.went_well || '')
    setWouldChange(week?.review?.would_change || '')
  }, [week])

  async function handleSave() {
    setSaving(true)
    try {
      await saveWeeklyReview({ week_start: week.week_start, went_well: wentWell.trim(), would_change: wouldChange.trim() })
      toast.success('Revisión guardada ✓')
      onClose()
    } catch (e) {
      toast.error('Error: ' + e.message)
    } finally { setSaving(false) }
  }

  const weekLabel = week ? `${fmt(week.week_start)} – ${fmt(week.week_end)}` : ''

  return (
    <Modal
      open={open} onClose={onClose}
      title="Revisión semanal"
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSave} disabled={saving || !week}>{saving ? 'Guardando…' : 'Guardar'}</Button>
        </div>
      }
    >
      <div className="space-y-5">
        {/* Semana */}
        <p className="text-xs text-white/35 -mt-1">{weekLabel}</p>

        {/* KPIs */}
        {weekQ.loading ? (
          <div className="text-sm text-white/30 text-center py-4">Cargando datos…</div>
        ) : week ? (
          <div className="grid grid-cols-2 gap-2.5">
            <KPITile
              label="Hábitos"
              value={`${week.habit_pct}%`}
              color={week.habit_pct >= 70 ? '#30D158' : week.habit_pct >= 50 ? '#FF9F0A' : '#FF453A'}
              sub={<Delta diff={week.habit_pct_delta} />}
            />
            <KPITile
              label="Mood promedio"
              value={week.avg_mood != null ? `${week.avg_mood.toFixed(1)}/5` : '—'}
              color="#BF5AF2"
              sub={MOOD_LABELS[week.mood_level] ?? ''}
            />
            <KPITile label="Días de Gym" value={week.gym_days} color="#30D158" />
            <KPITile label="Días de MMA" value={week.mma_days} color="#FF9F0A" />
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
