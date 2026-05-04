import { useMemo } from 'react'
import PageHeader from '../../components/PageHeader.jsx'
import Card from '../../components/Card.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchAnalyticsData } from './queries.js'
import { lastNDays, fmt, format, subDays } from '../../lib/dates.js'
import {
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  BarChart,
  Bar,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts'

export default function Analytics() {
  const dataQ = useAsync(() => fetchAnalyticsData(), [])
  const d = dataQ.data

  const scores = useMemo(() => calcScores(d), [d])
  const radarData = useMemo(
    () => [
      { area: 'Físico', score: scores.fisico },
      { area: 'Mente', score: scores.mente },
      { area: 'Negocio', score: scores.negocio },
      { area: 'Rutina', score: scores.rutina },
      { area: 'Hábitos', score: scores.habitos }
    ],
    [scores]
  )
  const heatmapDays = useMemo(() => buildHeatmap(d), [d])
  const weeklyBars = useMemo(() => buildWeeklyTrainingBars(d), [d])
  const weightSeries = useMemo(
    () => (d?.weight || []).slice(-90).map((w) => ({ date: w.date.slice(5), kg: Number(w.weight_kg) })),
    [d]
  )

  if (dataQ.loading) {
    return (
      <div>
        <PageHeader title="Analytics" subtitle="Tu vida en números" />
        <div className="text-sm text-ink-400">Cargando…</div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader title="Analytics" subtitle="Tu vida en números" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <ScoreCard label="Físico" value={scores.fisico} color="#D85A30" />
        <ScoreCard label="Mente" value={scores.mente} color="#1D9E75" />
        <ScoreCard label="Negocio" value={scores.negocio} color="#7F77DD" />
        <ScoreCard label="Rutina" value={scores.rutina} color="#3D8BFF" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <Card title="Balance de áreas" subtitle="Score por dimensión (0-100)">
          <div className="h-64">
            <ResponsiveContainer>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="area" tick={{ fill: '#b8b8c4', fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} stroke="rgba(255,255,255,0.08)" />
                <Radar dataKey="score" stroke="#7F77DD" fill="#7F77DD" fillOpacity={0.35} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Entrenamientos por semana" subtitle="Últimas 8 semanas (gym + MMA)">
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={weeklyBars}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="week" stroke="#5b5b68" fontSize={10} />
                <YAxis stroke="#5b5b68" fontSize={10} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#1d1d22', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8 }} />
                <Bar dataKey="gym" stackId="a" fill="#D85A30" radius={[4, 4, 0, 0]} />
                <Bar dataKey="mma" stackId="a" fill="#E33E3E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card title="Heatmap de actividad" subtitle="Días con cualquier registro · últimos 60d" className="mb-4">
        <Heatmap days={heatmapDays} />
      </Card>

      <Card title="Peso corporal" subtitle="Últimos 90 días">
        <div className="h-56">
          {weightSeries.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={weightSeries}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" stroke="#5b5b68" fontSize={10} />
                <YAxis stroke="#5b5b68" fontSize={10} domain={['dataMin - 1', 'dataMax + 1']} />
                <Tooltip contentStyle={{ background: '#1d1d22', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8 }} />
                <Line type="monotone" dataKey="kg" stroke="#7F77DD" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-xs text-ink-400">Aún no hay datos suficientes</div>
          )}
        </div>
      </Card>
    </div>
  )
}

function ScoreCard({ label, value, color }) {
  return (
    <Card>
      <div className="text-xs text-ink-400">{label}</div>
      <div className="stat-num" style={{ color }}>{value}</div>
      <div className="mt-1 h-1 bg-white/[0.06] rounded-full overflow-hidden">
        <div className="h-full" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
    </Card>
  )
}

function Heatmap({ days }) {
  const max = Math.max(1, ...days.map((d) => d.intensity))
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(14px,1fr))] gap-1">
      {days.map((d) => {
        const opacity = d.intensity === 0 ? 0.05 : 0.2 + (d.intensity / max) * 0.8
        return (
          <div
            key={d.date}
            title={`${d.date} · ${d.intensity} actividades`}
            className="aspect-square rounded-sm"
            style={{ backgroundColor: `rgba(127, 119, 221, ${opacity})` }}
          />
        )
      })}
    </div>
  )
}

