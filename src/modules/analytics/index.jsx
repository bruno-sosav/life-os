import { useState, useMemo } from 'react'
import {
  format, subDays, subMonths, startOfMonth, endOfMonth,
  eachDayOfInterval,
} from 'date-fns'
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
import { fetchAnalyticsData } from './queries.js'

const HABIT_COLORS = ['#BF5AF2', '#0A84FF', '#30D158', '#FF9F0A', '#FF453A', '#5AC8FA', '#FFD700', '#FF2D55', '#34C759', '#AF52DE']
const TT = {
  contentStyle: { background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, fontSize: 12 },
}
const AX = { stroke: 'rgba(255,255,255,0.13)', fontSize: 11 }
const GR = { stroke: 'rgba(255,255,255,0.04)', vertical: false }

// ─── Date helpers ─────────────────────────────────────────────
function fmtISO(d) { return format(d, 'yyyy-MM-dd') }
function fmtLabel(isoDate, pattern) { return format(new Date(isoDate + 'T12:00:00'), pattern, { locale: es }) }

function getWeekRange(offsetWeeks = 0) {
  const today = new Date()
  const dow = (today.getDay() + 6) % 7
  const monday = new Date(today)
  monday.setDate(today.getDate() - dow - offsetWeeks * 7)
  monday.setHours(0, 0, 0, 0)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  return { start: fmtISO(monday), end: fmtISO(sunday) }
}

function daysInRange(startISO, endISO) {
  return eachDayOfInterval({
    start: new Date(startISO + 'T12:00:00'),
    end: new Date(endISO + 'T12:00:00'),
  }).map(d => fmtISO(d))
}

function getDow(isoDate) {
  const d = new Date(isoDate + 'T12:00:00')
  return (d.getDay() + 6) % 7
}

// ─── Calc: Score Bruce ────────────────────────────────────────
function calcBruceScore(d, weekOffset) {
  const empty = { total: 0, habitScore: 0, workoutScore: 0, stratusScore: 0, completedHabits: 0, expectedHabits: 0, workoutsThisWeek: 0, stratusDays: 0 }
  if (!d) return empty

  const { start, end } = getWeekRange(weekOffset)
  const days = daysInRange(start, end)

  let expectedHabits = 0
  days.forEach(dt => {
    const dow = getDow(dt)
    expectedHabits += (d.habits || []).filter(h => !h.days_of_week?.length || h.days_of_week.includes(dow)).length
  })

  const weekLogs = (d.habitLogs || []).filter(l => l.completed && l.date >= start && l.date <= end)
  const completedHabits = weekLogs.length
  const habitScore = expectedHabits > 0 ? Math.round(Math.min(completedHabits / expectedHabits, 1) * 50) : 0

  const gymW = (d.gym || []).filter(g => g.attended && g.date >= start && g.date <= end).length
  const mmaW = (d.mma || []).filter(m => m.attended && m.date >= start && m.date <= end).length
  const workoutsThisWeek = gymW + mmaW
  const workoutScore = Math.round(Math.min(workoutsThisWeek / 5, 1) * 30)

  const stratusHabitIds = new Set((d.habits || []).filter(h => h.name?.toLowerCase().includes('stratus')).map(h => h.id))
  const stratusBlockIds = new Set((d.routineBlocks || []).filter(b => b.activity?.toLowerCase().includes('stratus')).map(b => b.id))
  const stratusDaysSet = new Set([
    ...weekLogs.filter(l => stratusHabitIds.has(l.habit_id)).map(l => l.date),
    ...((d.routineCompletions || []).filter(c => c.date >= start && c.date <= end && stratusBlockIds.has(c.block_id)).map(c => c.date)),
  ])
  const stratusDays = stratusDaysSet.size
  const stratusScore = Math.round(Math.min(stratusDays / 5, 1) * 20)

  return { total: habitScore + workoutScore + stratusScore, habitScore, workoutScore, stratusScore, completedHabits, expectedHabits, workoutsThisWeek, stratusDays }
}

function bruceLabel(score) {
  if (score >= 91) return { text: 'Elite ⚡', color: '#FFD700' }
  if (score >= 71) return { text: 'Modo Bruce', color: '#30D158' }
  if (score >= 41) return { text: 'Activando', color: '#FF9F0A' }
  return { text: 'Modo apagado', color: '#8E8E93' }
}

