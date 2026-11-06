import { motion } from 'framer-motion'
import { item, list } from '../../../shared/lib/motion.js'

function weightNote(trend) {
  if (trend == null) return 'sin datos recientes'
  if (trend > 0) return `+${trend} kg vs 30 días`
  if (trend < 0) return `${trend} kg vs 30 días`
  return 'igual que hace 30 días'
}

// "4 h 30" o "45 min": las horas sin decimales que confundan
const practice = (min) => (min >= 60 ? `${Math.floor(min / 60)} h${min % 60 ? ` ${min % 60}` : ''}` : `${min} min`)

// Los números van en texto principal; el color queda para lo que significa algo (la racha)
function Kpi({ label, value, suffix, note, tone = 'text-ink-100' }) {
  return (
    <motion.div variants={item} className="card p-4">
      <div className="text-[11px] text-ink-400 font-medium mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className={`font-mono text-2xl font-bold ${tone}`}>{value}</span>
        {suffix && <span className="text-xs text-ink-400">{suffix}</span>}
      </div>
      {note && <div className="text-[11px] text-ink-400 mt-0.5">{note}</div>}
    </motion.div>
  )
}

export default function KpiGrid({ kpis }) {
  return (
    <motion.div variants={list} initial="hidden" animate="show" className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <Kpi label="Racha actual" value={kpis.current_streak} suffix="días" note="seguidos con 70 % o más"
        tone={kpis.current_streak > 0 ? 'text-up' : 'text-ink-100'} />
      <Kpi label="Mejor racha" value={kpis.best_streak} suffix="días" note="en los últimos 90 días" />
      <Kpi label="Entrenos del mes" value={kpis.workouts_month} note={kpis.workouts_month === 1 ? 'día entrenado' : 'días entrenados'} />
      <Kpi label="Hábitos del mes" value={`${kpis.habit_month_pct}%`} note="de lo que tocaba" />
      <Kpi label="Peso" value={kpis.last_weight != null ? kpis.last_weight.toFixed(1) : '—'} suffix="kg" note={weightNote(kpis.weight_trend)} />
      <Kpi label="Práctica del mes" value={practice(kpis.practice_month_minutes)} note="minutos en tus skills" />
    </motion.div>
  )
}