// ─── Score calculation ───────────────────────────────────────
function calcScores(d) {
  if (!d) return { fisico: 0, mente: 0, negocio: 0, rutina: 0, habitos: 0 }
  const last30 = format(subDays(new Date(), 30), 'yyyy-MM-dd')

  // Físico: gym + mma + nutrición + peso registrado
  const gymCount = d.gym.filter((g) => g.attended && g.date >= last30).length
  const mmaCount = d.mma.filter((m) => m.attended && m.date >= last30).length
  const nutAvg = d.nutrition.length
    ? d.nutrition.reduce((s, n) => s + (n.quality_score || 0), 0) / d.nutrition.length
    : 0
  const fisico = clamp(((gymCount + mmaCount) * 5) + nutAvg * 10)

  // Mente: libros activos + mood promedio
  const reading = d.books.filter((b) => b.status === 'leyendo').length
  const yearRead = d.books.filter((b) => b.status === 'leido').length
  const moodAvg = d.mood.length
    ? d.mood.reduce((s, m) => s + (m.mood_score || 0), 0) / d.mood.length
    : 0
  const mente = clamp(reading * 15 + yearRead * 4 + moodAvg * 10)

  // Negocio: % tareas terminadas vs creadas (último mes)
  const recentTasks = d.tasks.filter((t) => t.created_at && t.created_at >= last30)
  const done = recentTasks.filter((t) => t.status === 'hecho').length
  const negocio = recentTasks.length ? Math.round((done / recentTasks.length) * 100) : 0

  // Hábitos: % cumplimiento últimos 30d
  const recentHabitLogs = d.habitLogs.filter((l) => l.date >= last30)
  const completedLogs = recentHabitLogs.filter((l) => l.completed).length
  const expected = (d.habits.length || 1) * 30
  const habitos = clamp(Math.round((completedLogs / expected) * 100))

  // Rutina: combinación de hábitos + actividad
  const activeDays = new Set([
    ...d.gym.filter((g) => g.date >= last30 && g.attended).map((g) => g.date),
    ...d.mma.filter((m) => m.date >= last30 && m.attended).map((m) => m.date),
    ...recentHabitLogs.filter((l) => l.completed).map((l) => l.date)
  ]).size
  const rutina = clamp(Math.round((activeDays / 30) * 100))

  return { fisico, mente, negocio, rutina, habitos }
}

function clamp(n) { return Math.max(0, Math.min(100, Math.round(n))) }

function buildHeatmap(d) {
  if (!d) return []
  const days = lastNDays(60)
  const counts = {}
  const bump = (date) => { if (date) counts[date] = (counts[date] || 0) + 1 }

  d.habitLogs.filter((l) => l.completed).forEach((l) => bump(l.date))
  d.gym.filter((g) => g.attended).forEach((g) => bump(g.date))
  d.mma.filter((m) => m.attended).forEach((m) => bump(m.date))
  d.nutrition.forEach((n) => bump(n.date))
  d.mood.forEach((m) => bump(m.date))

  return days.map((day) => {
    const iso = format(day, 'yyyy-MM-dd')
    return { date: iso, intensity: counts[iso] || 0 }
  })
}

function buildWeeklyTrainingBars(d) {
  if (!d) return []
  const buckets = []
  for (let w = 7; w >= 0; w--) {
    const end = subDays(new Date(), w * 7)
    const start = subDays(end, 6)
    const startISO = format(start, 'yyyy-MM-dd')
    const endISO = format(end, 'yyyy-MM-dd')
    const gym = d.gym.filter((g) => g.attended && g.date >= startISO && g.date <= endISO).length
    const mma = d.mma.filter((m) => m.attended && m.date >= startISO && m.date <= endISO).length
    buckets.push({ week: fmt(start, "d MMM"), gym, mma })
  }
  return buckets
}