// ─── Calc: KPI Cards ──────────────────────────────────────────
function calcKPI(d) {
  if (!d) return {}

  const today = fmtISO(new Date())
  const monthStart = format(startOfMonth(new Date()), 'yyyy-MM-dd')

  const logsByDate = {}
  ;(d.habitLogs || []).filter(l => l.completed).forEach(l => { logsByDate[l.date] = (logsByDate[l.date] || 0) + 1 })

  let currentStreak = 0, run = 0, inCurrent = true
  let bestStreak = 0, bRun = 0
  for (let i = 0; i <= 89; i++) {
    const iso = fmtISO(subDays(new Date(), i))
    if (logsByDate[iso] > 0) {
      run++
      if (inCurrent) currentStreak = run
    } else {
      if (i === 0) { /* today may not be done yet */ }
      else { inCurrent = false; run = 0 }
    }
  }
  for (let i = 89; i >= 0; i--) {
    const iso = fmtISO(subDays(new Date(), i))
    if (logsByDate[iso] > 0) { bRun++; bestStreak = Math.max(bestStreak, bRun) }
    else { bRun = 0 }
  }

  const gymMonth = (d.gym || []).filter(g => g.attended && g.date >= monthStart).length
  const mmaMonth = (d.mma || []).filter(m => m.attended && m.date >= monthStart).length

  const monthDays = daysInRange(monthStart, today)
  let expMonth = 0
  monthDays.forEach(dt => {
    const dow = getDow(dt)
    expMonth += (d.habits || []).filter(h => !h.days_of_week?.length || h.days_of_week.includes(dow)).length
  })
  const doneMonth = (d.habitLogs || []).filter(l => l.completed && l.date >= monthStart).length
  const habitMonthPct = expMonth > 0 ? Math.min(100, Math.round((doneMonth / expMonth) * 100)) : 0

  const sortedW = [...(d.weight || [])].sort((a, b) => a.date.localeCompare(b.date))
  const lastWeight = sortedW.length ? Number(sortedW[sortedW.length - 1].weight_kg) : null
  const date30ago = fmtISO(subDays(new Date(), 30))
  const weight30 = sortedW.filter(w => w.date <= date30ago).pop()
  const weightTrend = lastWeight != null && weight30 ? +(lastWeight - Number(weight30.weight_kg)).toFixed(1) : null

  const books2026 = (d.books || []).filter(b => b.status === 'leido' && b.finished_at?.startsWith('2026')).length

  return {
    currentStreak, bestStreak,
    workoutsMonth: gymMonth + mmaMonth,
    habitMonthPct, lastWeight, weightTrend, books2026,
  }
}

// ─── Calc: Habits by week ─────────────────────────────────────
function buildHabitsByWeek(d) {
  if (!d || !d.habits?.length) return { data: [], habits: [] }
  const weeks = []
  for (let w = 7; w >= 0; w--) {
    const endDate = subDays(new Date(), w * 7)
    const startDate = subDays(endDate, 6)
    const startISO = fmtISO(startDate)
    const endISO = fmtISO(endDate)
    const row = { week: format(startDate, 'd MMM', { locale: es }) }
    d.habits.forEach(h => {
      row[h.name] = (d.habitLogs || []).filter(
        l => l.habit_id === h.id && l.completed && l.date >= startISO && l.date <= endISO
      ).length
    })
    weeks.push(row)
  }
  return { data: weeks, habits: d.habits }
}

// ─── Calc: Bruce history ──────────────────────────────────────
function buildBruceHistory(d) {
  if (!d) return []
  return Array.from({ length: 12 }, (_, i) => {
    const offset = 11 - i
    const { start } = getWeekRange(offset)
    const score = calcBruceScore(d, offset)
    return { week: fmtLabel(start, 'd MMM'), score: score.total, isCurrent: offset === 0 }
  })
}

