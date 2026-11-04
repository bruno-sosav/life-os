import Card from '../../../shared/components/ui/Card.jsx'
import { fmt } from '../../../shared/lib/dates.js'

// 70 % es la regla de la racha
const tone = (pct) => (pct == null ? { stroke: '#5E6662', text: 'text-ink-400' }
  : pct >= 70 ? { stroke: '#2EBD85', text: 'text-up' }
    : pct >= 50 ? { stroke: '#E0B84A', text: 'text-warn' }
      : { stroke: '#F6465D', text: 'text-down' })

function deltaNote(delta) {
  if (delta == null) return 'sin semana anterior para comparar'
  if (delta > 0) return `+${delta} puntos vs la semana anterior`
  if (delta < 0) return `${delta} puntos vs la semana anterior`
  return 'igual que la semana anterior'
}

function Ring({ value, color, size = 104 }) {
  const r = size / 2 - 8
  const circ = 2 * Math.PI * r
  const filled = (Math.min(Math.max(value ?? 0, 0), 100) / 100) * circ
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`${value ?? 'sin datos'} por ciento`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1A201E" strokeWidth="7" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="7" strokeLinecap="round"
        strokeDasharray={`${filled} ${circ - filled}`} transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: 'stroke-dasharray 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)' }} />
      <text x="50%" y="52%" textAnchor="middle" dominantBaseline="middle" fill="#E8ECE9"
        fontFamily="JetBrains Mono, monospace" fontSize="20" fontWeight="700">{value == null ? '—' : `${value}%`}</text>
    </svg>
  )
}

export default function WeekCompliance({ summary, weekOffset, onWeekOffset }) {
  const { compliance, week_start: start, week_end: end } = summary
  const t = tone(compliance.pct)
  const missed = compliance.expected - compliance.done
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="label !mb-0.5">Cumplimiento de la semana</div>
          <div className="text-xs text-ink-400 font-mono">
            {fmt(start, 'd MMM')} – {fmt(end, 'd MMM')}{weekOffset > 0 && ` · hace ${weekOffset} sem.`}
          </div>
        </div>
        <div className="flex gap-1">
          <button onClick={() => onWeekOffset(weekOffset + 1)} aria-label="Semana anterior"
            className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">‹</button>
          <button onClick={() => onWeekOffset(Math.max(0, weekOffset - 1))} disabled={weekOffset === 0} aria-label="Semana siguiente"
            className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700 disabled:opacity-30 disabled:cursor-not-allowed">›</button>
        </div>
      </div>
      <div className="flex gap-5 items-center">
        <Ring value={compliance.pct} color={t.stroke} />
        <div className="flex-1 min-w-0 space-y-2">
          {compliance.expected ? (
            <>
              <div className="flex items-baseline gap-2 font-mono">
                <span className="text-2xl font-bold text-up">{compliance.done}</span>
                <span className="text-ink-500">/</span>
                <span className="text-2xl font-bold text-down">{missed}</span>
                <span className="text-xs text-ink-400 font-sans">hechas · faltaron</span>
              </div>
              <div className="flex gap-[2px] h-1.5" aria-hidden="true">
                <div className="bg-up rounded-sm" style={{ flex: compliance.done }} />
                <div className="bg-down rounded-sm" style={{ flex: missed }} />
              </div>
            </>
          ) : (
            <div className="text-sm text-ink-400">No tenías nada agendado</div>
          )}
          <div className={`text-xs ${compliance.delta > 0 ? 'text-up' : compliance.delta < 0 ? 'text-down' : 'text-ink-400'}`}>
            {deltaNote(compliance.delta)}
          </div>
        </div>
      </div>
    </Card>
  )
}
