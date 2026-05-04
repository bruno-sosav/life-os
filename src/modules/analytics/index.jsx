import { useMemo } from 'react'
import PageHeader from '../../components/PageHeader.jsx'
import Card from '../../components/Card.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchAnalyticsData } from './queries.js'
import { lastNDays, fmt, format, subDays } from '../../lib/dates.js'
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line,
  CartesianGrid, XAxis, YAxis, Tooltip, Legend
} from 'recharts'

export default function Analytics() {
  const dataQ = useAsync(() => fetchAnalyticsData(), [])
  const d = dataQ.data

  const stats = useMemo(() => calcStats(d), [d])
  const heatmapDays = useMemo(() => buildHeatmap(d), [d])
  const weeklyBars = useMemo(() => buildWeeklyTrainingBars(d), [d])
  const weightSeries = useMemo(
    () => (d?.weight || []).slice(-90).map((w) => ({ date: w.date.slice(5), kg: Number(w.weight_kg) })),
    [d]
  )
  const moodSeries = useMemo(
    () => (d?.mood || []).slice(-30).map((m) => ({ date: m.date.slice(5), mood: m.mood_score, sueño: Number(m.sleep_hours) })),
    [d]
  )

  if (dataQ.loading) return (
    <div>
      <PageHeader title="Stats" emoji="📊" subtitle="Tu vida en números" />
      <div className="text-sm text-white/30 mt-8 text-center">Cargando datos…</div>
    </div>
  )

  return (
    <div>
      <PageHeader title="Stats" emoji="📊" subtitle="Datos reales de los últimos 30 días" />

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <KPICard
          label="Días con gym"
          value={stats.gymDays}
          suffix={`/ ${stats.daysSinceStart}`}
          color="#30D158"
          note={`${stats.gymPct}% de asistencia`}
        />
        <KPICard
          label="Días con MMA"
          value={stats.mmaDays}
          suffix={`/ ${stats.daysSinceStart}`}
          color="#FF9F0A"
          note={`${stats.mmaPct}% de asistencia`}
        />
        <KPICard
          label="Hábitos cumplidos"
          value={`${stats.habitPct}%`}
          color="#BF5AF2"
          note={`${stats.habitDone} de ${stats.habitExpected} esperados`}
        />
        <KPICard
          label="Mood promedio"
          value={stats.avgMood > 0 ? stats.avgMood.toFixed(1) : '—'}
          suffix="/ 5"
          color="#0A84FF"
          note={stats.avgMood > 0 ? moodLabel(stats.avgMood) : 'Sin registros'}
        />
      </div>

      {/* Entrenamiento semanal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <Card title="Entrenamientos por semana" subtitle="Gym + MMA · últimas 8 semanas">
          <div className="h-52">
            {weeklyBars.some(w => w.gym > 0 || w.mma > 0) ? (
              <ResponsiveContainer>
                <BarChart data={weeklyBars} barCategoryGap="30%">
                  <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="week" stroke="#ffffff22" fontSize={10} />
                  <YAxis stroke="#ffffff22" fontSize={10} allowDecimals={false} />
                  <Tooltip contentStyle={{ background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="gym" fill="#30D158" radius={[4, 4, 0, 0]} name="Gym" />
                  <Bar dataKey="mma" fill="#FF9F0A" radius={[4, 4, 0, 0]} name="MMA" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Sin entrenamientos registrados aún" />
            )}
          </div>
        </Card>

        <Card title="Mood y sueño" subtitle="Últimos 30 días">
          <div className="h-52">
            {moodSeries.length > 1 ? (
              <ResponsiveContainer>
                <LineChart data={moodSeries}>
                  <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="date" stroke="#ffffff22" fontSize={10} />
                  <YAxis stroke="#ffffff22" fontSize={10} domain={[0, 5]} />
                  <Tooltip contentStyle={{ background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="mood" stroke="#BF5AF2" strokeWidth={2.5} dot={{ r: 2 }} name="Mood" />
                  <Line type="monotone" dataKey="sueño" stroke="#0A84FF" strokeWidth={2} dot={{ r: 2 }} strokeDasharray="4 3" name="Sueño (h)" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Registrá tu estado mental en la pestaña Mental" />
            )}
          </div>
        </Card>
      </div>

      {/* Peso */}
      <Card title="Peso corporal" subtitle="Kg · últimos 90 días" className="mb-4">
        <div className="h-52">
          {weightSeries.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={weightSeries}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" stroke="#ffffff22" fontSize={10} />
                <YAxis stroke="#ffffff22" fontSize={10} domain={['dataMin - 1', 'dataMax + 1']} />
                <Tooltip contentStyle={{ background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }} />
                <Line type="monotone" dataKey="kg" stroke="#FF9F0A" strokeWidth={2.5} dot={{ r: 3, fill: '#FF9F0A' }} name="Peso (kg)" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <NoData text="Registrá tu peso en la pestaña Físico → Peso" />
          )}
        </div>
      </Card>

      {/* Heatmap */}
      <Card title="Actividad diaria" subtitle="Días con al menos un registro · últimos 60 días">
        <Heatmap days={heatmapDays} />
        <div className="flex items-center gap-2 mt-3 text-[11px] text-white/30">
          <span>Menos</span>
          {[0.08, 0.3, 0.55, 0.8, 1].map((o) => (
            <div key={o} className="w-3 h-3 rounded-sm" style={{ background: `rgba(10,132,255,${o})` }} />
          ))}
          <span>Más</span>
        </div>
      </Card>

      {/* Libros */}
      {(d?.books || []).length > 0 && (
        <Card title="Lectura" subtitle="Estado de libros" className="mt-4">
          <div className="flex gap-6">
            {[
              { label: 'Leyendo', status: 'leyendo', color: '#0A84FF' },
              { label: 'Leídos', status: 'leido', color: '#30D158' },
              { label: 'Pendientes', status: 'pendiente', color: '#8E8E93' },
            ].map(({ label, status, color }) => {
              const count = (d?.books || []).filter(b => b.status === status).length
              return (
                <div key={status} className="flex flex-col items-center gap-1">
                  <span className="text-2xl font-bold" style={{ color }}>{count}</span>
                  <span className="text-[11px] text-white/35">{label}</span>
                </div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}

function KPICard({ label, value, suffix, color, note }) {
  return (
    <Card>
      <div className="text-[11px] text-white/35 mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold tabular-nums" style={{ color }}>{value}</span>
        {suffix && <span className="text-xs text-white/30">{suffix}</span>}
      </div>
      {note && <div className="text-[11px] text-white/30 mt-0.5">{note}</div>}
    </Card>
  )
}

function NoData({ text }) {
  return <div className="h-full grid place-items-center text-xs text-white/25 text-center px-4">{text}</div>
}

function moodLabel(avg) {
  if (avg >= 4.5) return 'Excelente 🔥'
  if (avg >= 3.5) return 'Bien 🙂'
  if (avg >= 2.5) return 'Regular 😐'
  return 'Difícil 😔'
}

function Heatmap({ days }) {
  const max = Math.max(1, ...days.map((d) => d.intensity))
  return (
    <div className="grid gap-1" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(14px, 1fr))' }}>
      {days.map((d) => {
        const opacity = d.intensity === 0 ? 0.06 : 0.15 + (d.intensity / max) * 0.85
        return (
          <div
            key={d.date}
            title={`${d.date}${d.intensity > 0 ? ` · ${d.intensity} actividad${d.intensity > 1 ? 'es' : ''}` : ''}`}
            className="aspect-square rounded-sm"
            style={{ backgroundColor: `rgba(10,132,255,${opacity})` }}
          />
        )
      })}
    </div>
  )
}

// ─── Cálculo de estadísticas reales ─────────────────────────
function calcStats(d) {
  if (!d) return { gymDays: 0, mmaDays: 0, daysSinceStart: 30, gymPct: 0, mmaPct: 0, habitDone: 0, habitExpected: 0, habitPct: 0, avgMood: 0 }

  const last30 = format(subDays(new Date(), 30), 'yyyy-MM-dd')
  const today = format(new Date(), 'yyyy-MM-dd')

  // Calcular rango real de días (desde primer registro o 30d)
  const allDates = [
    ...d.gym.map(g => g.date),
    ...d.mma.map(m => m.date),
    ...d.habitLogs.map(l => l.date),
  ].filter(Boolean).sort()
  const firstDate = allDates.length ? allDates[0] : last30
  const rangeStart = firstDate > last30 ? firstDate : last30
  const daysSinceStart = Math.max(1, Math.round((new Date(today) - new Date(rangeStart)) / 86400000) + 1)

  const gymDays = d.gym.filter(g => g.attended && g.date >= rangeStart).length
  const mmaDays = d.mma.filter(m => m.attended && m.date >= rangeStart).length
  const gymPct = Math.round((gymDays / daysSinceStart) * 100)
  const mmaPct = Math.round((mmaDays / daysSinceStart) * 100)

  // Hábitos: completados vs esperados (cada hábito activo * días desde su primera aparición)
  const habitDone = d.habitLogs.filter(l => l.completed && l.date >= rangeStart).length
  const habitExpected = Math.max(1, d.habits.length * daysSinceStart)
  const habitPct = Math.min(100, Math.round((habitDone / habitExpected) * 100))

  // Mood promedio (solo registros reales)
  const moodEntries = d.mood.filter(m => m.mood_score)
  const avgMood = moodEntries.length
    ? moodEntries.reduce((s, m) => s + m.mood_score, 0) / moodEntries.length
    : 0

  return { gymDays, mmaDays, daysSinceStart, gymPct, mmaPct, habitDone, habitExpected, habitPct, avgMood }
}

function buildHeatmap(d) {
  if (!d) return []
  const days = lastNDays(60)
  const counts = {}
  const bump = (date) => { if (date) counts[date] = (counts[date] || 0) + 1 }

  d.habitLogs.filter(l => l.completed).forEach(l => bump(l.date))
  d.gym.filter(g => g.attended).forEach(g => bump(g.date))
  d.mma.filter(m => m.attended).forEach(m => bump(m.date))
  d.nutrition.forEach(n => bump(n.date))
  d.mood.forEach(m => bump(m.date))

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
    const gym = d.gym.filter(g => g.attended && g.date >= startISO && g.date <= endISO).length
    const mma = d.mma.filter(m => m.attended && m.date >= startISO && m.date <= endISO).length
    buckets.push({ week: fmt(start, "d MMM"), gym, mma })
  }
  return buckets
}
