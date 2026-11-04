import { useEffect, useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Modal from '../../../components/Modal.jsx'
import Button from '../../../components/Button.jsx'
import { useAsync } from '../../../hooks/useAsync.js'
import { toast } from '../../../store/toastStore.js'
import { fetchWeeklyReview } from '../api/dashboard.api.js'
import { saveWeeklyReview } from '../api/revisiones.api.js'

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
  const arrow = diff >= 0 ? '↑' : '↓'
  return (
    <span className={`text-xs font-semibold ${diff >= 0 ? 'text-up' : 'text-down'}`}>
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
      toast.success('Revisión guardada')
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
        <p className="text-xs text-ink-400 -mt-1">{weekLabel}</p>

        {/* KPIs */}
        {weekQ.loading ? (
          <div className="text-sm text-ink-400 text-center py-4">Cargando datos…</div>
        ) : week ? (
          <div className="grid grid-cols-2 gap-2.5">
            <KPITile
              label="Hábitos"
              value={`${week.habit_pct}%`}
              tone={week.habit_pct >= 70 ? 'text-up' : week.habit_pct >= 50 ? 'text-warn' : 'text-down'}
              sub={<Delta diff={week.habit_pct_delta} />}
            />
            <KPITile
              label="Mood promedio"
              value={week.avg_mood != null ? `${week.avg_mood.toFixed(1)}/5` : '—'}
              sub={MOOD_LABELS[week.mood_level] ?? ''}
            />
            {week.activity_days.map((a) => (
              <KPITile key={a.id} label={`Días de ${a.name}`} value={a.days} dot={a.color} />
            ))}
          </div>
        ) : (
          <div className="text-sm text-ink-400 text-center py-2">Sin datos por ahora.</div>
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

function KPITile({ label, value, tone = 'text-ink-100', dot, sub }) {
  return (
    <div className="bg-ink-900 border border-ink-700 rounded-xl p-3.5">
      <div className="text-[11px] text-ink-400 mb-1 flex items-center gap-1.5">
        {dot && <span className="w-1.5 h-1.5 rounded-full" style={{ background: dot }} />}
        {label}
      </div>
      <div className={`font-mono text-2xl font-bold ${tone}`}>{value}</div>
      {sub && <div className="text-[11px] text-ink-400 mt-0.5">{sub}</div>}
    </div>
  )
}
