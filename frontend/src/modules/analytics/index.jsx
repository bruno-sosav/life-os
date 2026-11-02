import { useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import {
  ResponsiveContainer,
  BarChart, Bar,
  AreaChart, Area,
  LineChart, Line,
  CartesianGrid, XAxis, YAxis, Tooltip, Legend, ReferenceLine,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell,
} from 'recharts'
import PageHeader from '../../components/PageHeader.jsx'
import Card from '../../components/Card.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchAnalyticsSummary } from './queries.js'

// Todos los números vienen calculados desde /api/analytics/summary: acá solo se dibujan.

const HABIT_COLORS = ['#BF5AF2', '#0A84FF', '#30D158', '#FF9F0A', '#FF453A', '#5AC8FA', '#FFD700', '#FF2D55', '#34C759', '#AF52DE']
const TT = {
  contentStyle: { background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, fontSize: 12 },
}
const AX = { stroke: 'rgba(255,255,255,0.13)', fontSize: 11 }
const GR = { stroke: 'rgba(255,255,255,0.04)', vertical: false }

// Mismos cortes que el cierre semanal del dashboard; 70 % es la regla de la racha
const complianceColor = (pct) =>
  pct == null ? '#8E8E93' : pct >= 70 ? '#30D158' : pct >= 50 ? '#FF9F0A' : '#FF453A'

function deltaNote(delta) {
  if (delta == null) return 'sin semana anterior para comparar'
  if (delta > 0) return `↑ +${delta} puntos vs la semana anterior`
  if (delta < 0) return `↓ ${delta} puntos vs la semana anterior`
  return 'igual que la semana anterior'
}

// Formato de fechas para mostrar (yyyy-MM-dd → "12 oct")
const fmtDay = (iso) => format(new Date(iso + 'T12:00:00'), 'd MMM', { locale: es })
const fmtMonth = (iso) => format(new Date(iso + 'T12:00:00'), 'MMM yy', { locale: es })
const fmtShort = (iso) => iso.slice(5)

function weightNote(trend) {
  if (trend == null) return 'sin datos recientes'
  if (trend > 0) return `↑ +${trend} kg vs 30d`
  if (trend < 0) return `↓ ${trend} kg vs 30d`
  return 'sin cambio vs 30d'
}

// ─── Sub-components ───────────────────────────────────────────
function NoData({ text }) {
  return <div className="h-full grid place-items-center text-xs text-white/25 text-center px-4">{text}</div>
}

function ArcProgress({ value, color, size = 110 }) {
  const r = size / 2 - 10
  const cx = size / 2, cy = size / 2
  const circ = 2 * Math.PI * r
  const filled = (Math.min(Math.max(value ?? 0, 0), 100) / 100) * circ
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="9" />
      <circle
        cx={cx} cy={cy} r={r} fill="none"
        stroke={color} strokeWidth="9"
        strokeDasharray={`${filled} ${circ - filled}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${cx} ${cy})`}
        style={{ transition: 'stroke-dasharray 0.5s ease' }}
      />
      <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle" fill="white" fontSize="20" fontWeight="800">{value == null ? '—' : `${value}%`}</text>
    </svg>
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

// Misma regla que la racha: cumplido = 70 % o más de lo agendado ese día
const DAY_STATUS = {
  cumplido: { color: '#30D158', label: 'Cumplido' },
  parcial: { color: '#FF9F0A', label: 'Parcial' },
  sin_cumplir: { color: '#FF453A', label: 'Sin cumplir' },
  libre: { color: 'rgba(255,255,255,0.06)', label: 'Sin nada agendado' },
  pendiente: { color: 'rgba(10,132,255,0.35)', label: 'Hoy, en curso' },
}

function HeatmapGrid({ cells }) {
  return (
    <div className="overflow-x-auto">
      <div style={{ display: 'grid', gridTemplateRows: 'repeat(7, 13px)', gridAutoFlow: 'column', gridAutoColumns: '13px', gap: '3px' }}>
        {cells.map((cell, i) => (
          <div
            key={i}
            title={cell.date ? `${cell.date}: ${DAY_STATUS[cell.status].label}` : ''}
            style={{ width: 13, height: 13, borderRadius: 3, backgroundColor: cell.date ? DAY_STATUS[cell.status].color : 'transparent' }}
          />
        ))}
      </div>
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────
export default function Analytics() {
  const [weekOffset, setWeekOffset] = useState(0)
  const summaryQ = useAsync(() => fetchAnalyticsSummary(weekOffset), [weekOffset])
  const s = summaryQ.data

  if (!s) return (
    <div>
      <PageHeader title="Stats" subtitle="Tu vida en números" />
      <div className="text-sm text-white/30 mt-8 text-center">
        {summaryQ.error ? 'No se pudieron cargar los datos.' : 'Cargando datos…'}
      </div>
    </div>
  )

  const { compliance, kpis, habits_by_week: habitsByWeek } = s
  const color = complianceColor(compliance.pct)
  // Incluye actividades pausadas si tuvieron sesiones en el período
  const activityData = s.activity_distribution.map((a, i) => ({
    name: `${a.emoji ? `${a.emoji} ` : ''}${a.name}`,
    value: a.count,
    color: a.color || HABIT_COLORS[i % HABIT_COLORS.length],
  }))
  const hasWorkouts = activityData.length > 0
  const hasFinance = s.finance_monthly.some(m => m.income > 0 || m.expenses > 0)

  return (
    <div className="space-y-4">
      <PageHeader title="Stats" subtitle="Tu vida en números" />

      {/* ── 1. Cumplimiento de la semana ── */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-[11px] text-white/35 uppercase tracking-wider font-semibold mb-0.5">Cumplimiento de la semana</div>
            <div className="text-xs text-white/30">
              {fmtDay(s.week_start)} – {fmtDay(s.week_end)}
              {weekOffset > 0 && <span className="ml-1 text-white/20">(hace {weekOffset} sem.)</span>}
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setWeekOffset(o => o + 1)}
              aria-label="Semana anterior"
              className="w-7 h-7 rounded-full bg-white/[0.07] hover:bg-white/[0.12] text-white/50 hover:text-white text-sm grid place-items-center transition"
            >←</button>
            <button
              onClick={() => setWeekOffset(o => Math.max(0, o - 1))}
              disabled={weekOffset === 0}
              aria-label="Semana siguiente"
              className="w-7 h-7 rounded-full bg-white/[0.07] hover:bg-white/[0.12] text-white/50 hover:text-white text-sm grid place-items-center transition disabled:opacity-25 disabled:cursor-not-allowed"
            >→</button>
          </div>
        </div>

        <div className="flex gap-5 items-center">
          <div className="shrink-0">
            <ArcProgress value={compliance.pct} color={color} size={110} />
          </div>
          <div className="flex-1 min-w-0 space-y-1.5">
            <div className="text-[15px] font-bold" style={{ color }}>
              {compliance.expected
                ? `Hiciste ${compliance.done} de ${compliance.expected} cosas agendadas`
                : 'No tenías nada agendado'}
            </div>
            <div className="text-xs text-white/50">{deltaNote(compliance.delta)}</div>
            <div className="text-[11px] text-white/30">Hábitos y bloques de rutina, hasta hoy.</div>
          </div>
        </div>
      </Card>

      {/* ── 2. 6 KPI Cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <KPICard
          label="Racha actual"
          value={kpis.current_streak}
          suffix=" días"
          color={kpis.current_streak >= 7 ? '#FF9F0A' : kpis.current_streak >= 3 ? '#30D158' : '#0A84FF'}
          note="seguidos con 70 % o más"
        />
        <KPICard label="Mejor racha" value={kpis.best_streak} suffix=" días" color="#FFD700" note="en los últimos 90 días" />
        <KPICard label="Entrenos (mes)" value={kpis.workouts_month} color="#30D158" note="todas las actividades" />
        <KPICard label="Hábitos (mes)" value={`${kpis.habit_month_pct}%`} color="#BF5AF2" note="completados del total" />
        <KPICard
          label="Peso actual"
          value={kpis.last_weight != null ? kpis.last_weight.toFixed(1) : '—'}
          suffix=" kg"
          color="#FF9F0A"
          note={weightNote(kpis.weight_trend)}
        />
        <KPICard label={`Libros ${kpis.year}`} value={kpis.books_year} color="#5AC8FA" note="completados este año" />
      </div>

      {/* ── 3. Hábitos por semana  |  4. Cumplimiento semanal ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Hábitos por semana" subtitle="Días completados · últimas 8 semanas">
          <div className="h-52">
            {habitsByWeek.habits.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={habitsByWeek.weeks} barCategoryGap="30%">
                  <CartesianGrid {...GR} />
                  <XAxis dataKey="week_start" tickFormatter={fmtDay} {...AX} />
                  <YAxis {...AX} allowDecimals={false} />
                  <Tooltip {...TT} labelFormatter={fmtDay} />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                  {habitsByWeek.habits.map((h, i) => (
                    <Bar
                      key={h.id}
                      dataKey={h.id}
                      stackId="a"
                      fill={h.color || HABIT_COLORS[i % HABIT_COLORS.length]}
                      name={h.name}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Sin datos de hábitos aún" />
            )}
          </div>
        </Card>

        <Card title="Cumplimiento semanal" subtitle="Últimas 12 semanas">
          <div className="h-52">
            {s.compliance_history.some(w => w.pct != null) ? (
              <ResponsiveContainer>
                <AreaChart data={s.compliance_history}>
                  <defs>
                    <linearGradient id="complianceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#30D158" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#30D158" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid {...GR} />
                  <XAxis dataKey="week_start" tickFormatter={fmtDay} {...AX} />
                  <YAxis {...AX} domain={[0, 100]} />
                  <Tooltip {...TT} labelFormatter={fmtDay} formatter={(v) => [`${v}%`, 'Cumplimiento']} />
                  <ReferenceLine y={70} stroke="#30D158" strokeDasharray="4 3" opacity={0.4}
                    label={{ value: '70%', position: 'insideTopRight', fill: 'rgba(48,209,88,0.6)', fontSize: 10 }} />
                  <Area
                    type="monotone" dataKey="pct"
                    stroke="#30D158" strokeWidth={2.5}
                    fill="url(#complianceGrad)"
                    dot={({ cx, cy, payload }) => payload.pct == null ? <g key={payload.week_start} /> : (
                      <circle key={payload.week_start} cx={cx} cy={cy}
                        r={payload.is_current ? 5 : 2.5}
                        fill="#30D158"
                        stroke={payload.is_current ? 'white' : 'none'}
                        strokeWidth={payload.is_current ? 2 : 0}
                      />
                    )}
                    name="Cumplimiento"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Sin nada agendado en estas semanas" />
            )}
          </div>
        </Card>
      </div>

      {/* ── 5. Radar  |  6. Heatmap ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Perfil semanal" subtitle="Esta semana vs semana anterior">
          <div className="h-56">
            {s.radar.some(r => r.semana > 0 || r.anterior > 0) ? (
              <ResponsiveContainer>
                <RadarChart data={s.radar} outerRadius="70%">
                  <PolarGrid stroke="rgba(255,255,255,0.07)" />
                  <PolarAngleAxis dataKey="axis" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar dataKey="semana" stroke="#0A84FF" fill="#0A84FF" fillOpacity={0.2} name="Esta semana" />
                  <Radar dataKey="anterior" stroke="#FF9F0A" fill="#FF9F0A" fillOpacity={0.08} strokeDasharray="4 2" name="Sem. anterior" />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Tooltip {...TT} formatter={(v) => [`${v}%`]} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Sin datos suficientes para el radar" />
            )}
          </div>
        </Card>

        <Card
          title="Cumplimiento diario"
          subtitle={`Últimos 90 días: ${s.heatmap.cumplido} cumplidos · ${s.heatmap.parcial} parciales · ${s.heatmap.sin_cumplir} sin cumplir`}
        >
          <HeatmapGrid cells={s.heatmap.cells} />
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-3 text-[11px] text-white/40">
            {Object.entries(DAY_STATUS).map(([key, { color, label }]) => (
              <span key={key} className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm" style={{ background: color }} />
                {label}
              </span>
            ))}
          </div>
        </Card>
      </div>

      {/* ── 7. Físico expandido ── */}
      <Card title="Peso corporal" subtitle="Kg · últimos 90 días">
        <div className="h-48">
          {s.weight_series.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={s.weight_series}>
                <CartesianGrid {...GR} />
                <XAxis dataKey="date" tickFormatter={fmtShort} {...AX} />
                <YAxis {...AX} domain={['dataMin - 1', 'dataMax + 1']} />
                <Tooltip {...TT} formatter={(v) => [`${v} kg`, 'Peso']} />
                <Line type="monotone" dataKey="kg" stroke="#FF9F0A" strokeWidth={2.5} dot={{ r: 3, fill: '#FF9F0A' }} name="Peso (kg)" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <NoData text="Registrá tu peso en Físico → Peso" />
          )}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Mood y sueño" subtitle="Últimos 30 días">
          <div className="h-48">
            {s.mood_series.length > 1 ? (
              <ResponsiveContainer>
                <LineChart data={s.mood_series}>
                  <CartesianGrid {...GR} />
                  <XAxis dataKey="date" tickFormatter={fmtShort} {...AX} />
                  <YAxis {...AX} domain={[0, 5]} />
                  <Tooltip {...TT} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="mood" stroke="#BF5AF2" strokeWidth={2.5} dot={{ r: 2 }} name="Mood" />
                  <Line type="monotone" dataKey="sleep" stroke="#0A84FF" strokeWidth={2} dot={{ r: 2 }} strokeDasharray="4 3" name="Sueño (h)" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Registrá tu estado en Mental" />
            )}
          </div>
        </Card>

        <Card title="Actividades" subtitle="Distribución de entrenos · 30 días">
          <div className="h-48">
            {hasWorkouts ? (
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={activityData} cx="50%" cy="45%" innerRadius={45} outerRadius={72} dataKey="value" paddingAngle={3}>
                    {activityData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                  </Pie>
                  <Tooltip {...TT} formatter={(v, n) => [`${v} sesiones`, n]} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Sin entrenos en los últimos 30 días" />
            )}
          </div>
        </Card>
      </div>

      {/* ── 8. Finanzas ── */}
      {hasFinance && (
        <Card title="Finanzas" subtitle="Ingresos vs gastos · últimos 6 meses">
          <div className="h-52">
            <ResponsiveContainer>
              <BarChart data={s.finance_monthly} barCategoryGap="30%">
                <CartesianGrid {...GR} />
                <XAxis dataKey="month" tickFormatter={fmtMonth} {...AX} />
                <YAxis {...AX} />
                <Tooltip {...TT} labelFormatter={fmtMonth} formatter={(v) => [`$${v.toLocaleString()}`, '']} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="income" fill="#30D158" radius={[4, 4, 0, 0]} name="Ingresos" />
                <Bar dataKey="expenses" fill="#FF453A" radius={[4, 4, 0, 0]} name="Gastos" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-3 mt-4">
            {s.finance_monthly.slice(-3).map((m) => (
              <div key={m.month} className="text-center">
                <div className="text-[11px] text-white/35">{fmtMonth(m.month)}</div>
                <div className="text-xl font-bold" style={{ color: m.savings_pct != null && m.savings_pct >= 0 ? '#30D158' : '#FF453A' }}>
                  {m.savings_pct != null ? `${m.savings_pct}%` : '—'}
                </div>
                <div className="text-[10px] text-white/25">ahorro</div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