// ─── Calc: Radar ──────────────────────────────────────────────
function buildRadarData(d, weekOffset) {
  if (!d) return []
  function metrics(offset) {
    const { start, end } = getWeekRange(offset)
    const days = daysInRange(start, end)
    let expH = 0
    days.forEach(dt => {
      const dow = getDow(dt)
      expH += (d.habits || []).filter(h => !h.days_of_week?.length || h.days_of_week.includes(dow)).length
    })
    const doneH = (d.habitLogs || []).filter(l => l.completed && l.date >= start && l.date <= end).length
    const habitPct = expH > 0 ? Math.round((doneH / expH) * 100) : 0

    const gym = (d.gym || []).filter(g => g.attended && g.date >= start && g.date <= end).length
    const mma = (d.mma || []).filter(m => m.attended && m.date >= start && m.date <= end).length
    const workoutPct = Math.round(Math.min((gym + mma) / 5, 1) * 100)

    const stratusIds = new Set((d.habits || []).filter(h => h.name?.toLowerCase().includes('stratus')).map(h => h.id))
    const stratusDays = new Set((d.habitLogs || []).filter(l => l.date >= start && l.date <= end && stratusIds.has(l.habit_id) && l.completed).map(l => l.date)).size
    const stratusPct = Math.round(Math.min(stratusDays / 5, 1) * 100)

    const mentalDates = new Set([
      ...(d.journalEntries || []).map(j => j.created_at?.slice(0, 10)).filter(dt => dt && dt >= start && dt <= end),
      ...(d.mood || []).filter(m => m.date >= start && m.date <= end).map(m => m.date),
    ])
    const mentalPct = Math.round(Math.min(mentalDates.size / 7, 1) * 100)

    const hasFinance =
      (d.financeExpenses || []).some(e => e.date >= start && e.date <= end) ||
      (d.financeIncome || []).some(inc => inc.month >= start && inc.month <= end)

    return { habitPct, workoutPct, stratusPct, mentalPct, financePct: hasFinance ? 100 : 0 }
  }
  const cur = metrics(weekOffset)
  const prev = metrics(weekOffset + 1)
  return [
    { axis: 'Hábitos', semana: cur.habitPct, anterior: prev.habitPct },
    { axis: 'Entrenos', semana: cur.workoutPct, anterior: prev.workoutPct },
    { axis: 'Stratus', semana: cur.stratusPct, anterior: prev.stratusPct },
    { axis: 'Mental', semana: cur.mentalPct, anterior: prev.mentalPct },
    { axis: 'Finanzas', semana: cur.financePct, anterior: prev.financePct },
  ]
}

// ─── Calc: Heatmap 90 days ────────────────────────────────────
function buildHeatmap90(d) {
  if (!d) return []
  const counts = {}
  ;(d.habitLogs || []).filter(l => l.completed).forEach(l => { counts[l.date] = (counts[l.date] || 0) + 1 })

  const today = new Date()
  const startDate = subDays(today, 89)
  const startDow = (startDate.getDay() + 6) % 7

  const cells = []
  for (let i = 0; i < startDow; i++) cells.push({ date: null, count: -1 })
  for (let i = 0; i < 90; i++) {
    const dt = subDays(today, 89 - i)
    const iso = fmtISO(dt)
    cells.push({ date: iso, count: counts[iso] || 0 })
  }
  const rem = cells.length % 7
  if (rem > 0) for (let i = 0; i < 7 - rem; i++) cells.push({ date: null, count: -1 })
  return cells
}

// ─── Calc: Finance monthly ────────────────────────────────────
function buildFinanceMonthly(d) {
  if (!d) return []
  return Array.from({ length: 6 }, (_, i) => {
    const date = subMonths(new Date(), 5 - i)
    const mStart = format(startOfMonth(date), 'yyyy-MM-dd')
    const mEnd = format(endOfMonth(date), 'yyyy-MM-dd')
    const label = format(date, 'MMM yy', { locale: es })
    const income = (d.financeIncome || []).filter(r => r.month === mStart).reduce((s, r) => s + (r.amount || 0), 0)
    const expenses = (d.financeExpenses || []).filter(e => e.date >= mStart && e.date <= mEnd).reduce((s, e) => s + (e.amount || 0), 0)
    const savings = income > 0 ? Math.round(((income - expenses) / income) * 100) : null
    return { month: label, income: Math.round(income), expenses: Math.round(expenses), savings }
  })
}

// ─── Calc: Gym vs MMA ─────────────────────────────────────────
function buildGymVsMMA(d) {
  if (!d) return []
  const start30 = fmtISO(subDays(new Date(), 30))
  const gym = (d.gym || []).filter(g => g.attended && g.date >= start30).length
  const mma = (d.mma || []).filter(m => m.attended && m.date >= start30).length
  if (!gym && !mma) return []
  return [
    { name: 'Gym', value: gym, color: '#30D158' },
    { name: 'MMA', value: mma, color: '#FF9F0A' },
  ]
}

// ─── Sub-components ───────────────────────────────────────────
function NoData({ text }) {
  return <div className="h-full grid place-items-center text-xs text-white/25 text-center px-4">{text}</div>
}

function ArcProgress({ value, color, size = 110 }) {
  const r = size / 2 - 10
  const cx = size / 2, cy = size / 2
  const circ = 2 * Math.PI * r
  const filled = (Math.min(Math.max(value, 0), 100) / 100) * circ
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
      <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle" fill="white" fontSize="20" fontWeight="800">{value}</text>
      <text x={cx} y={cy + 17} textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize="10">pts</text>
    </svg>
  )
}

function ScoreBar({ label, value, max, color, detail }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px]">
        <span className="text-white/50">{label}</span>
        <span style={{ color }}>{value}/{max} pts · {detail}</span>
      </div>
      <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${max > 0 ? (value / max) * 100 : 0}%`, background: color }} />
      </div>
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

function HeatmapGrid({ days }) {
  const maxCount = Math.max(1, ...days.filter(c => c.count > 0).map(c => c.count))
  function cellColor(count) {
    if (count < 0) return 'transparent'
    if (count === 0) return 'rgba(255,255,255,0.04)'
    const pct = count / maxCount
    if (pct <= 0.25) return 'rgba(30,144,255,0.25)'
    if (pct <= 0.5) return 'rgba(30,144,255,0.45)'
    if (pct <= 0.75) return 'rgba(30,144,255,0.65)'
    return 'rgba(30,144,255,0.9)'
  }
  return (
    <div className="overflow-x-auto">
      <div style={{ display: 'grid', gridTemplateRows: 'repeat(7, 13px)', gridAutoFlow: 'column', gridAutoColumns: '13px', gap: '3px' }}>
        {days.map((cell, i) => (
          <div
            key={i}
            title={cell.date ? `${cell.date}: ${cell.count} hábitos` : ''}
            style={{ width: 13, height: 13, borderRadius: 3, backgroundColor: cellColor(cell.count) }}
          />
        ))}
      </div>
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────
export default function Analytics() {
  const [weekOffset, setWeekOffset] = useState(0)
  const dataQ = useAsync(() => fetchAnalyticsData(), [])
  const d = dataQ.data

  const bruceScore = useMemo(() => calcBruceScore(d, weekOffset), [d, weekOffset])
  const bruceLabel_ = bruceLabel(bruceScore.total)
  const bruceHistory = useMemo(() => buildBruceHistory(d), [d])
  const kpi = useMemo(() => calcKPI(d), [d])
  const { data: habitWeekData, habits: habitList } = useMemo(() => buildHabitsByWeek(d), [d])
  const radarData = useMemo(() => buildRadarData(d, weekOffset), [d, weekOffset])
  const heatmap = useMemo(() => buildHeatmap90(d), [d])
  const financeData = useMemo(() => buildFinanceMonthly(d), [d])
  const gymVsMMA = useMemo(() => buildGymVsMMA(d), [d])
  const weightSeries = useMemo(() => (d?.weight || []).slice(-90).map(w => ({ date: w.date.slice(5), kg: Number(w.weight_kg) })), [d])
  const moodSeries = useMemo(() => (d?.mood || []).slice(-30).map(m => ({ date: m.date.slice(5), mood: m.mood_score, sueño: Number(m.sleep_hours) })), [d])

  const { start: weekStart, end: weekEnd } = getWeekRange(weekOffset)
  const hasFin = financeData.some(m => m.income > 0 || m.expenses > 0)

  if (dataQ.loading) return (
    <div>
      <PageHeader title="Stats" subtitle="Tu vida en números" />
      <div className="text-sm text-white/30 mt-8 text-center">Cargando datos…</div>
    </div>
  )

  return (
    <div className="space-y-4">
      <PageHeader title="Stats" subtitle="Tu vida en números" />

      {/* ── 1. Score Bruce ── */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-[11px] text-white/35 uppercase tracking-wider font-semibold mb-0.5">Score Bruce</div>
            <div className="text-xs text-white/30">
              {fmtLabel(weekStart, 'd MMM')} – {fmtLabel(weekEnd, 'd MMM')}
              {weekOffset > 0 && <span className="ml-1 text-white/20">(hace {weekOffset} sem.)</span>}
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setWeekOffset(o => o + 1)}
              className="w-7 h-7 rounded-full bg-white/[0.07] hover:bg-white/[0.12] text-white/50 hover:text-white text-sm grid place-items-center transition"
            >←</button>
            <button
              onClick={() => setWeekOffset(o => Math.max(0, o - 1))}
              disabled={weekOffset === 0}
              className="w-7 h-7 rounded-full bg-white/[0.07] hover:bg-white/[0.12] text-white/50 hover:text-white text-sm grid place-items-center transition disabled:opacity-25 disabled:cursor-not-allowed"
            >→</button>
          </div>
        </div>

        <div className="flex gap-5 items-center">
          <div className="shrink-0">
            <ArcProgress value={bruceScore.total} color={bruceLabel_.color} size={110} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[15px] font-bold mb-3" style={{ color: bruceLabel_.color }}>{bruceLabel_.text}</div>
            <div className="space-y-2">
              <ScoreBar
                label="Hábitos"
                value={bruceScore.habitScore} max={50} color="#BF5AF2"
                detail={`${bruceScore.completedHabits}/${bruceScore.expectedHabits}`}
              />
              <ScoreBar
                label="Entrenos"
                value={bruceScore.workoutScore} max={30} color="#30D158"
                detail={`${bruceScore.workoutsThisWeek}/5 sesiones`}
              />
              <ScoreBar
                label="Stratus"
                value={bruceScore.stratusScore} max={20} color="#0A84FF"
                detail={`${bruceScore.stratusDays}/5 días`}
              />
            </div>
          </div>
        </div>
      </Card>

      {/* ── 2. 6 KPI Cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <KPICard
          label="Racha actual"
          value={kpi.currentStreak ?? 0}
          suffix=" días"
          color={kpi.currentStreak >= 7 ? '#FF9F0A' : kpi.currentStreak >= 3 ? '#30D158' : '#0A84FF'}
          note="consecutivos con hábitos"
        />
        <KPICard
          label="Mejor racha"
          value={kpi.bestStreak ?? 0}
          suffix=" días"
          color="#FFD700"
          note="en los últimos 90 días"
        />
        <KPICard
          label="Entrenos (mes)"
          value={kpi.workoutsMonth ?? 0}
          color="#30D158"
          note="gym + MMA este mes"
        />
        <KPICard
          label="Hábitos (mes)"
          value={`${kpi.habitMonthPct ?? 0}%`}
          color="#BF5AF2"
          note="completados del total"
        />
        <KPICard
          label="Peso actual"
          value={kpi.lastWeight != null ? kpi.lastWeight.toFixed(1) : '—'}
          suffix=" kg"
          color="#FF9F0A"
          note={
            kpi.weightTrend != null
              ? kpi.weightTrend > 0 ? `↑ +${kpi.weightTrend} kg vs 30d`
                : kpi.weightTrend < 0 ? `↓ ${kpi.weightTrend} kg vs 30d`
                  : 'sin cambio vs 30d'
              : 'sin datos recientes'
          }
        />
        <KPICard
          label="Libros 2026"
          value={kpi.books2026 ?? 0}
          color="#5AC8FA"
          note="completados este año"
        />
      </div>

      {/* ── 3. Hábitos por semana  |  4. Bruce histórico ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Hábitos por semana" subtitle="Días completados · últimas 8 semanas">
          <div className="h-52">
            {habitWeekData.length > 0 && habitList.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={habitWeekData} barCategoryGap="30%">
                  <CartesianGrid {...GR} />
                  <XAxis dataKey="week" {...AX} />
                  <YAxis {...AX} allowDecimals={false} />
                  <Tooltip {...TT} />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                  {habitList.map((h, i) => (
                    <Bar
                      key={h.id}
                      dataKey={h.name}
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

        <Card title="Score Bruce histórico" subtitle="Últimas 12 semanas">
          <div className="h-52">
            {bruceHistory.some(w => w.score > 0) ? (
              <ResponsiveContainer>
                <AreaChart data={bruceHistory}>
                  <defs>
                    <linearGradient id="bruceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFD700" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#FFD700" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid {...GR} />
                  <XAxis dataKey="week" {...AX} />
                  <YAxis {...AX} domain={[0, 100]} />
                  <Tooltip {...TT} formatter={(v) => [`${v}%`, 'Score']} />
                  <ReferenceLine y={70} stroke="#FFD700" strokeDasharray="4 3" opacity={0.4}
                    label={{ value: '70%', position: 'insideTopRight', fill: 'rgba(255,215,0,0.6)', fontSize: 10 }} />
                  <Area
                    type="monotone" dataKey="score"
                    stroke="#FFD700" strokeWidth={2.5}
                    fill="url(#bruceGrad)"
                    dot={({ cx, cy, payload }) => (
                      <circle key={payload.week} cx={cx} cy={cy}
                        r={payload.isCurrent ? 5 : 2.5}
                        fill="#FFD700"
                        stroke={payload.isCurrent ? 'white' : 'none'}
                        strokeWidth={payload.isCurrent ? 2 : 0}
                      />
                    )}
                    name="Score"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Sin datos de score aún" />
            )}
          </div>
        </Card>
      </div>

      {/* ── 5. Radar  |  6. Heatmap ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Perfil semanal" subtitle="Esta semana vs semana anterior">
          <div className="h-56">
            {radarData.some(r => r.semana > 0 || r.anterior > 0) ? (
              <ResponsiveContainer>
                <RadarChart data={radarData} outerRadius="70%">
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

        <Card title="Heatmap de hábitos" subtitle="Días completados · últimos 90 días">
          {heatmap.length > 0 ? (
            <>
              <HeatmapGrid days={heatmap} />
              <div className="flex items-center gap-2 mt-3 text-[11px] text-white/30">
                <span>0</span>
                {[0, 0.25, 0.45, 0.65, 0.9].map((o, i) => (
                  <div key={i} className="w-3 h-3 rounded-sm"
                    style={{ background: i === 0 ? 'rgba(255,255,255,0.04)' : `rgba(30,144,255,${o})` }}
                  />
                ))}
                <span>Máx</span>
              </div>
            </>
          ) : (
            <div className="h-32 grid place-items-center text-xs text-white/25">Sin datos</div>
          )}
        </Card>
      </div>

      {/* ── 7. Físico expandido ── */}
      <Card title="Peso corporal" subtitle="Kg · últimos 90 días">
        <div className="h-48">
          {weightSeries.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={weightSeries}>
                <CartesianGrid {...GR} />
                <XAxis dataKey="date" {...AX} />
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
            {moodSeries.length > 1 ? (
              <ResponsiveContainer>
                <LineChart data={moodSeries}>
                  <CartesianGrid {...GR} />
                  <XAxis dataKey="date" {...AX} />
                  <YAxis {...AX} domain={[0, 5]} />
                  <Tooltip {...TT} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="mood" stroke="#BF5AF2" strokeWidth={2.5} dot={{ r: 2 }} name="Mood" />
                  <Line type="monotone" dataKey="sueño" stroke="#0A84FF" strokeWidth={2} dot={{ r: 2 }} strokeDasharray="4 3" name="Sueño (h)" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <NoData text="Registrá tu estado en Mental" />
            )}
          </div>
        </Card>

        <Card title="Gym vs MMA" subtitle="Distribución de entrenos · 30 días">
          <div className="h-48">
            {gymVsMMA.length > 0 ? (
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={gymVsMMA} cx="50%" cy="45%" innerRadius={45} outerRadius={72} dataKey="value" paddingAngle={3}>
                    {gymVsMMA.map((entry, i) => <Cell key={i} fill={entry.color} />)}
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
      {hasFin && (
        <Card title="Finanzas" subtitle="Ingresos vs gastos · últimos 6 meses">
          <div className="h-52">
            <ResponsiveContainer>
              <BarChart data={financeData} barCategoryGap="30%">
                <CartesianGrid {...GR} />
                <XAxis dataKey="month" {...AX} />
                <YAxis {...AX} />
                <Tooltip {...TT} formatter={(v) => [`$${v.toLocaleString()}`, '']} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="income" fill="#30D158" radius={[4, 4, 0, 0]} name="Ingresos" />
                <Bar dataKey="expenses" fill="#FF453A" radius={[4, 4, 0, 0]} name="Gastos" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-3 mt-4">
            {financeData.slice(-3).map((m, i) => (
              <div key={i} className="text-center">
                <div className="text-[11px] text-white/35">{m.month}</div>
                <div className="text-xl font-bold" style={{ color: m.savings != null && m.savings >= 0 ? '#30D158' : '#FF453A' }}>
                  {m.savings != null ? `${m.savings}%` : '—'}
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
